import airflow.utils.dates
from airflow.decorators import dag, python_task


@dag(
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval=None,
)
def task_branching():
    def stap_1a():
        ...

    def stap_1b():
        ...

    @python_task
    def stap_1(input):
        if input:
            stap_1a()
        else:
            stap_1b()

    def stap_2():
        ...

    def stap_3():
        ...

    stap_1() >> stap_2() >> stap_3()


task_branching()
