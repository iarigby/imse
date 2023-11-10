# IMSE




### Environment Variables
These are ready in Pycharm run configurations.

```shell
DB_TYPE=sql
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```

## Development
### Setup
Prerequisites

- poetry
- docker
- postgresql (`brew install postgresql`)

Installation
```shell
poetry install
```

## Running

```shell
docker compose up
poetry run streamlit run ui/dashboard.py
```
Task queue is part of docker services, but can be run separately as well
```shell
poetry run celery --app backend.worker worker --loglevel INFO
```

## Tech Stack


#### Redis for Persisting Application State

## TODO

- https://docs.streamlit.io/library/api-reference/connections/st.connections.sqlconnection
- https://pypi.org/project/celery-progress/


### Issues
- cannot launch streamlit inside a container