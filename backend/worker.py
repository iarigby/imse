import os

from celery.result import AsyncResult

from celery import Celery
from redis import Redis

from backend.nosql.db import MongoDatabase
from backend.sql.db import SqlDatabase

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')


app = Celery('tasks',
             broker=os.environ.get('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:6379/0'),
             backend=os.environ.get('CELERY_RESULT_BACKEND', f'redis://{REDIS_HOST}:6379/0'),
             broker_connection_retry_on_startup=True)


def get_migration_task():
    celery_active = app.control.inspect().active()
    if celery_active is None:
        return

    active_tasks = celery_active[list(celery_active.keys())[0]]
    if active_tasks is None:
        return

    try:
        migration_task = next(task for task in active_tasks if 'migrate' in task["type"])
        migration_task_id = migration_task["id"]
    except StopIteration:
        r = Redis(host=REDIS_HOST)
        migration_task_id = r.get('migration_task_id')

    if migration_task_id is None:
        return
    # noinspection PyTypeChecker
    return AsyncResult(migration_task_id, app=app)


@app.task
def migrate():
    # on other pages check if session variable is changed. Eventually
    # the dashboard function will change it and pages will be reloaded
    mongo_client = MongoDatabase.database()
    mongo_db = MongoDatabase(mongo_client)
    engine = SqlDatabase.engine()
    SessionMaker = SqlDatabase.database(engine)
    with SqlDatabase.session(SessionMaker) as sql_db:
        mongo_db.add_users(sql_db.get_users())
        mongo_db.add_venues(sql_db.get_venues())
        mongo_db.add_events(sql_db.get_events())
    return "migration completed"


def launch_migrate():
    r = Redis(REDIS_HOST)
    task = migrate.delay()
    r.set('migration_task_id', task.id)
    return task


def clear_migrate_info():
    r = Redis(REDIS_HOST)
    r.flushdb()
