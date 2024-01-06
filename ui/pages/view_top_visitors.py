import streamlit as st

from ui.server_connections import authentication, database
from ui.server_connections.database import get_database


authentication.authorize()
connection = database.init_db_and_get_connection()

with connection.session as session:
    db = get_database(session)
    venues = db.get_venues()

selected_venue = st.selectbox(label='select venue: ', options=venues, format_func=lambda venue: venue.name)

cols = st.columns(2)
with cols[0]:
    sort = st.radio('Number Of Tickets Purchased: ', ["Ascending", "Descending"])
with cols[1]:
    month = st.slider('last n months: ', min_value=1, max_value=12)

st.write(sort)
st.write(month)
