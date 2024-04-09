import airflow.utils.dates
from airflow.decorators import dag, task


@dag(
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval=None,
)
def xcoms():
    @task()
    def stap_1():
        bericht = "hoi stap 2, stap 1 hier"
        return bericht

    @task()
    def stap_2(bericht):
        print(bericht)

    stap_1 >> stap_2


xcoms()
