import streamlit as st
import importlib
import pages

importlib.reload(pages)


pages_ = {
    "Consensus Model": [
        st.Page("pages/closed_economy.py", title="Closed Economy"),
        st.Page("pages/open_economy.py", title="Open Economy")

    ],
    "ECB Data": [
        st.Page("pages/ecb_data.py", title="ECB Data"),
    ],
}

pg = st.navigation(pages_, position="top")
pg.run()