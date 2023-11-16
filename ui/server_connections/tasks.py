import streamlit as st

from backend import worker


migration_triggered = "migration_triggered"


def migration_triggerred():
    task = st.session_state.get(migration_triggered)
    if not task:
        task = worker.get_migration_task()
    return task


def trigger_migration():
    st.session_state[migration_triggered] = worker.launch_migrate()


def remove_migration_info():
    st.session_state[migration_triggered] = None
    worker.clear_migrate_info()
    # for some reason r.flushdb() is not working
    st.rerun()

