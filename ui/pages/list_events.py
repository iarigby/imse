import os
import random
from math import ceil

import streamlit as st

from backend import schemas
from ui.server_connections import authentication, database
from ui.server_connections.database import get_database


authentication.authorize()
connection = database.init_db_and_get_connection()


with connection.session as session:
    db = get_database(session)
    events: list[schemas.Event] = db.get_events()
    st.write(f"{len(events)} events")
    col_number = 4
    for i in range(ceil(len(events)/col_number)):
        columns = st.columns(col_number)
        for j in range(col_number):
            with columns[j]:
                event = events[i*col_number + j]
                with st.container():
                    image = random.choice(os.listdir("./media/images"))
                    st.image("./media/images/" + image)
                    st.write(event.date.date())
                    st.write(event.name)
