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
# Output is an index with Ȳ = 100, so one unit of Y is one per cent of potential
# and the gap is in percentage points. The defaults below are chosen to read like
# a real economy at rest: Y = 100, π = πᵃ = 2 %, r = rᵃ = 2 %, wʳ = 100.
#
#   φ = 1.00  a 1 pp rise in the real rate costs 1 % of potential output
#   ψ = 0.25  a 1 % real depreciation adds 0.25 % to output (net-export channel)
#   λ_P = 0.5 Taylor weight on a gap in per cent
#   λ_I = 0.75 real-rate response to inflation (nominal response 1.75)
#   γ = 0.4   Phillips slope: 1 point of gap moves next period's inflation 0.4 pp
#   r' = rᵃ − λ_I·πᵃ = 0.5 is what puts the resting point exactly at Y = Ȳ
#   ω = Ȳ + φ·rᵃ − ψ·wʳ* = 77 does the same for the IS curve
PHI_BASE, PSI_BASE, OMEGA_BASE = 1.0, 0.25, 77.0
RP_BASE, LP_BASE, LI_BASE, GAMMA_BASE = 0.5, 0.5, 0.75, 0.4
RA_BASE, PIA_BASE = 2.0, 2.0
WR_BASELINE = (c.Y_potential - OMEGA_BASE + PHI_BASE * RA_BASE) / PSI_BASE   # → 100.0

# ―――― Shock sizes (Easy mode) ――――――――――――――――
# Sized so the impact reads like something that happens to a real economy: a
# demand swing of 1.5 % of GDP, a 50 bp policy move at home or abroad, a 1 pp
# import-price shock. Each one moves output by roughly half a point to a point
# and a half — small enough to be realistic, large enough to see.
FISCAL_SHOCK, MONETARY_SHOCK = 1.5, 0.5
FOREIGN_SHOCK, IMPORTED_SHOCK = 0.5, 1.0


