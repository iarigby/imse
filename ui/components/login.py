import streamlit as st

import backend.auth


def check_auth_and_login():
    display_login()
    st.stop()


def display_login():
    with st.form("user-details"):
        user = st.text_input("user name:")
        password = st.text_input("password: ", type="password")
        submitted = st.form_submit_button("Log In")
        if submitted:
            token = backend.auth.authenticate(user, password)
            if not token or token is None:
                st.error("authentication failed")
            else:
                return token
