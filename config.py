# Letters to copy: 𝜓 ç 𝜔


markdown_text = r"""
## Model Overview

This model represents a closed economy through four curves that jointly determine output $Y$ and inflation $\pi$ in each period. The economy begins in long-run equilibrium, is disturbed by a shock in period 1, and then returns to equilibrium over the following periods.

**Units.** Output is an **index with potential $\bar{Y} = 100$**, so one unit of $Y$ is one
per cent of potential output and the gap $\tilde{Y} = 100\,(Y-\bar{Y})/\bar{Y}$ is in
percentage points — the same units as $r$ and $\pi$. Every coefficient can then be read
directly: $\varphi = 1$ means *a 1 pp rise in the real rate costs 1 % of potential output*,
and $\gamma = 0.4$ means *a 1 % output gap moves next period's inflation by 0.4 pp*. The
economy starts at $Y = 100$, $\pi = 2\%$, $r = 2\%$.

---

### Curve Definitions

**IS curve** — *Investment–Savings*

Describes the goods market: output $Y$ is a decreasing function of the real interest rate $r$. Higher rates discourage investment and consumption, and output falls as a result.
$$
Y = \omega - \phi \, r \qquad \phi > 0
$$

| Parameter | Meaning | Default |
|-----------|---------|---------|
| $\omega$ | Autonomous demand (shifts IS right or left); one unit = 1 % of potential output | 102 |
| $\phi$ | Output cost of a 1 pp rise in the real rate, in % of potential | 1.0 |

---

**MP curve** — *Monetary Policy*

The central bank sets the real interest rate in response to the output gap $\tilde{Y} = 100\,\frac{Y - \bar{Y}}{\bar{Y}}$ (in percentage points) and to inflation $\pi$. Higher output or higher inflation leads to a higher rate.
$$
r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \qquad r' > 0,\ \lambda_P \ge 0,\ \lambda_I \ge 0
$$

| Parameter | Meaning | Default |
|-----------|---------|---------|
| $r'$ | Intercept of the rule — *not* the rate itself; with the defaults it leaves $r = 2\%$ | 0.5 |
| $\lambda_P$ | Response to the output gap, in pp of real rate per point of gap | 0.5 |
| $\lambda_I$ | Response to inflation — the **real** rate response, so the nominal one is $1+\lambda_I = 1.75$ | 0.75 |

---

**IA curve** — *Inflation Adjustment*

The IA curve records the prevailing rate of inflation, which reflects inflation expectations and price stickiness. In the **short run** (period 1) it is a horizontal line at the post-shock inflation level $\pi_0$, since prices do not adjust immediately to the new conditions:
$$
\pi_t = \pi_0 \qquad \text{(short run, } t = 1\text{)}
$$

Beyond the short run the IA curve shifts in each period according to the output gap and to any persistent exogenous price shock. When output exceeds potential, firms raise prices and inflation rises; when output falls short of potential, inflation declines:
$$
\boxed{\pi_{t+1} = \pi_t + \gamma \cdot \tilde{Y}_t + \eta = \pi_t + \gamma \cdot 100\,\frac{Y_t - \bar{Y}}{\bar{Y}} + \eta}
$$

| Parameter | Meaning |
|-----------|---------|
| $\gamma$ | Speed of inflation adjustment (a higher $\gamma$ gives faster convergence) |
| $\tilde{Y}_t$ | Output gap in period $t$ |
| $\eta$ | Exogenous price shock — a price change not driven by producer or worker behaviour (for example a crop failure, a raw material shortage, or a change in VAT). Applied in every period. |

The IA curve shifts **upward** when $Y_t > \bar{Y}$ or $\eta > 0$, and **downward** when $Y_t < \bar{Y}$ or $\eta < 0$. It comes to rest only when both $Y_t = \bar{Y}$ and $\eta = 0$, and this condition defines the long-run equilibrium.

**Phillips Curve** — *IA with the current output gap*

The IA equation is evaluated at the *previous* period's output gap, so by the time the diagram is drawn the inflation rate for the period is already determined and IA appears as a **horizontal line**. The Phillips curve states the same relationship as a condition: if current output were $Y$, what would inflation be in the next period?

$$
\pi_{t+1} = \pi_t + \gamma \cdot 100\,\frac{Y - \bar{Y}}{\bar{Y}}
$$

Rearranged as a function of $Y$:

$$
\pi_{t+1} = \underbrace{\frac{100\,\gamma}{\bar{Y}}}_{\text{slope}} \cdot Y + \underbrace{(\pi_t - 100\,\gamma)}_{\text{intercept}}
$$

This is an **upward-sloping line** in $\pi$–$Y$ space, anchored at $(\bar{Y},\, \pi_t)$: when output equals potential there is no gap, and inflation is unchanged. The IA curve is the Phillips curve evaluated at last period's $Y$ and then held fixed, so the horizontal line marks the value the Phillips curve produced one period earlier.

Displaying the Phillips curve alongside IA shows both perspectives at once: the sloped curve gives the full relationship between current output and future inflation, while the horizontal IA marks the single point on that curve which the economy actually reached.

---

**AD curve** — *Aggregate Demand*

Obtained by combining the IS and MP curves, the AD curve expresses inflation as a function of output. It describes how monetary policy transmits demand conditions into inflationary pressure, and it has a **negative slope**: higher output is associated with lower inflation, because the central bank raises rates to cool demand.

---

### Coefficient Derivation

**IS** (solved for $r$):
$$
Y = \omega - \phi r \implies
r = \underbrace{\frac{\omega}{\phi}}_{\text{intercept}}
+ \underbrace{\left(-\frac{1}{\phi}\right)}_{\text{slope}} \cdot Y
$$

**MP** (expanded in $Y$):
$$
r = r' + \lambda_P \cdot 100\,\frac{Y - \bar{Y}}{\bar{Y}} + \lambda_I \pi
= \underbrace{\left(r' - \lambda_P + \lambda_I \pi\right)}_{\text{intercept}}
+ \underbrace{\left(\frac{100\,\lambda_P}{\bar{Y}}\right)}_{\text{slope}} \cdot Y
$$

**AD** (set $r_{IS} = r_{MP}$ and solve for $\pi$):
$$
\frac{\omega}{\phi} - \frac{1}{\phi} Y = r' - 100\lambda_P + \lambda_I \pi + \frac{100\lambda_P}{\bar{Y}} Y \\[6pt]
\lambda_I \pi = \frac{\omega}{\phi} - \frac{1}{\phi} Y - r' + 100\lambda_P - \frac{100\lambda_P}{\bar{Y}} Y \\[6pt]
\pi = \underbrace{\left(\frac{\omega}{\phi\lambda_I} + \frac{100\lambda_P}{\lambda_I} - \frac{r'}{\lambda_I}\right)}_{\text{intercept}}
+ \underbrace{\left(- \frac{1}{\phi\lambda_I} - \frac{100\lambda_P}{\lambda_I\bar{Y}}\right)}_{\text{slope}} \cdot Y
$$

---

### Long-Run Equilibrium

The economy returns to equilibrium when $\pi_{t+1} = \pi_t$, which requires $Y_t = \bar{Y}$. Long-run inflation $\pi^*$ is therefore the value at which the AD curve crosses the potential output line $Y = \bar{Y}$:
$$
\pi^* = \frac{\omega}{\phi\lambda_I} + \frac{100\lambda_P}{\lambda_I} - \frac{r'}{\lambda_I}
+ \left(- \frac{1}{\phi\lambda_I} - \frac{100\lambda_P}{\lambda_I\bar{Y}}\right)\bar{Y}
$$
"""


