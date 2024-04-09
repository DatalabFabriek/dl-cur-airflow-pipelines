import airflow.utils.dates
from airflow.decorators import dag, task


@dag(
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval=None,
)
def task_condition():
    @task()
    def kies_stap_1(input):
        if input:
            return "stap_1a"
        else:
            return "stap_1b"

    @task()
    def stap_1a(): ...

    @task()
    def stap_1b(): ...

    @task()
    def stap_2(): ...

    def voer_stap_3_uit(): ...

    @task()
    def stap_3(input):
        if input:
            voer_stap_3_uit()

    kies_stap_1("stap_1a") >> [stap_1a(), stap_1b()] >> stap_2() >> stap_3()


task_condition()
