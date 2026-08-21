import streamlit as st
import pandas as pd
import time
import plotly.express as px

import config as c
import helpers as h


# ―――― Session State ――――――――――――――――
h.session_init(phase="idle",pi_prev=None,iter_counter=0,iteration_df=pd.DataFrame(columns=["Iteration", "Output", "Inflation", "Interest Rate"]),locked_df=None,)


def reset():
    st.session_state.phase = "idle"
    st.session_state.pi_prev = None
    st.session_state.iter_counter = 0
    st.session_state.iteration_df = pd.DataFrame(columns=["Iteration", "Output", "Inflation", "Interest Rate"])


def lock_run():
    if not st.session_state.iteration_df.empty:
        st.session_state.locked_df = st.session_state.iteration_df.copy()


def clear_lock():
    st.session_state.locked_df = None


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# ―――― Medium: when does a slider count as "shocked"? ――――――――――――――――
# The SAME thresholds pick the descriptive text and decide how many forces are
# active, so no setting can be active without a description. (They used to differ
# — text at ω>5 / r'>2.3 but activity at ω>4.6 / r'>2.1 — which left the panel
# blank for ω between 4.6 and 5, or r' between 2.1 and 2.3.)
OMEGA_HI, OMEGA_LO = 4.6, 4.4
RINIT_HI, RINIT_LO = 2.1, 1.9

# ―――― Sidebar ――――――――――――――――
st.sidebar.header("Closed Economy")
text_to_show = ''

with st.sidebar:
    phase = st.session_state.phase
    is_running = phase == "adjusting"
    is_paused = phase == "short_term_paused"

    level = st.selectbox('Control Level', options=['Easy', 'Medium', 'Advanced'],
                         disabled=is_running or is_paused, on_change=reset)


    show_phillips = st.toggle("Show the IA as a Phillips Curve", value=False, disabled=is_running or is_paused) if level == 'Advanced' else False

    # ―――― Parameter Inputs ――――――――――――――――
    if level == 'Easy':
        st.markdown('##### Please Select the shock:')
        shock_type = st.pills('shock', label_visibility='collapsed',
                              options=['Upward Inflation Shock', 'Downward Inflation Shock',
                                       'Expansionary Monetary Shock', 'Contractionary Monetary Shock',
                                       'Expansionary Demand Shock', 'Contractionary Demand Shock'],
                              disabled=is_running or is_paused, on_change=reset)
        phi = 1.0; lambda_p = 0.5; lambda_i = 0.5; gamma = 0.5; eta = 0.0; inflation_shock = 0.0
        if shock_type == 'Upward Inflation Shock':
            omega = 4.5; r_init = 2.0; pi_0_override = 4.0
            text_to_show = c.neg_inflation_shock
        elif shock_type == 'Downward Inflation Shock':
            omega = 4.5; r_init = 2.0; pi_0_override = 2.0
            text_to_show = c.pos_inflation_shock
        elif shock_type == 'Expansionary Monetary Shock':
            omega = 4.5; r_init = 1.3; pi_0_override = 3.0
            text_to_show = c.pos_monetary_shock
        elif shock_type == 'Contractionary Monetary Shock':
            omega = 4.5; r_init = 2.7; pi_0_override = 3.0
            text_to_show = c.neg_monetary_shock
        elif shock_type == 'Expansionary Demand Shock':
            omega = 5.0; r_init = 2.0; pi_0_override = 3.0
            text_to_show = c.pos_demand_shock
        elif shock_type == 'Contractionary Demand Shock':
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
        inflation_shock = st.slider(r"Initial inflation shock (%):", on_change=reset, min_value=-3.0, max_value=3.0, step=0.25, value=0.0,
                                    help=r"One-off shift of initial inflation away from equilibrium. 0 = no shock. "
                                         r"Distinct from the per-period $\eta$ of the IA curve (Advanced).")
        eta = 0
        pi_0_override = None  # resolved after pi_eq is computed

        if omega > OMEGA_HI:   omega_text = c.omega_text_exp
        elif omega < OMEGA_LO: omega_text = c.omega_text_res
        else:                  omega_text = ''

        if r_init > RINIT_HI:   r_text = c.r_text_con
        elif r_init < RINIT_LO: r_text = c.r_text_exp
        else:                   r_text = ''

        if inflation_shock > 0:   pi_text = c.pi_text_inf
        elif inflation_shock < 0: pi_text = c.pi_text_def
        else:                     pi_text = ''
        # text_to_show resolved after derived params (needs Y_shock, pi_eq)

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
        inflation_shock = st.number_input(r"Initial inflation shock (%):", on_change=reset, min_value=-3.0, max_value=3.0, step=0.25, value=0.0,
                                           help=r"One-off shift of initial inflation away from equilibrium. 0 = no shock. "
                                                r"Distinct from the per-period $\eta$ below.")
        pi_0_override = None  # resolved after pi_eq is computed
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### For IA Curve')
        gamma = st.number_input(r'$\gamma :$', on_change=reset, min_value=0.0, step=0.1, value=0.5)
        eta = st.number_input(r'$\eta$ (exogenous shock):', on_change=reset, step=0.1, value=0.0,
                              help=r"IA curve: π_{t+1} = π_t + γỸ_t + η. Persistent exogenous price shock each period.")


    # Play / Reset buttons
    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    bcol1, bcol2 = st.columns([1.2,0.8])
    with bcol1:
        if is_running:
            play_clicked = False
            st.button("⏸ Running…", disabled=True, width="stretch")
        elif is_paused:
            play_clicked = False
            st.button("▶▶ Paused", disabled=True, width="stretch")
        else:
            play_clicked = st.button("↻ Play again" if phase == "done" else "⏵ Play",
                                     type="primary", width="stretch")
    with bcol2:
        reset_clicked = st.button("↺ Reset", on_click=reset, width="stretch", disabled=is_running)


    continue_clicked = False
    if is_paused:
        st.info("**Period 1:** Initial shock, short-run impact shown. Click **Continue** to see the long-run adjustment.")
        continue_clicked = st.button("▶▶ Continue", type="primary", width="stretch")




