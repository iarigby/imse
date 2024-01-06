import streamlit as st

from ui.server_connections import authentication, database
from ui.server_connections.database import get_database

authentication.authorize()
connection = database.init_db_and_get_connection()

if authentication.get_user_id() != 'admin':
    st.write("Only admins can access this page")
    st.stop()


st.title("View Users")
with connection.session as session:
    db = get_database(session)
    users = db.get_users()
    for user in users:
        cols = st.columns(4)
        with cols[0]:
            st.write(user.first_name + ' ' + user.last_name)
        with cols[1]:
            st.write(user.email)
        with cols[2]:
            st.write(user.password)
        with cols[3]:
            st.write("balance: " + str(user.balance))
