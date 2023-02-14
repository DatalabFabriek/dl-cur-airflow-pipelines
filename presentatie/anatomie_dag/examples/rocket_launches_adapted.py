"""
In dit script wordt de meest recente stijl gebruikt om
download_rocket_launches DAG mee te definiëren: de taskflow API.
"""

import json
import pathlib
import pendulum

import requests
import requests.exceptions as requests_exceptions
from airflow.operators.bash import BashOperator

# 1: Er wordt geen DAG of PythonOperator object meer geïmporteerd
# In plaats daarvan worden decorators voor beiden geïmporteerd
# die functies kunnen ombouwen tot dezelfde objecten.
from airflow.decorators.python import python_task
from airflow.decorators import dag


# 2: Hier wordt de dag-decorator gebruikt om van de 'download_rocket_launches'
# functie een DAG object te maken. De eigenschappen van de DAG definieer je in
# de decorator boven de functie. Sommige eigenschappen zoals het dag_id worden
# automatisch van de functienaam afgeleid.
@dag(
    description="Download rocket pictures of recently launched rockets.",
    start_date=pendulum.yesterday(tz="Europe/Amsterdam"),
    schedule_interval="@daily",
)
def download_rocket_launches_v3():
    download_launches = BashOperator(
        task_id="download_launches",
        bash_command="curl -o ./data_store/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",  # noqa: E501
        cwd="/opt/airflow"
    )

    # 3: Hier wordt de python_task-decorator gebruikt om van de functie
    # get_pictures een PythonOperator te maken. Ook hier wordt de de task-id
    # afgeleid van de de functienaam.
    @python_task()
    def get_pictures():
        # Ensure directory exists
        pathlib.Path("./data_store/images").mkdir(parents=True, exist_ok=True)

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

    # 4: Er is hier dus geen sprake meer van een aparte PythonOperator waar
    # de functie aan meegegeven wordt.

    notify = BashOperator(
        task_id="notify",
        bash_command='echo "There are now $(ls ./data_store/images/ | wc -l) images."',
        cwd="/opt/airflow"
    )

    # 5: Omdat de get_pictures() dankzij de decorator nu een
    # PythonOperator object teruggeeft wanneer je hem aanroept,
    # kun je de functie direct aanroepen bij het definiëren van de
    # afhankelijkheden met de andere Operator objecten.
    download_launches >> get_pictures() >> notify


# 6: Anders is dat de dag-functie nog wel onderaan het script aangeroepen
# moet worden om Airflow te laten weten dat hier een DAG wordt gedefinieerd.
download_rocket_launches_v3()
