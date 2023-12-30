import os
from time import sleep

from celery.result import AsyncResult

from celery import Celery
from redis import Redis

app = Celery('tasks',
             broker=os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0'),
             backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'))


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
        r = Redis(host=os.environ.get('REDIS_HOST', 'redis'))
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
    r = Redis(host=os.environ.get('REDIS_HOST', 'redis'))
    task = migrate.delay()
    r.set('migration_task_id', task.id)
    return task


def clear_migrate_info():
    r = Redis(host=os.environ.get('REDIS_HOST', 'redis'))
    r.flushdb()
