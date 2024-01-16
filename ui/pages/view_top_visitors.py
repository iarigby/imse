import streamlit as st

from backend.database import OrderBy
from ui.server_connections import authentication, database
from ui.server_connections.database import get_database


connection = database.init_db_and_get_connection()
current_user_email = authentication.authorize(connection)


if current_user_email != 'admin':
    st.write("Only admins can access this page")
    st.stop()


with connection.session as session:
    db = get_database(session)
    venues = db.get_venues()


order_by_mapping = {
    "Descending": OrderBy.Descending,
    "Ascending": OrderBy.Ascending
}

cols = st.columns(2)

with cols[0]:
    selected_venue = st.selectbox(label='filter by venue: ', options=venues, format_func=lambda venue: venue.name)
with cols[1]:
    sort = st.radio('Number Of Tickets Purchased: ', order_by_mapping.keys())


with connection.session as session:
    db = get_database(session)
    reports = db.get_top_users_for_venue(selected_venue.id, order_by_mapping[sort])


for report in reports:
    report_columns = st.columns(3)
    with report_columns[0]:
        st.write(report.user.first_name + " " + report.user.last_name)
    with report_columns[1]:
        st.write(report.user.email)
    with report_columns[2]:
        st.write(report.tickets_purchased)
