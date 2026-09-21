import streamlit as st
import pandas as pd
import time
import plotly.express as px

import config as c
import helpers as h

# The model itself is in helpers.py (h.oe_*). This file is only the UI: parameter
# widgets, the regime choice, the diagrams and the narration.

# ―――― Default parameters ――――――――――――――――
# r' = rᵃ − λ_I·πᵃ and ω = Ȳ + φ·rᵃ − ψ·wʳ* rest the economy at Y = 100, π = 2,
# r = 2, wʳ = 100. The resting point is solved for, not hard-coded — see "Period 0".
PHI_BASE, PSI_BASE, OMEGA_BASE = 1.0, 0.25, 77.0
RP_BASE, LP_BASE, LI_BASE, GAMMA_BASE = 1.0, 0.5, 0.5, 0.4
RA_BASE, PIA_BASE = 2.0, 2.0

# ―――― Shock sizes (Easy mode) ――――――――――――――――
# A 1.5 % of GDP demand swing, a 50 bp policy move, a 1 pp import-price shock.
FISCAL_SHOCK, MONETARY_SHOCK = 1.5, 0.5
FOREIGN_SHOCK, IMPORTED_SHOCK = 0.5, 1.0


# ―――― Session State ――――――――――――――――
h.session_init(
    oe_phase="idle",        # idle | short_term_paused | adjusting | run_paused | done
    oe_pi_prev=None,
    oe_wr_prev=None,        # real-exchange-rate state (fixed peg without sterilization)
    oe_iter_counter=0,
    oe_iteration_df=pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX", "Rate"]),
    oe_locked_df=None,
)


# Widgets the Reset button restores: deleting the key makes Streamlit rebuild the
# widget from its `value=` default.
PARAM_KEYS = (
    "oe_shock",
    "oe_m_omega", "oe_m_rinit", "oe_m_rforeign", "oe_m_infl",
    "oe_a_phi", "oe_a_psi", "oe_a_omega", "oe_a_rinit", "oe_a_lp", "oe_a_li",
    "oe_a_rforeign", "oe_a_piforeign", "oe_a_gamma", "oe_a_infl",
)



# ―――― Functions ――――――――――――――――
def reset():
    """Clear the run only, so an on_change does not undo the change itself."""
    st.session_state.oe_phase = "idle"
    st.session_state.oe_pi_prev = None
    st.session_state.oe_wr_prev = None
    st.session_state.oe_iter_counter = 0
    st.session_state.oe_iteration_df = pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX", "Rate"])


def reset_all():
    """The ↺ Reset button: clear the run and restore every parameter widget.
    Control level, regime and a saved run are kept — they have their own controls."""
    reset()
    for key in PARAM_KEYS:
        st.session_state.pop(key, None)


def lock_run():
    if not st.session_state.oe_iteration_df.empty:
        st.session_state.oe_locked_df = st.session_state.oe_iteration_df.copy()


def clear_lock():
    st.session_state.oe_locked_df = None


# Pause/resume mid-run. Callbacks, not return values: a click arriving while the
# animation sleeps is applied before the next script run, so no step is lost.
def pause_run():
    if st.session_state.oe_phase == "adjusting":
        st.session_state.oe_phase = "run_paused"


def resume_run():
    if st.session_state.oe_phase == "run_paused":
        st.session_state.oe_phase = "adjusting"



# ―――― MAIN ――――――――――――――――
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# ―――― Sidebar ――――――――――――――――
st.sidebar.header("Open Economy")
text_to_show = ''

