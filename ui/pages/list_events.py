from math import ceil

import streamlit as st

from backend import schemas, services
from backend.services import EventService
from ui.components.events import display_event
from ui.server_connections import authentication, database
from ui.server_connections.database import get_database


connection = database.init_db_and_get_connection()
current_user_email = authentication.authorize(connection)


def display_buy_ticket(user_id: str):
    if st.button("Buy Ticket", key='buy_' + str(event.id)):
        with connection.session as session:
            db = get_database(session)
            service = EventService(db)
            try:
                service.buy_ticket(user_id=user_id, event_id=event.id)
                st.rerun()
            except services.OutOfBalanceError:
                st.error("Not enough balance on account")
            except services.OutOfSpaceError:
                st.error("Sorry, there are no more tickets left for this event")


with connection.session as session:
    db = get_database(session)
    events: list[schemas.Event] = db.get_events()
    venues: list[schemas.Venue] = db.get_venues()
    user: schemas.User = db.get_user_by_email(current_user_email)
    user_ticket_event_ids: list[schemas.Ticket] = [ut.event.id for ut in db.get_tickets_for_user(user_id=user.id)]


st.write(f"{len(events)} events")
col_number = 4
for i in range(ceil(len(events)/col_number)):
    columns = st.columns(col_number)
    for j in range(col_number):
        with columns[j]:
            index = i*col_number + j
            if index < len(events):
                event = events[index]
                venue = next(venue for venue in venues if venue.id == event.venue_id)
                with st.container():
                    display_event(event, venue)
                    if event.id in user_ticket_event_ids:
                        st.success("You have a ticket for this event")
                    else:
                        display_buy_ticket(user_id=user.id)