# r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \text{ with } r' > 0, \lambda_P \ge 0, \lambda_I \ge 0.

tabs_options = ['📊 Time Model', '🏠 Home', '🧾 Glossary']  #'📊 Data'

standard_line_width = 3
thin_line_width = 2

Y_potential = 100
speed = 0.1

iteration_count = 40




neg_inflation_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Upward Inflation Shock 📈
</div>

<div style="font-size:13px; color:gray;">
    Typically an external supply shock — a sudden increase in production costs or in prices, as in the oil crisis of the 1970s. Inflation rises while output falls below potential.
    <br><br>
    In the short run the central bank generally raises interest rates to contain inflation, which makes borrowing more expensive and reduces demand further. Over time the weaker demand brings inflation down, and output returns gradually to its potential level.
</div>
"""

pos_monetary_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Expansionary Monetary Shock 🏦
</div>

<div style="font-size:13px; color:gray;">
    An unexpected loosening of monetary policy: the central bank lowers the nominal interest rate. Borrowing becomes cheaper, and in the short run the real interest rate falls as well. Investment and consumption increase, and output rises above potential.
    <br><br>
    In the long run the higher demand raises inflation, which gradually pushes the real interest rate back up and returns output to its potential level.
</div>
"""

pos_demand_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Expansionary Demand Shock 🛒
</div>

<div style="font-size:13px; color:gray;">
    A sudden increase in aggregate demand, arising from higher consumption, investment, government spending, or exports.
    <br><br>
    In the short run output rises above potential, and the stronger demand raises inflation. The central bank responds by increasing interest rates, which slows economic activity and gradually returns output to its potential level.
</div>
"""

pos_inflation_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Downward Inflation Shock 📉
</div>

<div style="font-size:13px; color:gray;">
    A favourable supply-side development — falling commodity prices, an improvement in technology, or the easing of supply-chain pressures — moves inflation below its equilibrium level while output rises above potential.
    <br><br>
    With inflation below target, the central bank generally lowers interest rates to support demand. The recovery in demand then returns inflation to its equilibrium level.
</div>
"""

neg_monetary_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Contractionary Monetary Shock 🏦
</div>

<div style="font-size:13px; color:gray;">
    An unexpected tightening of monetary policy: the central bank raises the nominal interest rate. Borrowing becomes more expensive, and in the short run the real interest rate rises as well. Investment and consumption fall, and output drops below potential.
    <br><br>
    In the long run the weaker demand reduces inflation, which gradually lowers the real interest rate again and returns output to its potential level.
</div>
"""

neg_demand_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Contractionary Demand Shock 🛒
</div>

<div style="font-size:13px; color:gray;">
    A sudden fall in aggregate demand, arising from weaker consumer confidence, reduced investment, fiscal consolidation, or a decline in exports.
    <br><br>
    In the short run output falls below potential, and the weaker demand lowers inflation. The central bank responds by cutting interest rates, which stimulates economic activity and gradually returns output to its potential level.
</div>
"""

placeholder_shock = """
<div style="
    height: 140px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    font-size: 17px;
    color: #999999;
">
    Please Select a Shock
</div>
"""

# ---------- Fiscal Policy (omega) ----------
# NB: ω is autonomous DEMAND in the IS curve — these are demand-side shifts, not
# supply shocks. The thresholds that select these texts live in closed_economy.py
# (OMEGA_HI / OMEGA_LO), so no numeric range is quoted here.
omega_text_exp = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Expansionary Demand Shock (↑ω) 🏛️
</div>

<div style="font-size:13px; color:gray;">
    An increase in autonomous demand — higher public spending, lower taxes, or stronger private consumption and investment. The IS-curve shifts right, so output rises above potential and inflation follows.