with st.sidebar:
    phase = st.session_state.oe_phase
    is_running = phase == "adjusting"
    is_paused = phase == "short_term_paused"
    is_run_paused = phase == "run_paused"      # held mid-run by the user
    busy = is_running or is_paused or is_run_paused

    level = st.selectbox('Control Level', options=['Easy', 'Medium', 'Advanced'],
                         disabled=busy, on_change=reset, key="oe_level")

    regime = st.selectbox('Exchange-rate regime',
                          options=['Flexible', 'Fixed – no sterilization', 'Fixed – with sterilization'],
                          disabled=busy, on_change=reset, key="oe_regime",
                          help=("Flexible: the currency is free to move, which cancels out demand "
                                "changes but lets interest-rate changes work. "
                                "Fixed – no sterilization: the currency is held, so demand changes "
                                "have their full effect, monetary policy has none, and the interest "
                                "rate is left to the FX market — where it moves the wrong way and "
                                "amplifies the shock. "
                                "Fixed – with sterilization: the currency is held and the bank offsets "
                                "the money flows, so it keeps its own interest rate — for as long as "
                                "its reserves last."))

    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    # ―――― Parameter Inputs ――――――――――――――――
    # Structural defaults (overridden in Advanced)
    phi = PHI_BASE; psi = PSI_BASE; lambda_p = LP_BASE; lambda_i = LI_BASE
    gamma = GAMMA_BASE; pi_foreign = PIA_BASE; inflation_shock = 0.0
    omega = OMEGA_BASE; r_init = RP_BASE; r_foreign = RA_BASE; pi_0_override = None

    if level == 'Easy':
        st.markdown('##### Please Select the shock:')
        shock_type = st.pills('shock', label_visibility='collapsed',
                              options=['Expansionary Fiscal Shock', 'Contractionary Fiscal Shock',
                                       'Expansionary Monetary Shock', 'Contractionary Monetary Shock',
                                       'Rising Foreign Interest Rate', 'Falling Foreign Interest Rate',
                                       'Imported Inflation Shock', 'Imported Deflation Shock'],
                              disabled=busy, on_change=reset, key="oe_shock")
        if shock_type == 'Expansionary Fiscal Shock':
            omega = OMEGA_BASE + FISCAL_SHOCK
        elif shock_type == 'Contractionary Fiscal Shock':
            omega = OMEGA_BASE - FISCAL_SHOCK
        elif shock_type == 'Expansionary Monetary Shock':
            r_init = RP_BASE - MONETARY_SHOCK
        elif shock_type == 'Contractionary Monetary Shock':
            r_init = RP_BASE + MONETARY_SHOCK
        elif shock_type == 'Rising Foreign Interest Rate':
            r_foreign = RA_BASE + FOREIGN_SHOCK
        elif shock_type == 'Falling Foreign Interest Rate':
            r_foreign = RA_BASE - FOREIGN_SHOCK
        elif shock_type == 'Imported Inflation Shock':
            inflation_shock = IMPORTED_SHOCK
        elif shock_type == 'Imported Deflation Shock':
            inflation_shock = -IMPORTED_SHOCK
        text_to_show = c.oe_shock_panel(shock_type, regime)

    elif level == 'Medium':
        omega = st.slider(r'$\omega$:', on_change=reset,
                          min_value=OMEGA_BASE - 4.0, max_value=OMEGA_BASE + 4.0, step=0.25,
                          value=OMEGA_BASE, key="oe_m_omega",
                          help=r"IS: $Y = \omega - \varphi r + \psi w^r$ — demand that depends on neither $r$ "
                               r"nor $w^r$. Shifts IS sideways.")
        r_init = st.slider(r"$r'$ (%):", on_change=reset,
                           min_value=RP_BASE - 1.5, max_value=RP_BASE + 1.5, step=0.1,
                           value=RP_BASE, key="oe_m_rinit",
                           help=r"MP: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$ — the rule's intercept. "
                                r"Shifts MP up or down.")
        r_foreign = st.slider(r"$r^a$ (%) - abroad:", on_change=reset, min_value=0.0, max_value=4.0, step=0.1,
                              value=RA_BASE, key="oe_m_rforeign",
                              help=r"FX: $r = r^a$ under a float, $r = r^a + \pi^a - \pi$ under a peg without "
                                   r"sterilisation — the real interest rate abroad.")
        inflation_shock = st.slider(r"Imported inflation (%):", on_change=reset, min_value=-2.0, max_value=2.0,
                                    step=0.25, value=0.0, key="oe_m_infl",
                                    help=r"Imported inflation: a one-off jump added to $\pi_0$.")

    elif level == 'Advanced':
        st.markdown('##### IS Curve')
        phi = st.number_input(r'$\varphi$ :', on_change=reset, min_value=0.1, max_value=3.0, step=0.1,
                              value=PHI_BASE, key="oe_a_phi",
                              help=r"IS: $Y = \omega - \varphi r + \psi w^r$ — how much output falls when $r$ "
                                   r"rises by 1 pp.")
        psi = st.number_input(r'$\psi$ :', on_change=reset, min_value=0.05, max_value=1.0, step=0.05,
                              value=PSI_BASE, key="oe_a_psi",
                              help=r"IS: $Y = \omega - \varphi r + \psi w^r$ — how much output rises with a 1% "
                                   r"real depreciation.")
        omega = st.number_input(r'$\omega$ :', on_change=reset, min_value=60.0, max_value=95.0, step=0.5,
                                value=OMEGA_BASE, key="oe_a_omega",
                                help=r"IS: $Y = \omega - \varphi r + \psi w^r$ — demand that depends on "
                                     r"neither $r$ nor $w^r$. Shifts IS sideways.")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### MP Curve')
        r_init = st.number_input(r"$r'$ :", on_change=reset, step=0.1, value=RP_BASE, key="oe_a_rinit",
                                 help=r"MP: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$ — the rule's "
                                      r"intercept. Shifts MP up or down.")
        lambda_p = st.number_input(r'$\lambda_P$ :', on_change=reset, min_value=0.1, max_value=2.0, step=0.05,
                                   value=LP_BASE, key="oe_a_lp",
                                   help=r"MP: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$ — how hard the "
                                        r"bank reacts to the output gap.")
        lambda_i = st.number_input(r'$\lambda_I$ :', on_change=reset, min_value=0.1, max_value=3.0, step=0.05,
                                   value=LI_BASE, key="oe_a_li",
                                   help=r"MP: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$ — how hard the "
                                        r"bank reacts to inflation.")

        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### FX Curve')
        r_foreign = st.number_input(r"$r^a$ (%) - abroad:", on_change=reset, step=0.1, value=RA_BASE,
                                    key="oe_a_rforeign",
                                    help=r"FX: $r = r^a$ under a float, $r = r^a + \pi^a - \pi$ under a peg "
                                         r"without sterilisation — the real interest rate abroad.")
        pi_foreign = st.number_input(r"$\pi^a$ (%) - abroad:", on_change=reset, step=0.1, value=PIA_BASE,
                                     key="oe_a_piforeign", help=r"PPP: $w^r_t = \frac{1 + \pi^a}{1 + \pi_t} "
                                                                r"w^r_{t-1}$ — foreign inflation, and where a "
                                                                r"peg's inflation ends up.")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### IA Curve')
        gamma = st.number_input(r'$\gamma$ :', on_change=reset, min_value=0.0, max_value=1.5, step=0.05,
                                value=GAMMA_BASE, key="oe_a_gamma",
                                help=r"IA: $\pi_{t+1} = \pi_t + \gamma \tilde Y_t$ — how much the output gap "
                                     r"moves inflation.")
        inflation_shock = st.number_input(r"Imported Inflation (%):", on_change=reset, min_value=-3.0, max_value=3.0,
                                          step=0.25, value=0.0, key="oe_a_infl",
                                          help=r"Imported inflation: a one-off jump added to $\pi_0$.")

    # ―――― Play / Reset buttons ――――――――――――――――
    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    bcol1, bcol2 = st.columns([1.2, 0.8])
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
        reset_clicked = st.button("↺ Reset", on_click=reset_all, width="stretch", disabled=is_running,
                                  help="Clear the run and restore all shock/parameter values to their defaults.")

    # One slot, written on every rerun. Each animation pass ends in st.rerun(),
    # which aborts the script before Streamlit prunes elements the new run did not
    # re-render — so a status box from the previous phase would linger on screen.
    # Writing the slot unconditionally clears whatever the last phase put there.
    status_slot = st.empty()
    continue_clicked = False
    if is_paused:
        with status_slot.container():
            st.info("**Period 1:** short-run impact shown. Click **Continue** to see the long-run adjustment.")
            continue_clicked = st.button("▶▶ Continue", type="primary", width="stretch")
    elif is_run_paused:
        _held_at = (int(st.session_state.oe_iteration_df["Iteration"].iloc[-1])
                    if not st.session_state.oe_iteration_df.empty else 0)
        status_slot.info(f"**Paused at period {_held_at}.** **▶ Resume** carries on from here; "
                         f"**↺ Reset** stops the run for good.")
    else:
        status_slot.empty()


