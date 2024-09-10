import streamlit as st
from get_location import current_location

"""
dashboard for the Smart Street project
the dashboard will display the camera feed, location, and road name
"""
st.set_page_config(page_title="Smart Street", 
                   layout='wide', 
                   initial_sidebar_state='expanded')
