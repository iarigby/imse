import streamlit as st
from ui.server_connections import authentication, database

authentication.authorize()
db = database.init_session_and_get_database()


st.title("View Users")
users = db.get_users()
for user in users:
    st.write("user " + user.name)
