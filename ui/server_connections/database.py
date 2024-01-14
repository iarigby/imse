import os
from contextlib import contextmanager

import streamlit as st

import backend.sql.db
from backend.database import Database
from backend.nosql.db import MongoDatabase
from backend.sql.db import SqlDatabase
from backend.populate import populate_database


class Keys:
    session_db_key = 'DB_TYPE'
    db_sql = "sql"
    db_mongo = "mongo"


def init_db_and_get_connection():
    if Keys.session_db_key not in st.session_state:
        set_database(os.environ.get(Keys.session_db_key, Keys.db_sql))
    connection = get_connection()
    return connection


def get_database(session) -> Database:
    if current_database() == Keys.db_sql:
        return SqlDatabase(session)
    return MongoDatabase(session)


def reset_database():
    connection = get_connection()
    if current_database() == Keys.db_sql:
        SqlDatabase.reset(connection.engine)
    else:
        mongo_client = MongoDatabase.database(connection)
        MongoDatabase.reset(mongo_client)
    with connection.session as session:
        db = get_database(session)
        populate_database(db)


@st.cache_resource
def mongo_connection():
    return MongoDatabase.database()


class ConnectionWrapper:
    def __init__(self, mongo_conn):
        self.mongo_connection = mongo_conn

    @property
    @contextmanager
    def session(self):
        yield self.mongo_connection


def get_connection():
    if current_database() == Keys.db_sql:
        return st.connection("sql_db", type="sql", url=backend.sql.db.SQLALCHEMY_DATABASE_URL)
    return ConnectionWrapper(mongo_connection())


def switch_database():
    if current_database() == Keys.db_sql:
        set_database(Keys.db_mongo)
    elif current_database() == Keys.db_mongo:
        set_database(Keys.db_sql)


def current_database():
    return st.session_state[Keys.session_db_key]


def set_database(val: str):
    st.session_state[Keys.session_db_key] = val
