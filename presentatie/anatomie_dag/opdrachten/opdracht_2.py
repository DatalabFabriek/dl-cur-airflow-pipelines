import csv
import json
import pandas as pd
import requests
import pendulum
from sqlalchemy import create_engine
from airflow.decorators import dag
from airflow.decorators.python import python_task


raw_path = "./data_store/raw/weer/2023-02-13.json"
curated_path = "./data_store/curated/weer/2023-02-13.csv"


@dag(start_date=pendulum.today())
def opdracht_2():

    @python_task
    def fetch_data(raw_path):
        url = "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens"
        params = {
            "start": 2023021301,
            "end": 2023021323,
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

        df.to_sql(schema="cur", name="weer", con=conn, if_exists="replace", index=False)

    fetch_data() >> transform_data() >> write_to_database()


opdracht_2()
