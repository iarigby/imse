import os
import streamlit as st

from backend import schemas


images = os.listdir("./media/images")


def display_event(event: schemas.Event, venue: schemas.Venue):
    something_like_a_hash = int(''.join([s for s in str(event.id) if s.isdigit()][0:5])) % len(images)
    st.image("./media/images/" + images[something_like_a_hash])
    st.write(event.date.date())
    st.write(event.name)
    st.write("location: " + venue.name + " in " + venue.city)
    st.write("€" + str(event.price))
