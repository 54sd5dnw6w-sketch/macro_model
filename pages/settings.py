import streamlit as st
import config as c
import helpers as h

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.sidebar.header("Settings")

st.header("Settings")
st.info("Settings changes are active only at the current session. If the page is refreshed they return to default values")
st.markdown("#### Simulation")

h.settings_controls()
