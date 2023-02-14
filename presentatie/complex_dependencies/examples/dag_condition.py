import airflow.utils.dates
from airflow.decorators import dag, python_task, branch_task
from airflow.exceptions import AirflowSkipException


@dag(
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval=None,
)
def task_condition():
    @branch_task
    def kies_stap_1(input):
        if input:
            return "stap_1a"
        else:
            return "stap_1b"

    @python_task
    def stap_1a():
        ...

    @python_task
    def stap_1b():
        ...

    @python_task
    def stap_2():
        ...

    @python_task
    def stap_3_wel_of_niet(input):
        if input:
            raise AirflowSkipException("Voer stap 3 niet uit!")

    @python_task
    def stap_3():
        ...

    kies_stap_1() >> [stap_1a(), stap_1b()] >> stap_2() >> stap_3()
    stap_3_wel_of_niet >> stap_3()


task_condition()
