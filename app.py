import streamlit as st


pages_ = [
    st.Page("pages/closed_economy.py", title="Closed Economy", icon="🏛️", default=True),
    st.Page("pages/open_economy.py",   title="Open Economy",   icon="🌍"),
    st.Page("pages/settings.py",       title="Settings",       icon="⚙️"),
]

pg = st.navigation(pages_, position="top")
pg.run()
