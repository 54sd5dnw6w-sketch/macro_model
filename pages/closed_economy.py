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


# Pause/resume mid-run. Callbacks, not return values: a click arriving while the
# animation sleeps is applied before the next script run, so no step is lost.
def pause_run():
    if st.session_state.phase == "adjusting":
        st.session_state.phase = "run_paused"


def resume_run():
    if st.session_state.phase == "run_paused":
        st.session_state.phase = "adjusting"


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# ―――― Default parameters ――――――――――――――――
# Y is an index at Ȳ = 100 and the gap Ỹ = 100·(Y−Ȳ)/Ȳ is in percentage points.
# r' = r* − λ_I·π* and ω = Ȳ + φ·r* are what rest the economy at Y = 100, π = 2, r = 2.
PHI_BASE, OMEGA_BASE = 1.0, 102.0
RP_BASE, LP_BASE, LI_BASE, GAMMA_BASE = 1.0, 0.5, 0.5, 0.4

# Period 0 at the default parameters. Recomputed after the sidebar with whatever
# structural parameters the user set; the Easy level never changes them.
_AD_SLOPE_BASE = (-1.0 / PHI_BASE - LP_BASE) / LI_BASE
_AD_INT_BASE   = (OMEGA_BASE / PHI_BASE - RP_BASE + LP_BASE * c.Y_potential) / LI_BASE
PI_BASELINE = _AD_SLOPE_BASE * c.Y_potential + _AD_INT_BASE                      # → 2.0
R_BASELINE  = RP_BASE + LI_BASE * PI_BASELINE                                    # → 2.0

# ―――― Shock sizes (Easy mode) ――――――――――――――――
# A 1.5 % of GDP demand swing, a 100 bp policy move, a 1.5 pp price shock.
DEMAND_SHOCK, MONETARY_SHOCK, INFL_SHOCK = 1.5, 1.0, 1.5

# Half a slider step, so one click always registers. The same thresholds pick the
# descriptive text, so no setting can be active without a description.
OMEGA_HI, OMEGA_LO = OMEGA_BASE + 0.1, OMEGA_BASE - 0.1
RINIT_HI, RINIT_LO = RP_BASE + 0.05, RP_BASE - 0.05

# ―――― Sidebar ――――――――――――――――
st.sidebar.header("Closed Economy")
text_to_show = ''

