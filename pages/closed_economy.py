import streamlit as st
import pandas as pd
import time
import plotly.express as px

import config as c
import helpers as h


# ―――― Session State ――――――――――――――――
h.session_init(
    phase="idle",        # idle | short_term_paused | adjusting | done
    pi_prev=None,
    iter_counter=0,
    iteration_df=pd.DataFrame(columns=["Iteration", "Output", "Inflation"]),
    locked_df=None,
)


def reset():
    st.session_state.phase = "idle"
    st.session_state.pi_prev = None
    st.session_state.iter_counter = 0
    st.session_state.iteration_df = pd.DataFrame(columns=["Iteration", "Output", "Inflation"])


def lock_run():
    if not st.session_state.iteration_df.empty:
        st.session_state.locked_df = st.session_state.iteration_df.copy()


def clear_lock():
    st.session_state.locked_df = None


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# ―――― Sidebar ――――――――――――――――
st.sidebar.header("Closed Economy")
text_to_show = ''

with st.sidebar:
    phase = st.session_state.phase
    is_running = phase == "adjusting"
    is_paused = phase == "short_term_paused"

    # Play / Reset buttons
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if is_running:
            play_clicked = False
            st.button("⏸ Running…", disabled=True, width="stretch")
        elif is_paused:
            play_clicked = False
            # Continue shown in main area
            st.button("▶▶ Paused", disabled=True, width="stretch")
        else:
            play_clicked = st.button("⏵ Play", type="primary", width="stretch")
    with bcol2:
        reset_clicked = st.button("↺ Reset", on_click=reset, width="stretch", disabled=is_running)

    level = st.selectbox('Control Level', options=['Easy', 'Medium', 'Advanced'],
                         disabled=is_running or is_paused, on_change=reset)

    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>",
                        unsafe_allow_html=True)

    #show_phillips = st.toggle("Show Phillips Curve", value=False)

    # ―――― Parameter Inputs ――――――――――――――――
    if level == 'Easy':
        st.markdown('##### Please Select the shock:')
        shock_type = st.pills('shock', label_visibility='collapsed',
                              options=['Neg. Inflation shock', 'Pos. Inflation shock',
                                       'Pos. Monetary Shock', 'Neg. Monetary Shock',
                                       'Pos. Demand shock', 'Neg. Demand shock'],
                              disabled=is_running or is_paused, on_change=reset)
        phi = 1.0; lambda_p = 0.5; lambda_i = 0.5; gamma = 0.5; eta = 0.0
        if shock_type == 'Neg. Inflation shock':
            omega = 4.5; r_init = 2.0; pi_0_override = 4.0
            text_to_show = c.neg_inflation_shock
        elif shock_type == 'Pos. Inflation shock':
            omega = 4.5; r_init = 2.0; pi_0_override = 2.0
            text_to_show = c.pos_inflation_shock
        elif shock_type == 'Pos. Monetary Shock':
            omega = 4.5; r_init = 1.3; pi_0_override = 3.0
            text_to_show = c.pos_monetary_shock
        elif shock_type == 'Neg. Monetary Shock':
            omega = 4.5; r_init = 2.7; pi_0_override = 3.0
            text_to_show = c.neg_monetary_shock
        elif shock_type == 'Pos. Demand shock':
            omega = 5.0; r_init = 2.0; pi_0_override = 3.0
            text_to_show = c.pos_demand_shock
        elif shock_type == 'Neg. Demand shock':
            omega = 4.0; r_init = 2.0; pi_0_override = 3.0
            text_to_show = c.neg_demand_shock
        else:
            omega = 4.5; r_init = 2.0; pi_0_override = None
            text_to_show = c.placeholder_shock

    elif level == 'Medium':
        phi = 1.0; lambda_p = 0.5; lambda_i = 0.5; gamma = 0.5
        omega = st.slider(r'$\omega :$', on_change=reset, min_value=1.0, max_value=8.0, step=0.1, value=4.5,
                          help=r"IS Curve: $Y = \omega - \phi r$")
        r_init = st.slider(r"$r' (\%) :$", on_change=reset, min_value=0.1, max_value=3.5, step=0.1, value=2.0,
                           help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        pi = st.slider(r"$\pi (\%) :$", on_change=reset, min_value=-5.0, max_value=10.0, step=0.25, value=3.0,
                       help=r"Initial inflation level (IA curve position at period 1)")
        eta = st.slider(r"$\eta$ (exogenous shock):", on_change=reset, min_value=-2.0, max_value=2.0, step=0.1, value=0.0,
                        help=r"IA curve: $\pi_{t+1} = \pi_t + \gamma\tilde{Y}_t + \eta$. Persistent price-level shock each period (e.g. supply disruption, VAT change).")
        pi_0_override = pi

        empty_text_counter = 0
        if omega > 5.0:   omega_text = c.omega_text_exp
        elif omega < 4.0: omega_text = c.omega_text_res
        else:             omega_text = ''; empty_text_counter += 1

        if r_init > 2.3:   r_text = c.r_text_con
        elif r_init < 1.7: r_text = c.r_text_exp
        else:              r_text = ''; empty_text_counter += 1

        if pi > 5.0:   pi_text = c.pi_text_inf
        elif pi < 1.0: pi_text = c.pi_text_def
        else:          pi_text = ''; empty_text_counter += 1

        text_to_show = (omega_text + r_text + pi_text) if empty_text_counter < 3 \
            else c.empty_placeholder_moderate_level_shock

    elif level == 'Advanced':
        st.markdown('##### For IS Curve')
        phi = st.number_input(r'$\phi :$', on_change=reset, min_value=0.1, step=0.1, value=1.0,
                              help=r"IS Curve: $Y = \omega - \phi r$")
        omega = st.number_input(r'$\omega :$', on_change=reset, min_value=0.0, step=0.5, value=4.5,
                                help=r"IS Curve: $Y = \omega - \phi r$")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### For MP Curve')
        r_init = st.number_input(r"$r' (\%) :$", on_change=reset, min_value=0.1, max_value=10.0, step=0.1, value=2.0,
                                 help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        lambda_p = st.number_input(r'$\lambda_P :$', on_change=reset, min_value=0.0, max_value=10.0, step=0.1, value=0.5,
                                   help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        lambda_i = st.number_input(r'$\lambda_I :$', on_change=reset, min_value=0.1, max_value=10.0, step=0.1, value=0.5,
                                   help=r"MP Curve: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$")
        pi = st.number_input(r'$\pi$ (initial inflation):', on_change=reset, step=0.1, value=3.0)
        pi_0_override = pi
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### For IA Curve')
        gamma = st.number_input(r'$\gamma :$', on_change=reset, min_value=0.0, step=0.1, value=0.5)
        eta = st.number_input(r'$\eta$ (exogenous shock):', on_change=reset, step=0.1, value=0.0,
                              help=r"IA curve: π_{t+1} = π_t + γỸ_t + η. Persistent exogenous price shock each period.")



# ―――― Derived Model Parameters ――――――――――――――――
IS_slope = -1 / phi
IS_intercept = omega / phi
MP_slope = lambda_p / c.Y_potential
AD_slope = (IS_slope - lambda_p / c.Y_potential) / lambda_i
AD_intercept = (IS_intercept - r_init + lambda_p) / lambda_i
pi_eq = AD_slope * c.Y_potential + AD_intercept   # long-run equilibrium inflation

# pi_0: the IA level at period 1 (immediate post-shock) — falls back to equilibrium if not set
pi_0 = pi_0_override if pi_0_override is not None else pi_eq

# pi_cur: current IA level during animation (or pi_0 if not started)
if st.session_state.pi_prev is None:
    st.session_state.pi_prev = pi_0
pi_cur = st.session_state.pi_prev

# Intersection with current (animated) IA
MP_intercept_cur = r_init - lambda_p + lambda_i * pi_cur
Y_cur, r_cur = h.find_line_intersection(IS_slope, IS_intercept, MP_slope, MP_intercept_cur)

# Intersection at the shocked IA (period 1 short-run jump)
MP_intercept_shock = r_init - lambda_p + lambda_i * pi_0
Y_shock, r_shock = h.find_line_intersection(IS_slope, IS_intercept, MP_slope, MP_intercept_shock)

# Convergence check: stable if γ < 2·Ȳ·|AD_slope|
convergence_ok = (gamma < 2 * c.Y_potential * abs(AD_slope)) if AD_slope != 0 else True

# ―――― Play: initialize period 0 and period 1 ――――――――――――――――
if play_clicked and phase == "idle":
    st.session_state.phase = "short_term_paused"
    st.session_state.pi_prev = pi_0
    st.session_state.iter_counter = 2
    df = pd.DataFrame(columns=["Iteration", "Output", "Inflation"])
    df.loc[0] = [0, c.Y_potential, pi_eq]   # period 0: pre-shock equilibrium
    df.loc[1] = [1, Y_shock, pi_0]           # period 1: short-run jump
    st.session_state.iteration_df = df
    st.rerun()

phase = st.session_state.phase  # re-read after possible update

# ―――― Plot bounds ――――――――――――――――
if level != 'Easy':
    const = max(abs(Y_shock), abs(c.Y_potential), abs(c.Y_potential - Y_shock)) * 1.3
    const = max(const, 0.5)
else:
    const = 1.0

x_lo, x_hi = c.Y_potential - const, c.Y_potential + const

# ―――― Curve styling: idle = bold single curves, otherwise ST/LT split ――――――――――――――――
if phase == "idle":
    STMP_color, STMP_name, STMP_lw = "#F58518", "MP", c.standard_line_width
    STIA_color, STIA_name, STIA_lw = "#54A24B", "IA", c.standard_line_width
else:
    STMP_color, STMP_name, STMP_lw = "#FAD7B0", "STMP", c.thin_line_width
    STIA_color, STIA_name, STIA_lw = "#CDEACB", "STIA", c.thin_line_width

# ―――― Tabs ――――――――――――――――
tab1, tab2 = st.tabs(["📊 Model", "📖 Theory"])

with tab2:
    st.markdown(c.markdown_text)

with tab1:
    # ―――― Main layout ――――――――――――――――
    cols = st.columns([1.7, 1])

    # ―――― r–Y diagram ――――――――――――――――
    r_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="r - interest rate")
    h.add_line_to_plot(r_Y_fig, IS_slope, IS_intercept, x_lo, x_hi, name='IS', color="#4C78A8")
    h.add_line_to_plot(r_Y_fig, MP_slope, MP_intercept_shock, x_lo, x_hi,
                       name=STMP_name, color=STMP_color, line_width=STMP_lw)

    if phase != "idle":
        h.add_line_to_plot(r_Y_fig, MP_slope, MP_intercept_cur, x_lo, x_hi,
                           name="LTMP", color="#F58518", line_width=c.thin_line_width)
        h.add_vertical_line(r_Y_fig, Y_cur, y_max=r_cur,
                            name=f"Y ({Y_cur:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(r_Y_fig, Y_shock,
                            name=f"Y ({Y_shock:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(r_Y_fig, c.Y_potential, name=f'Ȳ ({c.Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(r_Y_fig, column_to_plot=cols[0])

    output_gap = Y_cur - c.Y_potential

    # ―――― π–Y diagram ――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="𝜋 - inflation")

    h.add_line_to_plot(pi_Y_fig, 0, pi_0, x_lo, x_hi,
                       name=STIA_name, color=STIA_color, line_width=STIA_lw)
    h.add_line_to_plot(pi_Y_fig, AD_slope, AD_intercept, x_lo, x_hi, name='AD', color="#B279A2")

    if phase != "idle":
        h.add_line_to_plot(pi_Y_fig, 0, pi_cur, x_lo, x_hi,
                           name="LTIA", color="#54A24B", line_width=c.thin_line_width)
        h.add_vertical_line(pi_Y_fig, Y_cur, y_max=pi_cur,
                            name=f"Y ({Y_cur:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        Y_IA_AD_shock, _ = h.find_line_intersection(0, pi_0, AD_slope, AD_intercept)
        h.add_vertical_line(pi_Y_fig, Y_IA_AD_shock, y_max=pi_0,
                            name=f"Y ({Y_IA_AD_shock:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(pi_Y_fig, c.Y_potential, name=f'Ȳ ({c.Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(pi_Y_fig, column_to_plot=cols[0])

    # Continue button shown between diagrams and right panel when paused
    if phase == "short_term_paused":
        with cols[0]:
            st.info("**Period 1:** Short-run impact shown. Click **Continue** to run the adjustment.")
            if st.button("▶▶ Continue →", type="primary"):
                st.session_state.phase = "adjusting"
                st.rerun()

    # ―――― Advanced: equation display ――――――――――――――――
    if level == 'Advanced':
        text_to_show = f"""
            <b style="color:black;">IA:</b> 𝜋 = {pi_0:.2f} &nbsp;&nbsp;
            <b style="color:black;">AD:</b> 𝜋 = {AD_slope:.2f}·Y + {AD_intercept:.2f}<br>
            <b style="color:black;">MP:</b> r = {MP_slope:.2f}·Y + {MP_intercept_cur:.2f} &nbsp;&nbsp;
            <b style="color:black;">IS:</b> r = {IS_slope:.2f}·Y + {IS_intercept:.2f}<br>
            <b style="color:black;">Output Gap (Y − Ȳ):</b> {output_gap:.2f}
        """

    # ―――― Right column ――――――――――――――――
    with cols[1].container(border=True):

        if not convergence_ok:
            st.warning("⚠️ These parameters may not converge. Try reducing γ.")

        st.markdown(text_to_show, unsafe_allow_html=True)

        # Lock / clear comparison run — only available once the run is complete
        lc1, lc2 = st.columns(2)
        with lc1:
            st.button("🔖 Remember this run", on_click=lock_run, width="stretch",
                      help="Save this run in gray so you can compare it with the next one",
                      disabled=phase != "done")
        with lc2:
            if st.session_state.locked_df is not None:
                st.button("✕ Forget", on_click=clear_lock, width="stretch")

        # ―――― Y / Periods chart ――――――――――――――――
        output_fig = px.scatter(st.session_state.iteration_df, x="Iteration", y="Output")
        output_fig.update_traces(mode="lines+markers", marker=dict(size=5))

        if st.session_state.locked_df is not None:
            output_fig.add_scatter(
                x=st.session_state.locked_df["Iteration"],
                y=st.session_state.locked_df["Output"],
                mode="lines", line=dict(color="#BBBBBB", dash="dash"), name="Previous run",
            )

        if not st.session_state.iteration_df.empty:
            last = st.session_state.iteration_df.iloc[-1]
            output_fig.add_annotation(x=last["Iteration"], y=last["Output"],
                                      text=f"Y={last['Output']:.2f}", showarrow=False,
                                      xanchor="left", yshift=12)

        output_fig.update_layout(xaxis_title="Period", yaxis_title="Y - Output", showlegend=False)
        h.add_line_to_plot(output_fig, 0, c.Y_potential, 0, c.iteration_count,
                           name=f"Ȳ ({c.Y_potential:.2f})", line_width=2, color="#999999", dash='dot')
        h.show_plotly_fig(output_fig, height=200)

        # ―――― π / Periods chart ――――――――――――――――
        inflation_fig = px.scatter(st.session_state.iteration_df, x="Iteration", y="Inflation")
        inflation_fig.update_traces(mode="lines+markers", marker=dict(size=5))

        if st.session_state.locked_df is not None:
            inflation_fig.add_scatter(
                x=st.session_state.locked_df["Iteration"],
                y=st.session_state.locked_df["Inflation"],
                mode="lines", line=dict(color="#BBBBBB", dash="dash"), name="Previous run",
            )

        if not st.session_state.iteration_df.empty:
            last = st.session_state.iteration_df.iloc[-1]
            inflation_fig.add_annotation(x=last["Iteration"], y=last["Inflation"],
                                         text=f"𝜋={last['Inflation']:.2f}", showarrow=False,
                                         xanchor="left", yshift=12)

        inflation_fig.update_layout(xaxis_title="Period", yaxis_title="𝜋 - inflation", showlegend=False)
        h.add_line_to_plot(inflation_fig, 0, pi_eq, 0, c.iteration_count,
                           name=f"𝜋* ({pi_eq:.2f})", line_width=2, color="#999999", dash='dot')
        h.show_plotly_fig(inflation_fig, height=200)

    # ―――― Animation step ――――――――――――――――
    if phase == "adjusting":
        new_row_idx = len(st.session_state.iteration_df)
        st.session_state.iteration_df.loc[new_row_idx] = [
            st.session_state.iter_counter, Y_cur, pi_cur
        ]
        st.session_state.pi_prev = pi_cur + gamma * (Y_cur - c.Y_potential) / c.Y_potential + eta
        st.session_state.iter_counter += 1

        if st.session_state.iter_counter >= c.iteration_count:
            st.session_state.phase = "done"

        time.sleep(c.speed)
        st.rerun()
