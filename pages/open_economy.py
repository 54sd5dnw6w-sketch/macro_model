import streamlit as st
import pandas as pd
import time
import plotly.express as px

import config as c
import helpers as h

# ―――― Open-economy model ――――――――――――――――
# The MODEL lives in helpers.py (h.oe_*): five equations — IS, MP, FX, IA and PPP
# — with no damping coefficients and nothing calibrated. This file holds only the
# UI: the parameter widgets, the regime choice, the diagrams and the narration.
#
# The peg mechanism is the exact law wʳ = wʳ₋₁·(1+πᵃ)/(1+π): with the nominal rate
# held fixed, the real rate keeps moving for as long as domestic inflation differs
# from foreign inflation. One law, no free parameters.
#
# ―――― χ: imported inflation ――――――――――――――――
# χ is the pass-through of a change in the real exchange rate to domestic prices
# (large for a CPI basket, small for the GDP deflator). It is an EXTENSION: every
# headline result — full crowding out under a float above all — holds with χ = 0,
# which is why χ defaults to 0 here and is offered only at the Advanced level.

# ―――― Fixed pre-shock baseline (period 0 of the charts) ――――――――――――――――
# Default parameters below give the resting point Y=Ȳ, π=πᵃ=3, r=rᵃ=2, wʳ=1.
PHI_BASE, PSI_BASE, OMEGA_BASE = 1.0, 1.0, 2.0
RP_BASE, LP_BASE, LI_BASE, GAMMA_BASE = 0.5, 0.5, 0.5, 0.5
RA_BASE, PIA_BASE = 2.0, 3.0
WR_BASELINE = (c.Y_potential - OMEGA_BASE + PHI_BASE * RA_BASE) / PSI_BASE   # → 1.0


# ―――― Session State ――――――――――――――――
h.session_init(
    oe_phase="idle",        # idle | short_term_paused | adjusting | done
    oe_pi_prev=None,
    oe_wr_prev=None,        # real-exchange-rate state (fixed peg without sterilization)
    oe_iter_counter=0,
    oe_iteration_df=pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX", "Rate"]),
    oe_locked_df=None,
)


# Every parameter widget that the Reset button must restore. Deleting the key makes
# Streamlit rebuild the widget from its `value=` default on the next run.
PARAM_KEYS = (
    "oe_shock",
    "oe_m_omega", "oe_m_rinit", "oe_m_rforeign", "oe_m_infl",
    "oe_a_phi", "oe_a_psi", "oe_a_omega", "oe_a_rinit", "oe_a_lp", "oe_a_li",
    "oe_a_rforeign", "oe_a_piforeign", "oe_a_gamma", "oe_a_infl", "oe_a_eta",
    "oe_a_chi",
)



# ―――― Functions ――――――――――――――――
def reset():
    """Clear the simulation only — used by on_change so changing a parameter
    discards a stale run without undoing the change the user just made."""
    st.session_state.oe_phase = "idle"
    st.session_state.oe_pi_prev = None
    st.session_state.oe_wr_prev = None
    st.session_state.oe_iter_counter = 0
    st.session_state.oe_iteration_df = pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX", "Rate"])


def reset_all():
    """The ↺ Reset button: clear the simulation AND restore every shock/parameter
    widget to its default, so the sidebar and the diagrams agree again.
    Control level and exchange-rate regime are framing choices and are kept, as is
    a run saved with 'Remember this run' (it has its own ✕ Forget button)."""
    reset()
    for key in PARAM_KEYS:
        st.session_state.pop(key, None)


def lock_run():
    if not st.session_state.oe_iteration_df.empty:
        st.session_state.oe_locked_df = st.session_state.oe_iteration_df.copy()


def clear_lock():
    st.session_state.oe_locked_df = None



# ―――― MAIN ――――――――――――――――
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# ―――― Sidebar ――――――――――――――――
st.sidebar.header("Open Economy")
text_to_show = ''