with st.sidebar:
    phase = st.session_state.phase
    is_running = phase == "adjusting"
    is_paused = phase == "short_term_paused"
    is_run_paused = phase == "run_paused"      # held mid-run by the user
    busy = is_running or is_paused or is_run_paused

    level = st.selectbox('Control Level', options=['Easy', 'Medium', 'Advanced'],
                         disabled=busy, on_change=reset)


    show_phillips = st.toggle("Show the IA as a Phillips Curve", value=False, disabled=busy) if level == 'Advanced' else False

    # ―――― Parameter Inputs ――――――――――――――――
    if level == 'Easy':
        st.markdown('##### Please Select the shock:')
        shock_type = st.pills('shock', label_visibility='collapsed',
                              options=['Upward Inflation Shock', 'Downward Inflation Shock',
                                       'Expansionary Monetary Shock', 'Contractionary Monetary Shock',
                                       'Expansionary Demand Shock', 'Contractionary Demand Shock'],
                              disabled=busy, on_change=reset)
        phi = PHI_BASE; lambda_p = LP_BASE; lambda_i = LI_BASE; gamma = GAMMA_BASE
        eta = 0.0; inflation_shock = 0.0
        omega = OMEGA_BASE; r_init = RP_BASE; pi_0_override = PI_BASELINE
        if shock_type == 'Upward Inflation Shock':
            pi_0_override = PI_BASELINE + INFL_SHOCK
            text_to_show = c.neg_inflation_shock
        elif shock_type == 'Downward Inflation Shock':
            pi_0_override = PI_BASELINE - INFL_SHOCK
            text_to_show = c.pos_inflation_shock
        elif shock_type == 'Expansionary Monetary Shock':
            r_init = RP_BASE - MONETARY_SHOCK
            text_to_show = c.pos_monetary_shock
        elif shock_type == 'Contractionary Monetary Shock':
            r_init = RP_BASE + MONETARY_SHOCK
            text_to_show = c.neg_monetary_shock
        elif shock_type == 'Expansionary Demand Shock':
            omega = OMEGA_BASE + DEMAND_SHOCK
            text_to_show = c.pos_demand_shock
        elif shock_type == 'Contractionary Demand Shock':
            omega = OMEGA_BASE - DEMAND_SHOCK
            text_to_show = c.neg_demand_shock
        else:
            pi_0_override = None
            text_to_show = c.placeholder_shock

    elif level == 'Medium':
        phi = PHI_BASE; lambda_p = LP_BASE; lambda_i = LI_BASE; gamma = GAMMA_BASE
        omega = st.slider(r'$\omega :$', on_change=reset,
                          min_value=OMEGA_BASE - 4.0, max_value=OMEGA_BASE + 4.0, step=0.25,
                          value=OMEGA_BASE,
                          help=r"IS: $Y = \omega - \phi r$ — demand that does not depend on $r$. Shifts IS "
                               r"sideways.")
        r_init = st.slider(r"$r' (\%) :$", on_change=reset,
                           min_value=RP_BASE - 1.5, max_value=RP_BASE + 1.5, step=0.1,
                           value=RP_BASE,
                           help=r"MP: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$ — the rule's intercept. "
                                r"Shifts MP up or down.")
        inflation_shock = st.slider(r"Initial inflation shock (%):", on_change=reset, min_value=-3.0, max_value=3.0, step=0.25, value=0.0,
                                    help=r"Starting inflation only: $\pi_0 = \pi^* +$ this. One-off; 0 = no "
                                         r"shock.")
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
        phi = st.number_input(r'$\phi :$', on_change=reset, min_value=0.1, max_value=3.0, step=0.1,
                              value=PHI_BASE,
                              help=r"IS: $Y = \omega - \phi r$ — how much output falls when $r$ rises by 1 pp.")
        omega = st.number_input(r'$\omega :$', on_change=reset, min_value=90.0, max_value=115.0, step=0.5,
                                value=OMEGA_BASE,
                                help=r"IS: $Y = \omega - \phi r$ — demand that does not depend on $r$. Shifts "
                                     r"IS sideways.")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### For MP Curve')
        r_init = st.number_input(r"$r' (\%) :$", on_change=reset, min_value=-2.0, max_value=5.0, step=0.1,
                                 value=RP_BASE,
                                 help=r"MP: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$ — the rule's "
                                      r"intercept. Shifts MP up or down.")
        lambda_p = st.number_input(r'$\lambda_P :$', on_change=reset, min_value=0.0, max_value=2.0, step=0.05,
                                   value=LP_BASE,
                                   help=r"MP: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$ — how hard the "
                                        r"bank reacts to the output gap.")
        lambda_i = st.number_input(r'$\lambda_I :$', on_change=reset, min_value=0.1, max_value=3.0, step=0.05,
                                   value=LI_BASE,
                                   help=r"MP: $r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$ — how hard the "
                                        r"bank reacts to inflation.")
        inflation_shock = st.number_input(r"Initial inflation shock (%):", on_change=reset, min_value=-3.0, max_value=3.0, step=0.25, value=0.0,
                                           help=r"Starting inflation only: $\pi_0 = \pi^* +$ this. One-off; 0 "
                                                r"= no shock.")
        pi_0_override = None  # resolved after pi_eq is computed
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### For IA Curve')
        gamma = st.number_input(r'$\gamma :$', on_change=reset, min_value=0.0, max_value=1.5, step=0.05,
                                value=GAMMA_BASE,
                                help=r"IA: $\pi_{t+1} = \pi_t + \gamma \tilde{Y}_t + \eta$ — how much the "
                                     r"output gap moves inflation.")
        eta = st.number_input(r'$\eta$ (exogenous shock):', on_change=reset,
                              min_value=-1.0, max_value=1.0, step=0.05, value=0.0,
                              help=r"IA: $\pi_{t+1} = \pi_t + \gamma \tilde{Y}_t + \eta$ — a price shock added "
                                   r"in every period.")


    # Play / Reset buttons
    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    bcol1, bcol2 = st.columns([1.2,0.8])
    with bcol1:
        if is_running:
            play_clicked = False
            st.button("⏸ Pause", on_click=pause_run, width="stretch",
                      help="Hold the run where it is. Resume picks it up from the same period.")
        elif is_run_paused:
            play_clicked = False
            st.button("▶ Resume", type="primary", on_click=resume_run, width="stretch")
        elif is_paused:
            play_clicked = False
            st.button("▶▶ Paused", disabled=True, width="stretch")
        else:
            play_clicked = st.button("↻ Play again" if phase == "done" else "⏵ Play",
                                     type="primary", width="stretch")
    with bcol2:
        reset_clicked = st.button("↺ Reset", on_click=reset, width="stretch", disabled=is_running)


    # One slot, written on every rerun. Each animation pass ends in st.rerun(),
    # which aborts the script before Streamlit prunes elements the new run did not
    # re-render — so a status box from the previous phase would linger on screen.
    # Writing the slot unconditionally clears whatever the last phase put there.
    status_slot = st.empty()
    continue_clicked = False
    if is_paused:
        with status_slot.container():
            st.info("**Period 1:** Initial shock, short-run impact shown. Click **Continue** to see the long-run adjustment.")
            continue_clicked = st.button("▶▶ Continue", type="primary", width="stretch")
    elif is_run_paused:
        _held_at = (int(st.session_state.iteration_df["Iteration"].iloc[-1])
                    if not st.session_state.iteration_df.empty else 0)
        status_slot.info(f"**Paused at period {_held_at}.** **▶ Resume** carries on from here; "
                         f"**↺ Reset** stops the run for good.")
    else:
        status_slot.empty()