# ―――― Settings (user-overridable via Settings page) ――――――――――――――――
iteration_count = st.session_state.get("setting_iterations", c.iteration_count)
sim_speed       = st.session_state.get("setting_speed", c.speed)

# ―――― Derived Model Parameters ――――――――――――――――
Ybar = c.Y_potential
IS_slope = -1 / phi
MP_slope = lambda_p                          # Ỹ = Y − Ȳ is in points already

# ―――― Exchange-rate regime ――――――――――――――――
# flexible    — r = rᵃ, AD is MP∩FX, so ω drops out of AD
# no steril.  — MP is abandoned, r = rᵃ + (πᵃ − π), AD is IS∩FX
# steril.     — the bank keeps its rule, AD is IS∩MP
fixed_regime = regime in ('Fixed – no sterilization', 'Fixed – with sterilization')
peg_no_steril = (regime == 'Fixed – no sterilization')
peg_steril = (regime == 'Fixed – with sterilization')
ppp_regime = fixed_regime           # ANY nominal peg forces π → πᵃ (the peg identity)
oe_regime = h.OE_PEG if peg_no_steril else (h.OE_PEG_STER if peg_steril else h.OE_FLOAT)

# Without sterilization the MP curve is not used, so r' does nothing. Keep what the
# user picked in r_init_selected — the sidebar panel reads that, not the override.
r_init_selected = r_init
monetary_neutralised = peg_no_steril and (r_init != RP_BASE)
if peg_no_steril:
    r_init = RP_BASE

