import airflow.utils.dates
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG(
    dag_id="task_branching",
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval=None,
) as dag:

    def _stap_1a(): pass
    def _stap_1b(): pass
    def _stap_2(): pass
    def _stap_3(): pass

    def _stap_1(input):
        if input:
            _stap_1a()
        else:
            _stap_1b()

    stap_1 = PythonOperator(
        task_id="stap_1",
        python_callable=_stap_1
    )

    stap_2 = PythonOperator(
        task_id="stap_2",
        python_callable=_stap_2
    )

    stap_3 = PythonOperator(
        task_id="stap_3",
        python_callable=_stap_3
    )

    stap_1 >> stap_2 >> stap_3



