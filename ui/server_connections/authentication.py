from extra_streamlit_components import CookieManager
from ui.components.login import display_login
import streamlit as st


authentication_cookie = 'authentication_token'


def authorize():
    cookies = CookieManager(key='a')
    if not cookies.get(authentication_cookie):
        token = display_login()
        if token is None:
            st.stop()
        else:
            st.text("setting token")
            cookies.set(authentication_cookie, token)
    else:
        with st.sidebar:
            if st.button("Log Out"):
                logout()


def logout():
    cookies = CookieManager(key='b')
    cookies.set(authentication_cookie, "")
