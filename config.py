# Letters to copy: 𝜓 ç 𝜔


markdown_text = r"""
## Closed Economy — Equations

**Units.** Potential output is an index, $\bar{Y} = 100$, so the gap
$\tilde{Y} = 100\,(Y-\bar{Y})/\bar{Y}$ is in percentage points — the same units as $r$ and
$\pi$. Baseline: $Y = 100$, $\pi = 2\%$, $r = 2\%$.

### Parameters

| Symbol | Meaning | Default |
|---|---|---|
| $\bar{Y}$ | Potential output (index) | 100 |
| $\omega$ | Autonomous demand — the IS shifter | 102 |
| $\phi$ | Output cost of a 1 pp rise in the real rate | 1.0 |
| $r'$ | Intercept of the policy rule (not the rate itself) | 1.0 |
| $\lambda_P$ | Policy response to the output gap | 0.5 |
| $\lambda_I$ | Policy response to inflation (real; nominal is $1+\lambda_I$) | 0.5 |
| $\gamma$ | Phillips slope: pp of inflation per point of gap | 0.4 |
| $\eta$ | Exogenous price shock, applied every period | 0 |

---

### Upper diagram — $r$–$Y$

**IS**

$$
Y = \omega - \phi\,r \qquad \phi > 0
$$

$$
r(Y) \;=\; \underbrace{\frac{\omega}{\phi}}_{\text{intercept}}
\;\underbrace{-\;\frac{1}{\phi}}_{\text{slope}}\,Y
$$

**MP**

$$
r = r' + \lambda_P \tilde{Y} + \lambda_I \pi,
\qquad \tilde{Y} = 100\,\frac{Y-\bar{Y}}{\bar{Y}}
$$

$$
r(Y) \;=\; \underbrace{\bigl(r' - 100\lambda_P + \lambda_I \pi\bigr)}_{\text{intercept}}
\;+\; \underbrace{\frac{100\lambda_P}{\bar{Y}}}_{\text{slope}}\,Y
$$

---

### Lower diagram — $\pi$–$Y$

**IA**

$$
\pi_{t+1} = \pi_t + \gamma\,\tilde{Y}_t + \eta
$$

Today's inflation was fixed by last period's gap, so IA is drawn **flat**:

$$
\pi(Y) = \pi_t \qquad (\text{slope } 0)
$$

Read as a Phillips curve — next period's inflation at a current output $Y$ — the same
equation slopes up through $(\bar{Y},\,\pi_t)$:

$$
\pi(Y) \;=\; \underbrace{\bigl(\pi_t + \eta - 100\gamma\bigr)}_{\text{intercept}}
\;+\; \underbrace{\frac{100\gamma}{\bar{Y}}}_{\text{slope}}\,Y
$$

**AD** — IS $\cap$ MP. Set $r_{IS}(Y) = r_{MP}(Y)$ and solve for $\pi$:

$$
\frac{\omega}{\phi} - \frac{1}{\phi}Y
= r' - 100\lambda_P + \lambda_I \pi + \frac{100\lambda_P}{\bar{Y}}Y
$$

$$
\pi(Y) \;=\;
\underbrace{\frac{1}{\lambda_I}\left(\frac{\omega}{\phi} - r' + 100\lambda_P\right)}_{\text{intercept}}
\;-\; \underbrace{\frac{1}{\lambda_I}\left(\frac{1}{\phi} + \frac{100\lambda_P}{\bar{Y}}\right)}_{|\text{slope}|}\,Y
$$

---

### Long run

Inflation rests when $\pi_{t+1} = \pi_t$, which needs $\tilde{Y} = 0$. So $\pi^*$ is AD
evaluated at $Y = \bar{Y}$:

$$
\pi^* = \frac{1}{\lambda_I}\left(\frac{\omega - \bar{Y}}{\phi} - r'\right)
\qquad r^* = r' + \lambda_I \pi^*
$$
"""


# r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \text{ with } r' > 0, \lambda_P \ge 0, \lambda_I \ge 0.

tabs_options = ['📊 Time Model', '🏠 Home', '🧾 Glossary']  #'📊 Data'

standard_line_width = 3
thin_line_width = 2

Y_potential = 100
speed = 0.1

iteration_count = 25




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
# The thresholds that pick these texts live in closed_economy.py (OMEGA_HI/LO)
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
# One description per (shock family, regime), assembled by oe_shock_panel().
# Direction words are substituted, so a shock and its mirror cannot disagree.

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

# What the shock is, before the regime enters
OE_LEAD = {
    'fiscal': "The government spends {more_less}, which shifts the IS-curve to the {right_left} (ω {up_down}).",
    'monetary': "The central bank takes a {looser_tighter} stance ({down_up} r').",
    'foreign': "The rest of the world moves to a {higher_lower} interest rate ({up_down} rᵃ).",
    'imported': "Import prices {jump_drop} once and feed straight into domestic prices — the one shock "
                "that moves inflation without an output gap first.",
}

