import pendulum
from airflow.decorators import dag
from airflow.decorators.python import python_task


@dag(start_date=pendulum.today(), schedule=None)
def python_operator_context_example():
    @python_task()
    def print_context_variables(
        data_interval_start=None, data_interval_end=None, run_id=None
    ):
        print(
            f"data_interval_start: {data_interval_start}\n"
            f"data_interval_end: {data_interval_end}\n"
            f"run_id: {run_id}"
        )

    print_context_variables()


python_operator_context_example()
