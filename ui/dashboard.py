from time import sleep

import streamlit as st

from ui import session

session.authorize()
db = session.init_session_and_get_database()

st.title("Database Dashboard")

cols = st.columns(3)

with cols[0]:
    st.write("current database is " + session.current_database())
with cols[1]:
    st.button("Switch Database", on_click=session.switch_database)

with cols[2]:

    migration_task = session.migration_triggerred()
    if not migration_task:
        st.button("migrate Database", on_click=session.trigger_migration)
    else:
        with st.spinner("migrating database, please wait"):
            while not migration_task.ready():
                sleep(1)
            st.write(migration_task.get())
            if st.button("flush redis"):
                session.remove_migration_info()