with st.sidebar:
    phase = st.session_state.oe_phase
    is_running = phase == "adjusting"
    is_paused = phase == "short_term_paused"

    level = st.selectbox('Control Level', options=['Easy', 'Medium', 'Advanced'],
                         disabled=is_running or is_paused, on_change=reset, key="oe_level")

    regime = st.selectbox('Exchange-rate regime',
                          options=['Flexible', 'Fixed – no sterilization', 'Fixed – with sterilization'],
                          disabled=is_running or is_paused, on_change=reset, key="oe_regime",
                          help=("Flexible: the currency is free to move, which cancels out demand "
                                "changes but lets interest-rate changes work. "
                                "Fixed – no sterilization: the currency is held, so demand changes "
                                "have their full effect and monetary policy has none. "
                                "Fixed – with sterilization: the currency is held and the bank offsets "
                                "the money flows, so it keeps its own interest rate — for as long as "
                                "its reserves last."))

    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    # ―――― Parameter Inputs ――――――――――――――――
    # Structural defaults (overridden in Advanced)
    phi = PHI_BASE; psi = PSI_BASE; lambda_p = LP_BASE; lambda_i = LI_BASE
    gamma = GAMMA_BASE; pi_foreign = PIA_BASE; eta = 0.0; inflation_shock = 0.0
    omega = OMEGA_BASE; r_init = RP_BASE; r_foreign = RA_BASE; pi_0_override = None
    chi = 0.0                      # imported-inflation pass-through — Advanced only

    if level == 'Easy':
        st.markdown('##### Please Select the shock:')
        shock_type = st.pills('shock', label_visibility='collapsed',
                              options=['Expansionary Fiscal Shock', 'Contractionary Fiscal Shock',
                                       'Expansionary Monetary Shock', 'Contractionary Monetary Shock',
                                       'Rising Foreign Interest Rate', 'Falling Foreign Interest Rate',
                                       'Imported Inflation Shock', 'Imported Deflation Shock'],
                              disabled=is_running or is_paused, on_change=reset, key="oe_shock")
        if shock_type == 'Expansionary Fiscal Shock':
            omega = OMEGA_BASE + 0.5
        elif shock_type == 'Contractionary Fiscal Shock':
            omega = OMEGA_BASE - 0.5
        elif shock_type == 'Expansionary Monetary Shock':
            r_init = RP_BASE - 0.3
        elif shock_type == 'Contractionary Monetary Shock':
            r_init = RP_BASE + 0.3
        elif shock_type == 'Rising Foreign Interest Rate':
            r_foreign = RA_BASE + 0.3
        elif shock_type == 'Falling Foreign Interest Rate':
            r_foreign = RA_BASE - 0.3
        elif shock_type == 'Imported Inflation Shock':
            inflation_shock = 0.5
        elif shock_type == 'Imported Deflation Shock':
            inflation_shock = -0.5
        # One story, for the regime actually selected — the pop-ups below never repeat it.
        text_to_show = c.oe_shock_panel(shock_type, regime)

    elif level == 'Medium':
        omega = st.slider(r'$\omega$:', on_change=reset, min_value=0.5, max_value=4.0, step=0.1,
                          value=OMEGA_BASE, key="oe_m_omega",
                          help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$")
        r_init = st.slider(r"$r'$ (%):", on_change=reset, min_value=-0.5, max_value=1.5, step=0.1,
                           value=RP_BASE, key="oe_m_rinit",
                           help=r"MP Curve: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$")
        r_foreign = st.slider(r"$r^a$ (%) - abroad:", on_change=reset, min_value=1.0, max_value=3.0, step=0.1,
                              value=RA_BASE, key="oe_m_rforeign",
                              help=r"FX Curve: $r = r^a$ under a flexible exchange rate")
        inflation_shock = st.slider(r"Imported inflation (%):", on_change=reset, min_value=-2.0, max_value=2.0,
                                    step=0.25, value=0.0, key="oe_m_infl",
                                    help="A one-off jump in import prices, which lands directly on inflation. "
                                         "Positive = prices from abroad rise, negative = they fall.")

    elif level == 'Advanced':
        st.markdown('##### IS Curve')
        phi = st.number_input(r'$\varphi$ :', on_change=reset, min_value=0.1, step=0.1, value=PHI_BASE,
                              key="oe_a_phi", help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$")
        psi = st.number_input(r'$\psi$ :', on_change=reset, min_value=0.1, step=0.1, value=PSI_BASE,
                              key="oe_a_psi", help=r"Real-exchange-rate sensitivity of demand")
        omega = st.number_input(r'$\omega$ :', on_change=reset, min_value=0.0, step=0.5, value=OMEGA_BASE,
                                key="oe_a_omega", help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### MP Curve')
        r_init = st.number_input(r"$r'$ :", on_change=reset, step=0.1, value=RP_BASE, key="oe_a_rinit",
                                 help=r"MP Curve: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$")
        lambda_p = st.number_input(r'$\lambda_P$ :', on_change=reset, min_value=0.1, max_value=10.0, step=0.1,
                                   value=LP_BASE, key="oe_a_lp", help=r"MP Curve output-gap weight")
        lambda_i = st.number_input(r'$\lambda_I$ :', on_change=reset, min_value=0.1, max_value=10.0, step=0.1,
                                   value=LI_BASE, key="oe_a_li", help=r"MP Curve inflation weight")

        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### FX Curve')
        r_foreign = st.number_input(r"$r^a$ (%) - abroad:", on_change=reset, step=0.1, value=RA_BASE,
                                    key="oe_a_rforeign", help=r"FX Curve: $r = r^a$")
        pi_foreign = st.number_input(r"$\pi^a$ (%) - abroad:", on_change=reset, step=0.1, value=PIA_BASE,
                                     key="oe_a_piforeign", help=r"Long-run domestic inflation anchor")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### IA Curve')
        gamma = st.number_input(r'$\gamma$ :', on_change=reset, min_value=0.0, step=0.1, value=GAMMA_BASE,
                                key="oe_a_gamma", help=r"IA curve: $\pi_{t+1} = \pi_t + \gamma \tilde Y_t + \eta$")
        inflation_shock = st.number_input(r"Imported Inflation (%):", on_change=reset, min_value=-3.0, max_value=3.0,
                                          step=0.25, value=0.0, key="oe_a_infl",
                                          help="A one-off jump in import prices. It lands on inflation once "
                                               "and is carried forward from there.")
        chi = st.number_input(r'$\chi$ (imported inflation):', on_change=reset, min_value=0.0, max_value=2.0,
                              step=0.1, value=0.0, key="oe_a_chi",
                              help=r"How much a move in the exchange rate feeds into domestic prices: a weaker "
                                   r"currency makes imports dearer straight away. Large if the price index "
                                   r"contains a lot of imported goods, small if it does not. Leave it at 0 for "
                                   r"the standard results.")
        eta = st.number_input(r'$\eta$ (exogenous shock):', on_change=reset, step=0.1, value=0.0,
                              key="oe_a_eta", help=r"Persistent exogenous price shock each period.")

    # ―――― Play / Reset buttons ――――――――――――――――
    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    bcol1, bcol2 = st.columns([1.2, 0.8])
    with bcol1:
        if is_running:
            play_clicked = False
            st.button("⏸ Running…", disabled=True, width="stretch")
        elif is_paused:
            play_clicked = False
            st.button("▶▶ Paused", disabled=True, width="stretch")
        else:
            play_clicked = st.button("⏵ Play", type="primary", width="stretch")
    with bcol2:
        reset_clicked = st.button("↺ Reset", on_click=reset_all, width="stretch", disabled=is_running,
                                  help="Clear the run and restore all shock/parameter values to their defaults.")

    continue_clicked = False
    if is_paused:
        st.info("**Period 1:** short-run impact shown. Click **Continue** to see the long-run adjustment.")
        continue_clicked = st.button("▶▶ Continue", type="primary", width="stretch")


# ―――― Settings (user-overridable via Settings page) ――――――――――――――――
iteration_count = st.session_state.get("setting_iterations", c.iteration_count)
sim_speed       = st.session_state.get("setting_speed", c.speed)

# ―――― Derived Model Parameters ――――――――――――――――
Ybar = c.Y_potential
IS_slope = -1 / phi
MP_slope = lambda_p / Ybar

# ―――― Exchange-rate regime ――――――――――――――――
# Each regime abandons ONE corner of the impossible trinity, and that choice is
# what drives every difference below.
#
# FLEXIBLE — gives up CONTROL OF THE EXCHANGE RATE. The nominal rate floats, so
#   interest parity binds: r = rᵃ. Output comes from MP∩FX, so ω drops out of AD
#   entirely and FISCAL POLICY IS FULLY CROWDED OUT. Monetary and foreign-rate
#   shocks are permanent → π* = (rᵃ − r')/λ_I, generally ≠ πᵃ, which means the
#   currency slides at that differential forever.
#
# FIXED – NO STERILIZATION — gives up MONETARY AUTONOMY. Reserve flows are left to
#   run, so they drag r to rᵃ and the Taylor rule is abandoned. Fiscal policy has
#   its full IS multiplier — the strongest of the three. But nothing responds to
#   inflation within the period: r cannot move and wʳ is a carried-over state, so
#   AD IS VERTICAL. The entire adjustment must come from accumulated price
#   differences, which is why this regime is slow and why a run overshoots rather
#   than settling.
#
# FIXED – WITH STERILIZATION — gives up FREE MOVEMENT OF CAPITAL. The bank offsets
#   the reserve flows and so keeps its own rate: r = r' + λ_P·Ỹ + λ_I·π. Output
#   comes from IS∩MP at the pegged wʳ, giving a STEEPER AD than the float. Fiscal
#   policy works and the economy is insulated from rᵃ. The catch is that holding r
#   away from rᵃ means capital keeps crossing the border, so this corner has to be
#   held shut with capital controls in the long run — it is NOT a way to have all
#   three at once.
#
# Under EITHER peg the nominal rate is fixed, so wʳ = w·pᵃ/p keeps drifting until
# π = πᵃ: a pegged economy cannot hold an inflation rate of its own.
fixed_regime = regime in ('Fixed – no sterilization', 'Fixed – with sterilization')
peg_no_steril = (regime == 'Fixed – no sterilization')
peg_steril = (regime == 'Fixed – with sterilization')
ppp_regime = fixed_regime           # ANY nominal peg forces π → πᵃ (the peg identity)
oe_regime = h.OE_PEG if peg_no_steril else (h.OE_PEG_STER if peg_steril else h.OE_FLOAT)

# Fixed without sterilization: reserve flows peg r to rᵃ, so domestic monetary
# policy (r') has no effect — neutralise any monetary shock.
# r_init_selected keeps what the USER chose: the Medium panel lists the settings as
# made, and the pop-up is what adds "…but it does nothing here". Reading the
# overwritten r_init there made the panel claim nothing had been changed at all.
r_init_selected = r_init
monetary_neutralised = peg_no_steril and (r_init != RP_BASE)
if peg_no_steril:
    r_init = RP_BASE

# Under sterilization the foreign rate never reaches the domestic economy.
foreign_neutralised = peg_steril and (r_foreign != RA_BASE)

# ―――― The model ――――――――――――――――
# Every equation is in helpers.oe_* — this page only supplies the parameters.
P = h.OEParams(omega=omega, phi=phi, psi=psi, r_init=r_init, lambda_p=lambda_p,
               lambda_i=lambda_i, r_foreign=r_foreign, pi_foreign=pi_foreign,
               gamma=gamma, chi=chi, Ybar=Ybar)

pi_eq, peg_lr_rate, WR_LONGRUN = h.oe_longrun(P, oe_regime)
PI_BASELINE = pi_foreign

# ―――― Is the peg actually defensible? ――――――――――――――――
# Under sterilisation the bank holds r = r' + λ_I·πᵃ in the long run. Whenever that
# differs from rᵃ, capital keeps flowing and reserves move without bound — which is
# precisely why capital controls sit at this corner of the trinity.
peg_unsustainable = peg_steril and abs(peg_lr_rate - r_foreign) > 1e-6

# The hard peg has no stabiliser at all: r is pinned to rᵃ and AD is vertical, so
# the output gap only ever feeds back through the slow drift of wʳ. Flagged so the
# UI can say the run overshoots instead of pretending it settles.
peg_undamped = peg_no_steril

# Where the run ends up — NUMBERS ONLY. The panel above it tells the story in
# words, so this line must not repeat the mechanism, only state the destination.
if ppp_regime or abs(pi_eq - pi_foreign) < 0.005:
    longrun_line = (f"<b>Long run:</b> output back at Ȳ; inflation at the world rate "
                    f"{pi_foreign:.2f}%; real exchange rate settles at {WR_LONGRUN:.2f}.")
else:
    longrun_line = (f"<b>Long run:</b> output back at Ȳ; inflation settles at {pi_eq:.2f}% against "
                    f"{pi_foreign:.2f}% abroad, so the currency slides {pi_eq - pi_foreign:+.2f}% a "
                    f"period; real exchange rate settles at {WR_LONGRUN:.2f}.")

# Fiscal policy enters through ω, and each regime's own AD decides what it does:
# absent from the float's AD → crowded out; present in both pegs → effective.
fiscal_shock = omega - OMEGA_BASE

# Period-1 inflation: predetermined at πᵃ and moved only by the one-off imported
# price shock. Inflation cannot jump with the shock — that is the point of the IA
# curve — so nothing else touches it.
pi_0 = pi_foreign + inflation_shock

# The animation's two state variables. Inflation is a state in every regime; the
# real exchange rate is only a state under a peg.
if st.session_state.oe_pi_prev is None:
    st.session_state.oe_pi_prev = pi_0
if st.session_state.oe_wr_prev is None:
    st.session_state.oe_wr_prev = WR_BASELINE
pi_cur = st.session_state.oe_pi_prev
wr_state = st.session_state.oe_wr_prev

# Current (animated) operating point. While IDLE the diagrams draw the pre-shock
# resting equilibrium, so the readouts must report that same point — otherwise the
# panel shows shocked numbers next to unshocked curves.
if phase == "idle":
    Y_cur, pi_cur, r_cur, wr_cur = Ybar, PIA_BASE, RA_BASE, WR_BASELINE
else:
    Y_cur, r_cur, wr_cur = h.oe_operating_point(P, oe_regime, pi_cur, wr_state)

# Shocked (period-1) operating point — the short-run impact jump. Evaluated at the
# PERIOD-1 state (WR_BASELINE), never the live one, so the pale short-run curves
# stay frozen where the shock actually put them while the run advances.
Y_shock, r_shock, wr_shock = h.oe_operating_point(P, oe_regime, pi_0, WR_BASELINE)

# AD in π–Y space. A slope of None means the curve is VERTICAL (hard peg), in
# which case the second element is the output level instead of an intercept.
AD_slope, AD_intercept = h.oe_ad_curve(P, oe_regime, wr_state if phase != "idle" else WR_BASELINE)
AD_slope_sr, AD_intercept_sr = h.oe_ad_curve(P, oe_regime, WR_BASELINE)

IS_intercept_cur = h.oe_is_intercept(P, wr_cur)
IS_intercept_shock = h.oe_is_intercept(P, wr_shock)
MP_intercept_cur = r_init - lambda_p + lambda_i * pi_cur
MP_intercept_shock = r_init - lambda_p + lambda_i * pi_0
MP_intercept_cur = r_init - lambda_p + lambda_i * pi_cur


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
        # One line per kind of setting changed, for this regime. Kinds the pop-ups
        # already handle have no entry, so nothing appears twice; where the run ends
        # is left to the long-run line.
        regime_key = c.REGIME_KEY[regime]
        notes = [c.OE_MEDIUM_NOTE[(k, regime_key)] for k in kinds
                 if (k, regime_key) in c.OE_MEDIUM_NOTE]
        text_to_show = c.oe_panel("Your settings", regime,
                                  f"<b>{' + '.join(forces)}</b><br><br>" + "<br>".join(notes), "🎛️")

# ―――― Continue: advance from short_term_paused to adjusting ――――――――――――――――
if continue_clicked and phase == "short_term_paused":
    # IA carries inflation forward; under a peg the real exchange rate then follows
    # from exact PPP at that new inflation rate.
    _pi_next = h.oe_next_inflation(P, oe_regime, pi_0, Y_shock, wr_shock)
    _Y_next, _, _ = h.oe_operating_point(P, oe_regime, _pi_next, wr_shock)
    st.session_state.oe_pi_prev = _pi_next
    st.session_state.oe_wr_prev = h.oe_wr_next(P, oe_regime, wr_shock, _pi_next, _Y_next)
    st.session_state.oe_phase = "adjusting"
    st.rerun()

# ―――― Play: initialize period 0 and period 1 ――――――――――――――――
if play_clicked and phase == "idle":
    st.session_state.oe_phase = "short_term_paused"
    st.session_state.oe_pi_prev = pi_0
    st.session_state.oe_wr_prev = WR_BASELINE
    st.session_state.oe_iter_counter = 2
    df = pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX", "Rate"])
    df.loc[0] = [0, Ybar, PI_BASELINE, WR_BASELINE, RA_BASE]      # period 0: pre-shock equilibrium
    df.loc[1] = [1, Y_shock, pi_0, wr_shock, r_shock]             # period 1: short-run jump
    st.session_state.oe_iteration_df = df
    st.rerun()

phase = st.session_state.oe_phase  # re-read after possible update

# ―――― Plot bounds ――――――――――――――――
const = max(abs(Y_shock), abs(Ybar), abs(Ybar - Y_shock)) * 1.3
const = max(const, 0.5)
x_lo, x_hi = Ybar - const, Ybar + const

# ―――― Curve styling: idle = bold single curves, otherwise ST/LT split ――――――――――――――――
if phase == "idle":
    STMP_color, STMP_name, STMP_lw = "#F58518", "MP", c.standard_line_width
    STIA_color, STIA_name, STIA_lw = "#54A24B", "IA", c.standard_line_width
    STIS_color, STIS_name, STIS_lw = "#4C78A8", "IS", c.standard_line_width
else:
    STMP_color, STMP_name, STMP_lw = "#FAD7B0", "STMP", c.thin_line_width
    STIA_color, STIA_name, STIA_lw = "#CDEACB", "STIA", c.thin_line_width
    STIS_color, STIS_name, STIS_lw = "#AEC7E8", "STIS", c.thin_line_width

# ―――― Static (short-run) curves: rest while idle, shocked after Play ――――――――――――――――
# Before Play the diagrams show the pre-shock resting equilibrium (Y=Ȳ, π=πᵃ, r=rᵃ);
# the curves jump to the shocked position only once Play is pressed.
if phase == "idle":
    sIS_slope, sIS_int = -1 / PHI_BASE, (OMEGA_BASE + PSI_BASE * WR_BASELINE) / PHI_BASE
    sMP_slope, sMP_int = LP_BASE / Ybar, RP_BASE - LP_BASE + LI_BASE * PIA_BASE
    sFX = RA_BASE
    _P0 = h.OEParams(OMEGA_BASE, PHI_BASE, PSI_BASE, RP_BASE, LP_BASE, LI_BASE,
                     RA_BASE, PIA_BASE, GAMMA_BASE, 0.0, Ybar)
    sAD_slope, sAD_int = h.oe_ad_curve(_P0, oe_regime, WR_BASELINE)
    sIA, sY = PIA_BASE, Ybar
else:
    sIS_slope, sIS_int = IS_slope, IS_intercept_shock
    sMP_slope, sMP_int = MP_slope, MP_intercept_shock
    # The FX curve is the INTEREST-PARITY constraint r = rᵃ, not the operating
    # point. Drawing it at the CB's own (sterilised) rate made the constraint
    # appear to move to meet the operating point, hiding the very gap that
    # generates the reserve flows sterilisation is about. It is always rᵃ.
    sFX = r_foreign
    # Short-run (shocked) AD. Under either peg the AD sits where the PERIOD-1
    # real-exchange-rate state puts it.
    sAD_slope, sAD_int = AD_slope_sr, AD_intercept_sr
    sIA, sY = pi_0, Y_shock

# ―――― Tabs ――――――――――――――――
tab1, tab2 = st.tabs(["📊 Model", "📖 Theory"])

with tab2:
    # The trinity diagram sits between the two halves of the text. It goes through
    # st.image: both st.markdown(unsafe_allow_html=True) and st.html run the SVG
    # through a sanitizer that drops it silently, leaving no element at all.
    st.markdown(c.THEORY_INTRO)
    st.image(c.TRINITY_SVG, width="stretch")
    st.markdown(c.THEORY_REST)

with tab1:
    # Three bordered panels of equal weight, each with a header: with only two of
    # them boxed the diagrams looked like a leftover. gap/alignment keep the tops
    # of the three borders on one line.
    cols = st.columns([0.8, 1], gap="small", vertical_alignment="top") # [1.4, 0.9, 0.7],
    diagrams = cols[0].container(border=True, height="stretch")
    h.panel_header("Diagrams", diagrams)

    # ―――― r–Y diagram ――――――――――――――――
    # No x-title on the upper chart: it shares the axis with the one below it, and
    # dropping the repeat binds the two into a single block.
    r_Y_fig = h.create_linear_plot(x_label="", y_label="r - interest rate")
    h.add_line_to_plot(r_Y_fig, sIS_slope, sIS_int, x_lo, x_hi, name=STIS_name, color=STIS_color, line_width=STIS_lw)
    h.add_line_to_plot(r_Y_fig, sMP_slope, sMP_int, x_lo, x_hi, name=STMP_name, color=STMP_color, line_width=STMP_lw)
    h.add_line_to_plot(r_Y_fig, 0, sFX, x_lo, x_hi, name='FX', color="#E45756")

    if phase != "idle":
        h.add_line_to_plot(r_Y_fig, IS_slope, IS_intercept_cur, x_lo, x_hi, name="LTIS", color="#4C78A8", line_width=c.thin_line_width)
        h.add_line_to_plot(r_Y_fig, MP_slope, MP_intercept_cur, x_lo, x_hi, name="LTMP", color="#F58518", line_width=c.thin_line_width)
        h.add_vertical_line(r_Y_fig, Y_cur, y_max=r_cur, name=f"Y ({Y_cur:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(r_Y_fig, sY, y_max=sFX, name=f"Y ({sY:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(r_Y_fig, Ybar, name=f'Ȳ ({Ybar})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(r_Y_fig, height=340, column_to_plot=diagrams, key="oe_rY")

    output_gap = Y_cur - Ybar

    # ―――― π–Y diagram ――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="𝜋 - inflation")
    h.add_line_to_plot(pi_Y_fig, 0, sIA, x_lo, x_hi, name=STIA_name, color=STIA_color, line_width=STIA_lw)
    # Under the hard peg r cannot respond and wʳ is fixed within the period, so
    # demand does not depend on current inflation at all — AD is VERTICAL. Drawing
    # it as a sloped line would imply a stabiliser that regime does not have.
    if sAD_slope is None:
        h.add_vertical_line(pi_Y_fig, sAD_int, name='AD', color="#B279A2", dash='solid')
    else:
        h.add_line_to_plot(pi_Y_fig, sAD_slope, sAD_int, x_lo, x_hi, name='AD', color="#B279A2")

    if phase != "idle":
        h.add_line_to_plot(pi_Y_fig, 0, pi_cur, x_lo, x_hi, name="LTIA", color="#54A24B", line_width=c.thin_line_width)
        h.add_vertical_line(pi_Y_fig, Y_cur, y_max=pi_cur, name=f"Y ({Y_cur:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(pi_Y_fig, sY, y_max=sIA, name=f"Y ({sY:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')

    # PPP-curve: horizontal at foreign inflation πᵃ (the long-run anchor). Labelled
    # on the left so it doesn't collide with the IA label on the right.
    h.add_line_to_plot(pi_Y_fig, 0, pi_foreign, x_lo, x_hi, dash='dash', name=f"PPP ({pi_foreign:.1f})", color="#999999", line_width=c.thin_line_width, label_position='left')
    h.add_vertical_line(pi_Y_fig, Ybar, name=f'Ȳ ({Ybar})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(pi_Y_fig, height=360, column_to_plot=diagrams, key="oe_piY")

    # ―――― Advanced: equation display ――――――――――――――――
    if level == 'Advanced':
        # Equations plus the live readouts. π* is deliberately absent: the long-run
        # line under this panel already reports where inflation ends.
        _ad_line = (f"vertical at Y = {sAD_int:.2f}" if sAD_slope is None
                    else f"𝜋 = {sAD_slope:.2f}·Y + {sAD_int:.2f}")
        _fx_line = (f'<b style="color:#E45756;">FX:</b> r set by the bank = {r_cur:.2f}'
                    if peg_steril else
                    f'<b style="color:#E45756;">FX:</b> r = rᵃ = {r_foreign:.2f}')
        text_to_show = c.oe_panel("Current model", regime, f"""
            <b style="color:#4C78A8;">IS:</b> Y = {omega:.1f} − {phi:.1f}·r + {psi:.1f}·wʳ<br>
            <b style="color:#F58518;">MP:</b> r = {MP_slope:.2f}·Y + {MP_intercept_cur:.2f}<br>
            {_fx_line}<br>
            <b style="color:#B279A2;">AD:</b> {_ad_line}<br>
            <b style="color:#54A24B;">IA:</b> 𝜋 = {pi_0:.2f}<br>
            <hr style="margin:4px 0; border:none; border-top:1px solid #ddd;">
            <b>Output gap (Y − Ȳ):</b> {output_gap:.2f}<br>
            <b>Real exchange rate wʳ:</b> {wr_cur:.2f}
        """, "⚙️")

    df_now = st.session_state.oe_iteration_df
    df_lock = st.session_state.oe_locked_df

    # ―――― Right column, upper panel ――――――――――――――――
    with cols[1].container(border=True, height="stretch"):
        # The header goes in FIRST: called after st.columns() it lands under the
        # charts instead of on top of them.
        h.panel_header("Over time")
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
            # Only the bottom ROW of the grid carries the "Period" title — the charts
            # share an x-axis, and repeating the label on all four chopped the panel up.
            fig.update_layout(xaxis_title="Period" if show_x else "", yaxis_title=y_title,
                              showlegend=False)
            h.add_line_to_plot(fig, 0, ref_value, 0, iteration_count,
                               name=f"{ref_label} ({ref_value:.2f})", line_width=2, color="#999999", dash='dot')
            h.show_plotly_fig(fig, height=185 if show_x else 165, key=f"oe_ts_{y_col}")

        with cols_graphs[0]:
            _series_chart("Output",    "Y - Output",           "Y",  Ybar,        "Ȳ")
            _series_chart("Inflation", "𝜋 - inflation",        "𝜋",  pi_eq,       "𝜋*", show_x=True)

        with cols_graphs[1]:
            # Reference is the LONG-RUN wʳ, not the pre-shock one: most shocks move
            # the real exchange rate permanently, so wʳ₀ was the wrong target line.
            _series_chart("RealFX",    "wʳ - real exch. rate", "wʳ", WR_LONGRUN,  "wʳ*")
            # r is pegged to rᵃ in every regime except 'fixed with sterilization', where
            # the CB sets its own rate — that is what makes the two pegs differ.
            _series_chart("Rate",      "r - interest rate",    "r", peg_lr_rate, "r*", show_x=True)

    # ―――― Right column, lower panel ――――――――――――――――
    with cols[1].container(border=True, height="stretch"):
        h.panel_header("What is happening")
        # ―――― Pop-ups ――――――――――――――――
        # Only things the description panel below does NOT say: a run that will not
        # settle, a peg that cannot be held, and — at Medium/Advanced, where the
        # panel lists settings instead of telling a story — a policy switched off by
        # the chosen regime. Nothing here repeats the panel.
        if peg_unsustainable:
            st.warning(f"⚠️ **This peg needs capital controls.** The bank ends up holding "
                       f"r = {peg_lr_rate:.2f} while the world rate is rᵃ = {r_foreign:.2f}, which is "
                       f"why the operating point sits away from the red FX line. Money keeps crossing "
                       f"the border, so reserves drain (or pile up) without limit. Sterilisation is not "
                       f"a way of having all three at once — it is the corner of the trinity where "
                       f"**free movement of capital** is the objective given up. Without controls the "
                       f"bank must eventually let the interest rate go (→ **Fixed – no sterilization**) "
                       f"or let the currency go (→ **Flexible**).")

        if peg_undamped and phase != "idle":
            st.warning("⚠️ **This run does not settle.** With no sterilisation the interest rate is "
                       "pinned to rᵃ and the Taylor rule is abandoned, so nothing responds to inflation "
                       "within the period — the AD curve is vertical. The only correcting force is the "
                       "slow drift of the real exchange rate, so output overshoots potential and swings "
                       "back and forth instead of coming to rest. That is a property of the regime, not "
                       "a glitch: a peg without sterilisation leaves the economy badly exposed to a shock.")

        if level != 'Easy':
            if monetary_neutralised:
                st.info(c.monetary_neutralised_text)
            if foreign_neutralised:
                st.info(c.foreign_neutralised_text)

        st.markdown(text_to_show, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:12px; color:gray; margin-top:8px;'>{longrun_line}</div>",
                    unsafe_allow_html=True)

        # Spacer: a stretch container eats whatever height is left, which pins the
        # buttons to the bottom edge however long the description is, so they stop
        # drifting up and down as you switch shocks. It needs a child — Streamlit
        # renders nothing at all for a container with no content.
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
        # Under a peg the real exchange rate keeps drifting for as long as domestic
        # inflation differs from foreign inflation — that is what eventually closes
        # the output gap and returns inflation to πᵃ.
        _pi_next = h.oe_next_inflation(P, oe_regime, pi_cur, Y_cur, wr_cur)
        _Y_next, _, _ = h.oe_operating_point(P, oe_regime, _pi_next, wr_cur)
        st.session_state.oe_pi_prev = _pi_next
        st.session_state.oe_wr_prev = h.oe_wr_next(P, oe_regime, wr_cur, _pi_next, _Y_next)
        st.session_state.oe_iter_counter += 1

        if st.session_state.oe_iter_counter >= iteration_count:
            st.session_state.oe_phase = "done"

        time.sleep(sim_speed)
        st.rerun()
