import streamlit as st
import pandas as pd

import config as c
import helpers as h


st.set_page_config(
    #page_title="Ex-stream-ly Cool App",
    #page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)





st.sidebar.header("Closed Economy")
phi = st.sidebar.number_input(r'$\phi :$', min_value=-5, max_value=10, step=1, value=1, help=r"IS Curve: $Y = \omega - \phi r$")
omega = st.sidebar.number_input(r'$\omega :$', min_value=5, max_value=20, step=1, value=8, help=r"IS Curve: $Y = \omega - \phi r$")
r_init = st.sidebar.number_input(r"$r' (\%) :$", min_value=1, max_value=10, step=1, value=2, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
pi = st.sidebar.number_input(r"$\pi (\%) :$", min_value=-5, max_value=15, step=1, value=3, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
lambda_p = st.sidebar.number_input(r'$\lambda_P :$', min_value=0.0, max_value=10.0, step=0.1, value=0.1, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
lambda_i = st.sidebar.number_input(r'$\lambda_I :$', min_value=0.0, max_value=10.0, step=0.1, value=0.1, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")

st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

Y_potential = st.sidebar.number_input(r'$\bar{Y} :$', min_value=0, step=1, value=10, help=r"MP Curve: $r = r' + \lambda_P (Y - \bar{Y}) + \lambda_I \pi$")
const_suggested = 1.1 * Y_potential
const = st.sidebar.number_input('Y borders', min_value=1.0, step=5.0, value=const_suggested, help="The length of the Y sown on the graph from the both sides of the potential output")

# ―――― IS Curve


tabs = st.tabs(c.tabs_options)
with tabs[0]:
    cols = st.columns([3,1])

    # ―――――――――――――――― Short term r Y graph ――――――――――――――――――――――――――――――――――――――――――――――――
    r_Y_fig = h.create_linear_plot(x_label="Y", y_label="r")

    # ―――― IS Curve ――――――――――――――――
    is_slope = -1 / phi
    is_intercept = omega/phi
    h.add_line_to_plot(r_Y_fig, slope=is_slope, intercept=is_intercept, x_min=Y_potential - const, color="#4C78A8",
                       x_max=Y_potential + const, name=f'IS')

    # ―――― MP Curve ――――――――――――――――
    mp_intercept = r_init - lambda_p * Y_potential + lambda_i * pi
    mp_slope = lambda_p
    h.add_line_to_plot(r_Y_fig, slope=mp_slope, intercept=mp_intercept, x_min=Y_potential - const, color="#F58518",
    x_max=Y_potential + const, name=f'MP')

    h.add_vertical_line(r_Y_fig, x_value=Y_potential, name='Y')
    h.show_plotly_fig(r_Y_fig, column_to_plot=cols[0])
    cols[1].write(f'MP Curve: `r = {mp_slope} * Y + {mp_intercept}`')
    cols[1].write(f'IS Curve: `r = {is_slope} * Y + {is_intercept}`')



    # ―――――――――――――――― Short term Pi Y Graph ――――――――――――――――――――――――――――――――――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y", y_label="pi")
    h.add_line_to_plot(pi_Y_fig, slope=0, intercept=pi, x_min=Y_potential - const, color="#54A24B",
                       x_max=Y_potential + const, name=f'IA')

    # ―――― AD curve ――――――――――――――――
    ad_slope = (is_slope - lambda_p) / lambda_i
    ad_intercept = (is_intercept - r_init + lambda_p * Y_potential) / lambda_i
    h.add_line_to_plot(pi_Y_fig, slope=ad_slope, intercept=ad_intercept, x_min=Y_potential - const, color="#B279A2",
                       x_max=Y_potential + const, name=f'AD')

    h.add_vertical_line(pi_Y_fig, x_value=Y_potential, name='Y')
    h.show_plotly_fig(pi_Y_fig, column_to_plot=cols[0])
    cols[1].space(375)
    cols[1].write(f'IA Curve: `pi = {pi}`')
    cols[1].write(f'AD Curve: `pi = {ad_slope} * Y + {ad_intercept}`')






with tabs[2]:
    st.markdown(c.markdown_text)

