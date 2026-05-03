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
pi = st.sidebar.number_input(r"$\pi (\%) :$",  step=1, value=3, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
lambda_p = st.sidebar.number_input(r'$\lambda_P :$', min_value=0.0, max_value=10.0, step=0.1, value=0.1, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
lambda_i = st.sidebar.number_input(r'$\lambda_I :$', min_value=0.0, max_value=10.0, step=0.1, value=0.1, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")

st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

Y_potential = st.sidebar.number_input(r'$\bar{Y} :$', min_value=0, step=1, value=10, help=r"MP Curve: $r = r' + \lambda_P (Y - \bar{Y}) + \lambda_I \pi$")
const_suggested = 1.1 * Y_potential
# const = st.sidebar.number_input('Y borders', min_value=1.0, step=5.0, value=const_suggested, help="The length of the Y sown on the graph from the both sides of the potential output")



tabs = st.tabs(c.tabs_options)
with tabs[0]:
    seg_control = st.segmented_control('no', label_visibility='collapsed', options=['📉 Short Term', '📈 Long Term'], width='stretch', default='📉 Short Term')


    if seg_control == '📉 Short Term':
        STMP_color = "#F58518"
        STMP_name = 'MP'
        STMP_line_width = c.standard_line_width

        STIA_color = "#54A24B"
        STIA_name = 'IA'
        STIA_line_width = c.standard_line_width
    else:
        STMP_color = "#FAD7B0"
        STMP_name = 'STMP'
        STMP_line_width = c.thin_line_width
        LTMP_color = "#F58518"
        LTMP_name = 'LTMP'

        STIA_color = "#CDEACB"
        STIA_name = 'STIA'
        STIA_line_width = c.thin_line_width
        LTIA_color = "#54A24B"
        LTIA_name = 'LTIA'



    cols = st.columns([3,1])
    r_Y_fig = h.create_linear_plot(x_label="Y", y_label="r")

    # ―――― Parameters ――――――――――――――――
    IS_slope = -1 / phi
    IS_intercept = omega / phi

    MP_slope = lambda_p
    MP_intercept = r_init - lambda_p * Y_potential + lambda_i * pi

    Y_IS_MP_intersection, r_is_mp_intersection = h.find_line_intersection(slope_1=IS_slope, intercept_1=IS_intercept, slope_2=MP_slope, intercept_2=MP_intercept)
    const = max(abs(Y_IS_MP_intersection), abs(Y_potential), abs(Y_potential - Y_IS_MP_intersection)) * 1.3

    # ―――― IS Curve ――――――――――――――――
    h.add_line_to_plot(r_Y_fig, slope=IS_slope, intercept=IS_intercept, x_min=Y_potential - const, color="#4C78A8", x_max=Y_potential + const, name=f'IS')
    # ―――― MP Curve ――――――――――――――――
    h.add_line_to_plot(r_Y_fig, slope=MP_slope, intercept=MP_intercept, x_min=Y_potential - const, color=STMP_color, x_max=Y_potential + const, name=STMP_name, line_width=STMP_line_width)
    # Actual Y
    h.add_vertical_line(r_Y_fig, x_value= Y_IS_MP_intersection, y_max=r_is_mp_intersection, name=f"Y ({Y_IS_MP_intersection: .1f})", name_position='bottom', color='#B0B0B0', dash='dot')


    if seg_control == '📈 Long Term':
        r_IS_at_Y_potential = IS_slope * Y_potential + IS_intercept
        r_MP_at_Y_potential = MP_slope * Y_potential + MP_intercept
        LTMP_intercept = MP_intercept + r_IS_at_Y_potential - r_MP_at_Y_potential
        h.add_line_to_plot(r_Y_fig, slope=MP_slope, intercept=LTMP_intercept, x_min=Y_potential - const, color=LTMP_color, x_max=Y_potential + const, name=LTMP_name)
        h.add_arrow(r_Y_fig,x_start=Y_potential,y_start=r_MP_at_Y_potential, x_end=Y_potential, y_end=r_IS_at_Y_potential)
        #h.add_arrow(r_Y_fig,x_start=Y_potential + const/2,y_start=r_MP_at_Y_potential, x_end=Y_potential + const/2, y_end=r_IS_at_Y_potential)


    # ―――― Plot ――――――――――――――――
    h.add_vertical_line(r_Y_fig, x_value=Y_potential, name=f'Ȳ({Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(r_Y_fig, column_to_plot=cols[0])
    cols[1].write(f'MP Curve: `r = {MP_slope:.1f}Y + {MP_intercept:.1f}`')
    cols[1].write(f'IS Curve: `r = {IS_slope:.1f}Y + {IS_intercept:.1f}`')
    output_gap = Y_IS_MP_intersection - Y_potential
    cols[1].write(f'Output Gap(Y - Ȳ): `{output_gap:.1f}`')

    if seg_control == '📈 Long Term':
        cols[1].write(f'Long Term r: `{r_IS_at_Y_potential:.1f} %`')



    # ―――――――――――――――― Short term Pi Y Graph ――――――――――――――――――――――――――――――――――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y", y_label="pi")

    # ―――― Parameters ――――――――――――――――
    AD_slope = (IS_slope - lambda_p) / lambda_i
    AD_intercept = (IS_intercept - r_init + lambda_p * Y_potential) / lambda_i
    Y_IA_AD_intersection, pi_IA_AD_intersection = h.find_line_intersection(slope_1=0, intercept_1=pi, slope_2=AD_slope, intercept_2=AD_intercept)

    # ―――― IA Curve ――――――――――――――――
    h.add_line_to_plot(pi_Y_fig, slope=0, intercept=pi, x_min=Y_potential - const, color=STIA_color,x_max=Y_potential + const, name=STIA_name, line_width=STIA_line_width)
    # ―――― AD curve ――――――――――――――――
    h.add_line_to_plot(pi_Y_fig, slope=AD_slope, intercept=AD_intercept, x_min=Y_potential - const, color="#B279A2", x_max=Y_potential + const, name=f'AD')
    # Actual Y
    h.add_vertical_line(pi_Y_fig, x_value= Y_IA_AD_intersection, y_max=pi_IA_AD_intersection, name=f"Y ({Y_IA_AD_intersection: .1f})", name_position='bottom', color='#B0B0B0', dash='dot')


    if seg_control == '📈 Long Term':
        pi_for_AD_at_Y_potential = AD_slope * Y_potential + AD_intercept
        h.add_line_to_plot(pi_Y_fig, slope=0, intercept=pi_for_AD_at_Y_potential, x_min=Y_potential - const, x_max=Y_potential + const, color = LTIA_color, name=LTIA_name)
        h.add_arrow(pi_Y_fig, x_start=Y_potential, y_start=pi, x_end=Y_potential, y_end=pi_for_AD_at_Y_potential)





    # ―――― Plot ――――――――――――――――
    h.add_vertical_line(pi_Y_fig, x_value=Y_potential, name=f'Ȳ({Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(pi_Y_fig, column_to_plot=cols[0])
    cols[1].space(375)
    cols[1].write(f'IA Curve: `pi = {pi:.1f}`')
    cols[1].write(f'AD Curve: `pi = {AD_slope:.1f}Y + {AD_intercept:.1f}`')

    if seg_control == '📈 Long Term':
        cols[1].write(f'Long term inflation: `{pi_for_AD_at_Y_potential:.1f} %`')







with tabs[2]:
    st.markdown(c.markdown_text)

