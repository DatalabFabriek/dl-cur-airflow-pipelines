import airflow.utils.dates
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(
    dag_id="xcoms",
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval=None,
) as dag:

    def _stap_1():
        bericht = 'hoi stap 2, stap 1 hier'
        return bericht

    def _stap_2(**context):
        bericht = context['task_instance'].xcom_pull(
            task_ids='stap_1', key='bericht'
        )
        print(bericht)

    stap_1 = PythonOperator(
        task_id="stap_1",
        python_callable=_stap_1
    )

    stap_2 = PythonOperator(
        task_id="stap_2",
        python_callable=_stap_2
    )

    stap_1 >> stap_2