# Under sterilization the foreign rate never reaches the domestic economy.
foreign_neutralised = peg_steril and (r_foreign != RA_BASE)

P = h.OEParams(omega=omega, phi=phi, psi=psi, r_init=r_init, lambda_p=lambda_p,
               lambda_i=lambda_i, r_foreign=r_foreign, pi_foreign=pi_foreign,
               gamma=gamma, Ybar=Ybar)

pi_eq, peg_lr_rate, WR_LONGRUN = h.oe_longrun(P, oe_regime)

# ―――― Period 0: the pre-shock resting point ――――――――――――――――
# P0 is the model at DEFAULT policy (ω, r′, rᵃ) with the user's structural
# parameters, so its rest point is where the economy starts. Constants would only
# be a rest point at the default φ, ψ, λ_I and πᵃ.
P0 = h.OEParams(omega=OMEGA_BASE, phi=phi, psi=psi, r_init=RP_BASE, lambda_p=lambda_p,
                lambda_i=lambda_i, r_foreign=RA_BASE, pi_foreign=pi_foreign,
                gamma=gamma, Ybar=Ybar)
PI_BASELINE, R_BASELINE, WR_BASELINE = h.oe_longrun(P0, oe_regime)

# Sterilising, the bank ends up holding r = r' + λ_I·πᵃ. If that is not rᵃ, capital
# keeps crossing the border and reserves move without bound.
peg_unsustainable = peg_steril and abs(peg_lr_rate - r_foreign) > 1e-6

# Growth factor per period of the unsterilised peg; always > 1, so the UI can say
# the shock is amplified rather than pretend the economy comes back.
peg_divergent = peg_no_steril
peg_root = h.oe_peg_root(P) if peg_no_steril else 1.0

# Where the run ends up, numbers only — the panel above tells the story in words.
if peg_no_steril:
    longrun_line = (f"<b>Rest point:</b> output Ȳ, inflation {pi_foreign:.2f}%, real exchange rate "
                    f"{WR_LONGRUN:.2f} — but the economy is not heading there. With the Taylor rule "
                    f"gone, the FX market sets r = rᵃ + (πᵃ − 𝜋), so any gap widens by about "
                    f"{(peg_root - 1) * 100:.0f}% a period instead of closing.")
elif ppp_regime or abs(pi_eq - pi_foreign) < 0.005:
    longrun_line = (f"<b>Long run:</b> output back at Ȳ; inflation at the world rate "
                    f"{pi_foreign:.2f}%; real exchange rate settles at {WR_LONGRUN:.2f}.")
else:
    longrun_line = (f"<b>Long run:</b> output back at Ȳ; inflation settles at {pi_eq:.2f}% against "
                    f"{pi_foreign:.2f}% abroad, so the currency slides {pi_eq - pi_foreign:+.2f}% a "
                    f"period; real exchange rate settles at {WR_LONGRUN:.2f}.")

fiscal_shock = omega - OMEGA_BASE

# Period-1 inflation is predetermined, so only the one-off import-price shock moves it
pi_0 = PI_BASELINE + inflation_shock

# The two state variables carried between periods
if st.session_state.oe_pi_prev is None:
    st.session_state.oe_pi_prev = pi_0
if st.session_state.oe_wr_prev is None:
    st.session_state.oe_wr_prev = WR_BASELINE
pi_cur = st.session_state.oe_pi_prev
wr_state = st.session_state.oe_wr_prev

# While idle the diagrams draw the pre-shock point, so the readouts must match it
if phase == "idle":
    Y_cur, pi_cur, r_cur, wr_cur = Ybar, PI_BASELINE, R_BASELINE, WR_BASELINE
