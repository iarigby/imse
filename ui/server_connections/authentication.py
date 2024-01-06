from extra_streamlit_components import CookieManager
from ui.components.login import display_login
import streamlit as st

user_id_key = 'user_id'


def get_user_id():
    cookies = CookieManager(key='c')
    return cookies.get(user_id_key)


def authorize():
    cookies = CookieManager(key='a')
    if not cookies.get(user_id_key):
        user_id = display_login()
        if user_id is None:
            st.stop()
        else:
            st.text("setting user_id")
            cookies.set(user_id_key, user_id)
    else:
        with st.sidebar:
            if st.button("Log Out"):
                logout()


def logout():
    cookies = CookieManager(key='b')
    cookies.set(user_id_key, "")