# ―――― Settings (user-overridable via Settings page) ――――――――――――――――
iteration_count = st.session_state.get("setting_iterations", c.iteration_count)
sim_speed       = st.session_state.get("setting_speed", c.speed)

# ―――― Derived Model Parameters ――――――――――――――――
IS_slope = -1 / phi
IS_intercept = omega / phi
MP_slope = lambda_p / c.Y_potential
AD_slope = (IS_slope - lambda_p / c.Y_potential) / lambda_i
AD_intercept = (IS_intercept - r_init + lambda_p) / lambda_i
pi_eq = AD_slope * c.Y_potential + AD_intercept   # long-run equilibrium inflation
r_eq = MP_slope * c.Y_potential + (r_init - lambda_p + lambda_i * pi_eq)   # rate at that point

# Fixed pre-shock (initial) equilibrium — the economy's resting point BEFORE any shock: Y=Ȳ, π=3.0, r=3.5 under the default parameters. The time-series charts start here (period 0) and then converge to the NEW long-run equilibrium (pi_eq / r_eq), which differs after demand or monetary shocks.
PI_BASELINE = 3.0
R_BASELINE  = (0.5 / c.Y_potential) * c.Y_potential + (2.0 - 0.5 + 0.5 * PI_BASELINE)  # default params → 3.5

# Medium & Advanced: anchor pi_0 to the FIXED baseline equilibrium (default omega=4.5, r_init=2.0, lambda=0.5 → π=3.0) plus only the inflation shock, so demand/monetary parameters never move the initial inflation — it stays constant unless the user explicitly changes η (inflation shock).
if level in ('Medium', 'Advanced'):
    _ad_slope_base = (-1.0 - 0.5) / 0.5          # phi=1, lambda_p=0.5, lambda_i=0.5
    _ad_int_base   = (4.5 - 2.0 + 0.5) / 0.5     # omega=4.5, r_init=2.0, lambda_p=0.5
    pi_eq_baseline = _ad_slope_base * c.Y_potential + _ad_int_base
    pi_0_override  = pi_eq_baseline + inflation_shock

# pi_0: expected/anchor inflation entering period 1 (immediate post-shock) — falls
# back to equilibrium if not set. Under the Phillips curve this is π^e (the level
# the PC crosses at Ȳ); the realised period-1 inflation is higher/lower once the
# output gap feeds through.
pi_0 = pi_0_override if pi_0_override is not None else pi_eq

# Slope of the Phillips curve π = π^e + (γ/Ȳ)·Ỹ
pc_slope = gamma / c.Y_potential

