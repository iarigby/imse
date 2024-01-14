from time import sleep

import streamlit as st

from ui.server_connections import database, authentication, tasks
from ui.server_connections.database import reset_database, Keys, current_database, set_database

connection = database.init_db_and_get_connection()
authentication.authorize(connection)


st.title("Database Dashboard")

cols = st.columns(4)

with cols[0]:
    st.write("current database is " + database.current_database())
with cols[1]:
    st.button("Switch Database", on_click=database.switch_database)

with cols[2]:
    if st.button("Reset/populate Database"):
        with connection.session as session:
            reset_database()

with cols[3]:
    with st.spinner("trying to connect to redis to fetch migration tasks"):
        try:
            migration_task = tasks.migration_triggerred()
        except Exception as e:
            if "Error 61 connecting to " in str(e):
                st.write("Failed to connect to redis")
            else:
                raise e
    if not migration_task:
        st.button("migrate Database", on_click=tasks.trigger_migration)
    else:
        with st.spinner("migrating database, please wait"):
            while not migration_task.ready():
                sleep(1)
            if st.button("flush redis"):
                tasks.remove_migration_info()
            st.write(migration_task.get())
            if current_database() != Keys.db_mongo:
                set_database(Keys.db_mongo)
