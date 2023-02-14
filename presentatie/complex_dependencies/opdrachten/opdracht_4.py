import csv
import json
import pandas as pd
import requests
import airflow.utils.dates
from sqlalchemy import create_engine
from airflow.decorators import dag, python_task, branch_task
from airflow.exceptions import AirflowSkipException


path_date_template = "{{ data_interval_start.to_date_string() }}"

raw_path = f"./data_store/raw/weer/{path_date_template}.json"
curated_path = f"./data_store/curated/weer/{path_date_template}.csv"


@dag(
    start_date=airflow.utils.dates.days_ago(7),
    schedule_interval="0 8 * * *",
    catchup=True,
)
def opdracht_4():

    # 1: Branch task die bepaalt of am of pm data opgehaald moet worden.
    @branch_task
    def pick_part_of_day(day):
        if (int(day) % 2) == 0:
            return "fetch_data_am"
        else:
            return "fetch_data_pm"

    @python_task
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

    # 2: Trigger rule zodat bij 1 van de 2 succes het transformeren plaatsvindt
    @python_task(trigger_rule="none_failed")
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

    # 3: Conditie toegevoegd voor de aanwezigheid van harde wind
    @python_task
    def check_for_wind(curated_path):
        df = pd.read_csv(curated_path, sep=";", quotechar='"')
        if df["windsnelheid"].max() <= 6:
            raise AirflowSkipException("Geen harde wind!")

    # 4: Stuur een berichtje wanneer harde wind plaatsvindt
    @python_task
    def send_message():
        print("Het was winderig!")

    @python_task
    def write_to_database(curated_path):
        df = pd.read_csv(curated_path, sep=";", quotechar='"')

        db = create_engine("postgresql://airflow:airflow@postgres/datawarehouse")
        conn = db.connect()

        df.to_sql(schema="cur", name="weer", con=conn, if_exists="append", index=False)

    api_date_template = "{{ data_interval_start.format('YYYYMMDD') }}"

    # 5: Tasks voor branching en conditie toegevoegd
    part_of_day = pick_part_of_day("{{ data_interval_start.day }}")
    # 6: fetch_data voor zowel am als pm gebruikt met verschillende task_id en inputs
    fetched_am = fetch_data.override(task_id="fetch_data_am")(
        f"{api_date_template}01", f"{api_date_template}12", raw_path
    )
    fetched_pm = fetch_data.override(task_id="fetch_data_pm")(
        f"{api_date_template}13", f"{api_date_template}23", raw_path
    )
    transformed = transform_data(raw_path, curated_path)
    wind_check = check_for_wind(curated_path)
    database = write_to_database(curated_path)

    part_of_day >> [fetched_am, fetched_pm] >> transformed
    transformed >> wind_check >> send_message()
    transformed >> database


opdracht_4()