# pi_e_cur: expected inflation carried into the current animated period (π^e).
if st.session_state.pi_prev is None:
    st.session_state.pi_prev = pi_0
pi_e_cur = st.session_state.pi_prev


def operating_point(pi_expected):
    """Short-run (Y, π, r) for a given expected inflation π^e.

    Phillips curve ON: inflation reacts to the CURRENT output gap, so (Y, π) is the
    joint solution of AD and the PC π = π^e + (γ/Ȳ)·Ỹ — inflation moves immediately.
    Phillips curve OFF (horizontal IA): inflation is predetermined at π^e and only
    output jumps (IS∩MP)."""
    if show_phillips:
        pc_int = pi_expected - pc_slope * c.Y_potential
        Y, pi_ = h.find_line_intersection(AD_slope, AD_intercept, pc_slope, pc_int)
    else:
        pi_ = pi_expected
        Y, _ = h.find_line_intersection(IS_slope, IS_intercept, MP_slope,
                                        r_init - lambda_p + lambda_i * pi_)
    r = MP_slope * Y + (r_init - lambda_p + lambda_i * pi_)
    return Y, pi_, r


# Current (animated) operating point and the period-1 short-run jump.
Y_cur, pi_cur, r_cur = operating_point(pi_e_cur)
Y_shock, pi_shock, r_shock = operating_point(pi_0)
MP_intercept_cur   = r_init - lambda_p + lambda_i * pi_cur
MP_intercept_shock = r_init - lambda_p + lambda_i * pi_shock

# Convergence check: stable if γ < 2·Ȳ·|AD_slope|
convergence_ok = (gamma < 2 * c.Y_potential * abs(AD_slope)) if AD_slope != 0 else True

# ―――― Medium: resolve combined text ――――――――――――――――
if level == 'Medium':
    demand_shifted = omega > OMEGA_HI or omega < OMEGA_LO
    money_shifted = r_init > RINIT_HI or r_init < RINIT_LO
    infl_shifted = inflation_shock != 0.0
    n_active = sum([demand_shifted, money_shifted, infl_shifted])

    if n_active == 0:
        text_to_show = c.empty_placeholder_moderate_level_shock
    elif n_active == 1:
        text_to_show = omega_text + r_text + pi_text
    else:
        # Characterise net outcome from model
        output_above = Y_shock > c.Y_potential * 1.01
        output_below = Y_shock < c.Y_potential * 0.99
        pi_above = pi_0 > pi_eq + 0.05
        pi_below = pi_0 < pi_eq - 0.05

        # Label active forces
        force_parts = []
        if omega > OMEGA_HI:
            force_parts.append("expansionary demand (↑ω)")
        elif omega < OMEGA_LO:
            force_parts.append("restrictive demand (↓ω)")
        if r_init < RINIT_LO:
            force_parts.append("loose monetary policy (↓r')")
        elif r_init > RINIT_HI:
            force_parts.append("tight monetary policy (↑r')")
        if inflation_shock > 0:
            force_parts.append("upward inflation shock (↑η)")
        elif inflation_shock < 0:
            force_parts.append("downward inflation shock (↓η)")
        forces_str = " + ".join(force_parts)

        # Detect conflict: forces push in opposite directions on output
        demand_exp = omega > OMEGA_HI
        demand_res = omega < OMEGA_LO
        money_loose = r_init < RINIT_LO
        money_tight_ = r_init > RINIT_HI
        conflicting = (demand_exp and money_tight_) or (demand_res and money_loose)

        if output_above:
            output_desc = "output <b>above potential</b>"
        elif output_below:
            output_desc = "output <b>below potential</b>"
        else:
            output_desc = "output <b>near potential</b>"

        if pi_above:
            pi_desc = "inflation <b>above equilibrium</b>"
        elif pi_below:
            pi_desc = "inflation <b>below equilibrium</b>"
        else:
            pi_desc = "inflation <b>near equilibrium</b>"

        if conflicting:
            if output_above:
                dominant = "Expansionary demand dominates — the monetary tightening is not enough to offset the stimulus."
            elif output_below:
                dominant = "Tight monetary policy dominates — it more than offsets the demand expansion."
            else:
                dominant = "The two forces roughly cancel out — output stays near potential."
            conflict_note = f"<br><i style='color:#888;'>{dominant}</i>"
        else:
            conflict_note = "<br><i style='color:#888;'>The shocks reinforce each other, amplifying the effect on output and inflation.</i>"

        text_to_show = f"""
                <div style="font-size:17px; font-weight:700; color:#222;">Combined Shock 🔀</div>
                <div style="font-size:13px; color:gray; margin-top:4px;">
                    <b>{forces_str}</b><br>
                    Net result: {output_desc} and {pi_desc}.{conflict_note}
                </div>"""

