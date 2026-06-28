import streamlit as st
import config as c

st.set_page_config(layout="wide", initial_sidebar_state="expanded")
st.sidebar.header("Settings")

st.header("Settings")
st.info("Settings changes are active only at the current session. If the page is refreshed they return to default values")
st.markdown("#### Simulation")

speed_labels = {"Slow": 0.4, "Normal": 0.15, "Fast": 0.05, "Instant": 0.0}
current_speed = st.session_state.get("setting_speed", c.speed)
current_label = min(speed_labels, key=lambda k: abs(speed_labels[k] - current_speed))

col1, col2 = st.columns(2)

with col1:
    iterations = st.number_input(
        "Number of iterations",
        min_value=5, max_value=200, step=1,
        value=st.session_state.get("setting_iterations", c.iteration_count),
        help="How many periods the model runs after the initial shock.",
    )

with col2:
    speed_choice = st.select_slider(
        "Animation speed",
        options=list(speed_labels.keys()),
        value=current_label,
        help="Controls the delay between animation steps.",
    )

changed = (iterations != st.session_state.get("setting_iterations", c.iteration_count) or
           speed_labels[speed_choice] != st.session_state.get("setting_speed", c.speed))

if st.button("Save settings", type="primary", disabled=not changed):
    st.session_state.setting_iterations = iterations
    st.session_state.setting_speed = speed_labels[speed_choice]
    st.success("Settings saved.")
