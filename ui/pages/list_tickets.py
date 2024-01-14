import os
import random
from math import ceil

import streamlit as st

from backend import schemas, services
from backend.services import EventService
from ui.components.events import display_event
from ui.server_connections import authentication, database
from ui.server_connections.database import get_database


connection = database.init_db_and_get_connection()
current_user_email = authentication.authorize(connection)


def display_cancel_ticket(user_id, event_id):
    if st.button("Cancel Ticket", key='cancel_' + str(ticket.id)):
        with connection.session as session:
            db = get_database(session)
            service = EventService(db)
            try:
                service.cancel_ticket(user_id=user_id, event_id=event_id)
                st.rerun()
            except services.LateCancelation:
                st.error("You can only return ticket two weeks before the event")


with connection.session as session:
    db = get_database(session)
    user = db.get_user_by_email(current_user_email)
    user_tickets = db.get_tickets_for_user(user.id)
    venues = db.get_venues()


st.write(f"{len(user_tickets)} events")
col_number = 4
for i in range(ceil(len(user_tickets)/col_number)):
    columns = st.columns(col_number)
    for j in range(col_number):
        index = i * col_number + j
        if index < len(user_tickets):
            with columns[j]:
                ticket, event = user_tickets[index].ticket, user_tickets[index].event
                with st.container():
                    display_event(event, next(venue for venue in venues if venue.id == event.venue_id))
                    if ticket.status == 'booked':
                        display_cancel_ticket(user.id, event.id)
                    else:
                        st.write("you cancelled this ticket")
