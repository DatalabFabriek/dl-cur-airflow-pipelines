"""
In dit script wordt de meest recente stijl gebruikt om
download_rocket_launches DAG mee te definiëren: de taskflow API.
"""

import json
import pathlib

import pendulum
import requests
import requests.exceptions as requests_exceptions

# 1: Er wordt geen DAG of PythonOperator object meer geïmporteerd
# In plaats daarvan worden decorators voor beiden geïmporteerd
# die functies kunnen ombouwen tot dezelfde objecten.
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator


# 2: Hier wordt de dag-decorator gebruikt om van de 'download_rocket_launches'
# functie een DAG object te maken. De eigenschappen van de DAG definieer je in
# de decorator boven de functie. Sommige eigenschappen zoals het dag_id worden
# automatisch van de functienaam afgeleid.
@dag(
    description="Download rocket pictures of recently launched rockets.",
    start_date=pendulum.today(),
    schedule_interval="@daily",
)
def download_rocket_launches_v3():
    download_launches = BashOperator(
        task_id="download_launches",
        bash_command="curl -o ./data_store/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",  # noqa: E501
        cwd="/opt/airflow",
        dag=dag,
    )

    @task()
    def get_pictures():
        # Ensure directory exists
        pathlib.Path("./data_store/images").mkdir(parents=True, exist_ok=True)

        number_of_images = 0
        # Download all pictures in launches.json

        # Download all pictures in launches.json
        with open("./data_store/launches.json") as f:
            launches = json.load(f)
            image_urls = [launch["image"] for launch in launches["results"]]
            for image_url in image_urls:
                try:
                    response = requests.get(image_url)
                    image_filename = image_url.split("/")[-1]
                    target_file = f"./data_store/images/{image_filename}"
                    with open(target_file, "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded {image_url} to {target_file}")
                except requests_exceptions.MissingSchema:
                    print(f"{image_url} appears to be an invalid URL.")
                except requests_exceptions.ConnectionError:
                    print(f"Could not connect to {image_url}.")

        print(f"There are now {len(number_of_images)} images.")

    download_launches >> get_pictures()


download_rocket_launches_v3()