# ―――― Session State ――――――――――――――――
h.session_init(
    oe_phase="idle",        # idle | short_term_paused | adjusting | done
    oe_pi_prev=None,
    oe_wr_prev=None,        # real-exchange-rate state (fixed peg without sterilization)
    oe_iter_counter=0,
    oe_peg_broke=False,     # unsterilised peg amplified until the model left its range
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
    st.session_state.oe_peg_broke = False
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
        # One story, for the regime actually selected — the pop-ups below never repeat it.
        text_to_show = c.oe_shock_panel(shock_type, regime)

    elif level == 'Medium':
        omega = st.slider(r'$\omega$:', on_change=reset,
                          min_value=OMEGA_BASE - 4.0, max_value=OMEGA_BASE + 4.0, step=0.25,
                          value=OMEGA_BASE, key="oe_m_omega",
                          help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$")
        r_init = st.slider(r"$r'$ (%):", on_change=reset, min_value=-1.0, max_value=2.0, step=0.1,
                           value=RP_BASE, key="oe_m_rinit",
                           help=r"MP Curve: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$")
        r_foreign = st.slider(r"$r^a$ (%) - abroad:", on_change=reset, min_value=0.0, max_value=4.0, step=0.1,
                              value=RA_BASE, key="oe_m_rforeign",
                              help=r"FX Curve: $r = r^a$ under a flexible exchange rate; "
                                   r"$r = r^a + (\pi^a - \pi)$ under a peg")
        inflation_shock = st.slider(r"Imported inflation (%):", on_change=reset, min_value=-2.0, max_value=2.0,
                                    step=0.25, value=0.0, key="oe_m_infl",
                                    help="A one-off jump in import prices, which lands directly on inflation. "
                                         "Positive = prices from abroad rise, negative = they fall.")

    elif level == 'Advanced':
        st.markdown('##### IS Curve')
        phi = st.number_input(r'$\varphi$ :', on_change=reset, min_value=0.1, max_value=3.0, step=0.1,
                              value=PHI_BASE, key="oe_a_phi",
                              help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$. Output cost of a "
                                   r"1 pp rise in the real rate, in per cent of potential.")
        psi = st.number_input(r'$\psi$ :', on_change=reset, min_value=0.05, max_value=1.0, step=0.05,
                              value=PSI_BASE, key="oe_a_psi",
                              help=r"Output gain from a 1 % real depreciation ($w^r$ is an index at 100). "
                                   r"0.25 is a normal net-export elasticity; above ~0.5 trade dominates "
                                   r"everything else.")
        omega = st.number_input(r'$\omega$ :', on_change=reset, min_value=60.0, max_value=95.0, step=0.5,
                                value=OMEGA_BASE, key="oe_a_omega",
                                help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$. One unit is one "
                                     r"per cent of potential output.")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### MP Curve')
        r_init = st.number_input(r"$r'$ :", on_change=reset, step=0.1, value=RP_BASE, key="oe_a_rinit",
                                 help=r"MP Curve: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$")
        lambda_p = st.number_input(r'$\lambda_P$ :', on_change=reset, min_value=0.1, max_value=2.0, step=0.05,
                                   value=LP_BASE, key="oe_a_lp",
                                   help=r"MP Curve weight on the output gap, in pp of real rate per point "
                                        r"of gap. 0.5 is the textbook Taylor weight.")
        lambda_i = st.number_input(r'$\lambda_I$ :', on_change=reset, min_value=0.1, max_value=3.0, step=0.05,
                                   value=LI_BASE, key="oe_a_li",
                                   help=r"MP Curve weight on inflation: the REAL rate response. 0.75 here "
                                        r"means a nominal response of 1.75, comfortably above the Taylor "
                                        r"principle.")

        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### FX Curve')
        r_foreign = st.number_input(r"$r^a$ (%) - abroad:", on_change=reset, step=0.1, value=RA_BASE,
                                    key="oe_a_rforeign",
                                    help=r"FX Curve: $1+r = (1+r^a)\,w^{r,e}_{+1}/w^r$ — this is "
                                         r"$r = r^a$ only when no move in the real exchange rate is "
                                         r"expected. Under a peg it is $r = r^a + (\pi^a - \pi)$.")
        pi_foreign = st.number_input(r"$\pi^a$ (%) - abroad:", on_change=reset, step=0.1, value=PIA_BASE,
                                     key="oe_a_piforeign", help=r"Long-run domestic inflation anchor")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### IA Curve')
        gamma = st.number_input(r'$\gamma$ :', on_change=reset, min_value=0.0, max_value=1.5, step=0.05,
                                value=GAMMA_BASE, key="oe_a_gamma",
                                help=r"IA curve: $\pi_{t+1} = \pi_t + \gamma \tilde Y_t$. Phillips slope "
                                     r"in pp of inflation per point of output gap.")
        inflation_shock = st.number_input(r"Imported Inflation (%):", on_change=reset, min_value=-3.0, max_value=3.0,
                                          step=0.25, value=0.0, key="oe_a_infl",
                                          help="A one-off jump in import prices. It lands on inflation once "
                                               "and is carried forward from there.")
        chi = st.number_input(r'$\chi$ (imported inflation):', on_change=reset, min_value=0.0, max_value=0.3,
                              step=0.01, value=0.0, key="oe_a_chi",
                              help=r"How much a move in the exchange rate feeds into domestic prices: a weaker "
                                   r"currency makes imports dearer straight away. $w^r$ is an index, so "
                                   r"$\chi = 0.05$ means a 10 % depreciation adds half a point to inflation. "
                                   r"Large for a CPI basket, small for the GDP deflator. Leave it at 0 for "
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
            play_clicked = st.button("↻ Play again" if phase == "done" else "⏵ Play",
                                     type="primary", width="stretch")
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
MP_slope = lambda_p * h.gap_per_Y(Ybar)      # Ỹ is in points, so d r/d Y = λ_P·100/Ȳ

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
#   run, the Taylor rule is abandoned and the FX MARKET sets the interest rate.
#   With the nominal rate pegged the expected real appreciation is just the
#   inflation differential, so eq. 3.9 becomes r = rᵃ + (πᵃ − π) — the same thing
#   as i = iᵃ with r = i − π, which is how the book writes it (§5.2, §5.4). r is
#   therefore NOT stuck at rᵃ: it moves against inflation. Fiscal policy has its
#   full IS multiplier, and then the real rate pushes the SAME way as the shock —
#   a slump lowers π, which raises r, which deepens the slump. AD slopes UPWARD
#   and the rest point is unstable, which is the book's "worrying policy" (§5.2)
#   and its currency-union divergence (§5.4).
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

# The hard peg has no stabiliser at all — worse, interest parity is a DEstabiliser:
# r = rᵃ + (πᵃ − π) moves the real rate against inflation, so every shock feeds on
# itself. oe_peg_root is the growth factor per period; it exceeds 1 for any φ > 0,
# so no parameter choice makes this regime settle. Flagged so the UI can say the
# shock is amplified instead of pretending the economy comes back.
peg_divergent = peg_no_steril
peg_root = h.oe_peg_root(P) if peg_no_steril else 1.0

# Where the run ends up — NUMBERS ONLY. The panel above it tells the story in
# words, so this line must not repeat the mechanism, only state the destination.
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

# AD in π–Y space, as (slope, intercept). It slopes DOWN under a float and under a
# sterilised peg, and UP (+1/φ) without sterilisation, where interest parity ties
# r to πᵃ − π so demand rises with inflation.
AD_slope, AD_intercept = h.oe_ad_curve(P, oe_regime, wr_state if phase != "idle" else WR_BASELINE)
AD_slope_sr, AD_intercept_sr = h.oe_ad_curve(P, oe_regime, WR_BASELINE)

IS_intercept_cur = h.oe_is_intercept(P, wr_cur)
IS_intercept_shock = h.oe_is_intercept(P, wr_shock)
MP_intercept_cur = r_init - lambda_p * 100.0 + lambda_i * pi_cur
MP_intercept_shock = r_init - lambda_p * 100.0 + lambda_i * pi_0


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
# Also fires from "done", so Play restarts a finished run instead of doing nothing:
# the block below rebuilds the whole run state from scratch, so replaying is just
# running it again. A run saved with "Remember this run" is deliberately kept, so
# the replay is drawn against it.
if play_clicked and phase in ("idle", "done"):
    st.session_state.oe_phase = "short_term_paused"
    st.session_state.oe_peg_broke = False
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
# Y is an index around 100 and the interesting moves are a point or two, so the
# window is sized from the ACTION, not from the level: 1.6× the largest gap the
# run has reached, with a floor of 2 points so a small shock still has room
# around it. Taking the live point in too lets the window follow a run that keeps
# widening (the unsterilised peg) instead of letting it walk off the chart.
MIN_HALF_WINDOW = 2.0
const = max(MIN_HALF_WINDOW,
            1.6 * max(abs(Y_shock - Ybar), abs(Y_cur - Ybar)))
x_lo, x_hi = Ybar - const, Ybar + const

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

_P0 = h.OEParams(OMEGA_BASE, PHI_BASE, PSI_BASE, RP_BASE, LP_BASE, LI_BASE,
                 RA_BASE, PIA_BASE, GAMMA_BASE, 0.0, Ybar)
init_IS = (-1 / PHI_BASE, (OMEGA_BASE + PSI_BASE * WR_BASELINE) / PHI_BASE)
init_MP = (LP_BASE * h.gap_per_Y(Ybar), RP_BASE - LP_BASE * 100.0 + LI_BASE * PIA_BASE)
init_FX = (0.0, RA_BASE)
init_AD = h.oe_ad_curve(_P0, oe_regime, WR_BASELINE)
init_IA = (0.0, PIA_BASE)

st_IS, st_MP = (IS_slope, IS_intercept_shock), (MP_slope, MP_intercept_shock)
st_AD, st_IA = (AD_slope_sr, AD_intercept_sr), (0.0, pi_0)
lt_IS, lt_MP = (IS_slope, IS_intercept_cur), (MP_slope, MP_intercept_cur)
lt_AD, lt_IA = (AD_slope, AD_intercept), (0.0, pi_cur)

# The FX curve is the INTEREST-PARITY constraint of eq. 3.9, never the operating
# point. Under a FLOAT the expected real exchange rate is the current one, so it
# sits at rᵃ and stays there. Under EITHER peg the nominal rate is fixed, so the
# expected real appreciation is the inflation differential and the line sits at
# rᵃ + (πᵃ − π) — it MOVES as inflation moves, which is the book shifting the FX
# curve for forward-looking expectations (§4.7, Figure 4.9). Without sterilisation
# the operating point rides that line; with sterilisation the bank holds its own r
# and the vertical distance to the line is the reserve flow it has to absorb.
st_FX = (0.0, h.oe_fx_rate(P, oe_regime, pi_0))
lt_FX = (0.0, h.oe_fx_rate(P, oe_regime, pi_cur))

# Operating point marker.
sY, sIA = (Ybar, PIA_BASE) if phase == "idle" else (Y_cur, pi_cur)
sFX = RA_BASE if phase == "idle" else r_foreign

# ―――― Tabs ――――――――――――――――
# Settings gets its own right-aligned row; the tabs stay at FULL width. Wrapping
# the tabs in a column instead — st.columns([6,1]) with cols[0].tabs(...) — puts
# every diagram and panel inside them into that column, which is what made the
# page stop at the settings border instead of running to the edge.
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
    h.add_curve_set(r_Y_fig, 'IS', x_lo, x_hi, init_IS, st_IS, lt_IS, show_initial, show_long)
    h.add_curve_set(r_Y_fig, 'MP', x_lo, x_hi, init_MP, st_MP, lt_MP, show_initial, show_long)
    h.add_curve_set(r_Y_fig, 'FX', x_lo, x_hi, init_FX, st_FX, lt_FX, show_initial, show_long)

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

    # PPP-curve: horizontal at foreign inflation πᵃ (the long-run anchor). Labelled
    # on the left so it doesn't collide with the IA label on the right.
    h.add_line_to_plot(pi_Y_fig, 0, pi_foreign, x_lo, x_hi, dash='dash', name=f"PPP ({pi_foreign:.1f})", color="#999999", line_width=c.thin_line_width, label_position='left')

    # AD comes AFTER the horizontals so its label is placed against curves that are
    # already on the figure.
    h.add_curve_set(pi_Y_fig, 'AD', x_lo, x_hi, init_AD, st_AD, lt_AD, show_initial, show_long)

    if phase != "idle":
        h.add_vertical_line(pi_Y_fig, Y_cur, y_max=pi_cur, name=f"Y ({Y_cur:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(pi_Y_fig, sY, y_max=sIA, name=f"Y ({sY:.1f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(pi_Y_fig, Ybar, name=f'Ȳ ({Ybar})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(pi_Y_fig, height=360, column_to_plot=diagrams, key="oe_piY")

    # ―――― Advanced: equation display ――――――――――――――――
    if level == 'Advanced':
        # Equations plus the live readouts. π* is deliberately absent: the long-run
        # line under this panel already reports where inflation ends.
        _ad_slope, _ad_int = (init_AD if phase == "idle" else
                              (st_AD if show_initial else lt_AD))
        # Written around Ȳ rather than as a raw intercept: with Y an index at 100
        # the intercept is a three-digit number that tells the reader nothing.
        _ad_at_Ybar = _ad_slope * Ybar + _ad_int
        _ad_line = f"𝜋 = {_ad_at_Ybar:.2f} {_ad_slope:+.2f}·(Y − Ȳ)"
        # FX is the parity line; under a peg it moves with inflation, and under
        # sterilisation the bank's own r sits away from it (that gap is the reserve
        # flow), so both numbers are worth showing.
        _fx_level = h.oe_fx_rate(P, oe_regime, pi_cur)
        if peg_steril:
            _fx_line = (f'<b style="color:#E45756;">FX:</b> parity needs r = {_fx_level:.2f}; '
                        f'bank holds r = {r_cur:.2f}')
        elif peg_no_steril:
            _fx_line = (f'<b style="color:#E45756;">FX:</b> r = rᵃ + (πᵃ − 𝜋) = {_fx_level:.2f}')
        else:
            _fx_line = f'<b style="color:#E45756;">FX:</b> r = rᵃ = {r_foreign:.2f}'
        text_to_show = c.oe_panel("Current model", regime, f"""
            <b style="color:#4C78A8;">IS:</b> Y = {omega:.1f} − {phi:.2f}·r + {psi:.2f}·wʳ<br>
            <b style="color:#F58518;">MP:</b> r = {r_init:.2f} + {lambda_p:.2f}·Ỹ + {lambda_i:.2f}·𝜋<br>
            {_fx_line}<br>
            <b style="color:#B279A2;">AD:</b> {_ad_line}<br>
            <b style="color:#54A24B;">IA:</b> 𝜋 = {pi_0:.2f}<br>
            <hr style="margin:4px 0; border:none; border-top:1px solid #ddd;">
            <b>Output gap:</b> {output_gap:+.2f}% of potential<br>
            <b>Real exchange rate wʳ:</b> {wr_cur:.1f}
        """, "⚙️")

    df_now = st.session_state.oe_iteration_df
    df_lock = st.session_state.oe_locked_df

    # ―――― Right column, upper panel ――――――――――――――――
    with cols[1].container(border=True, height="stretch"):
        # The header goes in FIRST: called after st.columns() it lands under the
        # charts instead of on top of them.
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
            # Only the bottom ROW of the grid carries the "Period" title — the charts
            # share an x-axis, and repeating the label on all four chopped the panel up.
            fig.update_layout(xaxis_title="Period" if show_x else "", yaxis_title=y_title,
                              showlegend=False)
            h.add_line_to_plot(fig, 0, ref_value, 0, iteration_count,
                               name=f"{ref_label} ({ref_value:.2f})", line_width=2, color="#999999", dash='dot')
            h.show_plotly_fig(fig, height=185 if show_x else 165, key=f"oe_ts_{y_col}")

        with cols_graphs[0]:
            _series_chart("Output",    "Y — output (Ȳ=100)", "Y",  Ybar,        "Ȳ")
            _series_chart("Inflation", "𝜋 - inflation",        "𝜋",  pi_eq,       "𝜋*", show_x=True)

        with cols_graphs[1]:
            # Reference is the LONG-RUN wʳ, not the pre-shock one: most shocks move
            # the real exchange rate permanently, so wʳ₀ was the wrong target line.
            _series_chart("RealFX",    "wʳ — real exch. rate", "wʳ", WR_LONGRUN,  "wʳ*")
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

        if peg_divergent and phase != "idle":
            st.warning(f"⚠️ **This shock feeds on itself.** The Taylor rule is gone, so the FX market "
                       f"sets the interest rate: the nominal rate is pegged (i = iᵃ), which leaves "
                       f"r = rᵃ + (πᵃ − 𝜋). A slump pulls inflation below the world rate, so the real "
                       f"rate RISES and the slump deepens; a boom does the reverse. That is why AD "
                       f"slopes upward here and why the gap grows about {(peg_root - 1) * 100:.0f}% a "
                       f"period. Competitiveness does pull the other way — cheaper domestic prices "
                       f"raise wʳ — but it works through the slow drift of the price level and never "
                       f"catches up. This is the book's *worrying policy*: a peg without sterilisation "
                       f"leaves the economy badly exposed to a shock, and it is the same mechanism "
                       f"that made the Eurozone diverge.")

        if st.session_state.oe_peg_broke:
            st.error("🛑 **The peg breaks.** The run stopped because output or inflation left the range "
                     "where a linear IS curve means anything. That is not a numerical glitch — it is "
                     "where this regime ends up: holding the rate demands an interest rate the economy "
                     "cannot bear, so the bank either raises it anyway (France 1992) or gives up the "
                     "peg (the UK on Black Wednesday). A smaller shock — the Medium or Advanced "
                     "level — takes longer to get there and shows more of the path.")

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
        _wr_next = h.oe_wr_next(P, oe_regime, wr_cur, _pi_next, _Y_next)
        st.session_state.oe_pi_prev = _pi_next
        st.session_state.oe_wr_prev = _wr_next
        st.session_state.oe_iter_counter += 1

        # An unsterilised peg amplifies without limit, so the run has to be stopped
        # where the model stops describing anything — see helpers.oe_out_of_range.
        if peg_divergent and h.oe_out_of_range(P, _Y_next, _pi_next, _wr_next):
            st.session_state.oe_peg_broke = True
            st.session_state.oe_phase = "done"
        elif st.session_state.oe_iter_counter >= iteration_count:
            st.session_state.oe_phase = "done"

        time.sleep(sim_speed)
        st.rerun()
