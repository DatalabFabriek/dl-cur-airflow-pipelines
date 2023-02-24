import csv
import json
import pendulum
import pandas as pd
import requests
from sqlalchemy import create_engine
from airflow.decorators import dag, python_task


# 1: File path met datum template
raw_path = "./data_store/raw/weer/{{ data_interval_start.to_date_string() }}.json"
curated_path = "./data_store/curated/weer/{{ data_interval_start.to_date_string() }}.csv"


@dag(
    # 2: Begint precies 7 dagen geleden
    start_date=pendulum.datetime(2023, 2, 9),
    # 3: Cron schema voor het dagelijks ophalen om 08:00 uur.
    schedule_interval="0 8 * * *",
    # 4: Deze setting zorgt dat hij ook intervallen in het verleden afspeelt
    catchup=True,
)
def opdracht_3():

    # 5: Start en end templates als input voor de API call
    @python_task
    def fetch_data(start, end, raw_path):

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

    @python_task
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

    @python_task
    def write_to_database(curated_path):
        df = pd.read_csv(curated_path, sep=";", quotechar='"')

        db = create_engine("postgresql://airflow:airflow@postgres/datawarehouse")
        conn = db.connect()

        # 6: if_exists = 'append', zodat records niet overschreven worden
        df.to_sql(schema="cursus", name="weer", con=conn, if_exists="append", index=False)

    start_template = "{{ data_interval_start.format('YYYYMMDD') }}01"
    end_template = "{{ data_interval_start.format('YYYYMMDD') }}23"

    # 7: Start en end templates als input
    fetched = fetch_data(start_template, end_template, raw_path)
    transformed = transform_data(raw_path, curated_path)
    database = write_to_database(curated_path)

    # 8: Operators los van de functie calls gekoppeld voor meer overzicht
    fetched >> transformed >> database


opdracht_3()
