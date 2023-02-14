import pendulum
from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator


@dag(start_date=pendulum.today(), schedule="@daily")
def macro_schedule_example():
    EmptyOperator(task_id="Nothing")


macro_schedule_example()
