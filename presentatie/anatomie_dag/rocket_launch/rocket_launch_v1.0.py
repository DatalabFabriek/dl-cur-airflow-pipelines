"""
In dit script wordt de oude/basis stijl van Airflow gebruikt om
de download_rocket_launches te definiëren.
"""

import json
import pathlib

# 1: Hier importeer je alle relevante packages
# Zowel voor het definiëren van je DAG ...
from airflow import DAG
import airflow.utils.dates
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
# ... als voor de logica in je tasks
import requests
import requests.exceptions as requests_exceptions

# 2: Dit object refereert naar je DAG en alle settings/eigenschappen
# die je eraan wilt geven. Van ids, tot beschrijvingen, tot tijdschema's
dag = DAG(
    dag_id="download_rocket_launches_v1",
    description="Download rocket pictures of recently launched rockets.",
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval="@daily",
)

# 3: Hier wordt een BashOperator gebruikt om de task 'download_launches'
# te definiëren. Deze operator geeft de mogelijkheid om Bash commando's
# aan te roepen in een van je tasks.
download_launches = BashOperator(
    task_id="download_launches",
    bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.0.0/launch/upcoming'",  # noqa: E501
    dag=dag,
)


# 4: Hier wordt een functie gebruikt die de custom logica van de task
# 'get_pictures' definieert. Wat er in de task gebeurt beschrijf je net zoals
# in elke andere Python functie.
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


# 5: Hier wordt de functie '_get_pictures' meegegeven aan een PythonOperator.
# Door het in een PythonOperator object te verpakken kan Airflow het oppakken
# en als een task in de pipeline uitvoeren.
get_pictures = PythonOperator(
    task_id="get_pictures", python_callable=_get_pictures, dag=dag
)

# 6: Wederom een BashOperator om de laatste taak te definiëren.
notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
    dag=dag,
)

# 7: De drie Operator objecten die eerder hierboven gemaakt zijn
# worden hier aan elkaar gekoppeld. De afhankelijkheden en de richting
# tussen taken worden hier aangegeven, zodat Airflow begrijpt hoe het
# verloop van de DAG in elkaar steekt.
download_launches >> get_pictures >> notify
