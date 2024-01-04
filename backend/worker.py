import os
from time import sleep

from celery.result import AsyncResult

from celery import Celery
from redis import Redis


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
    sleep(15)
    return "migration completed"


def launch_migrate():
    r = Redis(REDIS_HOST)
    task = migrate.delay()
    r.set('migration_task_id', task.id)
    return task


def clear_migrate_info():
    r = Redis(REDIS_HOST)
    r.flushdb()
