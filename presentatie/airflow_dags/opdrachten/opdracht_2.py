import csv
import json

import pandas as pd
import pendulum
import requests
from airflow.decorators import dag
from airflow.decorators.python import task
from sqlalchemy import create_engine

raw_path = "./data_store/raw/weer/2024-04-09.json"
curated_path = "./data_store/curated/weer/2024-04-09.csv"


@dag(start_date=pendulum.datetime(2024, 4, 9, tz="Europe/Amsterdam"), schedule=None)
def opdracht_2():

    @task()
    def fetch_data(raw_path):
        url = "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens"
        params = {
            "start": 2024040901,
            "end": 2024040923,
            "vars": "station_code:date:FH:RH:T",
            "fmt": "json",
            "stns": 310,
        }

        result = requests.get(url=url, params=params).json()

        with open(raw_path, "w") as f:
            json.dump(result, f, indent=4)

    @task()
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

    @task()
    def write_to_database(curated_path):
        df = pd.read_csv(curated_path, sep=";", quotechar='"')

        db = create_engine("postgresql://airflow:airflow@postgres/datawarehouse")
        conn = db.connect()

        df.to_sql(
            schema="cursus", name="weer", con=conn, if_exists="replace", index=False
        )

    (
        fetch_data(raw_path)
        >> transform_data(raw_path, curated_path)
        >> write_to_database(raw_path)
    )


opdracht_2()
