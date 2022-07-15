import sqlite3
import csv
import pandas as pd
import requests
import json
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id='opdracht_2',
    start_date=pendulum.datetime(2022, 7, 18)
)

def _fetch_data():

    url = 'https://www.daggegevens.knmi.nl/klimatologie/uurgegevens'
    params = {
        'start':2022070100, 'end':2022070123, 'vars': 'station_code:date:FH:RH:T', 
        'fmt':'json', 'stns':310
    }

    result = requests.get(url=url, params=params).json()

    with open('./data_store/raw/weer.json', 'w') as f:
        json.dump(result, f, indent=4)

def _sanitize_data():
    
    df = pd.read_json('./data_store/raw/weer.json')
    
    df['date'] = pd.to_datetime(df['date']).dt.date
    df[["FH", "RH", 'T']] = df[["FH", "RH", 'T']].apply(lambda x: x / 10)
    df.columns = ['station', 'datum', 'uur', 'windsnelheid', 'neerslag', 'temperatuur']

    df.to_csv(
        path_or_buf='./data_store/curated/weer.csv', index=False, 
        sep=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC
    )

def _write_to_database():

    df = pd.read_csv('./data_store/curated/weer.csv',sep=';', quotechar='"') 
    conn = sqlite3.connect('./data_store/database/weer.db')
    df.to_sql('weer', conn, if_exists='append', index=False)
    conn.close()


fetch_data = PythonOperator(
    task_id='fetch_data',
    python_callable=_fetch_data,
    dag=dag
)

sanitize_data = PythonOperator(
    task_id='sanitize_data',
    python_callable=_sanitize_data,
    dag=dag
)

write_to_database = PythonOperator(
    task_id='write_to_database',
    python_callable=_write_to_database,
    dag=dag
)

fetch_data >> sanitize_data >> write_to_database


