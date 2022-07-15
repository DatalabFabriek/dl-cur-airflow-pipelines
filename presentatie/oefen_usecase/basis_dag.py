import requests
import json
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="dag_condition",
    start_date=pendulum.datetime(2022, 7, 18)
)

def _fetch_data():

    url = "https://www.daggegevens.knmi.nl/klimatologie/uurgegevens"
    params = {"start":2022070100, "end":2022070123, "vars": "station_code:date:FH:T", "fmt":"json", "stns":310}

    result = requests.get(url=url, params=params).json()

    with open('./data_store/raw/weer.json') as f:
        json.dump(result, f)