else:
    Y_cur, r_cur, wr_cur = h.oe_operating_point(P, oe_regime, pi_cur, wr_state)

# Period-1 impact. Evaluated at WR_BASELINE, never the live state, so the pale
# short-run curves stay frozen where the shock put them while the run advances.
Y_shock, r_shock, wr_shock = h.oe_operating_point(P, oe_regime, pi_0, WR_BASELINE)

AD_slope, AD_intercept = h.oe_ad_curve(P, oe_regime, wr_state if phase != "idle" else WR_BASELINE)
AD_slope_sr, AD_intercept_sr = h.oe_ad_curve(P, oe_regime, WR_BASELINE)

IS_intercept_cur = h.oe_is_intercept(P, wr_cur)
IS_intercept_shock = h.oe_is_intercept(P, wr_shock)
MP_intercept_cur = r_init - lambda_p * Ybar + lambda_i * pi_cur
MP_intercept_shock = r_init - lambda_p * Ybar + lambda_i * pi_0


# ―――― Medium: concise dynamic description ――――――――――――――――
if level == 'Medium':
    forces, kinds = [], []
    if omega > OMEGA_BASE + 0.05:
        forces.append("expansionary demand (↑ω)"); kinds.append('demand')
    elif omega < OMEGA_BASE - 0.05:
        forces.append("contractionary demand (↓ω)"); kinds.append('demand')
    if r_init_selected < RP_BASE - 0.05:
        forces.append("looser monetary policy (↓r')"); kinds.append('monetary')
    elif r_init_selected > RP_BASE + 0.05:
        forces.append("tighter monetary policy (↑r')"); kinds.append('monetary')
    if r_foreign > RA_BASE + 0.05:
        forces.append("higher foreign rate (↑rᵃ)"); kinds.append('foreign')
    elif r_foreign < RA_BASE - 0.05:
        forces.append("lower foreign rate (↓rᵃ)"); kinds.append('foreign')
    if inflation_shock > 0:
        forces.append("imported inflation (one-off)"); kinds.append('imported')
    elif inflation_shock < 0:
        forces.append("imported deflation (one-off)"); kinds.append('imported')

    if not forces:
        text_to_show = c.empty_placeholder_moderate_level_shock
    else:
        # One line per kind of setting changed. Kinds a pop-up already covers have
        # no entry, so nothing is said twice.
        regime_key = c.REGIME_KEY[regime]
        notes = [c.OE_MEDIUM_NOTE[(k, regime_key)] for k in kinds
                 if (k, regime_key) in c.OE_MEDIUM_NOTE]
        text_to_show = c.oe_panel("Your settings", regime,
                                  f"<b>{' + '.join(forces)}</b><br><br>" + "<br>".join(notes), "🎛️")

# ―――― Continue: advance from short_term_paused to adjusting ――――――――――――――――
if continue_clicked and phase == "short_term_paused":
    _pi_next = h.oe_next_inflation(P, pi_0, Y_shock)
    _Y_next, _, _ = h.oe_operating_point(P, oe_regime, _pi_next, wr_shock)
    st.session_state.oe_pi_prev = _pi_next
    st.session_state.oe_wr_prev = h.oe_wr_next(P, oe_regime, wr_shock, _pi_next, _Y_next)
    st.session_state.oe_phase = "adjusting"
    st.rerun()

# ―――― Play: initialize period 0 and period 1 ――――――――――――――――
# Also fires from "done" so Play restarts a finished run. A run saved with
# "Remember this run" is kept, so the replay is drawn against it.
if play_clicked and phase in ("idle", "done"):
    st.session_state.oe_phase = "short_term_paused"
    st.session_state.oe_pi_prev = pi_0
    st.session_state.oe_wr_prev = WR_BASELINE
    st.session_state.oe_iter_counter = 2
    df = pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX", "Rate"])
    df.loc[0] = [0, Ybar, PI_BASELINE, WR_BASELINE, R_BASELINE]   # period 0: pre-shock equilibrium
    df.loc[1] = [1, Y_shock, pi_0, wr_shock, r_shock]             # period 1: short-run jump
    st.session_state.oe_iteration_df = df
    st.rerun()

phase = st.session_state.oe_phase  # re-read after possible update

# ―――― Plot bounds ――――――――――――――――
# Sized from the largest gap so far, so a widening run stays on the chart.
MIN_HALF_WINDOW = 2.0
const = max(MIN_HALF_WINDOW,
            1.6 * max(abs(Y_shock - Ybar), abs(Y_cur - Ybar)))
