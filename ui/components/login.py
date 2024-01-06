import streamlit as st
from pydantic import ValidationError

import backend.auth
from ui.server_connections import database


def check_auth_and_login():
    display_login()
    st.stop()


def display_login():
    with st.form("user-details"):
        email = st.text_input("email:")
        password = st.text_input("password: ", type="password")
        submitted = st.form_submit_button("Log In")
        if submitted:
            if email == "admin":
                return backend.auth.authenticate(email, password)
            try:
                connection = database.init_db_and_get_connection()
                with connection.session as session:
                    db = database.get_database(session)
                    user = db.get_user_by_email(email)
                if user.password == password:
                    return str(user.id)
                else:
                    st.write(user)
                    st.error("authentication failed: password is not correct")
            except ValidationError:
                st.error("authentication failed: email is not correct")
