import streamlit as st

pages_ = {
    "Consensus Model": [
        st.Page("pages/closed_economy.py", title="Closed Economy"),
        st.Page("pages/open_economy.py", title="Open Economy"),
        st.Page("pages/settings.py", title="⚙ Settings")
    ]
}

pg = st.navigation(pages_, position="top")
pg.run()