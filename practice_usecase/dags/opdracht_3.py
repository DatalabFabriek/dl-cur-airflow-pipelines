import sqlite3
import csv
import pandas as pd
import requests
import json
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(
    dag_id='opdracht_3',
    start_date=pendulum.datetime(2022, 7, 12), 
    schedule_interval='0 8 * * *'
) as dag:

    def _fetch_data(start, end, raw_path):

        url = 'https://www.daggegevens.knmi.nl/klimatologie/uurgegevens'
        params = {
            'start':start, 'end':end, 'vars': 'station_code:date:FH:RH:T', 
            'fmt':'json', 'stns':310
        }

        result = requests.get(url=url, params=params).json()

        with open(raw_path, 'w') as f:
            json.dump(result, f, indent=4)

    def _sanitize_data(raw_path, curated_path):
        
        df = pd.read_json(raw_path)
        
        df['date'] = pd.to_datetime(df['date']).dt.date
        df[["FH", "RH", "T"]] = df[["FH", "RH", "T"]].apply(lambda x: x / 10)
        df.columns = ['station', 'datum', 'uur', 'windsnelheid', 'neerslag', 'temperatuur']

        df.to_csv(
            path_or_buf=curated_path, index=False, 
            sep=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC
        )

    def _write_to_database(curated_path):

        df = pd.read_csv(curated_path,sep=';', quotechar='"') 
        conn = sqlite3.connect('./data_store/database/weer.db')
        df.to_sql('weer', conn, if_exists='append', index=False)
        conn.close()


    fetch_data = PythonOperator(
        task_id='fetch_data',
        python_callable=_fetch_data,
        op_kwargs={
            'start': '{{ds_nodash}}01',
            'end': '{{ds_nodash}}24',
            'raw_path': './data_store/raw/weer/{{ds}}.json'
        }
    )

    sanitize_data = PythonOperator(
        task_id='sanitize_data',
        python_callable=_sanitize_data,
        op_kwargs={
            'raw_path': './data_store/raw/weer/{{ds}}.json',
            'curated_path': './data_store/curated/weer/{{ds}}.csv'
        }
    )

    write_to_database = PythonOperator(
        task_id='write_to_database',
        python_callable=_write_to_database,
        op_kwargs={
            'curated_path': './data_store/curated/weer/{{ds}}.csv'
        }
    )

    fetch_data >> sanitize_data >> write_to_database


