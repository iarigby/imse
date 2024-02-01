import streamlit as st

from ui.server_connections import authentication, database
from ui.server_connections.database import get_database


connection = database.init_db_and_get_connection()
current_user_email = authentication.authorize(connection)


with connection.session as session:
    db = get_database(session)
    venues = db.get_venues()
    artists = db.get_artists()

selected_artist = st.selectbox(label='selected artist: ', options= artists, format_func=lambda  artist: artist.stage_name)

with connection.session as session:
    db = get_database(session)
    try:
        artist_info = db.get_artist_info(selected_artist.id)
    except AttributeError:
        st.write("This artist has not performed in any event")
        st.stop()

    report_columns = st.columns(3)

    with report_columns[0]:
        st.subheader("Events")
        st.write(artist_info.number_of_events)
    with report_columns[1]:
        st.subheader("Booked tickets")
        st.write(artist_info.number_of_booked_tickets)
    with report_columns[2]:
        st.subheader("Cancelled tickets")
        st.write(artist_info.number_of_cancelled_tickets)