# What the chosen regime does with it
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


# Medium level: one line per kind of setting changed. Kinds a pop-up already
# covers have no entry here, so nothing is said twice.
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


# What the charts actually show, checked against the simulation — under a float a
# line can end up not moving at all, and the text has to say so.
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
## Open Economy — Equations

### Variables and parameters

| Symbol | Meaning | Default |
|---|---|---|
| $Y,\ \bar{Y}$ | Output and potential output (index) | — , 100 |
| $\tilde{Y}$ | Output gap, $100\,(Y-\bar{Y})/\bar{Y}$, in points | — |
| $\pi$ | Inflation, % | 2 |
| $r$ | Real interest rate, % | 2 |
| $w^r$ | Real exchange rate $w\,p^a/p$ — a **rise** is a depreciation | 100 |
| $\omega$ | Autonomous demand — the fiscal instrument | 77 |
| $\varphi$ | Output cost of a 1 pp rise in $r$ | 1.0 |
| $\psi$ | Output gain from a 1 % real depreciation | 0.25 |
| $r'$ | Intercept of the policy rule, not the rate itself | 1.0 |
| $\lambda_P$ | Policy response to the output gap | 0.5 |
| $\lambda_I$ | Policy response to inflation (real) | 0.5 |
| $\gamma$ | Phillips slope: pp of inflation per point of gap | 0.4 |
| $\chi$ | Pass-through of a move in $w^r$ into prices | 0 |
| $r^a,\ \pi^a$ | Foreign real rate and inflation | 2.0 , 2.0 |

### The five equations

$$
\textbf{IS}\quad Y = \omega - \varphi\,r + \psi\,w^r
$$

$$
\textbf{MP}\quad r = r' + \lambda_P \tilde{Y} + \lambda_I \pi
$$

$$
\textbf{FX}\quad 1 + r = (1 + r^a)\,\frac{w^{r,e}_{+1}}{w^r}
$$

$$
\textbf{PPP}\quad w^r_t = w^r_{t-1}\,\frac{1 + \pi^a}{1 + \pi_t}
$$

$$
\textbf{IA}\quad \pi_{t+1} = \pi_t + \gamma\,\tilde{Y}_t
$$

IS, MP and IA are the same in all three regimes. **AD** is not a separate assumption —
it is two of the curves above solved together, and *which* two depends on the regime.

---

### Exchange-rate regimes

A country would like a **stable exchange rate**, **free movement of capital** and a
**monetary policy of its own**. It can have any two.
"""


THEORY_REST = r"""
| | Flexible | Fixed – no sterilization | Fixed – with sterilization |
|---|---|---|---|
| **Gives up** | the stable exchange rate | its own monetary policy | free movement of capital |
| **FX becomes** | $r = r^a$ | $r = r^a + (\pi^a - \pi)$ | $r = r^a + (\pi^a - \pi)$, not met |
| **AD is** | MP $\cap$ FX | IS $\cap$ FX | IS $\cap$ MP |
| **AD slope** | $-\lambda_P/(\lambda_I)$ | $1/\varphi$ | $-\bigl(1/\varphi + \lambda_P\bigr)/\lambda_I$ |


**AD, flexible** — MP $\cap$ FX, FX: $r = r^a$:

