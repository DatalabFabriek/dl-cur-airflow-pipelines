######################
# Opdracht 1: Airflow in action
######################

# 1) Maak een nieuwe project folder aan
mkdir airflow_cursus
cd airflow_cursus

# 2) Zet een virtual environment op
python3 -m venv .venv
source .venv/bin/activate

# 3) Installeer airflow
pip install apache-airflow

# 4) Maak een airflow folder aan en exporteer deze als variabele
mkdir airflow
export AIRFLOW_HOME=$(pwd)/airflow

# 5) Run airflow lokaal
airflow standalone

# óf met individuele stappen
# airflow db init
# airflow users create \
#         --username admin \
#         --firstname Peter \
#         --lastname Parker \
#         --role Admin \
#         --email spiderman@superhero.org
# airflow webserver --port 8080
# airflow scheduler