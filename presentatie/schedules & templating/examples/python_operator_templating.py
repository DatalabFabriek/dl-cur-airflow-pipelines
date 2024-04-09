import pendulum
from airflow.decorators import dag
from airflow.decorators.python import task


@dag(start_date=pendulum.today(), schedule=None)
def python_operator_templating_example():
    @task()
    def print_interval_start(interval_string, data_interval_end=None):
        print(interval_string)
        print(data_interval_end.format("YYMMDD"))

    print_interval_start(
        "Het interval begint op: {{ data_interval_end.format('YYMMDD') }}"
    )


python_operator_templating_example()
