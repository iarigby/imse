from extra_streamlit_components import CookieManager
from psycopg2 import errorcodes, ProgrammingError
from pydantic import ValidationError

from ui.components.login import display_login
import streamlit as st

from ui.server_connections.database import get_database

user_id_key = 'user_email'


def authorize(connection):
    cookies = CookieManager(key='a')
    current_user_email = cookies.get(user_id_key)
    if current_user_email is None or current_user_email == '':
        user_email = display_login(connection)
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
                try:
                    user = db.get_user_by_email(current_user_email)
                except ValidationError:
                    st.write('DB has not been populated yet')
                    st.stop()
                except Exception as e:
                    if e.orig.pgcode == errorcodes.UNDEFINED_TABLE:
                        st.write('DB has not been populated yet')
                    st.stop()
                st.write("User balance: ", user.balance)
            if st.button("Log Out"):
                logout()

        return current_user_email


def logout():
    cookies = CookieManager(key='b')
    cookies.set(user_id_key, "")
