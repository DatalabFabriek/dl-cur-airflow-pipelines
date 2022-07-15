######################
# Opdracht 1: Airflow in action, bonus
######################

# Run een losse task binnen een DAG
airflow tasks run example_bash_operator runme_0 2015-01-01

# Run een DAG binnen een specifieke datum (backfill)
airflow dags backfill example_bash_operator \
    --start-date 2015-01-01 \
    --end-date 2015-01-02