# ―――― Continue: advance from short_term_paused to adjusting ――――――――――――――――
if continue_clicked and phase == "short_term_paused":
    st.session_state.pi_prev = pi_0 + gamma * (Y_shock - c.Y_potential) / c.Y_potential + eta
    st.session_state.phase = "adjusting"
    st.rerun()

# ―――― Play: initialize period 0 and period 1 ――――――――――――――――
# Also fires from "done", so Play restarts a finished run instead of doing nothing:
# the block below rebuilds the whole run state from scratch, so replaying is just
# running it again. A run saved with "Remember this run" is deliberately kept, so
# the replay is drawn against it.
if play_clicked and phase in ("idle", "done"):
    st.session_state.phase = "short_term_paused"
    st.session_state.pi_prev = pi_0
    st.session_state.iter_counter = 2
    df = pd.DataFrame(columns=["Iteration", "Output", "Inflation", "Interest Rate"])
    df.loc[0] = [0, c.Y_potential, PI_BASELINE, R_BASELINE]  # period 0: initial pre-shock equilibrium
    df.loc[1] = [1, Y_shock, pi_shock, r_shock]              # period 1: short-run jump
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

# ―――― Curve positions in each phase ――――――――――――――――
# Every curve is held in three positions and the phase decides which are drawn:
#   initial — the pre-shock resting point (period 0)
#   short   — the period-1 impact, frozen where the shock put it
#   long    — where the curve is right now
# idle shows `initial` alone; Play adds `short` and keeps `initial` as a dotted
# ghost so it is obvious which curves moved; Continue drops `initial` and brings
# out `long`, which then drifts away from `short` period by period.
show_initial = phase == "short_term_paused"
show_long = phase in ("adjusting", "done")

# Pre-shock resting point, at the default parameters (ω=4.5, φ=1, r'=2, λ=0.5).
init_IS = (-1.0, 4.5)
init_MP = (0.5 / c.Y_potential, 3.0)
init_AD = ((init_IS[0] - 0.5 / c.Y_potential) / 0.5, (4.5 - 2.0 + 0.5) / 0.5)
init_IA = (0.0, PI_BASELINE)

# IS and AD are built from parameters alone, so they do not move DURING a run —
# only the shock itself displaces them. MP and IA are the ones that travel.
st_IS = lt_IS = (IS_slope, IS_intercept)
st_AD = lt_AD = (AD_slope, AD_intercept)
st_MP, lt_MP = (MP_slope, MP_intercept_shock), (MP_slope, MP_intercept_cur)


def _ia_spec(pi_level, y_at):
    """IA in π–Y space. With the Phillips curve on it is drawn against THIS
    period's output gap (π = π^e + γ·Ỹ), so it pivots on the operating point
    instead of lying flat."""
    if show_phillips:
        return (pc_slope, pi_level - pc_slope * y_at)
    return (0.0, pi_level)


st_IA = _ia_spec(pi_shock, Y_shock)
lt_IA = _ia_spec(pi_cur, Y_cur)
IA_label = "IA(PC)" if show_phillips else "IA"

# Operating point marker.
sY, sIA_pi = (c.Y_potential, PI_BASELINE) if phase == "idle" else (Y_cur, pi_cur)

# ―――― Tabs ――――――――――――――――
tab1, tab2 = st.tabs(["📊 Model", "📖 Theory"])

with tab2:
    st.markdown(c.markdown_text)

