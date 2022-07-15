import sqlite3
import csv
import pandas as pd
import requests
import json
import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.exceptions import AirflowSkipException

with DAG(
    dag_id='opdracht_4',
    start_date=pendulum.datetime(2022, 7, 12), 
    schedule_interval='0 8 * * *'
) as dag:

    def _pick_part_of_day(day):
        
        if (int(day) % 2) == 0:
            return "fetch_data_am"
        else:
            return "fetch_data_pm"

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

    def _check_for_wind(curated_path):
        
        df = pd.read_csv(curated_path, sep=';', quotechar='"')
        if df['windsnelheid'].max() <= 6:
            raise AirflowSkipException("Geen harde wind!")
        
    def _send_message():
        print("Het was winderig!")

    def _write_to_database(curated_path):

        df = pd.read_csv(curated_path, sep=';', quotechar='"') 
        conn = sqlite3.connect('./data_store/database/weer.db')
        df.to_sql('weer', conn, if_exists='append', index=False)
        conn.close()


    pick_part_of_day = BranchPythonOperator(
        task_id='pick_part_of_day',
        python_callable=_pick_part_of_day,
        op_kwargs={'day': '{{data_interval_start.day}}'}
    )

    fetch_data_am = PythonOperator(
        task_id='fetch_data_am',
        python_callable=_fetch_data,
        op_kwargs={
            'start': '{{ds_nodash}}01',
            'end': '{{ds_nodash}}12',
            'raw_path': './data_store/raw/weer/{{ds}}.json'
        }
    )

    fetch_data_pm = PythonOperator(
        task_id='fetch_data_pm',
        python_callable=_fetch_data,
        op_kwargs={
            'start': '{{ds_nodash}}13',
            'end': '{{ds_nodash}}24',
            'raw_path': './data_store/raw/weer/{{ds}}.json'
        }
    )

    sanitize_data = PythonOperator(
        task_id='sanitize_data',
        python_callable=_sanitize_data,
        trigger_rule='all_done',
        op_kwargs={
            'raw_path': './data_store/raw/weer/{{ds}}.json',
            'curated_path': './data_store/curated/weer/{{ds}}.csv'
        }
    )

    check_for_wind = PythonOperator(
        task_id='check_for_wind',
        python_callable=_check_for_wind,
        op_kwargs={'curated_path': './data_store/curated/weer/{{ds}}.csv'}
    )

    send_koen_message = PythonOperator(
        task_id='send_koen_message',
        python_callable=_send_message
    )

    write_to_database = PythonOperator(
        task_id='write_to_database',
        python_callable=_write_to_database,
        op_kwargs={
            'curated_path': './data_store/curated/weer/{{ds}}.csv'
        }
    )

    pick_part_of_day >> [fetch_data_am, fetch_data_pm] >> sanitize_data 
    sanitize_data >> check_for_wind >> send_koen_message
    sanitize_data >> write_to_database


