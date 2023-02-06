import airflow.utils.dates
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator

with DAG(
    dag_id="dag_branching",
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval=None,
) as dag:

    def _stap_1a(): pass
    def _stap_1b(): pass
    def _stap_2(): pass
    def _stap_3(): pass

    def _kies_stap_1(input):
        if input:
            return "stap_1a"
        else:
            return "stap_1b"

    kies_stap_1 = BranchPythonOperator(
        task_id="kies_stap_1",
        python_callable=_kies_stap_1,
        op_kwargs={'input': 'stap_1a'}
    )

    stap_1a = PythonOperator(
        task_id="stap_1a",
        python_callable=_stap_1a
    )

    stap_1b = PythonOperator(
        task_id="stap_1b",
        python_callable=_stap_1b
    )

    stap_2 = PythonOperator(
        task_id="stap_2",
        python_callable=_stap_2,
        trigger_rule='none_failed'
    )

    stap_3 = PythonOperator(
        task_id="stap_3",
        python_callable=_stap_3
    )

    kies_stap_1 >> [stap_1a, stap_1b] >> stap_2 >> stap_3

