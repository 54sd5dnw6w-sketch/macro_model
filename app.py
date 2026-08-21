import streamlit as st

# A FLAT LIST, not {section: [pages]}.
#
# With position="top", a DICT renders each section as one collapsible drop-down
# named after its key — which is why the pages used to hide behind a "Consensus
# Model" menu instead of showing up. A plain list (equivalently, "" as the section
# key) puts every page straight on the bar, all visible at once.
pages_ = [
    st.Page("pages/closed_economy.py", title="Closed Economy", icon="🏛️", default=True),
    st.Page("pages/open_economy.py",   title="Open Economy",   icon="🌍"),
    st.Page("pages/settings.py",       title="Settings",       icon="⚙️"),
]

pg = st.navigation(pages_, position="top")
pg.run()
