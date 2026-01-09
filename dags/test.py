from __future__ import annotations

# [START simplest_dag]
from airflow.sdk import dag, task


@dag
def example_simple_dag():
    @task
    def my_task():
        pass

    my_task()


# [END simplest_dag]

example_simple_dag()