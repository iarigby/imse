import streamlit as st
from sqlalchemy.exc import IntegrityError

from backend import schemas
from ui.server_connections import authentication, database

authentication.authorize()
db = database.init_session_and_get_database()
st.title("Create New User")

user_name = st.text_input("user name: ")
if st.button("add new user"):
    try:
        db.add_user(schemas.NewUser(name=user_name))
        st.write("added new user " + user_name)
    except IntegrityError as e:
        error = str(e)
        st.error("could not create new user. ")
        if ("UNIQUE" in error and "user.name" in error) or "errors.UniqueViolation" in error:
            st.error("name needs to be unique")
        else:
            st.error("unknown error" + error)
