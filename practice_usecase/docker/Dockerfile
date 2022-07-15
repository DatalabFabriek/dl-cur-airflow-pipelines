# NOTE: paths are relative to the project root since the build context we specify is the project root
# NOTE: Uncomment the user + apt installation part to install apt-packages

FROM apache/airflow:latest-python3.9
# USER root

# RUN apt-get update -y \
#     && apt-get install -y --no-install-recommends \
#             # add apt packages \
#     && apt-get autoremove -yqq --purge \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

COPY requirements-airflow.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# USER airflow
