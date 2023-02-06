import csv
import json
import pandas as pd
import requests
import pendulum
from sqlalchemy import create_engine
from airflow.decorators import dag
from airflow.decorators.python import python_task


@dag(start_date=pendulum.datetime(2023, 2, 5))
def opdracht_2():

    @python_task
    def fetch_data():

        url = "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens"
        params = {
            "start": 2022070100,
            "end": 2022070123,
            "vars": "station_code:date:FH:RH:T",
            "fmt": "json",
            "stns": 310,
        }

        result = requests.get(url=url, params=params).json()

        with open("data_store/raw/weer.json", "w") as f:
            json.dump(result, f, indent=4)

    @python_task
    def clean_and_transform_data():

        df = pd.read_json("./data_store/raw/weer.json")

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
            path_or_buf="./data_store/curated/weer.csv",
            index=False,
            sep=";",
            quotechar='"',
            quoting=csv.QUOTE_NONNUMERIC,
        )

    @python_task
    def write_to_database():

        df = pd.read_csv("./data_store/curated/weer.csv", sep=";", quotechar='"')

        db = create_engine("postgresql://airflow:airflow@postgres/datawarehouse")
        conn = db.connect()

        df.to_sql(schema="cur", name="weer", con=conn, if_exists="replace", index=False)

    fetch_data() >> clean_and_transform_data() >> write_to_database()


opdracht_2()