x_lo, x_hi = Ybar - const, Ybar + const

# ―――― Curve positions in each phase ――――――――――――――――
# initial = period 0, short = the period-1 impact, long = where the curve is now.
show_initial = phase == "short_term_paused"
show_long = phase in ("adjusting", "run_paused", "done")

init_IS = (-1 / phi, (OMEGA_BASE + psi * WR_BASELINE) / phi)
init_MP = (MP_slope, RP_BASE - lambda_p * Ybar + lambda_i * PI_BASELINE)
init_FX = (0.0, h.oe_fx_rate(P0, oe_regime, PI_BASELINE))
init_AD = h.oe_ad_curve(P0, oe_regime, WR_BASELINE)
init_IA = (0.0, PI_BASELINE)

st_IS, st_MP = (IS_slope, IS_intercept_shock), (MP_slope, MP_intercept_shock)
st_AD, st_IA = (AD_slope_sr, AD_intercept_sr), (0.0, pi_0)
lt_IS, lt_MP = (IS_slope, IS_intercept_cur), (MP_slope, MP_intercept_cur)
lt_AD, lt_IA = (AD_slope, AD_intercept), (0.0, pi_cur)

# FX is the parity constraint, not the operating point: fixed at rᵃ under a float,
# moving with inflation under the unsterilised peg. Computed either way; only drawn
# where the regime leaves it binding (see the r–Y diagram).
st_FX = (0.0, h.oe_fx_rate(P, oe_regime, pi_0))
lt_FX = (0.0, h.oe_fx_rate(P, oe_regime, pi_cur))

sY, sIA = (Ybar, PI_BASELINE) if phase == "idle" else (Y_cur, pi_cur)
sFX = R_BASELINE if phase == "idle" else r_foreign

# ―――― Tabs ――――――――――――――――
# Settings gets its own row; wrapping the tabs in a column would confine every
# diagram inside them to that column's width.
tab1, tab2 = st.tabs(["📊 Model", "📖 Theory"])

with tab2:
    # st.image, not st.markdown/st.html: those sanitize the SVG away silently
    st.markdown(c.THEORY_INTRO)
    st.image(c.TRINITY_SVG, width="stretch")
    st.markdown(c.THEORY_REST)

