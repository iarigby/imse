import os

import streamlit as st
from extra_streamlit_components import CookieManager

from backend import worker
from backend.database import Database
from backend.nosql.db import MongoDatabase
from backend.sql.db import SqlDatabase
from backend.populate import populate_database

from ui.components.login import display_login


class Keys:
    session_db_key = 'DB_TYPE'
    db_sql = "sql"
    db_mongo = "mongo"
    db_initialised_prefix = 'DB_INITIALISED'
    authentication_cookie = 'authentication_token'
    migration_triggered = "migration_triggered"


def init_session_and_get_database() -> Database:
    if Keys.session_db_key not in st.session_state:
        set_database(os.environ.get(Keys.session_db_key, Keys.db_sql))
    db = get_database()
    session_db_initialised = Keys.db_initialised_prefix + current_database()

    if session_db_initialised not in st.session_state:
        st.session_state[session_db_initialised] = 1
        db.reset()
        populate_database(db)
    return db


def get_database():
    if current_database() == Keys.db_sql:
        return SqlDatabase()
    return MongoDatabase()


def switch_database():
    if current_database() == Keys.db_sql:
        set_database(Keys.db_mongo)
    elif current_database() == Keys.db_mongo:
        set_database(Keys.db_sql)


def current_database():
    return st.session_state[Keys.session_db_key]


def set_database(val: str):
    st.session_state[Keys.session_db_key] = val


def migration_triggerred():
    task = st.session_state.get(Keys.migration_triggered)
    if not task:
        task = worker.get_migration_task()
    return task


def trigger_migration():
    st.session_state[Keys.migration_triggered] = worker.launch_migrate()


def remove_migration_info():
    st.session_state[Keys.migration_triggered] = None
    worker.clear_migrate_info()
    # for some reason r.flushdb() is not working
    st.rerun()


def authorize():
    cookies = CookieManager(key='a')
    if not cookies.get(Keys.authentication_cookie):
        token = display_login()
        if token is None:
            st.stop()
        else:
            st.text("setting token")
            cookies.set(Keys.authentication_cookie, token)
    else:
        with st.sidebar:
            if st.button("Log Out"):
                logout()


def logout():
    cookies = CookieManager(key='b')
    cookies.set(Keys.authentication_cookie, "")
