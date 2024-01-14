from extra_streamlit_components import CookieManager


from ui.components.login import display_login
import streamlit as st

from ui.server_connections import database
from ui.server_connections.database import get_database

user_id_key = 'user_email'
connection = database.init_db_and_get_connection()

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

            with connection.session as session:
                db = get_database(session)
                user = db.get_user_by_email(current_user_email)
                st.write("User balance: ", user.balance)
            if st.button("Log Out"):
                logout()
        return current_user_email


def logout():
    cookies = CookieManager(key='b')
    cookies.set(user_id_key, "")
