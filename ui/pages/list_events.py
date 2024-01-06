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


def display_buy_ticket():
    if st.button("Buy Ticket", key='buy_' + str(event.id)):
        with connection.session as session:
            db = get_database(session)
            service = EventService(db)
            users = db.get_users()
            user: schemas.User = random.choice(users)
            try:
                service.buy_ticket(user_id=user.id, event_id=event.id)
            except services.OutOfBalanceError:
                st.error("Not enough balance on account")
            except services.OutOfSpaceError:
                st.error("Sorry, there are no more tickets left for this event")


with connection.session as session:
    db = get_database(session)
    events: list[schemas.Event] = db.get_events()
    venues: list[schemas.Venue] = db.get_venues()

st.write(f"{len(events)} events")
col_number = 4
for i in range(ceil(len(events)/col_number)):
    columns = st.columns(col_number)
    for j in range(col_number):
        with columns[j]:
            event = events[i*col_number + j]

            venue = next(venue for venue in venues if venue.id == event.venue_id)
            with st.container():
                image = random.choice(os.listdir("./media/images"))
                st.image("./media/images/" + image)
                st.write(event.date.date())
                st.write(event.name)
                st.write("location: " + venue.name + " in " + venue.city)
                st.write("€" + str(event.price))
                display_buy_ticket()