$$
\pi(Y) = \frac{r^a - r' + \lambda_P}{\lambda_I} \;-\; \frac{\lambda_P}{\lambda_I}Y
$$

**AD, fixed with sterilization** — IS $\cap$ MP at the pegged $w^r$:

$$
\pi(Y) = \frac{\omega - \varphi r' + \varphi \lambda_P + \psi w^r}{\varphi \lambda_I}
\;-\; \frac{1 + \varphi \lambda_P}{\varphi \lambda_I}Y
$$

**AD, fixed without sterilization** — IS $\cap$ FX at the pegged $w^r$:

$$
\pi(Y) = \frac{ - \omega + \varphi r^a + \varphi \pi^a - \psi w^r}{\varphi} \;+\; \frac{1}{\varphi}Y
$$

The last slope is **positive**: with the policy rule gone, higher inflation means a lower
real rate and more demand, so the rest point is unstable.
"""


# One triangle per regime: the two corners it reaches are joined, the one it gives
# up is crossed out.
TRINITY_SVG = '<svg viewBox="0 0 900 300" width="900" height="300" xmlns="http://www.w3.org/2000/svg" font-family="system-ui, -apple-system, sans-serif">\n<g transform="translate(0,0)">\n<text x="150" y="24" text-anchor="middle" font-size="13" font-weight="600" fill="#555">Flexible</text>\n<line x1="150" y1="78" x2="58" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<line x1="58" y1="220" x2="242" y2="220" stroke="#4C78A8" stroke-width="3" />\n<line x1="150" y1="78" x2="242" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<circle cx="150" cy="78" r="7" fill="#FFFFFF" stroke="#CCCCCC" stroke-width="1.5" />\n<path d="M146,74 L154,82 M154,74 L146,82" stroke="#E45756" stroke-width="1.8" stroke-linecap="round" />\n<circle cx="58" cy="220" r="7" fill="#4C78A8" />\n<circle cx="242" cy="220" r="7" fill="#4C78A8" />\n<text x="150" y="48" text-anchor="middle" font-size="11" fill="#BBBBBB">Stable exchange<tspan x="150" dy="13">rate</tspan></text>\n<text x="58" y="244" text-anchor="middle" font-size="11" fill="#666666">Free movement<tspan x="58" dy="13">of money</tspan></text>\n<text x="242" y="244" text-anchor="middle" font-size="11" fill="#666666">Own monetary<tspan x="242" dy="13">policy</tspan></text>\n<text x="150" y="288" text-anchor="middle" font-size="11" fill="#999">the currency absorbs the shocks</text>\n</g>\n<g transform="translate(300,0)">\n<text x="150" y="24" text-anchor="middle" font-size="13" font-weight="600" fill="#555">Fixed – no sterilization</text>\n<line x1="150" y1="78" x2="58" y2="220" stroke="#4C78A8" stroke-width="3" />\n<line x1="58" y1="220" x2="242" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<line x1="150" y1="78" x2="242" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<circle cx="150" cy="78" r="7" fill="#4C78A8" />\n<circle cx="58" cy="220" r="7" fill="#4C78A8" />\n<circle cx="242" cy="220" r="7" fill="#FFFFFF" stroke="#CCCCCC" stroke-width="1.5" />\n<path d="M238,216 L246,224 M246,216 L238,224" stroke="#E45756" stroke-width="1.8" stroke-linecap="round" />\n<text x="150" y="48" text-anchor="middle" font-size="11" fill="#666666">Stable exchange<tspan x="150" dy="13">rate</tspan></text>\n<text x="58" y="244" text-anchor="middle" font-size="11" fill="#666666">Free movement<tspan x="58" dy="13">of money</tspan></text>\n<text x="242" y="244" text-anchor="middle" font-size="11" fill="#BBBBBB">Own monetary<tspan x="242" dy="13">policy</tspan></text>\n<text x="150" y="288" text-anchor="middle" font-size="11" fill="#999">the world sets the interest rate</text>\n</g>\n<g transform="translate(600,0)">\n<text x="150" y="24" text-anchor="middle" font-size="13" font-weight="600" fill="#555">Fixed – with sterilization</text>\n<line x1="150" y1="78" x2="58" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<line x1="58" y1="220" x2="242" y2="220" stroke="#DDDDDD" stroke-width="1.5" stroke-dasharray="4 4" />\n<line x1="150" y1="78" x2="242" y2="220" stroke="#4C78A8" stroke-width="3" />\n<circle cx="150" cy="78" r="7" fill="#4C78A8" />\n<circle cx="58" cy="220" r="7" fill="#FFFFFF" stroke="#CCCCCC" stroke-width="1.5" />\n<path d="M54,216 L62,224 M62,216 L54,224" stroke="#E45756" stroke-width="1.8" stroke-linecap="round" />\n<circle cx="242" cy="220" r="7" fill="#4C78A8" />\n<text x="150" y="48" text-anchor="middle" font-size="11" fill="#666666">Stable exchange<tspan x="150" dy="13">rate</tspan></text>\n<text x="58" y="244" text-anchor="middle" font-size="11" fill="#BBBBBB">Free movement<tspan x="58" dy="13">of money</tspan></text>\n<text x="242" y="244" text-anchor="middle" font-size="11" fill="#666666">Own monetary<tspan x="242" dy="13">policy</tspan></text>\n<text x="150" y="288" text-anchor="middle" font-size="11" fill="#999">capital controls hold it together</text>\n</g>\n</svg>'


# ―――― Pop-ups ―――――――――――――――――――――――――――――――――――
# Shown only at Medium/Advanced, where the panel lists settings instead of telling
# a story, so a policy the regime switches off still gets flagged.

monetary_neutralised_text = """🏦 **Monetary policy has no effect here.** Holding the exchange rate
fixed pulls the domestic interest rate back to the world rate, so the change in r'
never reaches the economy."""

foreign_neutralised_text = """🌍 **The foreign rate does not reach the economy.** The bank offsets the
currency flows, so output and inflation are unaffected."""
