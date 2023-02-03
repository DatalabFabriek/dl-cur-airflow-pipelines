"""
In dit script wordt een context manager (with) gebruikt om de
download_rocket_launches DAG mee te definiëren.
"""

import json
import pathlib

import airflow.utils.dates
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# 1: Anders hier is het with-statement dat gebruikt wordt
# om het DAG object aan te maken. Alle Operators die binnen dit
# statement vallen worden automatisch gekoppeld aan de DAG.
with DAG(
    dag_id="download_rocket_launches_v2",
    description="Download rocket pictures of recently launched rockets.",
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval="@daily",
) as dag:

    # 2: Wat hier moet opvallen is dat de parameter dag=dag is
    # weggelaten. Het with statement heeft het DAG object al
    # automatisch aan de BashOperator gekoppeld.
    download_launches = BashOperator(
        task_id="download_launches",
        bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",  # noqa: E501
    )

    def _get_pictures():
        # Ensure directory exists
        pathlib.Path("/tmp/images").mkdir(parents=True, exist_ok=True)

        # Download all pictures in launches.json
        with open("/tmp/launches.json") as f:
            launches = json.load(f)
            image_urls = [launch["image"] for launch in launches["results"]]
            for image_url in image_urls:
                try:
                    response = requests.get(image_url)
                    image_filename = image_url.split("/")[-1]
                    target_file = f"/tmp/images/{image_filename}"
                    with open(target_file, "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded {image_url} to {target_file}")
                except requests_exceptions.MissingSchema:
                    print(f"{image_url} appears to be an invalid URL.")
                except requests_exceptions.ConnectionError:
                    print(f"Could not connect to {image_url}.")

    # 2: En hier ook...
    get_pictures = PythonOperator(
        task_id="get_pictures", python_callable=_get_pictures, dag=dag
    )

    # 2: En ook hier...
    notify = BashOperator(
        task_id="notify",
        bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
    )

    download_launches >> get_pictures >> notify