</div>
"""

omega_text_res = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Contractionary Demand Shock (↓ω) 🏛️
</div>

<div style="font-size:13px; color:gray;">
    A fall in autonomous demand — lower public spending, higher taxes, or weaker private consumption and investment. The IS-curve shifts left, so output falls below potential and inflation follows it down.
</div>
"""


# ---------- Monetary Policy (r) ----------
r_text_con = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Contractionary Monetary Policy (↑r') 💰
</div>

<div style="font-size:13px; color:gray;">
    The central bank raises interest rates and tightens financial conditions.
    Borrowing and investment decline, which slows aggregate demand and inflation.
</div>
"""

r_text_exp = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Expansionary Monetary Policy (↓r') 💰
</div>

<div style="font-size:13px; color:gray;">
    The central bank lowers interest rates and increases liquidity in the economy.
    Credit conditions improve, which stimulates consumption, investment, and output.
</div>
"""


# ---------- Inflation Shock (pi) ----------
pi_text_inf = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Upward Inflation Shock (↑π₀) 📈
</div>

<div style="font-size:13px; color:gray;">
    Inflation starts above its long-run equilibrium, following supply disruptions, rising
    production costs, or higher commodity prices. Inflation accelerates and real purchasing
    power declines. The economy returns to equilibrium as the central bank tightens policy.
</div>
"""

pi_text_def = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Downward Inflation Shock (↓π₀) 📉
</div>

<div style="font-size:13px; color:gray;">
    Inflation starts below its long-run equilibrium, following weak demand or falling costs.
    Economic activity may weaken as firms reduce production and investment.
    The economy returns to equilibrium as monetary policy is eased.
</div>
"""

empty_placeholder_moderate_level_shock = """
<div style="
    height: 140px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    font-size: 17px;
    color: #999999;
">
    Use the sliders to bring the system out of equilibrium
</div>
"""

# ―――― Open-economy consensus model ――――――――――――――――
# ―――― Easy-mode shock panel ――――――――――――――――
# ONE description per (shock family, regime), assembled by oe_shock_panel(). The
# regime is chosen in the sidebar, so the panel only ever tells the story of the
# regime actually running — the info/warning boxes never repeat it.
#
# Direction words are substituted rather than written out twice, so an expansion
# and its mirror image cannot disagree about a sign (a contraction used to be
# described as an appreciation because both shared one hand-written string).

OE_SHOCK_META = {
    # shock name                      → (family, direction, emoji)
    'Expansionary Fiscal Shock':      ('fiscal', +1, '🏛️'),
    'Contractionary Fiscal Shock':    ('fiscal', -1, '🏛️'),
    'Expansionary Monetary Shock':    ('monetary', +1, '🏦'),
    'Contractionary Monetary Shock':  ('monetary', -1, '🏦'),
    'Rising Foreign Interest Rate':   ('foreign', +1, '🌍'),
    'Falling Foreign Interest Rate':  ('foreign', -1, '🌍'),
    'Imported Inflation Shock':       ('imported', +1, '📈'),
    'Imported Deflation Shock':       ('imported', -1, '📉'),
}

OE_REGIME_LABEL = {
    'Flexible': '🌊 Flexible',
    'Fixed – no sterilization': '🔒 Fixed – no sterilization',
    'Fixed – with sterilization': '🛡️ Fixed – with sterilization',
}

# What the shock is, before any regime enters the picture.
OE_LEAD = {
    'fiscal': "The government spends {more_less}, which shifts the IS-curve to the {right_left} (ω {up_down}).",
    'monetary': "The central bank takes a {looser_tighter} stance ({down_up} r').",
    'foreign': "The rest of the world moves to a {higher_lower} interest rate ({up_down} rᵃ).",
    'imported': "Import prices {jump_drop} once and feed straight into domestic prices — the one shock "
                "that moves inflation without an output gap first.",
}

# What the chosen regime then does with it.
OE_STORY = {
    ('fiscal', 'float'):
        "The change in demand <i>would</i> push the interest rate {higher_lower}, so money {capital_flow} "
        "and the currency {strengthens_weakens} (wʳ {down_up}) instead. Net exports {fall_rise} by exactly "
        "what the government {added_removed}, so <b>output and inflation never move</b> — the exchange rate "
        "cancels fiscal policy out.",
    ('fiscal', 'hard'):
        "The exchange rate cannot move, so the whole impulse lands on output: it {rises_falls} {above_below} "
        "potential, the strongest fiscal effect of the three regimes. From there it feeds on itself. "
        "Domestic prices {outrun_lag} foreign ones, and since the peg ties the nominal interest rate to the "
        "world one, the real rate is r = rᵃ + (πᵃ − 𝜋): it moves {down_up}, the wrong way, and pushes demand "
        "further {above_below} potential. Competitiveness {worsens_improves} (wʳ {down_up}) and does pull "
        "back, but only through the slow drift of the price level, so it never catches up.",
    ('fiscal', 'ster'):
        "The exchange rate still cannot move, so output {rises_falls} — but the bank moves its own interest "
        "rate against the shock, so the effect is smaller than without sterilization. Trade then closes the "
        "gap: domestic prices {outrun_lag} foreign ones (wʳ {down_up}) and output returns to potential.",

    ('monetary', 'float'):
        "Money {capital_flow_rev}, the currency {weakens_strengthens} (wʳ {up_down}) and net "
        "exports {rise_fall}, so output {rises_falls} {above_below} potential. As the gap closes, inflation "
        "settles at a permanently {higher_lower} level and the currency keeps sliding to make up the "
        "difference with the rest of the world.",
    ('monetary', 'hard'):
        "<b>This does nothing here.</b> Holding the exchange rate forces the bank to buy and sell foreign "
        "currency, and that pulls the domestic interest rate straight back to the world rate. Output and "
        "inflation stay exactly where they were.",
    ('monetary', 'ster'):
        "Because the bank offsets those currency flows it keeps its own interest rate, so output "
        "{rises_falls} — but by less than under a flexible rate, since the exchange rate cannot help. "
        "Inflation ends back at the world rate: a country holding its exchange rate fixed cannot keep an "
        "inflation rate of its own.",

    ('foreign', 'float'):
        "Money {chases_return}, the currency {weakens_strengthens} "
        "(wʳ {up_down}) and exports {rise_fall}, so output {rises_falls} {above_below} potential. The "
        "domestic interest rate follows the world rate, and inflation settles {higher_lower} than before.",
    ('foreign', 'hard'):
        "With the exchange rate fixed nothing softens the blow: the {higher_lower} world rate is imported "
        "directly, borrowing becomes {dearer_cheaper} and output {falls_rises} {below_above} potential — "
        "the opposite sign to a flexible rate. It then gets worse rather than better: domestic prices "
        "{lag_outrun} foreign ones, so the real rate r = rᵃ + (πᵃ − 𝜋) moves {up_down} again and pushes "
        "output further {below_above} potential. Competitiveness {improves_worsens} (wʳ {up_down}) is the "
        "only force pulling back, and it works far too slowly to.",
    ('foreign', 'ster'):
        "The bank offsets the currency flows, so the foreign rate never reaches the economy — <b>output "
        "and inflation do not move at all</b>.",

    ('imported', 'float'):
        "Inflation starts {above_below} the world rate. With the domestic interest rate tied to the world "
        "rate, that leaves output {below_above} potential, and the currency {strengthens_weakens} "
        "(wʳ {down_up}) at the same time. The output gap then pulls inflation back to the world rate.",
    ('imported', 'hard'):
        "Inflation starts {above_below} the world rate. The peg ties the nominal interest rate to the "
        "world one, so the real rate r = rᵃ + (πᵃ − 𝜋) moves {down_up} and output lands {above_below} "
        "potential — the opposite way round from the other two regimes. The gap then pushes inflation "
        "further {up_down}, which moves the real rate {down_up} again, and the two feed each other. "
        "Domestic prices are {price_gap} foreign ones, so the currency becomes {stronger_weaker} in real "
        "terms (wʳ {down_up}): the one force pulling back, and much too slow to.",
    ('imported', 'ster'):
        "Inflation starts {above_below} the world rate, and the bank's own interest-rate response leaves "
        "output {below_above} potential. The output gap then brings inflation back to the world rate, "
        "while the real exchange rate drifts {down_up_word} as prices come back into line.",
}


# Medium level: one line per KIND of setting the user has changed, for the regime
# actually selected. Entries that a pop-up already covers (monetary under a plain
# fixed rate, the foreign rate when flows are offset) are deliberately absent, so
# nothing is ever said twice.
OE_MEDIUM_NOTE = {
    ('demand', 'float'): "The exchange rate cancels a change in demand out completely — nothing on "
                         "the charts moves except wʳ.",
    ('demand', 'hard'): "With the exchange rate held fixed, a change in demand has its full effect on "
                        "output — and the interest rate then moves the wrong way, so the gap widens "
                        "instead of closing.",
    ('demand', 'ster'): "A change in demand moves output, damped by the bank's own interest-rate response.",
    ('monetary', 'float'): "An interest-rate change moves output now, and inflation permanently.",
    ('monetary', 'ster'): "The bank keeps its own interest rate, so it still moves output — by less than "
                          "under a flexible rate.",
    ('foreign', 'float'): "A change in the world rate reaches the economy through the currency, and "
                          "output moves with it.",
    ('foreign', 'hard'): "The world rate is imported directly, so output moves the opposite way to a "
                         "flexible rate — and the gap then widens on its own.",
    ('imported', 'hard'): "With the nominal rate tied to the world, faster inflation means a LOWER real "
                          "rate, so the price shock pushes output the opposite way to the other regimes.",
    ('imported', 'float'): "The jump in import prices lands on inflation first; output then moves to bring "
                           "it back.",
}
OE_MEDIUM_NOTE[('imported', 'hard')] = OE_MEDIUM_NOTE[('imported', 'float')]
OE_MEDIUM_NOTE[('imported', 'ster')] = OE_MEDIUM_NOTE[('imported', 'float')]


# What the user will actually SEE, verified against the simulation rather than
# against the economics. The two differ often enough to matter: under a float the
# IS-curve shifts and the appreciation pushes it back inside the same period, so
# the diagram shows no movement at all, and a description that stops at "spending
# rises" reads as flatly wrong next to a flat Y line. Where a line refuses to move,
# say so and say why.
OE_CHART = {
    ('fiscal', 'float'):
        "<b>nothing moves except wʳ.</b> IS does shift {right_left}, but the currency "
        "{strengthens_weakens} in the same period and pushes it straight back, so the diagram only "
        "ever shows the net position. Y, π and r stay exactly where they were.",
    ('fiscal', 'hard'):
        "IS shifts {right_left} and Y jumps in period 1, with r still on the red FX line — inflation "
        "has not moved yet. From period 2 the FX <b>line itself</b> slides {down_up} as inflation leaves "
        "the world rate, r rides it down, and Y gets further from Ȳ every period until the run stops. "
        "wʳ drifts {down_up} by roughly the inflation gap each period, which is all the "
        "pull-back there is.",
    ('fiscal', 'ster'):
        "IS shifts {right_left} and Y jumps, by less than without sterilization. r leaves the red "
        "FX line — the only regime where it does. wʳ is flat on impact and drifts {down_up} later.",

    ('monetary', 'float'):
        "MP shifts {down_up} and Y jumps, but <b>r stays flat at rᵃ</b>: the bank's stance moved, "
        "the market rate cannot. wʳ does the moving instead — it jumps {up_down} on impact and then "
        "comes back.",
    ('monetary', 'hard'):
        "<b>nothing moves at all</b> — not IS, not MP, not one of the four lines below. The change "
        "in r' is undone before it ever reaches the diagram.",
    ('monetary', 'ster'):
        "MP shifts {down_up} and the point slides along IS, so Y {rises_falls} and r moves away from "
        "the red FX line. IS itself stays put, and wʳ is flat until inflation leaves the world rate.",

    ('foreign', 'float'):
        "the red FX line shifts {up_down} and r follows it. IS moves with the currency, Y jumps, and "
        "wʳ settles {higher_lower} than it began.",
    ('foreign', 'hard'):
        "the red FX line shifts {up_down} and r follows it, but <b>IS does not move</b> — the point "
        "just slides along it to the {left_right}, which is why Y goes the opposite way to a "
        "flexible rate. The FX line then keeps moving the same way as inflation drifts, so the point "
        "keeps sliding and Y does not come back. wʳ inches {up_down} against it.",
    ('foreign', 'ster'):
        "<b>only the red FX line moves.</b> Y, π and wʳ stay flat and r stays where the bank put it. "
        "The gap you can see between r and the FX line is the flow the bank is absorbing.",

    ('imported', 'float'):
        "the IA line jumps {up_down} while AD stays where it is, so output slides along AD to "
        "{below_above} potential. wʳ jumps {down_up} with it and r stays flat at rᵃ; both then work "
        "their way back.",
    ('imported', 'hard'):
        "the IA line jumps {up_down} and the red FX line jumps {down_up} with it — that is the peg "
        "leaving r at rᵃ + (πᵃ − 𝜋) — so output lands {above_below} potential. Both lines then keep "
        "going the same way period after period, with IS pulled {left_right} a little by the "
        "{stronger_weaker} currency.",
    ('imported', 'ster'):
        "the IA line jumps {up_down} and output lands {below_above} potential, but <b>IS does not "
        "move and wʳ is flat on impact</b> — with the flows sterilized the exchange rate only drifts "
        "later. r moves with the bank's own rule.",
}


def _direction_words(up):
    """Every word that flips with the sign of the shock, in one place."""
    def p(a, b):
        return a if up else b
    return dict(
        rises_falls=p('rises', 'falls'), falls_rises=p('falls', 'rises'),
        rise_fall=p('rise', 'fall'), fall_rise=p('fall', 'rise'),
        above_below=p('above', 'below'), below_above=p('below', 'above'),
        up_down=p('↑', '↓'), down_up=p('↓', '↑'),
        more_less=p('more', 'less'), higher_lower=p('higher', 'lower'),
        right_left=p('right', 'left'), left_right=p('left', 'right'),
        added_removed=p('added', 'took away'),
        capital_flow=p('flows in from abroad', 'flows out to other countries'),
        capital_flow_rev=p('flows out to other countries', 'flows in from abroad'),
        chases_return=p('leaves in search of the better return abroad',
                        'flows in, because the return at home is now the better one'),
        strengthens_weakens=p('strengthens', 'weakens'), weakens_strengthens=p('weakens', 'strengthens'),
        stronger_weaker=p('stronger', 'weaker'),
        looser_tighter=p('looser', 'tighter'), dearer_cheaper=p('dearer', 'cheaper'),
        outrun_lag=p('outrun', 'lag behind'), lag_outrun=p('lag behind', 'outrun'),
        worsens_improves=p('worsens', 'improves'), improves_worsens=p('improves', 'worsens'),
        price_gap=p('rising faster than', 'rising more slowly than'),
        down_up_word=p('down', 'up'), jump_drop=p('jump', 'drop'),
    )


REGIME_KEY = {'Flexible': 'float', 'Fixed – no sterilization': 'hard',
              'Fixed – with sterilization': 'ster'}


def oe_panel(title, regime, body, emoji=''):
    """The one shape every open-economy description uses: what was selected, which
    regime it is running in, then the explanation."""
    return f"""
<div style="text-align:center; font-size:17px; font-weight:700;">{title} {emoji}</div>
<div style="text-align:center; font-size:12px; color:#999; margin:2px 0 8px 0;">{OE_REGIME_LABEL[regime]}</div>
<div style="font-size:13px; color:gray;">{body}</div>"""


def oe_shock_panel(shock, regime):
    """Easy-mode description of `shock` as it plays out under `regime`."""
    if shock not in OE_SHOCK_META:
        return placeholder_shock
    family, direction, emoji = OE_SHOCK_META[shock]
    words = _direction_words(direction > 0)
    regime_key = REGIME_KEY[regime]
    lead = OE_LEAD[family].format(**words)
    story = OE_STORY[(family, regime_key)].format(**words)
    charts = OE_CHART[(family, regime_key)].format(**words)
    body = (f"{lead}<br><br>{story}"
            f"<div style='margin-top:10px; padding-top:8px; border-top:1px solid #eee;'>"
            f"<b>On the charts:</b> {charts}</div>")
    return oe_panel(shock, regime, body, emoji)


THEORY_INTRO = r"""
## The Open Economy

A closed economy trades with no one. Opening it adds two channels: **goods** can be sold
abroad and bought from abroad, and **money** can cross the border in search of a better
interest rate. Almost everything below follows from those two.

**Units.** Output is an **index with potential $\bar{Y} = 100$**, so one unit of $Y$ is one
per cent of potential and the gap $\tilde{Y} = 100\,(Y-\bar{Y})/\bar{Y}$ is in percentage
points, like $r$ and $\pi$. The real exchange rate is an index too, $w^r = 100$ at the
start, so $w^r = 106$ means the currency is 6 % weaker in real terms. The economy starts at
$Y = 100$, $\pi = \pi^a = 2\%$, $r = r^a = 2\%$.

---

### The real exchange rate

The new variable is the real exchange rate $w^r$ — how expensive foreign goods are
compared with domestic ones.

| If $w^r$ **rises** (say 100 → 106) | If $w^r$ **falls** (say 100 → 94) |
|---|---|
| the currency is **weaker** (depreciation) | the currency is **stronger** (appreciation) |
| domestic goods look cheap abroad → exports rise | domestic goods look dear abroad → exports fall |
| demand for domestic output **rises** | demand for domestic output **falls** |

Two rates hide inside that one symbol. The **nominal** rate is the quoted one, and a
central bank can hold it fixed by decree. The **real** rate is that nominal rate adjusted
for prices at home and abroad, and it keeps moving whenever domestic inflation differs
from foreign inflation. A price can be fixed; a price *difference* cannot.

---

### Curve Definitions

**IS curve** — *the goods market*

Output is higher when borrowing is cheap and when the currency is weak.

$$
Y = \omega - \varphi \, r + \psi \, w^r \qquad \varphi, \psi > 0
$$

| Parameter | Meaning | Default |
|-----------|---------|---------|
| $\omega$ | Autonomous demand — **government spending enters here**, so this is the fiscal instrument. One unit = 1 % of potential output | 77 |
| $\varphi$ | Output cost of a 1 pp rise in the real rate, in % of potential | 1.0 |
| $\psi$ | Output gain from a 1 % real depreciation — the net-export channel | 0.25 |

The $\psi w^r$ term is the only addition to the closed-economy IS curve, and it accounts
for most of the difference in behaviour.

---

**MP curve** — *the central bank's rule*

The bank raises the rate when the economy runs hot or inflation climbs.

$$
r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \qquad \tilde{Y} = 100\,\frac{Y - \bar{Y}}{\bar{Y}}
$$

| Parameter | Meaning | Default |
|-----------|---------|---------|
| $r'$ | The bank's stance — a **lower** $r'$ is looser policy. The intercept of the rule, not the rate: with the defaults it leaves $r = 2\%$ | 0.5 |
| $\lambda_P$ | Weight on the output gap, in pp of real rate per point of gap | 0.5 |
| $\lambda_I$ | Weight on inflation — the **real** rate response, so the nominal one is 1.75 | 0.75 |

---

**FX curve** — *capital mobility*

Money chases the highest return, so the domestic rate is pulled towards the world rate.
What counts is the return in one currency, so an expected move in the exchange rate is
part of it:

$$
1 + r = (1 + r^a)\,\frac{w^{r,e}_{+1}}{w^r}
$$

If nobody expects the real exchange rate to move, this is just $r = r^a$ — the flexible
case, and the one the book uses through chapter 4.

Under a **peg** it is not. The nominal rate is held, so $w^r = w\,p^a/p$ is expected to
move with the inflation difference alone, and the parity condition becomes

$$
r = r^a + (\pi^a - \pi)
$$

which is the same statement as $i = i^a$ with $r = i - \pi$: pegging fixes the *nominal*
rate to the world's, so the *real* rate is whatever domestic inflation leaves. Below
$\pi^a$, prices are falling relative to abroad, the foreign currency is appreciating in
real terms, investors have to be paid for that, and the real rate is **higher** than the
world's — in a slump, exactly when it should be lower.

Whether this constraint actually binds is exactly what the exchange-rate regime decides.

---

**IA curve** — *inflation adjustment*

Inflation is fixed within the period and drifts according to whether the economy runs hot
or cold.

$$
\pi_{t+1} = \pi_t + \gamma \tilde{Y}_t + \chi\,(w^r_{t+1} - w^r_t) + \eta
$$

| Parameter | Meaning | Default |
|-----------|---------|---------|
| $\gamma$ | Phillips slope: pp of inflation per point of output gap | 0.4 |
| $\chi$ | How much a move in the exchange rate feeds into prices directly (imports get dearer). $\chi = 0.05$ means a 10 % depreciation adds half a point to inflation | 0 |
| $\eta$ | A price shock applied in every period | 0 |

Two consequences run through everything. Inflation **cannot jump** in the period a shock
arrives, since wages and contracts are already agreed — so output moves first and
inflation follows. And inflation stops moving only once output is back at potential.

---

**AD curve** — *aggregate demand*

Not a separate assumption: it is IS, MP and FX solved together and drawn in $\pi$–$Y$
space. *Which* curves go into it depends on the regime, and so does its slope:

| Regime | AD is | Slope |
|---|---|---|
| Flexible | MP ∩ FX | down, $-\lambda_P/\lambda_I$ |
| Fixed – with sterilization | IS ∩ MP | down, steeper |
| Fixed – no sterilization | IS ∩ FX | **up**, $1/\varphi$ |

The third row is the odd one, and it is the whole character of that regime. With the
Taylor rule gone, higher inflation no longer brings a higher real rate — under a peg it
brings a **lower** one, so demand rises with inflation. An AD that slopes up against a
horizontal IA is a picture of an unstable equilibrium: the economy runs away from
$\bar{Y}$ rather than towards it.

---

### Reading the two diagrams

- **Upper, $r$–$Y$:** IS, MP and the flat FX line. The sideways movement of IS *is* the
  exchange rate doing its work.
- **Lower, $\pi$–$Y$:** IA is horizontal, because today's inflation is already
  determined; AD slopes down in two of the three regimes and up in the third.

A run therefore goes in two stages. The shock lands and the economy moves **sideways**
along IA — output changes, inflation cannot. Then, period by period, the output gap drags
IA up or down and the economy **slides along AD**. Where AD slopes down that walk ends at
$\bar{Y}$; where it slopes up — a peg without sterilization — it goes the other way, and
each period's gap is bigger than the last.

Note also that under a peg the **red FX line moves**, because the parity condition above
depends on inflation. Without sterilization the operating point rides that line; with
sterilization the bank holds its own rate and the vertical gap to the line is the flow of
reserves it is absorbing.

---

### Exchange-rate Regimes

A country would like three things at the same time: a **stable exchange rate**, **free
movement of money** across its border, and a **monetary policy of its own** — an interest
rate it sets for conditions at home, rather than one the rest of the world sets for it. It
can have any two. Never all three.

The three settings in the sidebar are the three ways of choosing. **Sterilization** is the
name for what the third one does: the bank offsets the money flows its defence of the
exchange rate sets off, so that they leave its own interest rate alone.
"""


THEORY_REST = r"""
| | Flexible | Fixed – no sterilization | Fixed – with sterilization |
|---|---|---|---|
| **Gives up** | the stable exchange rate | its own monetary policy | free movement of capital |
| **Fiscal policy** | no effect at all | strongest of the three | works, damped |
| **Monetary policy** | works, permanently | no effect at all | works |
| **Inflation ends at** | its own rate $\pi^*$ | nowhere — it runs away | the world rate $\pi^a$ |
| **Held in place by** | nothing — the currency floats | reserve flows setting the rate | capital controls, once $r \neq r^a$ |

The middle column's second row is not a typo. $\pi^a$ is the only rate at which that
economy could rest, and it is a rest point it moves *away* from: with $r = r^a +
(\pi^a - \pi)$ the real interest rate always pushes the same way as the shock. The trade
channel pushes back — cheaper domestic goods mean a higher $w^r$ and more demand — but it
works through accumulated price differences, a fraction of a percent a period, and never
catches up. That is the book's *worrying policy*: a peg without sterilization leaves the
economy badly exposed to a shock. It is also why inflation differences inside a currency
union widened instead of closing.

Note the third column carefully. Sterilisation is **not** a way of having all three
at once. The bank keeps its interest rate and its exchange rate, but the moment its
rule calls for an $r$ different from $r^a$, capital keeps crossing the border and
reserves drain without limit. That corner has to be held shut with capital controls
in the long run — which is exactly the corner being given up. Reserves buy time; they
do not buy the third objective.

**Why fiscal policy does nothing under a flexible rate.** Higher spending pulls the
interest rate up, money flows in, the currency strengthens, and exports fall by exactly
what spending added. Both happen in the same period, so the diagram never shows the
outward shift — only the net result.

**Why a fixed rate forces inflation back to the world rate.** By definition
$w^r = w \cdot p^a / p$. Hold the nominal rate $w$ fixed and let domestic prices rise
faster than foreign ones, and $w^r$ *must* keep falling. Nothing can be at rest until the
two inflation rates are equal, so $\pi^a$ is the only candidate for the long run — reached
slowly, because it works through accumulated price differences rather than through a rate
that can jump. This says where the economy could come to rest, not that it gets there:
with sterilization the bank's own rule walks it in, and without sterilization the interest
rate pushes it out.

**Why sterilization is the capital-controls corner.** The bank keeps its own interest rate, so in
the long run its rule leaves $r = r' + \lambda_I \pi^a$. If that is not equal to $r^a$,
money never stops crossing the border and reserves drain (or pile up) without limit. The
app warns you when the settings are in this position.

**When the reserves run out.** Offsetting the flows means trading foreign currency for
domestic currency day after day, and a central bank only has so much of it. Once the stock
is gone, one of the two things it was holding on to has to go:

- **It lets the interest rate go.** It stops sterilizing, the domestic rate is pulled to
  the world rate, and the economy carries on as **Fixed – no sterilization** — the column
  above. Whatever the bank had done with $r'$ stops mattering from that moment.
- **It lets the currency go.** It stops defending the rate, which then jumps and moves
  freely — **Flexible**, the column. Inflation now heads for the country's own rate
  $\pi^*$ rather than the world rate.

Note that **Fixed – no sterilization does not face this**. It lets the flows change the
money supply instead of sterilizing them, so they stop by themselves as soon as the domestic
rate has satisfied the parity condition — which is exactly why that regime has no monetary
policy of its own to lose. It has a different failure instead: the rate the parity
condition asks for keeps getting further from the rate the economy needs. Britain gave up
on Black Wednesday rather than pay it; France paid it and took the depression.

This app stops at the break: it draws the path *while* the fixed rate lasts, and warns you
when your settings put you on that path. To see what comes next, switch the regime in the
sidebar and run the same shock again — **🔖 Remember this run** keeps the first path on the
charts in grey.

**Where the long run comes from.** Under a flexible rate $r = r^a$ pins the interest
rate, output is set by MP and FX together, and $\omega$ drops out entirely:

$$
\pi^* = \frac{r^a - r'}{\lambda_I}
$$

so the country keeps an inflation rate of its own and the nominal exchange rate slides at
$\pi^* - \pi^a$ per period to stay competitive. Under either fixed rate the identity above
takes over instead, and $\pi \to \pi^a$.

---

### How a simulation unfolds

| Stage | What is shown |
|---|---|
| **Period 0** | The resting point: $Y = \bar{Y}$, $\pi = \pi^a$, $r = r^a$ — everything still. |
| **Period 1** — *the impact* | The shock lands. **Output moves, inflation does not.** The run pauses here so the short run can be examined. |
| **Adjustment** | Press **Continue**. The output gap moves inflation each period and the economy slides along AD. |
| **Long run** | Output is back at $\bar{Y}$ — under a flexible rate, and under a fixed one with sterilization. Without sterilization there is no long run to reach: the run is stopped once output or inflation leaves the range the model can describe. |

**A useful exercise:** run the *same* shock in all three regimes and compare. **🔖 Remember
this run** keeps the previous path on the charts in grey.
"""


# The impossible trinity, one triangle per regime: the two corners it reaches are
# joined by a solid edge, the one it gives up is crossed out. Built in code rather
# than hand-written so the three panels cannot drift apart.
TRINITY_SVG = '<svg viewBox="0 0 900 300" width="900" height="300" xmlns="http://www.w3.org/2000/svg" font-family="system-ui, -apple-system, sans-serif">\n<g transform="translate(0,0)">\n<text x="150" y="24" text-anchor="middle" font-size="13" font-weight="600" fill="#555">Flexible</text>\n<line x1="150" y1="78" x2="58" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<line x1="58" y1="220" x2="242" y2="220" stroke="#4C78A8" stroke-width="3" />\n<line x1="150" y1="78" x2="242" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<circle cx="150" cy="78" r="7" fill="#FFFFFF" stroke="#CCCCCC" stroke-width="1.5" />\n<path d="M146,74 L154,82 M154,74 L146,82" stroke="#E45756" stroke-width="1.8" stroke-linecap="round" />\n<circle cx="58" cy="220" r="7" fill="#4C78A8" />\n<circle cx="242" cy="220" r="7" fill="#4C78A8" />\n<text x="150" y="48" text-anchor="middle" font-size="11" fill="#BBBBBB">Stable exchange<tspan x="150" dy="13">rate</tspan></text>\n<text x="58" y="244" text-anchor="middle" font-size="11" fill="#666666">Free movement<tspan x="58" dy="13">of money</tspan></text>\n<text x="242" y="244" text-anchor="middle" font-size="11" fill="#666666">Own monetary<tspan x="242" dy="13">policy</tspan></text>\n<text x="150" y="288" text-anchor="middle" font-size="11" fill="#999">the currency absorbs the shocks</text>\n</g>\n<g transform="translate(300,0)">\n<text x="150" y="24" text-anchor="middle" font-size="13" font-weight="600" fill="#555">Fixed – no sterilization</text>\n<line x1="150" y1="78" x2="58" y2="220" stroke="#4C78A8" stroke-width="3" />\n<line x1="58" y1="220" x2="242" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<line x1="150" y1="78" x2="242" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<circle cx="150" cy="78" r="7" fill="#4C78A8" />\n<circle cx="58" cy="220" r="7" fill="#4C78A8" />\n<circle cx="242" cy="220" r="7" fill="#FFFFFF" stroke="#CCCCCC" stroke-width="1.5" />\n<path d="M238,216 L246,224 M246,216 L238,224" stroke="#E45756" stroke-width="1.8" stroke-linecap="round" />\n<text x="150" y="48" text-anchor="middle" font-size="11" fill="#666666">Stable exchange<tspan x="150" dy="13">rate</tspan></text>\n<text x="58" y="244" text-anchor="middle" font-size="11" fill="#666666">Free movement<tspan x="58" dy="13">of money</tspan></text>\n<text x="242" y="244" text-anchor="middle" font-size="11" fill="#BBBBBB">Own monetary<tspan x="242" dy="13">policy</tspan></text>\n<text x="150" y="288" text-anchor="middle" font-size="11" fill="#999">the world sets the interest rate</text>\n</g>\n<g transform="translate(600,0)">\n<text x="150" y="24" text-anchor="middle" font-size="13" font-weight="600" fill="#555">Fixed – with sterilization</text>\n<line x1="150" y1="78" x2="58" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<line x1="58" y1="220" x2="242" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<line x1="150" y1="78" x2="242" y2="220" stroke="#4C78A8" stroke-width="3" />\n<circle cx="150" cy="78" r="7" fill="#4C78A8" />\n<circle cx="58" cy="220" r="7" fill="#FFFFFF" stroke="#CCCCCC" stroke-width="1.5" />\n<path d="M54,216 L62,224 M62,216 L54,224" stroke="#E45756" stroke-width="1.8" stroke-linecap="round" />\n<circle cx="242" cy="220" r="7" fill="#4C78A8" />\n<text x="150" y="48" text-anchor="middle" font-size="11" fill="#666666">Stable exchange<tspan x="150" dy="13">rate</tspan></text>\n<text x="58" y="244" text-anchor="middle" font-size="11" fill="#BBBBBB">Free movement<tspan x="58" dy="13">of money</tspan></text>\n<text x="242" y="244" text-anchor="middle" font-size="11" fill="#666666">Own monetary<tspan x="242" dy="13">policy</tspan></text>\n<text x="150" y="288" text-anchor="middle" font-size="11" fill="#999">capital controls hold it together</text>\n</g>\n</svg>'


# ―――― Pop-ups ―――――――――――――――――――――――――――――――――――
# Shown ONLY where the main panel does not already say it: at Medium/Advanced the
# panel lists the settings rather than telling a story, so a policy that cannot
# work in the chosen regime needs flagging. At Easy the story says it instead.

monetary_neutralised_text = """🏦 **Monetary policy has no effect here.** Holding the exchange rate
fixed pulls the domestic interest rate back to the world rate, so the change in r'
never reaches the economy."""

foreign_neutralised_text = """🌍 **The foreign rate does not reach the economy.** The bank offsets the
currency flows, so output and inflation are unaffected."""