# ―――― Settings (user-overridable via Settings page) ――――――――――――――――
iteration_count = st.session_state.get("setting_iterations", c.iteration_count)
sim_speed       = st.session_state.get("setting_speed", c.speed)

# ―――― Derived Model Parameters ――――――――――――――――
# Ỹ = Y − Ȳ is already in points, so a coefficient on the gap is a slope in Y
IS_slope = -1 / phi
IS_intercept = omega / phi
MP_slope = lambda_p
AD_slope = (IS_slope - lambda_p) / lambda_i
AD_intercept = (IS_intercept - r_init + lambda_p * c.Y_potential) / lambda_i
pi_eq = AD_slope * c.Y_potential + AD_intercept   # long-run equilibrium inflation
r_eq = MP_slope * c.Y_potential + (r_init - lambda_p * c.Y_potential + lambda_i * pi_eq)   # rate at that point

# ―――― Period 0: the pre-shock resting point ――――――――――――――――
# Re-derived with the user's structural parameters (φ, λ_P, λ_I) at DEFAULT policy
# (ω, r′), so period 0 really is a rest point whatever φ and λ are set to.
_AD_SLOPE_BASE = (-1.0 / phi - lambda_p) / lambda_i
_AD_INT_BASE   = (OMEGA_BASE / phi - RP_BASE + lambda_p * c.Y_potential) / lambda_i
PI_BASELINE = _AD_SLOPE_BASE * c.Y_potential + _AD_INT_BASE
R_BASELINE  = RP_BASE + lambda_i * PI_BASELINE

# Anchor π₀ to the baseline plus the price shock alone, so demand and monetary
# settings never move the starting inflation.
if level in ('Medium', 'Advanced'):
    pi_0_override = PI_BASELINE + inflation_shock

# Inflation entering period 1. With the Phillips curve on this is π^e, and the
# realised period-1 inflation moves once the output gap feeds through.
pi_0 = pi_0_override if pi_0_override is not None else pi_eq

# Slope of the Phillips curve π = π^e + (γ/Ȳ)·Ỹ
pc_slope = gamma

# pi_e_cur: expected inflation carried into the current animated period (π^e).
if st.session_state.pi_prev is None:
    st.session_state.pi_prev = pi_0