with tab1:
    cols = st.columns([0.8, 1], gap="small", vertical_alignment="top") # [1.4, 0.9, 0.7],
    diagrams = cols[0].container(border=True, height="stretch")
    h.panel_header("Diagrams", diagrams)

    # No x-title here: this chart shares its axis with the one below
    r_Y_fig = h.create_linear_plot(x_label="", y_label="r - interest rate")
    h.add_curve_set(r_Y_fig, 'IS', x_lo, x_hi, init_IS, st_IS, lt_IS, show_initial, show_long)
    h.add_curve_set(r_Y_fig, 'MP', x_lo, x_hi, init_MP, st_MP, lt_MP, show_initial, show_long)
    # Sterilising, the bank breaks the arbitrage instead of satisfying it: the free
    # variable is the stock of reserves, which is not in the diagram, so FX imposes
    # nothing on r and is absorbed out of the system — no line to draw.
    # Labelled plainly, like every other curve. The rule behind the line — r = rᵃ
    # under a float, r = rᵃ + (𝜋ᵃ − 𝜋) under the unsterilised peg, which is why it
    # moves with inflation — is spelled out in the Advanced panel and the
    # divergence warning, so the label does not have to carry the equation.
    if not peg_steril:
        h.add_curve_set(r_Y_fig, 'FX', x_lo, x_hi, init_FX, st_FX, lt_FX, show_initial, show_long,
                        label_position='left')

    if phase != "idle":
        h.add_vertical_line(r_Y_fig, Y_cur, y_max=r_cur, name=f"Y ({Y_cur:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(r_Y_fig, sY, y_max=sFX, name=f"Y ({sY:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(r_Y_fig, Ybar, name=f'Ȳ ({Ybar})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(r_Y_fig, height=340, column_to_plot=diagrams, key="oe_rY")

    output_gap = h.output_gap(Y_cur, Ybar)

    # ―――― π–Y diagram ――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="𝜋 - inflation")
    h.add_curve_set(pi_Y_fig, 'IA', x_lo, x_hi, init_IA, st_IA, lt_IA, show_initial, show_long)

    # PPP: horizontal at πᵃ. Labelled left so it misses the IA label on the right.
    h.add_line_to_plot(pi_Y_fig, 0, pi_foreign, x_lo, x_hi, dash='dash', name=f"PPP ({pi_foreign:.1f})", color="#999999", line_width=c.thin_line_width, label_position='left', label_offset=9)

    # AD last, so its label is placed against the curves already on the figure
    h.add_curve_set(pi_Y_fig, 'AD', x_lo, x_hi, init_AD, st_AD, lt_AD, show_initial, show_long)

    if phase != "idle":
        h.add_vertical_line(pi_Y_fig, Y_cur, y_max=pi_cur, name=f"Y ({Y_cur:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(pi_Y_fig, sY, y_max=sIA, name=f"Y ({sY:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(pi_Y_fig, Ybar, name=f'Ȳ ({Ybar})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(pi_Y_fig, height=360, column_to_plot=diagrams, key="oe_piY")

    # ―――― Advanced: equation display ――――――――――――――――
    if level == 'Advanced':
        # π* is left out: the long-run line under this panel already reports it
        _ad_slope, _ad_int = (init_AD if phase == "idle" else
                              (st_AD if show_initial else lt_AD))
        # IA is flat, so only its level is worth printing — but take it from the
        # same phase the green line is drawn at, or mid-run the panel keeps
        # reporting the period-1 number
        _ia_level = (init_IA if phase == "idle" else
                     (st_IA if show_initial else lt_IA))[1]
        # Written around Ȳ — the raw intercept is a meaningless three-digit number
        _ad_at_Ybar = _ad_slope * Ybar + _ad_int
        _ad_line = f"𝜋 = {_ad_at_Ybar:.2f} {_ad_slope:+.2f}·(Y − Ȳ)"
        _fx_level = h.oe_fx_rate(P, oe_regime, pi_cur)
        if peg_steril:
            # Absorbed by the reserve flow, so it constrains nothing and is not drawn
            _fx_line = ('<b style="color:#E45756;">FX:</b> absorbed by reserves '
                        '— no constraint on r')
        elif peg_no_steril:
            _fx_line = (f'<b style="color:#E45756;">FX:</b> r = rᵃ + (πᵃ − 𝜋) = {_fx_level:.2f}')
        else:
            _fx_line = f'<b style="color:#E45756;">FX:</b> r = rᵃ = {r_foreign:.2f}'
        text_to_show = c.oe_panel("Current model", regime, f"""
            <b style="color:#4C78A8;">IS:</b> Y = {omega:.1f} − {phi:.2f}·r + {psi:.2f}·wʳ<br>
            <b style="color:#F58518;">MP:</b> r = {r_init:.2f} + {lambda_p:.2f}·Ỹ + {lambda_i:.2f}·𝜋<br>
            {_fx_line}<br>
            <b style="color:#B279A2;">AD:</b> {_ad_line}<br>
            <b style="color:#54A24B;">IA:</b> 𝜋 = {_ia_level:.2f}<br>
            <hr style="margin:4px 0; border:none; border-top:1px solid #ddd;">
            <b>Output gap:</b> {output_gap:+.2f}% of potential<br>
            <b>Real exchange rate wʳ:</b> {wr_cur:.1f}
        """, "⚙️")

    df_now = st.session_state.oe_iteration_df
    df_lock = st.session_state.oe_locked_df

    # ―――― Right column, upper panel ――――――――――――――――
    with cols[1].container(border=True, height="stretch"):
        # Header first: called after st.columns() it lands under the charts
        cols_header = st.columns(2)
        with cols_header[0]:
            h.panel_header("Over time")

        with cols_header[1]:
            h.settings_popover(key_prefix="oe_")


        cols_graphs = st.columns(2)

        def _series_chart(y_col, y_title, label, ref_value, ref_label, show_x=False):
            fig = px.scatter(df_now, x="Iteration", y=y_col)
            fig.update_traces(mode="lines")
            if df_lock is not None:
                fig.add_scatter(x=df_lock["Iteration"], y=df_lock[y_col], mode="lines",
                                line=dict(color="#BBBBBB", dash="dot"), name="Previous run")
            if not df_now.empty:
                last = df_now.iloc[-1]
                fig.add_annotation(x=last["Iteration"], y=last[y_col],
                                   text=f"{label}={last[y_col]:.2f}", showarrow=False,
                                   xanchor="left", yshift=12)
            # Only the bottom row carries the "Period" title; the charts share an x-axis
            fig.update_layout(xaxis_title="Period" if show_x else "", yaxis_title=y_title,
                              showlegend=False)
            h.add_line_to_plot(fig, 0, ref_value, 0, iteration_count,
                               name=f"{ref_label} ({ref_value:.2f})", line_width=2, color="#999999", dash='dot')
            h.show_plotly_fig(fig, height=185 if show_x else 165, key=f"oe_ts_{y_col}")

        with cols_graphs[0]:
            _series_chart("Output",    "Y — output (Ȳ=100)", "Y",  Ybar,        "Ȳ")
            _series_chart("Inflation", "𝜋 - inflation",        "𝜋",  pi_eq,       "𝜋*", show_x=True)

        with cols_graphs[1]:
            # Long-run wʳ, not the pre-shock one — most shocks move it permanently
            _series_chart("RealFX",    "wʳ — real exch. rate", "wʳ", WR_LONGRUN,  "wʳ*")
            _series_chart("Rate",      "r - interest rate",    "r", peg_lr_rate, "r*", show_x=True)

    # ―――― Right column, lower panel ――――――――――――――――
    with cols[1].container(border=True, height="stretch"):
        h.panel_header("What is happening")
        # Pop-ups: only what the description panel below does not already say
        if peg_unsustainable:
            st.warning(f"⚠️ **This peg needs capital controls.** The bank holds r = {peg_lr_rate:.2f} "
                       f"while the world pays rᵃ = {r_foreign:.2f}. Capital keeps crossing the border "
                       f"on that gap and the bank absorbs it in reserves, which drain (or pile up) "
                       f"without limit — that reserve flow is the free variable, which is why no FX "
                       f"line is drawn here. Sterilisation is the corner of the trinity that gives up "
                       f"**free movement of capital**. Without controls the bank must eventually "
                       f"release the interest rate (→ **Fixed – no sterilization**) or the currency "
                       f"(→ **Flexible**).")

        if peg_divergent and phase != "idle":
            st.warning(f"⚠️ **This shock feeds on itself.** With the nominal rate pegged (i = iᵃ) the "
                       f"Taylor rule is gone and the FX market sets r = rᵃ + (πᵃ − 𝜋). A slump pulls "
                       f"inflation below the world rate, so the real rate **rises** and the slump "
                       f"deepens — a boom does the reverse. Hence the upward-sloping AD, and a gap "
                       f"that grows about {(peg_root - 1) * 100:.0f}% a period. Competitiveness pulls "
                       f"the other way, but only through the slow drift of prices, and never catches "
                       f"up. This is the mechanism behind the Eurozone's divergence.")


        if level != 'Easy':
            if monetary_neutralised:
                st.info(c.monetary_neutralised_text)
            if foreign_neutralised:
                st.info(c.foreign_neutralised_text)

        st.markdown(text_to_show, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:12px; color:gray; margin-top:8px;'>{longrun_line}</div>",
                    unsafe_allow_html=True)

        # Spacer that pins the buttons to the bottom edge. Needs a child, or
        # Streamlit renders nothing at all.
        st.container(height="stretch", border=False).html("<div></div>")

        lc1, lc2 = st.columns([1.2, 0.8])
        with lc1:
            st.button("🔖 Remember this run", on_click=lock_run, width="stretch",
                      help="Save this run in gray so you can compare it with the next one",
                      disabled=phase != "done")
        with lc2:
            if st.session_state.oe_locked_df is not None:
                st.button("✕ Forget", on_click=clear_lock, width="stretch")

    # ―――― Animation step ――――――――――――――――
    if phase == "adjusting":
        new_row_idx = len(st.session_state.oe_iteration_df)
        st.session_state.oe_iteration_df.loc[new_row_idx] = [
            st.session_state.oe_iter_counter, Y_cur, pi_cur, wr_cur, r_cur
        ]
        _pi_next = h.oe_next_inflation(P, pi_cur, Y_cur)
        _Y_next, _, _ = h.oe_operating_point(P, oe_regime, _pi_next, wr_cur)
        _wr_next = h.oe_wr_next(P, oe_regime, wr_cur, _pi_next, _Y_next)
        st.session_state.oe_pi_prev = _pi_next
        st.session_state.oe_wr_prev = _wr_next
        st.session_state.oe_iter_counter += 1

        # The unsterilised peg amplifies without limit and is left to do so: the run
        # ends on the iteration count like every other regime, however large the
        # numbers get.
        if st.session_state.oe_iter_counter >= iteration_count:
            st.session_state.oe_phase = "done"

        time.sleep(sim_speed)
        st.rerun()
