from extra_streamlit_components import CookieManager
from ui.components.login import display_login
import streamlit as st

user_id_key = 'user_email'


def authorize():
    cookies = CookieManager(key='a')
    current_user_email = cookies.get(user_id_key)
    if not current_user_email:
        user_email = display_login()
        if user_email is None:
            st.stop()
        else:
            st.text("setting user_email")
            cookies.set(user_id_key, user_email)
            return user_email
    else:
        with st.sidebar:
            st.text("User: " + current_user_email)
            if st.button("Log Out"):
                logout()
        return current_user_email


def logout():
    cookies = CookieManager(key='b')
    cookies.set(user_id_key, "")