pi_e_cur = st.session_state.pi_prev


def operating_point(pi_expected):
    """Short-run (Y, π, r) for a given expected inflation π^e.

    Phillips curve on: (Y, π) solves AD together with π = π^e + (γ/Ȳ)·Ỹ.
    Off: π is predetermined at π^e and only output jumps (IS ∩ MP)."""
    if show_phillips:
        pc_int = pi_expected - pc_slope * c.Y_potential
        Y, pi_ = h.find_line_intersection(AD_slope, AD_intercept, pc_slope, pc_int)
    else:
        pi_ = pi_expected
        Y, _ = h.find_line_intersection(IS_slope, IS_intercept, MP_slope,
                                        r_init - lambda_p * c.Y_potential + lambda_i * pi_)
    r = MP_slope * Y + (r_init - lambda_p * c.Y_potential + lambda_i * pi_)
    return Y, pi_, r


# Current (animated) operating point and the period-1 short-run jump.
Y_cur, pi_cur, r_cur = operating_point(pi_e_cur)
Y_shock, pi_shock, r_shock = operating_point(pi_0)
MP_intercept_cur   = r_init - lambda_p * c.Y_potential + lambda_i * pi_cur
MP_intercept_shock = r_init - lambda_p * c.Y_potential + lambda_i * pi_shock

# Convergence check: stable if γ < 2·Ȳ·|AD_slope|
convergence_ok = (gamma < 2 * abs(AD_slope)) if AD_slope != 0 else True

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
        output_above = h.output_gap(Y_shock, c.Y_potential) > 0.1
        output_below = h.output_gap(Y_shock, c.Y_potential) < -0.1
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
    st.session_state.pi_prev = pi_0 + gamma * h.output_gap(Y_shock, c.Y_potential) + eta
    st.session_state.phase = "adjusting"
    st.rerun()

# ―――― Play: initialize period 0 and period 1 ――――――――――――――――
# Also fires from "done" so Play restarts a finished run. A saved comparison run
# is kept, so the replay is drawn against it.
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
# Sized from the largest gap the run reaches, with a floor so a small shock has room.
MIN_HALF_WINDOW = 2.0
const = max(MIN_HALF_WINDOW,
            1.6 * max(abs(Y_shock - c.Y_potential), abs(Y_cur - c.Y_potential)))
x_lo, x_hi = c.Y_potential - const, c.Y_potential + const

# ―――― Curve positions in each phase ――――――――――――――――
# initial = period 0, short = the period-1 impact, long = where the curve is now.
show_initial = phase == "short_term_paused"
show_long = phase in ("adjusting", "run_paused", "done")

# Pre-shock resting point: default POLICY (ω, r′), the user's structural parameters.
init_IS = (-1.0 / phi, OMEGA_BASE / phi)
init_MP = (MP_slope, RP_BASE - lambda_p * c.Y_potential + lambda_i * PI_BASELINE)
init_AD = (_AD_SLOPE_BASE, _AD_INT_BASE)
init_IA = (0.0, PI_BASELINE)

# IS and AD depend on parameters alone, so only the shock displaces them; MP and
# IA are the ones that travel during a run.
st_IS = lt_IS = (IS_slope, IS_intercept)
st_AD = lt_AD = (AD_slope, AD_intercept)
st_MP, lt_MP = (MP_slope, MP_intercept_shock), (MP_slope, MP_intercept_cur)


def _ia_spec(pi_level, y_at):
    """IA in π–Y space. With the Phillips curve on it is drawn against this
    period's output gap (π = π^e + γ·Ỹ), so it pivots on the operating point
    instead of lying flat."""
    if show_phillips:
        return (pc_slope, pi_level - pc_slope * y_at)
    return (0.0, pi_level)


st_IA = _ia_spec(pi_shock, Y_shock)
lt_IA = _ia_spec(pi_cur, Y_cur)
IA_label = "IA(PC)" if show_phillips else "IA"

sY, sIA_pi = (c.Y_potential, PI_BASELINE) if phase == "idle" else (Y_cur, pi_cur)

