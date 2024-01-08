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

- python 3.11
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

## Architecture

![](./architecture.png)
### Tech Stack
- `SqlAlchemy` and `pymongo` libraries are used for database driver.
- `Streamlit` is used as the main user facing application. This library allows developers to create a reactive server in pure python. UI elements are defined in python files and generate html when the client connects, while the database connections are kept on server side.
- `Celery` - We would like to keep long-running processes independent of the user facing application server in order to have a more robust and reliable service. The database migration is dispatched as a celery task which will run independently of the application server. 


### Packages
#### backend
- Database operations and schemas
- celery tasks

#### ui
All the files in this package are ui components, and are rendered when the user visits the corresponding page (`dashboard.py` is the homepage, and `pages` folder has the rest of the website pages). Connections to the database and celery workers are handled in `server_connections`


### Deployment (docker-compose.yml Services)
following containers are part of the full deployment
- postgres
- mongo
- redis
- our package - entrypoint `celery backend/worker.py`  for running celery workers
- our package - entrypoint `streamlit ui/dashboard.py` for running the application

### Exporting sql scripts
```shell
poetry run export_schemas
```

I also set up to do it from alembic but the result is same. Still will document the process
#### Setup
```shell
alembic init alembic
```
Change alembic configuration in `env.py`:
```python
from backend.sql.models import Base
# find this line and change to
# target_metadata = None
target_metadata = Base.metadata
```

Change sqlalchemy url in `alembic.ini` to `postgresql://postgres:postgres@localhost/backend`

#### Generate
```
alembic revision --autogenerate -m "initialise schemas"
```

copy revision number from the output

```shell
alembic upgrade $REVISION_NUMBER --sql > create_table.sql
```
You will need to delete `alembic/versions` to regenerate it

## TODO

### Later/maybe
- track task progress https://pypi.org/project/celery-progress/

