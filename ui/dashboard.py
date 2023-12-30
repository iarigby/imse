from time import sleep

import streamlit as st

from ui.server_connections import database, authentication, tasks

authentication.authorize()
db = database.init_session_and_get_database()

st.title("Database Dashboard")

cols = st.columns(3)

with cols[0]:
    st.write("current database is " + database.current_database())
with cols[1]:
    st.button("Switch Database", on_click=database.switch_database)

with cols[2]:
    # TODO 2 spinners display
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
            st.write(migration_task.get())
            if st.button("flush redis"):
                tasks.remove_migration_info()
