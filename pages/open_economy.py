import streamlit as st
import pandas as pd
import time
import plotly.express as px

import config as c
import helpers as h

# ―――― Open-economy consensus model (flexible exchange rate) ――――――――――――――――
# Five equations (Lambsdorff & Giamattei, ch. 5):
#   IS : Y = ω − φ·r + ψ·wʳ
#   MP : r = r' + λ_P·Ỹ + λ_I·π
#   FX : r = rᵃ                      (UIP, static expectations)
#   IA : π = π₋₁ + γ·Ỹ₋₁
#   PPP: long-run domestic inflation converges to foreign inflation πᵃ
#
# Under a FLEXIBLE exchange rate the FX line binds (r = rᵃ). Output is therefore
# pinned by MP∩FX and the real exchange rate wʳ adjusts so IS passes through the
# same point. Consequences:
#   • AD (from MP∩FX):  π = (rᵃ − r' + λ_P)/λ_I − λ_P/(λ_I·Ȳ)·Y
#   • π* = (rᵃ − r')/λ_I      ← ω and ψ drop out ⇒ demand shocks fully crowd out
#   • wʳ = (Y − ω + φ·rᵃ)/ψ

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
    oe_iter_counter=0,
    oe_iteration_df=pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX"]),
    oe_locked_df=None,
)


def reset():
    st.session_state.oe_phase = "idle"
    st.session_state.oe_pi_prev = None
    st.session_state.oe_iter_counter = 0
    st.session_state.oe_iteration_df = pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX"])


def lock_run():
    if not st.session_state.oe_iteration_df.empty:
        st.session_state.oe_locked_df = st.session_state.oe_iteration_df.copy()


def clear_lock():
    st.session_state.oe_locked_df = None