with tab1:
    # ―――― Main layout ――――――――――――――――
    # Same shape as the open-economy page: bordered panels with a header each, so
    # the two pages read as one app.
    cols = st.columns([1.7, 1], gap="small", vertical_alignment="top")
    diagrams = cols[0].container(border=True, height="stretch")
    h.panel_header("Diagrams", diagrams)

    # ―――― r–Y diagram ――――――――――――――――
    # The x-title is on the lower chart only: the two share the axis.
    r_Y_fig = h.create_linear_plot(x_label="", y_label="r - interest rate")
    h.add_curve_set(r_Y_fig, 'IS', x_lo, x_hi, init_IS, st_IS, lt_IS, show_initial, show_long)
    h.add_curve_set(r_Y_fig, 'MP', x_lo, x_hi, init_MP, st_MP, lt_MP, show_initial, show_long)

    if phase != "idle":
        h.add_vertical_line(r_Y_fig, Y_cur, y_max=r_cur,
                            name=f"Y ({Y_cur:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(r_Y_fig, sY,
                            name=f"Y ({sY:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(r_Y_fig, c.Y_potential, name=f'Ȳ ({c.Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(r_Y_fig, height=340, column_to_plot=diagrams, key="ce_rY")

    output_gap = Y_cur - c.Y_potential

    # ―――― π–Y diagram ――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="𝜋 - inflation")
    h.add_curve_set(pi_Y_fig, 'IA', x_lo, x_hi, init_IA, st_IA, lt_IA,
                    show_initial, show_long, label=IA_label)
    h.add_curve_set(pi_Y_fig, 'AD', x_lo, x_hi, init_AD, st_AD, lt_AD, show_initial, show_long)

    if phase != "idle":
        h.add_vertical_line(pi_Y_fig, Y_cur, y_max=pi_cur,
                            name=f"Y ({Y_cur:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(pi_Y_fig, sY, y_max=sIA_pi,
                            name=f"Y ({sY:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(pi_Y_fig, c.Y_potential, name=f'Ȳ ({c.Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(pi_Y_fig, height=360, column_to_plot=diagrams, key="ce_piY")

    # ―――― Advanced: equation display ――――――――――――――――
    if level == 'Advanced':
        shock_size = pi_0 - pi_eq
        shock_label = f"+{shock_size:.1f}" if shock_size >= 0 else f"{shock_size:.1f}"
        if show_phillips:
            pi_e = pi_e_cur   # π^e: the level the PC crosses at Ȳ
            ia_line = (f'<b style="color:#54A24B;">IA (Phillips):</b> '
                       f'𝜋 = {pi_e:.1f} + {gamma:.1f}·Ỹ &nbsp;'
                       f'<span style="color:gray;">(𝜋<sub>expected</sub> at Ȳ)</span>')
        else:
            ia_line = (f'<b style="color:#54A24B;">IA:</b> 𝜋 = {pi_0:.1f} &nbsp;'
                       f'<span style="color:gray;">(shock: {shock_label})</span>')
        text_to_show = f"""
            <b style="color:#4C78A8;">IS:</b> Y = {omega:.1f} − {phi:.1f}·r &nbsp;→&nbsp; r = {IS_slope:.1f}·Y + {IS_intercept:.1f}<br>
            <b style="color:#F58518;">MP:</b> r = {MP_slope:.1f}·Y + {MP_intercept_cur:.1f}<br>
            <b style="color:#B279A2;">AD:</b> 𝜋 = {AD_slope:.1f}·Y + {AD_intercept:.1f}<br>
            {ia_line}<br>
            <hr style="margin:4px 0; border:none; border-top:1px solid #ddd;">
            <b>Output gap (Y − Ȳ):</b> {output_gap:.1f}<br>
            <b>r:</b> {r_cur:.1f}
        """

    # ―――― Right column ――――――――――――――――
    with cols[1].container(border=True, height="stretch"):
        h.panel_header("What is happening")

        if not convergence_ok:
            st.warning("⚠️ **These settings never settle.** Output and inflation keep swinging "
                       "instead of coming to rest. Try a smaller γ.")

        st.markdown(text_to_show, unsafe_allow_html=True)
        # Where the run ends up — numbers only. The description above says it in words.
        st.markdown(f"<div style='font-size:12px; color:gray; margin-top:8px;'><b>Long run:</b> "
                    f"output back at Ȳ = {c.Y_potential:.2f}; inflation settles at {pi_eq:.2f}%; "
                    f"interest rate at {r_eq:.2f}%.</div>", unsafe_allow_html=True)

        # Lock / clear comparison run — only available once the run is complete
        lc1, lc2 = st.columns([1.2,0.8])
        with lc1:
            st.button("🔖 Remember this run", on_click=lock_run, width="stretch",
                      help="Save this run in gray so you can compare it with the next one",
                      disabled=phase != "done")
        with lc2:
            if st.session_state.locked_df is not None:
                st.button("✕ Forget", on_click=clear_lock, width="stretch")

        h.panel_header("Over time")

        # ―――― Y / Periods chart ――――――――――――――――
        # Only the bottom chart shows the "Period" title — the three share one x-axis.
        output_fig = px.scatter(st.session_state.iteration_df, x="Iteration", y="Output")
        output_fig.update_traces(mode="lines", marker=dict(size=5))

        if st.session_state.locked_df is not None:
            output_fig.add_scatter( x=st.session_state.locked_df["Iteration"], y=st.session_state.locked_df["Output"], mode="lines", line=dict(color="#BBBBBB", dash="dot"), name="Previous run", )

        if not st.session_state.iteration_df.empty:
            last = st.session_state.iteration_df.iloc[-1]
            output_fig.add_annotation(x=last["Iteration"], y=last["Output"], text=f"Y={last['Output']:.2f}", showarrow=False, xanchor="left", yshift=12)

        output_fig.update_layout(xaxis_title="", yaxis_title="Y - Output", showlegend=False)
        h.add_line_to_plot(output_fig, 0, c.Y_potential, 0, iteration_count,
                           name=f"Ȳ ({c.Y_potential:.2f})", line_width=2, color="#999999", dash='dot')
        h.show_plotly_fig(output_fig, height=180, key="ce_ts_output")

        # ―――― π / Periods chart ――――――――――――――――
        inflation_fig = px.scatter(st.session_state.iteration_df, x="Iteration", y="Inflation")
        inflation_fig.update_traces(mode="lines", marker=dict(size=5))

        if st.session_state.locked_df is not None:
            inflation_fig.add_scatter( x=st.session_state.locked_df["Iteration"], y=st.session_state.locked_df["Inflation"], mode="lines", line=dict(color="#BBBBBB", dash="dot"), name="Previous run", )

        if not st.session_state.iteration_df.empty:
            last = st.session_state.iteration_df.iloc[-1]
            inflation_fig.add_annotation(x=last["Iteration"], y=last["Inflation"],text=f"𝜋={last['Inflation']:.2f}", showarrow=False,xanchor="left", yshift=12)

        inflation_fig.update_layout(xaxis_title="", yaxis_title="𝜋 - inflation", showlegend=False)
        h.add_line_to_plot(inflation_fig, 0, pi_eq, 0, iteration_count,
                           name=f"𝜋* ({pi_eq:.2f})", line_width=2, color="#999999", dash='dot')
        h.show_plotly_fig(inflation_fig, height=180, key="ce_ts_inflation")

        # ―――― r / Periods chart ――――――――――――――――
        rate_fig = px.scatter(st.session_state.iteration_df, x="Iteration", y="Interest Rate")
        rate_fig.update_traces(mode="lines", marker=dict(size=5))

        if st.session_state.locked_df is not None:
            rate_fig.add_scatter( x=st.session_state.locked_df["Iteration"], y=st.session_state.locked_df["Interest Rate"], mode="lines", line=dict(color="#BBBBBB", dash="dot"), name="Previous run", )

        if not st.session_state.iteration_df.empty:
            last = st.session_state.iteration_df.iloc[-1]
            rate_fig.add_annotation(x=last["Iteration"], y=last["Interest Rate"], text=f"r={last['Interest Rate']:.2f}", showarrow=False, xanchor="left", yshift=12)

        rate_fig.update_layout(xaxis_title="Period", yaxis_title="r - interest rate", showlegend=False)
        h.add_line_to_plot(rate_fig, 0, r_eq, 0, iteration_count,
                           name=f"r* ({r_eq:.2f})", line_width=2, color="#999999", dash='dot')
        h.show_plotly_fig(rate_fig, height=200, key="ce_ts_rate")

    # ―――― Animation step ――――――――――――――――
    if phase == "adjusting":
        new_row_idx = len(st.session_state.iteration_df)
        st.session_state.iteration_df.loc[new_row_idx] = [st.session_state.iter_counter, Y_cur, pi_cur, r_cur]
        # Next period's expected inflation = π^e + γ·Ỹ (+ persistent η). Anchored on
        # π^e (this period's expectation), not the realised π, so the Phillips-curve
        # gap is not double-counted.
        st.session_state.pi_prev = pi_e_cur + gamma * (Y_cur - c.Y_potential) / c.Y_potential + eta
        st.session_state.iter_counter += 1

        if st.session_state.iter_counter >= iteration_count:
            st.session_state.phase = "done"

        time.sleep(sim_speed)
        st.rerun()
