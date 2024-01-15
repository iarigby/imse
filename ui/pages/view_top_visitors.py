import streamlit as st

from backend.database import OrderBy
from ui.server_connections import authentication, database
from ui.server_connections.database import get_database


connection = database.init_db_and_get_connection()
authentication.authorize(connection)


with connection.session as session:
    db = get_database(session)
    venues = db.get_venues()

selected_venue = st.selectbox(label='select venue: ', options=venues, format_func=lambda venue: venue.name)


order_by_mapping = {
    "Descending": OrderBy.Descending,
    "Ascending": OrderBy.Ascending
}

cols = st.columns(2)

with cols[0]:
    sort = st.radio('Number Of Tickets Purchased: ', order_by_mapping.keys())
with cols[1]:
    month = st.slider('last n months: ', min_value=1, max_value=12)


with connection.session as session:
    db = get_database(session)
    reports = db.get_top_users_for_venue(selected_venue.id, order_by_mapping[sort])


if sort == "Ascending":
    reports = sorted(reports, key=lambda r: r.tickets_purchased)
else:
    reports = sorted(reports, key=lambda r: r.tickets_purchased, reverse=True)


for report in reports:
    report_columns = st.columns(2)
    with report_columns[0]:
        st.write(report.user.first_name + " " + report.user.last_name)
    with report_columns[1]:
        st.write(report.tickets_purchased)
