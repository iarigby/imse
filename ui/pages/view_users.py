import streamlit as st
from ui import session

session.authorize()
db = session.init_session_and_get_database()


st.title("View Users")
users = db.get_users()
for user in users:
    st.write("user " + user.name)
