import streamlit as st
from ui.server_connections import authentication, database
from ui.server_connections.database import get_database

authentication.authorize()
connection = database.init_db_and_get_connection()


st.title("View Users")
with connection.session as session:
    db = get_database(session)
    users = db.get_users()
    for user in users:
        st.write("user " + user.name)
