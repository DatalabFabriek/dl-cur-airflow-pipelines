import pendulum
from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.timetables.base import Timetable


class AfterWorkdayTimetable(Timetable):
    pass


@dag(start_date=pendulum.today(), schedule=AfterWorkdayTimetable())
def macro_schedule_example():
    EmptyOperator(task_id="Nothing")


macro_schedule_example()
