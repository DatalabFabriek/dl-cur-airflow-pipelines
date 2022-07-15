from asyncio import Task
import airflow.utils.dates
from airflow import DAG

with DAG(
    dag_id="task_branching",
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval=None,
) as dag:

    @Task
    def stap_1():
        bericht = 'hoi stap 2, stap 1 hier'
        return bericht

    @Task
    def stap_2(bericht):
        print(bericht)

    bericht = stap_1()
    stap_2(bericht)



