# Airflow Development Setup
A complete development environment setup for working with Airflow, largely following the setup provided by [this github repo by ninja-van](https://github.com/ninja-van/airflow-boilerplate.git), but trimmed down and somewhat adapted/updated using the more recent [quickstart guide provided by apache airflow](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html#docker-compose-yaml).

![The overall setup diagram](/images/setup_diagram.png)

# Getting Started

Install `docker` and `docker-compose` at:
- https://docs.docker.com/install/
- https://docs.docker.com/compose/install/

Clone this repo and `cd` into it:
```
git clone https://github.com/DatalabFabriek/dl-air-devsetup.git && cd dl-air-devsetup
```

Create a virtualenv for this project. Feel free to choose your preferred way of managing Python virtual 
environments. I usually do it this way:
```
python3 -m venv .venv
```

Activate the virtual environment:
```
source .venv/bin/activate
```

Install the requirements (if required):
```
pip install apache-airflow psycopg2-binary
pip install -r requirements-airflow.txt
pip install -r requirements-dev.txt
```


# Setting up the Docker environment

If you only want the DB to be up because you will mostly work using your local IDE (e.g. vs-code):
```
docker-compose -f docker/docker-compose.yml up -d airflow-init
```

If you want the whole suit of Airflow components to be up and running:
```
docker-compose -f docker/docker-compose.yml up -d
```
This brings up the Airflow `postgres` metadatabase, `scheduler`, and `webserver`.

To access the `webserver`, once the Docker container is up and healthy, go to `localhost:8080`.


*NOTE: If the `docker-compose` command does not work, try `docker compose`.*
*It means you installed Docker Compose as a plugin for Docker instead of as a program on itself.*

*NOTE: Although the default airflow image that is being pulled is the latest version, it could be that*
*docker nevertheless uses a previous version when this image is already in your local registry. In that case,*
*remove the older image from your local registry and rebuild the image.*
```
docker-compose -f docker/docker-compose.yml up -d --build
```

# Setting up Visual Studio Code

Ensure that your Project Interpreter is pointing to the correct virtual environment.

![Ensure that your Project Interpreter is pointing to the correct virtual environment](/images/interpreter.png)

Run `source dev_env.sh` on the terminal and copy the environment variables into .env file.
You could call it `.debug_env` for example. (Don't forget to add it to the .gitignore of your project)

![Run env.sh and copy the env vars](/images/environment_variables.png)

Add a new run/debug configuration using a launch.json file, altering/adding the following parameters:  
- name: `<whatever_you_want>`   
- program: `<path_to_your_virtualenv_airflow_executable>`
- args: `tasks test <dag_id> <task_id> <execution_date>` 
- envFile: `<path_to_the_.env_file_you_just_created>`

![Example run/debug configuration](/images/run_debug_config.png)

# Generating a new fernet key
Included in this dev setup is a pre-generated fernet key. There should not be any security concern here
because after all you are meant to run this environment only locally. If you wish to have a new fernet key,
you can follow these steps below.

Generate a fernet key:
```
python -c "from cryptography.fernet import Fernet; FERNET_KEY = Fernet.generate_key().decode(); print(FERNET_KEY)"
```

Copy that fernet key to clipboard.
In `dev_env.sh`, paste it here:
```
export AIRFLOW__CORE__FERNET_KEY=<YOUR_FERNET_KEY_HERE>
```

In `airflow.cfg`, paste it here:
```
fernet_key = <YOUR_FERNET_KEY_HERE>
```

# Caveats
- The PyPi packages are installed during build time instead of run time, to minimise the start-up time of our 
development environment. As a side-effect, if there is any new PyPi packages, the images need to be rebuilt. 
You can do so by passing the extra `--build` flag:
  ```
  docker-compose -f docker/docker-compose.yml up -d --build
  ```

- Not related to the build environment, but rather how Airflow works - some of the configs (like `rbac = True`) 
you change in `airflow.cfg` might not be reflected immediately on runtime, because they are static 
configurations and are only evaluated once in the startup. To solve that problem, just restart your `webserver`:
  ```
  docker-compose -f docker/docker-compose.yml restart airflow_webserver
  ```
- Not related to the build environment, but rather how Airflow works - you cannot have a ;
package/module in `dags/` and `plugins/` with the same name. This will likely give you a `ModuleNotFoundError`

# Concluding tips
- If you are only interested in just using your IDE, and you do not need the Airflow `scheduler` or `webserver`, run:
  ```
  docker-compose -f docker/docker-compose.yml up -d airflow_initdb
  ```

- To add the examples from the Webserver, change the following line in the `airflow.cfg`:
  ```
  load_examples = False
  ```
  Notice that the `docker-compose` immediately picks up the changes in `airflow.cfg`.