# ―――― Tabs ――――――――――――――――
tab1, tab2 = st.tabs(["📊 Model", "📖 Theory"])

with tab2:
    st.markdown(c.markdown_text)

with tab1:
    # Same shape as the open-economy page, so the two read as one app
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
                            name=f"Y ({Y_cur:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(r_Y_fig, sY,
                            name=f"Y ({sY:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(r_Y_fig, c.Y_potential, name=f'Ȳ ({c.Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(r_Y_fig, height=340, column_to_plot=diagrams, key="ce_rY")

    output_gap = h.output_gap(Y_cur, c.Y_potential)

    # ―――― π–Y diagram ――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="𝜋 - inflation")
    h.add_curve_set(pi_Y_fig, 'IA', x_lo, x_hi, init_IA, st_IA, lt_IA,
                    show_initial, show_long, label=IA_label)
    h.add_curve_set(pi_Y_fig, 'AD', x_lo, x_hi, init_AD, st_AD, lt_AD, show_initial, show_long)

    if phase != "idle":
        h.add_vertical_line(pi_Y_fig, Y_cur, y_max=pi_cur,
                            name=f"Y ({Y_cur:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(pi_Y_fig, sY, y_max=sIA_pi,
                            name=f"Y ({sY:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(pi_Y_fig, c.Y_potential, name=f'Ȳ ({c.Y_potential})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(pi_Y_fig, height=360, column_to_plot=diagrams, key="ce_piY")

    # ―――― Advanced: equation display ――――――――――――――――
    if level == 'Advanced':
        # Distance from the NEW equilibrium, not the size of a price shock — a
        # demand or monetary shock moves π* without touching π₀
        shock_size = pi_0 - pi_eq
        shock_label = f"+{shock_size:.1f}" if shock_size >= 0 else f"{shock_size:.1f}"
        if show_phillips:
            pi_e = pi_e_cur   # π^e: the level the PC crosses at Ȳ
            ia_line = (f'<b style="color:#54A24B;">IA (Phillips):</b> '
                       f'𝜋 = {pi_e:.2f} + {gamma:.2f}·Ỹ &nbsp;'
                       f'<span style="color:gray;">(𝜋<sub>expected</sub> at Ȳ)</span>')
        else:
            ia_line = (f'<b style="color:#54A24B;">IA:</b> 𝜋 = {pi_0:.1f} &nbsp;'
                       f'<span style="color:gray;">({shock_label} from 𝜋*)</span>')
        text_to_show = f"""
            <b style="color:#4C78A8;">IS:</b> Y = {omega:.1f} − {phi:.2f}·r<br>
            <b style="color:#F58518;">MP:</b> r = {r_init:.2f} + {lambda_p:.2f}·Ỹ + {lambda_i:.2f}·𝜋<br>
            <b style="color:#B279A2;">AD:</b> 𝜋 = {pi_eq:.2f} {AD_slope:+.2f}·(Y − Ȳ)<br>
            {ia_line}<br>
            <hr style="margin:4px 0; border:none; border-top:1px solid #ddd;">
            <b>Output gap:</b> {output_gap:+.2f}% of potential<br>
            <b>r:</b> {r_cur:.2f}%
        """

    # ―――― Right column ――――――――――――――――
    with cols[1].container(border=True, height="stretch"):
        h.panel_header("What is happening")

        if not convergence_ok:
            st.warning("⚠️ **These settings never settle.** Output and inflation keep swinging "
                       "instead of coming to rest. Try a smaller γ.")

        st.markdown(text_to_show, unsafe_allow_html=True)
        # Where the run ends up, numbers only — the description above says it in words
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

        output_fig.update_layout(xaxis_title="", yaxis_title="Y — output (Ȳ=100)", showlegend=False)
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
        # Anchored on π^e, not the realised π, so the Phillips-curve gap is not
        # double-counted
        st.session_state.pi_prev = pi_e_cur + gamma * h.output_gap(Y_cur, c.Y_potential) + eta
        st.session_state.iter_counter += 1

        if st.session_state.iter_counter >= iteration_count:
            st.session_state.phase = "done"

        time.sleep(sim_speed)
        st.rerun()
