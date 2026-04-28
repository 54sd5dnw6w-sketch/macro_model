import streamlit as st

st.header('Hello World')

a = st.slider('Select a number', min_value=1, max_value=10)

st.markdown(f'You have seleted: {a} !')