# ―――― Easy-mode shock descriptions ――――――――――――――――
SHOCK_TEXT = {
    'Expansionary Monetary Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Expansionary Monetary Shock 🏦</div>
<div style="font-size:13px; color:gray;">
The central bank adopts a looser policy stance (↓r'). The MP-curve shifts down and the AD-curve shifts right.
<br><br>
In the short run output rises above potential. The lower rate induces capital outflows, the domestic currency depreciates (wʳ ↑) and net exports rise. Over time the positive output gap raises inflation to its new, higher long-run level π* = (rᵃ − r')/λ<sub>I</sub>.
</div>""",
    'Contractionary Monetary Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Contractionary Monetary Shock 🏦</div>
<div style="font-size:13px; color:gray;">
The central bank tightens its policy stance (↑r'). The MP-curve shifts up and the AD-curve shifts left.
<br><br>
Output falls below potential and capital flows in, appreciating the domestic currency (wʳ ↓). The negative output gap gradually lowers inflation to its new long-run level π* = (rᵃ − r')/λ<sub>I</sub>, which now lies below foreign inflation πᵃ.
</div>""",
    'Rising Foreign Interest Rate': """
<div style="text-align:center; font-size:17px; font-weight:700;">Rising Foreign Interest Rate 🌍</div>
<div style="font-size:13px; color:gray;">
The foreign central bank raises its rate (↑rᵃ). The FX-line shifts up.
<br><br>
Capital flows abroad, the domestic currency depreciates and the real exchange rate wʳ rises, shifting IS right. Output rises in the short run and the domestic real rate follows rᵃ upward. Inflation climbs to π* = (rᵃ − r')/λ<sub>I</sub>.
</div>""",
    'Falling Foreign Interest Rate': """
<div style="text-align:center; font-size:17px; font-weight:700;">Falling Foreign Interest Rate 🌍</div>
<div style="font-size:13px; color:gray;">
The foreign central bank lowers its rate (↓rᵃ). The FX-line shifts down.
<br><br>
Capital flows in, the domestic currency appreciates (wʳ ↓) and net exports fall, shifting IS left. Output falls in the short run and inflation declines to its new long-run level π* = (rᵃ − r')/λ<sub>I</sub>.
</div>""",
    'Imported Inflation Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Imported Inflation Shock 📈</div>
<div style="font-size:13px; color:gray;">
A one-off rise in the real exchange rate makes foreign goods more expensive and passes directly into domestic prices (χ·Δwʳ), shifting the IA-curve up — even with no output gap (eq. 5.2).
<br><br>
Inflation jumps above foreign inflation πᵃ. The central bank raises the real rate, output falls below potential, and the negative output gap brings inflation back down to πᵃ.
</div>""",
    'Imported Deflation Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Imported Deflation Shock 📉</div>
<div style="font-size:13px; color:gray;">
A one-off fall in the real exchange rate makes foreign goods cheaper and passes directly into domestic prices (χ·Δwʳ), shifting the IA-curve down — even with no output gap (eq. 5.2).
<br><br>
Inflation drops below foreign inflation πᵃ. The central bank lowers the real rate, output rises above potential, and the positive output gap brings inflation back up to πᵃ.
</div>""",
    'Expansionary Fiscal Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Expansionary Fiscal Shock 🏛️</div>
<div style="font-size:13px; color:gray;">
Higher government demand shifts the IS-curve right (↑ω). What happens next depends entirely on the <b>exchange-rate regime</b>:
<br><br>
<b>Flexible:</b> the currency appreciates (wʳ ↓), net exports fall, and output is <b>fully crowded out</b> — Y and π are unchanged.
<br><br>
<b>Fixed peg:</b> the exchange rate cannot move, so fiscal policy is <b>effective</b> — output jumps above potential, then real appreciation gradually crowds it out and inflation returns to πᵃ.
</div>""",
    'Contractionary Fiscal Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Contractionary Fiscal Shock 🏛️</div>
<div style="font-size:13px; color:gray;">
Lower government demand shifts the IS-curve left (↓ω). The effect depends on the <b>exchange-rate regime</b>:
<br><br>
<b>Flexible:</b> the currency depreciates (wʳ ↑), net exports rise, and the demand cut is <b>fully crowded out</b> — Y and π are unchanged.
<br><br>
<b>Fixed peg:</b> fiscal policy is <b>effective</b> — output falls below potential, then real depreciation restores it and inflation returns to πᵃ.
</div>""",
    None: c.placeholder_shock,
}

MARKDOWN_THEORY = r"""
### Open economy with variable inflation

The closed-economy consensus model is extended to an open economy by (i) adding a
real-exchange-rate term to the IS-curve and (ii) tying the domestic real interest
rate to the foreign one through the FX-curve (uncovered interest parity):

$$Y = \omega - \varphi\, r + \psi\, w^r \qquad\text{(IS)}$$
$$r = r' + \lambda_P\,\tilde Y + \lambda_I\,\pi \qquad\text{(MP)}$$
$$r = r^a \qquad\text{(FX, flexible rate)}$$
$$\pi = \pi_{-1} + \gamma\,\tilde Y_{-1} \qquad\text{(IA)}$$

Under a **flexible exchange rate** the real interest rate is pinned to the foreign
rate $r^a$. Output is determined by MP∩FX and the real exchange rate $w^r$ adjusts
so that IS passes through the same point. Because $\omega$ and $\psi$ drop out of
the resulting AD-curve, **demand shocks are fully crowded out** by the exchange
rate, while **monetary** and **foreign-rate** shocks move output and inflation
toward the new long-run equilibrium $\pi^* = (r^a - r')/\lambda_I$.
"""


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
                          help=("Flexible: float absorbs shocks, π → πᵃ (PPP). "
                                "Fixed – no sterilization: monetary policy is powerless (r tied to rᵃ). "
                                "Fixed – with sterilization: monetary policy is temporarily independent and "
                                "ends in a crawling peg (π* ≠ πᵃ, the nominal rate crawls at π − πᵃ)."))

    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    # ―――― Parameter Inputs ――――――――――――――――
    # Structural defaults (overridden in Advanced)
    phi = PHI_BASE; psi = PSI_BASE; lambda_p = LP_BASE; lambda_i = LI_BASE
    gamma = GAMMA_BASE; pi_foreign = PIA_BASE; eta = 0.0; inflation_shock = 0.0
    omega = OMEGA_BASE; r_init = RP_BASE; r_foreign = RA_BASE; pi_0_override = None

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
        text_to_show = SHOCK_TEXT.get(shock_type, c.placeholder_shock)

    elif level == 'Medium':
        omega = st.slider(r'$\omega$:', on_change=reset, min_value=0.5, max_value=4.0, step=0.1,
                          value=OMEGA_BASE, help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$")
        r_init = st.slider(r"$r'$ (%):", on_change=reset, min_value=-0.5, max_value=1.5, step=0.1,
                           value=RP_BASE, help=r"MP Curve: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$")
        r_foreign = st.slider(r"$r^a$ (%) - abroad:", on_change=reset, min_value=1.0, max_value=3.0, step=0.1,
                              value=RA_BASE, help=r"FX Curve: $r = r^a$ under a flexible exchange rate")
        inflation_shock = st.slider(r"Imported inflation (%):", on_change=reset, min_value=-2.0, max_value=2.0,
                                    step=0.25, value=0.0,
                                    help="One-off shift of the IA-curve (χ·Δwʳ). Positive = imported inflation, negative = imported deflation.")

    elif level == 'Advanced':
        st.markdown('##### IS Curve')
        phi = st.number_input(r'$\varphi$ :', on_change=reset, min_value=0.1, step=0.1, value=PHI_BASE,
                              help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$")
        psi = st.number_input(r'$\psi$ :', on_change=reset, min_value=0.1, step=0.1, value=PSI_BASE,
                              help=r"Real-exchange-rate sensitivity of demand")
        omega = st.number_input(r'$\omega$ :', on_change=reset, min_value=0.0, step=0.5, value=OMEGA_BASE,
                                help=r"IS Curve: $Y = \omega - \varphi r + \psi w^r$")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### MP Curve')
        r_init = st.number_input(r"$r'$ :", on_change=reset, step=0.1, value=RP_BASE,
                                 help=r"MP Curve: $r = r' + \lambda_P \tilde Y + \lambda_I \pi$")
        lambda_p = st.number_input(r'$\lambda_P$ :', on_change=reset, min_value=0.1, max_value=10.0, step=0.1,
                                   value=LP_BASE, help=r"MP Curve output-gap weight")
        lambda_i = st.number_input(r'$\lambda_I$ :', on_change=reset, min_value=0.1, max_value=10.0, step=0.1,
                                   value=LI_BASE, help=r"MP Curve inflation weight")

        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### FX Curve')
        r_foreign = st.number_input(r"$r^a$ (%) - abroad:", on_change=reset, step=0.1, value=RA_BASE,
                                    help=r"FX Curve: $r = r^a$")
        pi_foreign = st.number_input(r"$\pi^a$ (%) - abroad:", on_change=reset, step=0.1, value=PIA_BASE,
                                     help=r"Long-run domestic inflation anchor")
        st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
        st.markdown('##### IA Curve')
        gamma = st.number_input(r'$\gamma$ :', on_change=reset, min_value=0.0, step=0.1, value=GAMMA_BASE,
                                help=r"IA curve: $\pi_{t+1} = \pi_t + \gamma \tilde Y_t + \eta$")
        inflation_shock = st.number_input(r"Imported Inflation (%):", on_change=reset, min_value=-3.0, max_value=3.0,
                                          step=0.25, value=0.0, help="One-off shift of the initial IA level (χ·Δwʳ).")
        eta = st.number_input(r'$\eta$ (exogenous shock):', on_change=reset, step=0.1, value=0.0,
                              help=r"Persistent exogenous price shock each period.")

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
        reset_clicked = st.button("↺ Reset", on_click=reset, width="stretch", disabled=is_running)

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
AD_slope = -lambda_p / (lambda_i * Ybar)

# ―――― Exchange-rate regime ――――――――――――――――
# With the MP rule r = r' + λ_P·Ỹ + λ_I·π, long-run inflation is pinned wherever
# the nominal exchange rate is free to move, so the regimes split as:
#   • Flexible → the nominal rate floats. Monetary/foreign-rate shocks are
#       permanent and the economy ends in a CRAWLING PEG: π* = (rᵃ − r')/λ_I ≠ πᵃ,
#       with the nominal rate crawling at π* − πᵃ. (Fiscal is crowded out.)
#   • Fixed-with-sterilization → the CB sterilises to keep monetary policy
#       independent; the hard peg is unsustainable and also ends in the same
#       CRAWLING PEG π* = (rᵃ − r')/λ_I. (Fiscal is effective.)
#   • Fixed-no-sterilization → reserve flows tie r to rᵃ (monetary policy is
#       powerless) and the fixed nominal peg forces PPP, so π → πᵃ.
# Only the no-sterilization peg returns inflation to foreign inflation.
ppp_regime = (regime == 'Fixed – no sterilization')

# Fixed without sterilization: reserve flows peg r to rᵃ, so domestic monetary
# policy (r') has no effect — neutralise any monetary shock.
monetary_neutralised = (regime == 'Fixed – no sterilization') and (r_init != RP_BASE)
if regime == 'Fixed – no sterilization':
    r_init = RP_BASE

# Short-run (shocked) AD — governs the period-1 impact jump in every regime.
AD_intercept_sr = (r_foreign - r_init + lambda_p) / lambda_i
if ppp_regime:
    pi_eq = pi_foreign                              # PPP: inflation returns to πᵃ
    AD_intercept = pi_foreign - AD_slope * Ybar     # dynamics AD crosses (Ȳ, πᵃ)
else:
    pi_eq = (r_foreign - r_init) / lambda_i         # crawling peg: π* ≠ πᵃ
    AD_intercept = AD_intercept_sr

# Fixed pre-shock equilibrium — charts start here (period 0).
PI_BASELINE = pi_foreign

# Regime outcome summary (shown in the right column).
if ppp_regime:
    regime_outcome = (f"<b>{regime}</b><br><span style='color:gray;'>Long-run: π → πᵃ = "
                      f"{pi_foreign:.2f} (PPP holds).</span>")
else:
    regime_outcome = (f"<b>{regime}</b><br><span style='color:gray;'>Long-run: <b>crawling peg</b> — "
                      f"π* = {pi_eq:.2f} ≠ πᵃ = {pi_foreign:.2f}; the nominal exchange rate crawls at "
                      f"π − πᵃ ≈ {pi_eq - pi_foreign:+.2f}%/period.</span>")

# ―――― Fiscal policy (demand shock via ω) ――――――――――――――――
# Under a FLOAT a fiscal expansion is fully crowded out: the currency appreciates
# (wʳ ↓) and net exports fall, so output is unchanged (ω already drops out of the
# AD-curve, and realfx_at picks up the appreciation). Under a FIXED peg the
# exchange rate cannot jump, so fiscal policy is effective — output jumps on
# impact and is then gradually crowded out as higher inflation appreciates the
# real exchange rate, with inflation returning to πᵃ.
fiscal_shock = omega - OMEGA_BASE
fixed_regime = regime in ('Fixed – no sterilization', 'Fixed – with sterilization')
fiscal_effective = fixed_regime and fiscal_shock != 0.0
FISCAL_CROWD_OUT = 0.5   # per-period decay of the fiscal output boost (real appreciation)


def fiscal_boost(period):
    """Fiscal output boost in a given period — 0 under a float (crowded out)."""
    if not fiscal_effective or phase == "idle":
        return 0.0
    return fiscal_shock * (FISCAL_CROWD_OUT ** max(period - 1, 0))


# Initial (period-1) inflation: predetermined at πᵃ, moved only by an imported/initial shock.
pi_0 = pi_foreign + inflation_shock

# pi_cur: current IA level during animation (or pi_0 if not started)
if st.session_state.oe_pi_prev is None:
    st.session_state.oe_pi_prev = pi_0
pi_cur = st.session_state.oe_pi_prev


def output_at(pi, ad_intercept=None):
    """Output on the AD-curve at inflation π (MP∩FX). Defaults to the dynamics AD
    (which converges to π*); pass the short-run AD for the impact jump."""
    return (pi - (AD_intercept if ad_intercept is None else ad_intercept)) / AD_slope


def realfx_at(y):
    """Real exchange rate wʳ that makes IS pass through (Y, rᵃ)."""
    return (y - omega + phi * r_foreign) / psi


def is_intercept_at(y):
    """IS intercept for the r/Y diagram, given the wʳ implied by output Y."""
    return (omega + psi * realfx_at(y)) / phi


# Current period (animated) operating point. During the short-run pause the point
# sits on the shocked AD (the impact jump); once adjusting it moves along the
# dynamics AD toward π*. A fixed-peg fiscal boost is added on top (0 under a float).
_cur_ad = AD_intercept_sr if phase == "short_term_paused" else AD_intercept
_cur_period = 1 if phase == "short_term_paused" else st.session_state.oe_iter_counter
Y_cur = output_at(pi_cur, _cur_ad) + fiscal_boost(_cur_period)
r_cur = r_foreign
wr_cur = realfx_at(Y_cur)
IS_intercept_cur = is_intercept_at(Y_cur)
MP_intercept_cur = r_init - lambda_p + lambda_i * pi_cur

# Shocked (period-1) operating point — the short-run impact jump on the shocked AD.
Y_shock = output_at(pi_0, AD_intercept_sr) + fiscal_boost(1)
wr_shock = realfx_at(Y_shock)
IS_intercept_shock = is_intercept_at(Y_shock)
MP_intercept_shock = r_init - lambda_p + lambda_i * pi_0

# Convergence check: stable if γ < 2·Ȳ·|AD_slope|
convergence_ok = (gamma < 2 * Ybar * abs(AD_slope)) if AD_slope != 0 else True

# ―――― Medium: concise dynamic description ――――――――――――――――
if level == 'Medium':
    forces = []
    if omega > OMEGA_BASE + 0.05:   forces.append("expansionary demand (↑ω)")
    elif omega < OMEGA_BASE - 0.05: forces.append("contractionary demand (↓ω)")
    if r_init < RP_BASE - 0.05:     forces.append("looser monetary policy (↓r')")
    elif r_init > RP_BASE + 0.05:   forces.append("tighter monetary policy (↑r')")
    if r_foreign > RA_BASE + 0.05:  forces.append("higher foreign rate (↑rᵃ)")
    elif r_foreign < RA_BASE - 0.05: forces.append("lower foreign rate (↓rᵃ)")
    if inflation_shock > 0:         forces.append("imported inflation (↑χ·Δwʳ)")
    elif inflation_shock < 0:       forces.append("imported deflation (↓χ·Δwʳ)")

    if not forces:
        text_to_show = c.empty_placeholder_moderate_level_shock
    else:
        demand_only = all("demand" in f for f in forces)
        if demand_only and not fixed_regime:
            note = ("<br><i style='color:#888;'>Under a float, a pure demand shock is fully crowded "
                    "out by the exchange rate — output and inflation are unchanged.</i>")
        elif demand_only:
            note = ("<br><i style='color:#888;'>Under a fixed peg, fiscal/demand policy is effective — "
                    "output moves on impact before real-exchange-rate adjustment crowds it out.</i>")
        else:
            note = (f"<br><i style='color:#888;'>New long-run inflation π* = {pi_eq:.2f} "
                    f"(foreign inflation πᵃ = {pi_foreign:.2f}).</i>")
        text_to_show = f"""
<div style="font-size:17px; font-weight:700; color:#222;">Open-Economy Shock 🌍</div>
<div style="font-size:13px; color:gray; margin-top:4px;"><b>{' + '.join(forces)}</b>{note}</div>"""

# ―――― Continue: advance from short_term_paused to adjusting ――――――――――――――――
if continue_clicked and phase == "short_term_paused":
    st.session_state.oe_pi_prev = pi_0 + gamma * (Y_shock - Ybar) / Ybar + eta
    st.session_state.oe_phase = "adjusting"
    st.rerun()

# ―――― Play: initialize period 0 and period 1 ――――――――――――――――
if play_clicked and phase == "idle":
    st.session_state.oe_phase = "short_term_paused"
    st.session_state.oe_pi_prev = pi_0
    st.session_state.oe_iter_counter = 2
    df = pd.DataFrame(columns=["Iteration", "Output", "Inflation", "RealFX"])
    df.loc[0] = [0, Ybar, PI_BASELINE, WR_BASELINE]   # period 0: pre-shock equilibrium
    df.loc[1] = [1, Y_shock, pi_0, wr_shock]           # period 1: short-run jump
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
    sAD_slope, sAD_int = -LP_BASE / (LI_BASE * Ybar), (RA_BASE - RP_BASE + LP_BASE) / LI_BASE
    sIA, sY = PIA_BASE, Ybar
else:
    sIS_slope, sIS_int = IS_slope, IS_intercept_shock
    sMP_slope, sMP_int = MP_slope, MP_intercept_shock
    sFX = r_foreign
    sAD_slope, sAD_int = AD_slope, AD_intercept_sr   # short-run (shocked) AD
    sIA, sY = pi_0, Y_shock

# ―――― Tabs ――――――――――――――――
tab1, tab2 = st.tabs(["📊 Model", "📖 Theory"])

with tab2:
    #st.markdown(MARKDOWN_THEORY)
    st.info('To be added soon')

with tab1:
    cols = st.columns([1.7, 1])

    # ―――― r–Y diagram ――――――――――――――――
    r_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="r - interest rate")
    h.add_line_to_plot(r_Y_fig, sIS_slope, sIS_int, x_lo, x_hi,
                       name=STIS_name, color=STIS_color, line_width=STIS_lw)
    h.add_line_to_plot(r_Y_fig, sMP_slope, sMP_int, x_lo, x_hi,
                       name=STMP_name, color=STMP_color, line_width=STMP_lw)
    h.add_line_to_plot(r_Y_fig, 0, sFX, x_lo, x_hi, name='FX', color="#E45756")

    if phase != "idle":
        h.add_line_to_plot(r_Y_fig, IS_slope, IS_intercept_cur, x_lo, x_hi,
                           name="LTIS", color="#4C78A8", line_width=c.thin_line_width)
        h.add_line_to_plot(r_Y_fig, MP_slope, MP_intercept_cur, x_lo, x_hi,
                           name="LTMP", color="#F58518", line_width=c.thin_line_width)
        h.add_vertical_line(r_Y_fig, Y_cur, y_max=r_cur,
                            name=f"Y ({Y_cur:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(r_Y_fig, sY, y_max=sFX,
                            name=f"Y ({sY:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')

    h.add_vertical_line(r_Y_fig, Ybar, name=f'Ȳ ({Ybar})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(r_Y_fig, column_to_plot=cols[0])

    output_gap = Y_cur - Ybar

    # ―――― π–Y diagram ――――――――――――――――
    pi_Y_fig = h.create_linear_plot(x_label="Y - Output", y_label="𝜋 - inflation")
    h.add_line_to_plot(pi_Y_fig, 0, sIA, x_lo, x_hi,
                       name=STIA_name, color=STIA_color, line_width=STIA_lw)
    h.add_line_to_plot(pi_Y_fig, sAD_slope, sAD_int, x_lo, x_hi, name='AD', color="#B279A2")

    if phase != "idle":
        h.add_line_to_plot(pi_Y_fig, 0, pi_cur, x_lo, x_hi,
                           name="LTIA", color="#54A24B", line_width=c.thin_line_width)
        h.add_vertical_line(pi_Y_fig, Y_cur, y_max=pi_cur,
                            name=f"Y ({Y_cur:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')
    else:
        h.add_vertical_line(pi_Y_fig, sY, y_max=sIA,
                            name=f"Y ({sY:.2f})", name_position='bottom', color='#B0B0B0', dash='dot')

    # PPP-curve: horizontal at foreign inflation πᵃ (the long-run anchor). Labelled
    # on the left so it doesn't collide with the IA label on the right.
    h.add_line_to_plot(pi_Y_fig, 0, pi_foreign, x_lo, x_hi, dash='dash',
                       name=f"PPP ({pi_foreign:.1f})", color="#999999", line_width=c.thin_line_width,
                       label_position='left')
    h.add_vertical_line(pi_Y_fig, Ybar, name=f'Ȳ ({Ybar})', color='#555555', dash='8px,5px')
    h.show_plotly_fig(pi_Y_fig, column_to_plot=cols[0])

    # ―――― Advanced: equation display ――――――――――――――――
    if level == 'Advanced':
        text_to_show = f"""
            <b style="color:#4C78A8;">IS:</b> Y = {omega:.1f} − {phi:.1f}·r + {psi:.1f}·wʳ<br>
            <b style="color:#F58518;">MP:</b> r = {MP_slope:.2f}·Y + {MP_intercept_cur:.2f}<br>
            <b style="color:#E45756;">FX:</b> r = rᵃ = {r_foreign:.2f}<br>
            <b style="color:#B279A2;">AD:</b> 𝜋 = {AD_slope:.2f}·Y + {AD_intercept_sr:.2f}<br>
            <b style="color:#54A24B;">IA:</b> 𝜋 = {pi_0:.2f}<br>
            <hr style="margin:4px 0; border:none; border-top:1px solid #ddd;">
            <b style="color:black;">π* (LR eq.):</b> {pi_eq:.2f} &nbsp; <span style="color:gray;">(πᵃ = {pi_foreign:.1f})</span><br>
            <b style="color:black;">Output gap (Y − Ȳ):</b> {output_gap:.2f}<br>
            <b style="color:black;">Real exchange rate wʳ:</b> {wr_cur:.2f}
        """

    # ―――― Right column ――――――――――――――――
    with cols[1].container(border=True):
        if not convergence_ok:
            st.warning("⚠️ These parameters may not converge. Try reducing γ.")

        if monetary_neutralised:
            st.info("🏛️ **Fixed peg, no sterilization:** monetary policy is powerless — reserve "
                    "flows tie r to rᵃ, so the change in r' has no effect.")

        if fiscal_shock != 0:
            if fixed_regime:
                st.info("🏛️ **Fixed peg — fiscal policy is effective:** output jumps on impact, then "
                        "real appreciation (wʳ ↓) crowds it out and inflation returns to πᵃ.")
            else:
                st.info("🏛️ **Float — fiscal policy is crowded out:** the currency appreciates (wʳ ↓) "
                        "and net exports fall, so output and inflation are unchanged.")

        st.markdown(text_to_show, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:13px; margin-top:6px;'>{regime_outcome}</div>",
                    unsafe_allow_html=True)

        lc1, lc2 = st.columns([1.2, 0.8])
        with lc1:
            st.button("🔖 Remember this run", on_click=lock_run, width="stretch",
                      help="Save this run in gray so you can compare it with the next one",
                      disabled=phase != "done")
        with lc2:
            if st.session_state.oe_locked_df is not None:
                st.button("✕ Forget", on_click=clear_lock, width="stretch")

        df_now = st.session_state.oe_iteration_df
        df_lock = st.session_state.oe_locked_df

        def _series_chart(y_col, y_title, label, ref_value, ref_label):
            fig = px.scatter(df_now, x="Iteration", y=y_col)
            fig.update_traces(mode="lines+markers", marker=dict(size=5))
            if df_lock is not None:
                fig.add_scatter(x=df_lock["Iteration"], y=df_lock[y_col], mode="lines",
                                line=dict(color="#BBBBBB", dash="dot"), name="Previous run")
            if not df_now.empty:
                last = df_now.iloc[-1]
                fig.add_annotation(x=last["Iteration"], y=last[y_col],
                                   text=f"{label}={last[y_col]:.2f}", showarrow=False,
                                   xanchor="left", yshift=12)
            fig.update_layout(xaxis_title="Period", yaxis_title=y_title, showlegend=False)
            h.add_line_to_plot(fig, 0, ref_value, 0, iteration_count,
                               name=f"{ref_label} ({ref_value:.2f})", line_width=2, color="#999999", dash='dot')
            h.show_plotly_fig(fig, height=190)

        _series_chart("Output",    "Y - Output",           "Y",  Ybar,        "Ȳ")
        _series_chart("Inflation", "𝜋 - inflation",        "𝜋",  pi_eq,       "𝜋*")
        _series_chart("RealFX",    "wʳ - real exch. rate", "wʳ", WR_BASELINE, "wʳ₀")

    # ―――― Animation step ――――――――――――――――
    if phase == "adjusting":
        new_row_idx = len(st.session_state.oe_iteration_df)
        st.session_state.oe_iteration_df.loc[new_row_idx] = [
            st.session_state.oe_iter_counter, Y_cur, pi_cur, wr_cur
        ]
        st.session_state.oe_pi_prev = pi_cur + gamma * (Y_cur - Ybar) / Ybar + eta
        st.session_state.oe_iter_counter += 1

        if st.session_state.oe_iter_counter >= iteration_count:
            st.session_state.oe_phase = "done"

        time.sleep(sim_speed)
        st.rerun()
