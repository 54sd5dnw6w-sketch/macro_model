import streamlit as st
import pandas as pd
import time
import plotly.express as px


import config as c
import helpers as h




h.session_init(running = False, pi_prev = None, first_iteration =  True, iter_counter = 0, iteration_df = pd.DataFrame(columns=["Iteration", "Output", "Inflation"]))

def btn_play_clicked():
    st.session_state.running = not st.session_state.running
    clear()

def clear():
    st.session_state.pi_prev = None
    st.session_state.iter_counter = 0
    st.session_state.iteration_df = pd.DataFrame(columns=["Iteration", "Output", "Inflation"])
    st.session_state.first_iteration = True


st.set_page_config(layout="wide",initial_sidebar_state="expanded",)


# ―――― Sidebar Configuration ――――――――――――――――
st.sidebar.header("Closed Economy")

#text to change
text_to_show = ''

with st.sidebar:
    btn_label = '⏹ Stop' if st.session_state.running else '⏵ Start'
    btn_type = 'secondary' if st.session_state.running else 'primary'
    start_btn = st.button(btn_label, type = btn_type, on_click=btn_play_clicked, width='stretch')



    # ―――― Complexity Level Configuration ――――――――――――――――
    level = st.selectbox('Control Level', options=['Easy', 'Medium', 'Advanced'], disabled=st.session_state.running, on_change=clear)

    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    if level == 'Easy':
        st.markdown('##### Please Select the shock:')
        shock_type = st.pills('no', label_visibility='collapsed', options=['Inflation shock', 'Monetary Shock', 'Demand shock'], disabled=st.session_state.running, on_change=clear)

        #st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

        phi = 1.0
        lambda_p = 0.5
        lambda_i = 0.5
        gamma = 0.5
        eta = 0.0
        if shock_type == 'Inflation shock':
            omega = 4.5
            r_init = 2.0
            pi = 4
            text_to_show = c.neg_inflation_shock
        elif shock_type == 'Monetary Shock':
            omega = 4.5
            r_init = 1.3
            pi = 3.0
            text_to_show = c.pos_monetary_shock
        elif shock_type == 'Demand shock':
            omega = 6.1
            r_init = 3.0
            pi = 3.0
            text_to_show = c.pos_demand_shock
        else:
            omega = 4.5
            r_init = 2.0
            pi = 3.0
            text_to_show = c.placeholder_shock

    elif level == 'Medium':
        phi = 1
        omega = st.slider(r'$\omega :$',on_change=clear, min_value=1.0 ,max_value=8.0, step=0.1, value=4.5, help=r"IS Curve: $Y = \omega - \phi r$")
        r_init = st.slider(r"$r' (\%) :$",on_change=clear, min_value=0.1, max_value=3.5, step=0.1, value=2.0, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        pi = st.slider(r"$\pi (\%) :$",on_change=clear, min_value=-5.0, max_value=10.0, step=0.25, value=3.0, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        lambda_p = 0.5
        lambda_i = 0.5
        gamma = 0.5
        eta = 0


        empty_text_counter = 0
        # ---------- Fiscal Policy (omega) ----------
        if omega > 5.0:
            omega_text = c.omega_text_exp
        elif omega <4.0:
            omega_text = c.omega_text_res
        else:
            omega_text =''
            empty_text_counter += 1

        # ---------- Monetary Policy (r) ----------
        if r_init > 2.3:
            r_text = c.r_text_con
        elif r_init < 1.7:
            r_text = c.r_text_exp
        else:
            r_text = ''
            empty_text_counter += 1

        # ---------- Inflation Shock (pi) ----------
        if pi > 5:
            pi_text = c.pi_text_inf
        elif pi < 0:
            pi_text = c.pi_text_def
        else:
            pi_text = ''
            empty_text_counter += 1

        # ---------- Final Combined Output ----------
        if empty_text_counter < 3:
            text_to_show = omega_text + r_text + pi_text
        else:
            text_to_show = c.empty_placeholder_moderate_level_shock


    elif level == 'Advanced':
        st.markdown('##### For IS Curve')
        phi = st.number_input(r'$\phi :$',on_change=clear, min_value=0, step=1, value=1, help=r"IS Curve: $Y = \omega - \phi r$")
        omega = st.number_input(r'$\omega :$',on_change=clear, min_value=0.0, step=0.5, value=4.5, help=r"IS Curve: $Y = \omega - \phi r$")

        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### For MP Curve')
        r_init = st.number_input(r"$r' (\%) :$",on_change=clear, min_value=1, max_value=10, step=1, value=2, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        pi = st.number_input(r"$\pi (\%) :$",on_change=clear, step=1, value=3, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        lambda_p = st.number_input(r'$\lambda_P :$',on_change=clear, min_value=0.0, max_value=10.0, step=0.1, value=0.5, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        lambda_i = st.number_input(r'$\lambda_I :$',on_change=clear, min_value=0.0, max_value=10.0, step=0.1, value=0.5, help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")

        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### For IA Curve')
        gamma = st.number_input(r'$\gamma :$',on_change=clear, min_value=0.0, step=0.1, value=0.5, )
        eta = st.number_input(r'$\eta :$',on_change=clear, min_value=0.0, step=0.1, value=0.0)




if st.session_state.pi_prev is None:
    st.session_state.pi_prev = pi



#tabs = st.tabs(c.tabs_options)

#with tabs[0]:
with st.container():
    if st.session_state.running or not st.session_state.first_iteration:
        STMP_color = "#FAD7B0"
        STMP_name = 'STMP'
        STMP_line_width = c.thin_line_width


        STIA_color = "#CDEACB"
        STIA_name = 'STIA'
        STIA_line_width = c.thin_line_width

        LTIA_color = "#54A24B"
        LTIA_name = 'LTIA'
        LTMP_color = "#F58518"
        LTMP_name = 'LTMP'

    else:
        STMP_color = "#F58518"
        STMP_name = 'MP'
        STMP_line_width = c.standard_line_width

        STIA_color = "#54A24B"
        STIA_name = 'IA'
        STIA_line_width = c.standard_line_width






    cols = st.columns([1.7,1])
    r_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="r - interest rate")

    # ―――― Parameters ――――――――――――――――
    IS_slope = -1 / phi
    IS_intercept = omega / phi

    MP_slope = lambda_p / c.Y_potential
    MP_intercept = r_init - lambda_p + lambda_i * st.session_state.pi_prev
    MP_intercept_0 = r_init - lambda_p + lambda_i * pi

    Y_IS_MP_intersection, r_is_mp_intersection = h.find_line_intersection(slope_1=IS_slope, intercept_1=IS_intercept, slope_2=MP_slope, intercept_2=MP_intercept)
    Y_IS_MP_intersection_0, _ = h.find_line_intersection(slope_1=IS_slope, intercept_1=IS_intercept, slope_2=MP_slope, intercept_2=MP_intercept_0)

    if level != 'Easy':
        const = max(abs(Y_IS_MP_intersection_0), abs(c.Y_potential), abs(c.Y_potential - Y_IS_MP_intersection_0)) * 1.3
        const = max(const, 0.5)
    else:
        const = 1


    # ―――― IS Curve ――――――――――――――――
    h.add_line_to_plot(r_Y_fig, slope=IS_slope, intercept=IS_intercept, x_min=c.Y_potential - const, color="#4C78A8", x_max=c.Y_potential + const,name=f'IS')
    # ―――― MP Curve ――――――――――――――――
    h.add_line_to_plot(r_Y_fig, slope=MP_slope, intercept=MP_intercept_0, x_min=c.Y_potential - const, color=STMP_color, x_max=c.Y_potential + const, name=STMP_name, line_width=STMP_line_width)

    if st.session_state.running or not st.session_state.first_iteration:
        h.add_line_to_plot(r_Y_fig, slope=MP_slope, intercept=MP_intercept, x_min=c.Y_potential - const, color=LTMP_color, x_max=c.Y_potential + const, name=LTMP_name, line_width=STMP_line_width)

    # Actual Y
    h.add_vertical_line(r_Y_fig, x_value= Y_IS_MP_intersection, y_max=r_is_mp_intersection, name=f"Y ({Y_IS_MP_intersection: .2f})", name_position='bottom', color='#B0B0B0', dash='dot')


    # ―――― Plot ――――――――――――――――
    h.add_vertical_line(r_Y_fig, x_value=c.Y_potential, name=f'Ȳ({c.Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(r_Y_fig, column_to_plot=cols[0])
    # cols[1].write(f'MP Curve: `r = {MP_slope:.1f}Y + {MP_intercept:.1f}`')
    # cols[1].write(f'IS Curve: `r = {IS_slope:.1f}Y + {IS_intercept:.1f}`')
    output_gap = Y_IS_MP_intersection - c.Y_potential
    # cols[1].write(f'Output Gap(Y - Ȳ): `{output_gap:.1f}`')


    # ―――――――――――――――― Short term Pi Y Graph ――――――――――――――――――――――――――――――――――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="𝜋 - inflation")

    # ―――― Parameters ――――――――――――――――
    AD_slope = (IS_slope - lambda_p/c.Y_potential) / lambda_i
    AD_intercept = (IS_intercept - r_init + lambda_p) / lambda_i
    Y_IA_AD_intersection, pi_IA_AD_intersection = h.find_line_intersection(slope_1=0, intercept_1=st.session_state.pi_prev, slope_2=AD_slope, intercept_2=AD_intercept)
    pi_potential = AD_slope * c.Y_potential + AD_intercept

    # ―――― IA Curve ――――――――――――――――
    h.add_line_to_plot(pi_Y_fig, slope=0, intercept=pi, x_min= c.Y_potential - const, color= STIA_color,x_max= c.Y_potential + const, name=STIA_name, line_width=STIA_line_width)
    # ―――― AD curve ――――――――――――――――
    h.add_line_to_plot(pi_Y_fig, slope=AD_slope, intercept=AD_intercept, x_min=c.Y_potential - const, color="#B279A2", x_max=c.Y_potential + const, name=f'AD')

    if st.session_state.running or not st.session_state.first_iteration:
        h.add_line_to_plot(pi_Y_fig, slope=0, intercept=st.session_state.pi_prev, x_min=c.Y_potential - const, color=LTIA_color,x_max=c.Y_potential + const, name=LTIA_name, line_width=STIA_line_width)

    # Actual Y
    h.add_vertical_line(pi_Y_fig, x_value= Y_IA_AD_intersection, y_max=pi_IA_AD_intersection, name=f"Y ({Y_IA_AD_intersection: .2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    h.add_vertical_line(pi_Y_fig, x_value=c.Y_potential, name=f'Ȳ({c.Y_potential})', color='#555555', dash='8px,5px')



    # ―――― Plot ――――――――――――――――
    h.show_plotly_fig(pi_Y_fig, column_to_plot=cols[0])
    #cols[1].space(375)
    # cols[1].write(f'IA Curve: `pi = {pi:.1f}`')
    # cols[1].write(f'AD Curve: `pi = {AD_slope:.1f}Y + {AD_intercept:.1f}`')
    if level == 'Advanced':
        text_to_show = model_info = f"""
                    <b style="color:black;">IA Curve:</b>
                    𝜋 = {pi:.1f}
                    <br>
                
                    <b style="color:black;">AD Curve:</b>
                    𝜋 = {AD_slope:.1f}Y + {AD_intercept:.1f}
                    <br>
                
                    <b style="color:black;">MP Curve:</b>
                    r = {MP_slope:.1f}Y + {MP_intercept:.1f}
                    <br>
                
                    <b style="color:black;">IS Curve:</b>
                    r = {IS_slope:.1f}Y + {IS_intercept:.1f}
                    <br>
                
                    <b style="color:black;">Output Gap (Y - Ȳ):</b>
                    {output_gap:.1f}
                """


    with cols[1].container(border=True):
        st.markdown(text_to_show, unsafe_allow_html=True)

        # ―――― Plot Output graph helper ――――――――――――――――
        output_fig = px.scatter( st.session_state.iteration_df, x="Iteration", y="Output", )

        if not st.session_state.iteration_df.empty:
            last_row = st.session_state.iteration_df.iloc[-1]
            output_fig.add_annotation( x=last_row["Iteration"], y=last_row["Output"], text=f"Y = {last_row['Output']:.2f}", showarrow=False, xanchor="left", xshift=0, yshift=12, )

        output_fig.update_layout( xaxis_title="Iterations", yaxis_title="Y - Output", showlegend=False, )

        output_fig.update_traces(mode="lines")
        h.add_line_to_plot(output_fig,slope=0,intercept=c.Y_potential,x_min=0,x_max=c.iteration_count,name=f"Ȳ ({c.Y_potential:.2f})",line_width=2,color="#999999",dash='dot',)
        h.show_plotly_fig(output_fig, height=200) #, column_to_plot=cols[1]


        # ―――― Plot Inflation graph helper ――――――――――――――――
        inflation_fig = px.scatter( st.session_state.iteration_df, x="Iteration", y="Inflation", )

        if not st.session_state.iteration_df.empty:
            last_row = st.session_state.iteration_df.iloc[-1]
            inflation_fig.add_annotation( x=last_row["Iteration"], y=last_row["Inflation"], text=f"𝜋 = {last_row['Inflation']:.2f}", showarrow=False, xanchor="left", xshift=0, yshift=12 )

        inflation_fig.update_layout( xaxis_title="Iterations", yaxis_title="𝜋 - inflation", showlegend=False, )

        inflation_fig.update_traces(mode="lines")
        h.add_line_to_plot( inflation_fig, slope=0, intercept=pi_potential, x_min=0, x_max=c.iteration_count, name=f"𝜋̄ ({pi_potential:.2f})", line_width=2, color="#999999", dash='dot', )
        h.show_plotly_fig(inflation_fig, height=200) #, column_to_plot=cols[1]




    if st.session_state.running:
        st.session_state.iteration_df.loc[len(st.session_state.iteration_df)] = [st.session_state.iter_counter,Y_IS_MP_intersection,st.session_state.pi_prev]
        st.session_state.pi_prev = st.session_state.pi_prev + gamma * (Y_IS_MP_intersection - c.Y_potential) / c.Y_potential + eta
        st.session_state.iter_counter += 1

        if st.session_state.iter_counter == c.iteration_count:
            st.session_state.running = False
            st.session_state.first_iteration = False

        time.sleep(c.speed)
        st.rerun()




# with tabs[2]:
#     st.markdown(c.markdown_text)

