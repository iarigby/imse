import os
import random
from math import ceil

import streamlit as st

from backend import schemas, services
from backend.services import EventService
from ui.server_connections import authentication, database
from ui.server_connections.database import get_database


authentication.authorize()
connection = database.init_db_and_get_connection()


def display_cancel_ticket():
    if st.button("Cancel Ticket", key='cancel_' + str(ticket.id)):
        with connection.session as session:
            db = get_database(session)
            service = EventService(db)
            users = db.get_users()
            user: schemas.User = random.choice(users)
            try:
                service.cancel_ticket(ticket_id=ticket.id)
                # service.buy_ticket(user_id=user.id, event_id=event.id)

                # service.buy_ticket(user_id=user.id, event_id=event.id)
            except services.OutOfBalanceError:
                st.error("Not enough balance on account")
            except services.OutOfSpaceError:
                st.error("Sorry, there are no more tickets left for this event")


with connection.session as session:
    db = get_database(session)
    events: list[schemas.Event] = db.get_events()
    tickets: list[schemas.Ticket] = db.get_tickets()
    # venues: list[schemas.Venue] = db.get_venues()

st.write(f"{len(tickets)} events")
col_number = 4
for i in range(ceil(len(tickets)/col_number)):
    columns = st.columns(col_number)
    for j in range(col_number):
        with columns[j]:
            ticket = tickets[i*col_number + j]

            event = next(event for event in events if ticket.event_id == event.id)
            with st.container():
                st.write("Event name: " + event.name)
                st.write("Event date: " + str(event.date.date()))
                st.write("Ticket status: " + ticket.status)
                display_cancel_ticket()