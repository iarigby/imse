import random
import os
import streamlit as st

from backend import schemas


def display_event(event: schemas.Event, venue: schemas.Venue):
    image = random.choice(os.listdir("./media/images"))
    st.image("./media/images/" + image)
    st.write(event.date.date())
    st.write(event.name)
    st.write("location: " + venue.name + " in " + venue.city)
    st.write("€" + str(event.price))

