from datetime import timedelta
import pendulum
from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator


@dag(start_date=pendulum.today(), schedule=timedelta(1))
def macro_schedule_example():
    EmptyOperator(task_id="Nothing")


macro_schedule_example()
