import os
import streamlit as st


from backend.database import Database
from backend.nosql.db import MongoDatabase
from backend.sql.db import SqlDatabase
from backend.populate import populate_database


class Keys:
    session_db_key = 'DB_TYPE'
    db_sql = "sql"
    db_mongo = "mongo"
    db_initialised_prefix = 'DB_INITIALISED'


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
