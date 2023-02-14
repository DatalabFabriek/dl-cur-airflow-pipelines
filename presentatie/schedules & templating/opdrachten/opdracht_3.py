import csv
import json
import pandas as pd
import requests
import airflow.utils.dates
from sqlalchemy import create_engine
from airflow.decorators import dag, python_task


# 1: File path met datum template
path_date_template = "{{ data_interval_start.to_date_string() }}"

raw_path = f"./data_store/raw/weer/{path_date_template}.json"
curated_path = f"./data_store/curated/weer/{path_date_template}.csv"


@dag(
    # 2: Begint precies 7 dagen geleden
    start_date=airflow.utils.dates.days_ago(7),
    # 3: Cron schema voor het dagelijks ophalen om 08:00 uur.
    schedule_interval="0 8 * * *",
    # 4: Deze setting zorgt dat hij ook intervallen in het verleden afspeelt
    catchup=True,
)
def opdracht_3():

    # 5: Start en end templates als input voor de API call
    @python_task()
    def fetch_data(start, end, raw_path):
        print(start)
        print(end)
        url = "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens"
        params = {
            "start": start,
            "end": end,
            "vars": "station_code:date:FH:RH:T",
            "fmt": "json",
            "stns": 310,
        }

        result = requests.get(url=url, params=params).json()

        with open(raw_path, "w") as f:
            json.dump(result, f, indent=4)

    @python_task()
    def transform_data(raw_path, curated_path):
        df = pd.read_json(raw_path)

        df["date"] = pd.to_datetime(df["date"]).dt.date
        df[["FH", "RH", "T"]] = df[["FH", "RH", "T"]] / 10
        df.columns = [
            "station",
            "datum",
            "uur",
            "windsnelheid",
            "neerslag",
            "temperatuur",
        ]

        df.to_csv(
            path_or_buf=curated_path,
            index=False,
            sep=";",
            quotechar='"',
            quoting=csv.QUOTE_NONNUMERIC,
        )

    @python_task()
    def write_to_database(curated_path):
        df = pd.read_csv(curated_path, sep=";", quotechar='"')

        db = create_engine("postgresql://airflow:airflow@postgres/datawarehouse")
        conn = db.connect()

        # 6: if_exists = 'append', zodat records niet overschreven worden
        df.to_sql(schema="cur", name="weer", con=conn, if_exists="append", index=False)

    api_date_template = "{{ data_interval_start.format('YYYYMMDD') }}"

    # 7: Start en end templates als input
    fetched = fetch_data(f"{api_date_template}01", f"{api_date_template}23", raw_path)
    transformed = transform_data(raw_path, curated_path)
    database = write_to_database(curated_path)

    # 8: Operators los van de functie calls gekoppeld voor meer overzicht
    fetched >> transformed >> database


opdracht_3()
