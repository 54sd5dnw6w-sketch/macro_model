# Letters to copy: 𝜓 ç 𝜔


markdown_text = r"""
## Model Overview

This model represents a closed economy through four curves that jointly determine output $Y$ and inflation $\pi$ in each period. The economy begins in long-run equilibrium, is disturbed by a shock in period 1, and then returns to equilibrium over the following periods.

---

### Curve Definitions

**IS curve** — *Investment–Savings*

Describes the goods market: output $Y$ is a decreasing function of the real interest rate $r$. Higher rates discourage investment and consumption, and output falls as a result.
$$
Y = \omega - \phi \, r \qquad \phi > 0
$$

| Parameter | Meaning |
|-----------|---------|
| $\omega$ | Autonomous demand (shifts IS right or left) |
| $\phi$ | Sensitivity of output to the interest rate |

---

**MP curve** — *Monetary Policy*

The central bank sets the real interest rate in response to the output gap $\tilde{Y} = \frac{Y - \bar{Y}}{\bar{Y}}$ and to inflation $\pi$. Higher output or higher inflation leads to a higher rate.
$$
r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \qquad r' > 0,\ \lambda_P \ge 0,\ \lambda_I \ge 0
$$

| Parameter | Meaning |
|-----------|---------|
| $r'$ | Baseline (neutral) real interest rate |
| $\lambda_P$ | Response to the output gap |
| $\lambda_I$ | Response to inflation |

---

**IA curve** — *Inflation Adjustment*

The IA curve records the prevailing rate of inflation, which reflects inflation expectations and price stickiness. In the **short run** (period 1) it is a horizontal line at the post-shock inflation level $\pi_0$, since prices do not adjust immediately to the new conditions:
$$
\pi_t = \pi_0 \qquad \text{(short run, } t = 1\text{)}
$$

Beyond the short run the IA curve shifts in each period according to the output gap and to any persistent exogenous price shock. When output exceeds potential, firms raise prices and inflation rises; when output falls short of potential, inflation declines:
$$
\boxed{\pi_{t+1} = \pi_t + \gamma \cdot \tilde{Y}_t + \eta = \pi_t + \gamma \cdot \frac{Y_t - \bar{Y}}{\bar{Y}} + \eta}
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
\pi_{t+1} = \pi_t + \gamma \cdot \frac{Y - \bar{Y}}{\bar{Y}}
$$

Rearranged as a function of $Y$:

$$
\pi_{t+1} = \underbrace{\frac{\gamma}{\bar{Y}}}_{\text{slope}} \cdot Y + \underbrace{(\pi_t - \gamma)}_{\text{intercept}}
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
r = r' + \lambda_P \frac{Y - \bar{Y}}{\bar{Y}} + \lambda_I \pi
= \underbrace{\left(r' - \lambda_P + \lambda_I \pi\right)}_{\text{intercept}}
+ \underbrace{\left(\frac{\lambda_P}{\bar{Y}}\right)}_{\text{slope}} \cdot Y
$$

**AD** (set $r_{IS} = r_{MP}$ and solve for $\pi$):
$$
\frac{\omega}{\phi} - \frac{1}{\phi} Y = r' - \lambda_P + \lambda_I \pi + \frac{\lambda_P}{\bar{Y}} Y \\[6pt]
\lambda_I \pi = \frac{\omega}{\phi} - \frac{1}{\phi} Y - r' + \lambda_P - \frac{\lambda_P}{\bar{Y}} Y \\[6pt]
\pi = \underbrace{\left(\frac{\omega}{\phi\lambda_I} + \frac{\lambda_P}{\lambda_I} - \frac{r'}{\lambda_I}\right)}_{\text{intercept}}
+ \underbrace{\left(- \frac{1}{\phi\lambda_I} - \frac{\lambda_P}{\lambda_I\bar{Y}}\right)}_{\text{slope}} \cdot Y
$$

---

### Long-Run Equilibrium

The economy returns to equilibrium when $\pi_{t+1} = \pi_t$, which requires $Y_t = \bar{Y}$. Long-run inflation $\pi^*$ is therefore the value at which the AD curve crosses the potential output line $Y = \bar{Y}$:
$$
\pi^* = \frac{\omega}{\phi\lambda_I} + \frac{\lambda_P}{\lambda_I} - \frac{r'}{\lambda_I}
+ \left(- \frac{1}{\phi\lambda_I} - \frac{\lambda_P}{\lambda_I\bar{Y}}\right)\bar{Y}
$$
"""


# r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \text{ with } r' > 0, \lambda_P \ge 0, \lambda_I \ge 0.

tabs_options = ['📊 Time Model', '🏠 Home', '🧾 Glossary']  #'📊 Data'

standard_line_width = 3
thin_line_width = 2


Y_potential = 1
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
omega_text_exp = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Positive Supply Shock (ω > 5) 🏛️
</div>

<div style="font-size:13px; color:gray;">
    Either a favourable external supply shock, or an increase in public spending or a reduction in taxes.
</div>
"""

omega_text_res = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Negative Supply Shock (ω < 4) 🏛️
</div>

<div style="font-size:13px; color:gray;">
    Either an adverse external event that raises world prices, or a reduction in aggregate demand through lower public spending or higher taxes.
</div>
"""


# ---------- Monetary Policy (r) ----------
r_text_con = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Contractionary Monetary Policy (r > 2.3) 💰
</div>

<div style="font-size:13px; color:gray;">
    The central bank raises interest rates and tightens financial conditions.
    Borrowing and investment decline, which slows aggregate demand and inflation.
</div>
"""

r_text_exp = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Expansionary Monetary Policy (r < 1.7) 💰
</div>

<div style="font-size:13px; color:gray;">
    The central bank lowers interest rates and increases liquidity in the economy.
    Credit conditions improve, which stimulates consumption, investment, and output.
</div>
"""


# ---------- Inflation Shock (pi) ----------
pi_text_inf = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Upward Inflation Shock (η > 0) 📈
</div>

<div style="font-size:13px; color:gray;">
    Inflation starts above its long-run equilibrium, following supply disruptions, rising
    production costs, or higher commodity prices. Inflation accelerates and real purchasing
    power declines. The economy returns to equilibrium as the central bank tightens policy.
</div>
"""

pi_text_def = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Downward Inflation Shock (η < 0) 📉
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
# ―――― Easy-mode shock descriptions ――――――――――――――――
SHOCK_TEXT = {
    'Expansionary Monetary Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Expansionary Monetary Shock 🏦</div>
<div style="font-size:13px; color:gray;">
The central bank adopts a looser policy stance (↓r'). The MP-curve shifts down and the AD-curve shifts right.
<br><br>
In the short run output rises above potential. The lower rate induces capital outflows, the domestic currency depreciates (wʳ ↑) and net exports rise. The positive output gap then raises inflation to its new, higher long-run level π* = (rᵃ − r')/λ<sub>I</sub>.
</div>""",
    'Contractionary Monetary Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Contractionary Monetary Shock 🏦</div>
<div style="font-size:13px; color:gray;">
The central bank tightens its policy stance (↑r'). The MP-curve shifts up and the AD-curve shifts left.
<br><br>
Output falls below potential and capital flows in, which appreciates the domestic currency (wʳ ↓). The negative output gap gradually lowers inflation to its new long-run level π* = (rᵃ − r')/λ<sub>I</sub>, which now lies below foreign inflation πᵃ.
</div>""",
    'Rising Foreign Interest Rate': """
<div style="text-align:center; font-size:17px; font-weight:700;">Rising Foreign Interest Rate 🌍</div>
<div style="font-size:13px; color:gray;">
The foreign central bank raises its rate (↑rᵃ). The FX-line shifts up.
<br><br>
Capital flows abroad, the domestic currency depreciates and the real exchange rate wʳ rises, which shifts IS to the right. Output rises in the short run and the domestic real rate follows rᵃ upward. Inflation converges to π* = (rᵃ − r')/λ<sub>I</sub>.
</div>""",
    'Falling Foreign Interest Rate': """
<div style="text-align:center; font-size:17px; font-weight:700;">Falling Foreign Interest Rate 🌍</div>
<div style="font-size:13px; color:gray;">
The foreign central bank lowers its rate (↓rᵃ). The FX-line shifts down.
<br><br>
Capital flows in, the domestic currency appreciates (wʳ ↓) and net exports fall, which shifts IS to the left. Output falls in the short run and inflation declines to its new long-run level π* = (rᵃ − r')/λ<sub>I</sub>.
</div>""",
    'Imported Inflation Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Imported Inflation Shock 📈</div>
<div style="font-size:13px; color:gray;">
A one-off increase in import prices passes directly into domestic prices — the χ·Δwʳ term of eq. (5.2) — and shifts the IA-curve up <b>even in the absence of an output gap</b>. It is modelled here as an exogenous one-off shift of IA: it is applied once and then carried forward into later periods.
<br><br>
Inflation rises above foreign inflation πᵃ. Output falls below potential, and the negative output gap brings inflation back down to πᵃ.
<br><br>
<i>Reading the wʳ chart:</i> the line shown is the <b>response</b> of the economy, not the shock. Higher inflation with the interest rate tied to rᵃ requires the currency to strengthen (wʳ ↓) — under a peg because domestic prices outrun foreign ones, and under a float through appreciation. The shock itself originates abroad and is not drawn.
</div>""",
    'Imported Deflation Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Imported Deflation Shock 📉</div>
<div style="font-size:13px; color:gray;">
A one-off fall in import prices passes directly into domestic prices — the χ·Δwʳ term of eq. (5.2) — and shifts the IA-curve down <b>even in the absence of an output gap</b>. It is modelled here as an exogenous one-off shift of IA: it is applied once and then carried forward into later periods.
<br><br>
Inflation falls below foreign inflation πᵃ. Output rises above potential, and the positive output gap brings inflation back up to πᵃ.
<br><br>
<i>Reading the wʳ chart:</i> the line shown is the <b>response</b> of the economy, not the shock — lower inflation with r tied to rᵃ requires the currency to weaken (wʳ ↑). The shock itself originates abroad and is not drawn.
</div>""",
    'Expansionary Fiscal Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Expansionary Fiscal Shock 🏛️</div>
<div style="font-size:13px; color:gray;">
Higher government demand shifts the IS-curve to the right (↑ω). What follows depends entirely on the <b>exchange-rate regime</b>:
<br><br>
<b>Flexible:</b> the currency appreciates (wʳ ↓), net exports fall, and the expansion is <b>fully crowded out</b> — Y and π are unchanged.
<br><br>
<b>Fixed peg:</b> the nominal rate cannot move, so fiscal policy is <b>effective</b> — output rises above potential, by the full amount without sterilization and by less with it. Crowding out then arrives slowly through the trade balance, as domestic prices outrun foreign ones (wʳ ↓), and inflation returns to πᵃ.
</div>""",
    'Contractionary Fiscal Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Contractionary Fiscal Shock 🏛️</div>
<div style="font-size:13px; color:gray;">
Lower government demand shifts the IS-curve to the left (↓ω). The effect depends on the <b>exchange-rate regime</b>:
<br><br>
<b>Flexible:</b> the currency depreciates (wʳ ↑), net exports rise, and the reduction in demand is <b>fully crowded out</b> — Y and π are unchanged.
<br><br>
<b>Fixed peg:</b> fiscal policy is <b>effective</b> — output falls below potential, and real depreciation (wʳ ↑) then restores it gradually while inflation returns to πᵃ.
</div>""",
    None: placeholder_shock,
}


MARKDOWN_THEORY = r"""
## The Open Economy

In a **closed** economy the country trades with no one: everything it produces, it also
consumes itself. This is a useful simplification, but no actual economy works that way.

Opening the economy adds two channels to the model:

- **A goods channel** — output can be sold abroad (exports) and bought from abroad
  (imports).
- **A financial channel** — savers can move funds abroad in search of a higher interest
  rate, and foreign investors can move funds in.

Almost every result that follows comes from a single question: how do these two channels
respond when something in the economy changes?

---

## 1. The real exchange rate

The variable that carries most of the adjustment in this model is the **real exchange
rate**, written $w^r$. It measures how expensive foreign goods are relative to domestic
ones.

| If $w^r$ **rises** | If $w^r$ **falls** |
|---|---|
| The domestic currency is **weaker** (depreciation) | The domestic currency is **stronger** (appreciation) |
| Foreign goods become expensive at home | Foreign goods become cheap at home |
| Domestic goods look cheap abroad → **exports rise** | Domestic goods look expensive abroad → **exports fall** |
| **Demand for domestic output rises** | **Demand for domestic output falls** |

> **In one sentence:** a depreciation ($w^r \uparrow$) raises demand for domestic output,
> and an appreciation ($w^r \downarrow$) reduces it.

Two distinct exchange rates are contained in this single symbol, and the distinction
becomes important later:

- The **nominal** rate is the quoted exchange rate. A central bank can hold it fixed by
  decree.
- The **real** rate $w^r$ is the nominal rate *adjusted for prices at home and abroad*.
  Even when the nominal rate is frozen, $w^r$ continues to move whenever domestic
  inflation differs from foreign inflation. **A price can be fixed; a price difference
  cannot.** This property governs much of the analysis in the second half of this page.

---

## 2. The five building blocks

The model consists of five relationships. Each is stated first as a sentence, and the
algebra is the same sentence written compactly.

#### IS — where does demand come from?

*Output is higher when borrowing is cheap and when the currency is weak.*

$$Y = \omega - \varphi\, r + \psi\, w^r$$

| Symbol | Meaning |
|---|---|
| $Y$ | Output (GDP) — how much the economy produces |
| $\omega$ | Autonomous demand. **Government spending enters here**, so this is the fiscal-policy instrument |
| $\varphi$ | Strength with which high interest rates reduce investment |
| $\psi$ | Strength with which a weak currency raises net exports |

The term $\psi\, w^r$ is the **only** addition relative to the closed economy, and it
accounts for most of the difference in behaviour.

#### MP — what does the central bank do?

*Raise the rate when the economy runs hot or inflation climbs.*

$$r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$$

Here $\tilde{Y} = (Y - \bar{Y})/\bar{Y}$ is the **output gap**, the deviation of output
from the level the economy can sustain, $\bar{Y}$. The intercept $r'$ represents the
bank's overall stance: **a lower $r'$ means looser policy**.

#### FX — why is the domestic interest rate not free?

*Capital moves towards the highest return, so the domestic rate is drawn to the world rate.*

$$r = r^a$$

If the domestic rate stood above the world rate $r^a$, foreign capital would flow in
until the difference disappeared. This is the **capital-mobility** constraint. Whether it
actually binds depends on the exchange-rate regime, which is the subject of section 4.

#### IA — how does inflation move?

*Inflation is sticky within the period and drifts according to whether the economy runs hot or cold.*

$$\pi_{t+1} = \pi_t + \gamma \tilde{Y}_t + \chi\,(w^r_{t+1} - w^r_t) + \eta$$

Two features matter throughout:

1. **Inflation is predetermined.** Today's inflation was set by yesterday's conditions
   and cannot jump in the period a shock arrives, since wages and contracts are already
   agreed. Output therefore moves first, and inflation follows.
2. **The output gap drives inflation.** Running above capacity ($\tilde{Y}>0$) pushes
   inflation up and running below capacity pushes it down. Inflation stops moving only
   once output has returned to potential.

The $\chi$ term represents **imported inflation** (§5.5): when the currency weakens,
imports cost more and this enters the price index directly, with no output gap required.
$\chi$ is large for a consumer price index, which contains imported final goods, and
small for the GDP deflator, which does not. The term is an **extension** — every result
stated below is derived for $\chi = 0$, which is why it defaults to zero and appears only
at the Advanced level. Section 9 sets out what changes when it is switched on.

#### PPP — where does inflation eventually settle?

*Under a fixed currency, domestic inflation is drawn in the long run to the foreign rate.*

Purchasing power parity provides the anchor $\pi^a$ (foreign inflation), shown as the
grey dashed line. Whether domestic inflation actually returns to it is **precisely** what
separates the three regimes.

---

## 3. Reading the two diagrams

**Upper chart — the $r$–$Y$ diagram (interest rates)**

The intersection of IS, MP and FX determines output and the interest rate. The sideways
movement of the <span style="color:#4C78A8;">**IS**</span> line *is* the exchange rate
doing its work.

**Lower chart — the $\pi$–$Y$ diagram (inflation)**

- The <span style="color:#B279A2;">**AD**</span> curve, which slopes downward, summarises
  the whole upper diagram in a single line: *for each rate of inflation, what output
  results once the central bank and the exchange rate have responded?*
- The <span style="color:#54A24B;">**IA**</span> curve is horizontal because inflation is
  predetermined — it records *today's* inflation, which cannot move today.

**A run therefore proceeds as follows.** The shock arrives, AD shifts, and the economy
moves **sideways** along the horizontal IA line, so output changes while inflation cannot.
Period by period the output gap then drags IA up or down, and the economy **slides along
AD** until output is back at $\bar{Y}$.

Once a run is under way, the pale curves show the **short-run** position (period 1) and
the bright curves show **the current position**, so the distance the economy has travelled
remains visible.

---

## 4. The three regimes — not all objectives are attainable

This is the central proposition of open-economy macroeconomics, and the reason for the
regime switch in the sidebar. A country may wish to have three things at once:

1. A **stable exchange rate**
2. **Free movement of capital** across borders
3. An **independent monetary policy**, set for domestic conditions

**Only two of the three are attainable.** This is the *impossible trinity*, and each
regime in this application represents a different choice about which objective to give up.

### 🌊 Flexible — the stable exchange rate is given up

The currency floats. Capital moves freely, so $r = r^a$ binds.

The currency then acts as a **shock absorber**, and it is effective enough to neutralise
fiscal policy entirely. Higher spending attracts an inflow, the currency strengthens, and
exports fall by exactly the amount that spending added. **Fiscal policy is fully crowded
out.**

### 🔒 Fixed, no sterilization — monetary independence is given up

The bank commits to the exchange rate and allows capital to flow. Defending the peg
requires buying and selling foreign currency, which changes the domestic money supply, and
the domestic interest rate is consequently tied to $r^a$ whether the bank intends it or
not.

**Monetary policy therefore has no effect.** A change in $r'$ produces no response, and
the application reports this.

Since the currency can no longer absorb anything, **fiscal policy reaches its maximum
effect** and the full impact falls on output.

Adjustment operates through the *real* rate. If domestic inflation exceeds foreign
inflation, domestic goods slowly become more expensive, exports slowly fall, and output
slowly cools, until inflation is back at $\pi^a$. **Purchasing power parity holds in the
end.** The process is slow, because it works through accumulated price differences rather
than through a rate that can jump.

### 🛡️ Fixed, with sterilization — an attempt to obtain all three

Here the bank defends the peg **and** offsets the side effects on the money supply
("sterilises" them), so that it retains control of its own interest rate.

For a time this succeeds: the exchange rate is stable and monetary policy still has an
effect. The economy is also **insulated from foreign interest-rate shocks**, since a
change in $r^a$ leaves domestic output and inflation unaffected.

The peg nevertheless carries an unavoidable implication:

> **The peg identity.** By definition $w^r = w\,p^a/p$. If the nominal rate $w$ is held
> fixed and domestic inflation exceeds foreign inflation, $w^r$ *must* keep falling,
> without limit. The system can come to rest only when $w^r$ stops moving, and that
> requires $\pi = \pi^a$. **A country with a pegged currency cannot sustain an inflation
> rate of its own,** whether or not it sterilises.

In *this model*, therefore, sterilisation changes the interest rate and the *speed* of
adjustment, but not the destination. Inflation still returns to $\pi^a$, and crowding out
still arrives, though through the **trade balance** rather than through a jump in the
exchange rate.

The trinity also cannot be evaded indefinitely. In the long run the bank's own rule leaves
$r = r' + \lambda_I \pi^a$. If $r'$ has been changed, or if $r^a$ has moved, this is *not*
equal to $r^a$, so capital keeps flowing and reserves are depleted without limit. The peg
must eventually be abandoned, or converted into a genuine **crawling peg**. The
application issues a warning when the selected scenario is in this position.

> ⚠️ **Where this application and the book differ — worth reading before quoting a long run.**
> For a **monetary** shock, or a change in the foreign rate, under the **sterilised peg**,
> book §5.3 obtains a *different* long run from the one simulated here. The book holds
> $w^r$ constant, lets inflation carry the entire adjustment, and arrives at
> $$P_\infty:\quad \pi^* = \frac{r^a - r'}{\lambda_I},\qquad r \to r^a$$
> — that is, **the same long run as under a float**, which is reached only by converting
> the peg into a crawling peg. In its own words: *"The difference between fixed and
> flexible exchange rates is, therefore, not in the long-run equilibrium but in the
> adjustment path."*
>
> This application instead lets $w^r$ drift, in line with the peg identity above, so that
> inflation returns to $\pi^a$ and it is the *interest rate* that ends away from parity.
> Both treatments are internally consistent; they differ in **which variable is assumed to
> give way** while the peg is held. What is shown here is the path *while the peg lasts*.
> The book's $P_\infty$ requires a fourth regime — a genuine crawling peg — which is not
> implemented.
>
> This affects **only** the sterilised peg following a monetary or foreign-rate shock. For
> demand shocks the book applies the same drift in $w^r$ as this application (§5.2), and
> both conclude that inflation returns to $\pi^a$.

---

## 5. The crawling peg

This is the mechanism the model is chiefly built to demonstrate, so it is worth stating
precisely.

Suppose domestic inflation settles at 3.6% while world inflation remains at 3%. Domestic
goods then become roughly 0.6% more expensive relative to foreign goods each year. If the
nominal rate were genuinely frozen, exports would be squeezed continuously.

The central bank therefore allows the nominal exchange rate to **depreciate by exactly
that 0.6% per year** — the peg *crawls*. The real exchange rate then holds still, and
competitiveness is preserved indefinitely.

$$\pi^* = \frac{r^a - r'}{\lambda_I} \neq \pi^a \qquad \text{nominal rate crawls at } \pi^* - \pi^a$$

> **The central result:** under a crawling peg a country **retains an inflation rate of
> its own**, permanently different from the world rate. Monetary policy has a *lasting*
> effect on inflation instead of being drawn back to $\pi^a$. This is what is meant by the
> statement that monetary policy ends in a crawling peg.

This is the essential difference from a *fixed* peg. Under a genuine nominal peg the peg
identity forces $\pi \to \pi^a$; only by allowing the nominal rate to move — through a
float or a crawl — can a country retain an inflation rate of its own. In this model the
**Flexible** regime is the one that ends in a crawling peg, and both fixed regimes end at
$\pi^a$ — subject to the qualification above, since book §5.3 places the sterilised peg's
long run after a monetary shock at $\pi^*$ as well.

The **π\*** reference line in the inflation chart shows this: under a float it lies *away*
from the grey PPP line, and inflation converges to it rather than to $\pi^a$.

---

## 6. Which policy works in which regime?

The same shock produces three markedly different outcomes. The period-1 output figures
below are exactly those the application produces.

| | 🌊 Flexible | 🔒 Fixed, no steril. | 🛡️ Fixed, sterilised |
|---|---|---|---|
| **Fiscal policy** (higher spending) | ❌ Fully crowded out — no effect | ✅ **Strongest of the three** | ⚠️ Effective, but damped |
| *period-1 output* | $1.00$ (unchanged) | $1.50$ | $1.33$ |
| **Monetary policy** (lower rates) | ✅ Effective, permanently | ❌ **No effect** | ✅ Effective, permanently |
| *period-1 output* | $1.60$ | $1.00$ (unchanged) | $1.20$ |
| **Foreign rate rises** | Expansionary $(1.60)$ | **Contractionary** $(0.70)$ | Insulated $(1.00)$ |
| **Inflation converges to** | crawling peg $\pi^* \neq \pi^a$ | $\pi^a$ (the peg identity) | $\pi^a$ here — but see the note in §4; book §5.3 places it at $\pi^*$, and the peg is not sustainable in either case |

One further row records the property that defines the sterilised peg:

| | 🌊 Flexible | 🔒 Fixed, no steril. | 🛡️ Fixed, sterilised |
|---|---|---|---|
| **Is the regime sustainable?** | yes | yes | **only until reserves are exhausted** |

Three results deserve particular attention:

- **Fiscal and monetary policy are mirror images.** Whichever regime makes one instrument
  powerful renders the other ineffective: a floating currency removes the effect of fiscal
  policy, and a hard peg removes the effect of monetary policy.
- **A rise in the foreign rate changes sign between regimes.** Under a float the currency
  weakens and exports expand, so output *rises*. Under a peg the currency cannot weaken,
  the higher interest rate is simply imported, and output *falls*.
- **Sterilisation changes the path, not the destination.** Because the nominal rate remains
  pegged, inflation ends at $\pi^a$ just as it does under the hard peg. What sterilisation
  provides is a temporarily independent interest rate, at the cost of a peg that eventually
  becomes indefensible.

---

## 7. The shocks, one by one

**🏛️ Fiscal (↑ or ↓ $\omega$)** — the government spends more or less, and IS shifts. The
effect depends entirely on the regime; see the table above.

**🏦 Monetary (↓ or ↑ $r'$)** — the central bank loosens or tightens. Under a float or a
sterilised peg this moves output immediately and inflation permanently. Under a hard peg
it has no effect at all.

**🌍 Foreign interest rate (↑ or ↓ $r^a$)** — the rest of the world changes its rate. Note
the change of sign described above, and that sterilisation blocks the transmission
entirely.

**📈📉 Imported inflation and deflation** — a one-off change in import prices moves
inflation up or down *directly*, with no output gap required. This is the one shock that
reaches the IA curve before the AD curve. Output then deviates from potential, and the
resulting gap slowly returns inflation to its earlier level.

The $w^r$ chart requires care for these two shocks: the line is the **response** of the
economy, not the shock. The shock arrives from abroad and is applied to the IA curve; the
currency then *strengthens* ($w^r \downarrow$), because higher inflation with $r$ tied to
$r^a$ can only be reconciled by a stronger real exchange rate. For the exchange rate to
act as the *source* of the price shock instead, see the $\chi$ channel in §9.

---

## 8. How a simulation unfolds

| Stage | What is shown |
|---|---|
| **Period 0** | The starting equilibrium. $Y = \bar{Y}$, $\pi = \pi^a$, $r = r^a$ — everything at rest. |
| **Period 1** — *the impact* | The shock arrives. **Output moves, inflation does not**, since it is predetermined. The simulation pauses here so that the short run can be examined. |
| **Adjustment** | Select **Continue**. The output gap moves inflation in each period, and the economy slides along AD. |
| **Long run** | Output returns to $\bar{Y}$. Inflation settles at $\pi^a$ under a hard peg, and at the crawling-peg rate $\pi^*$ otherwise. |

**A useful exercise:** run the *same* shock in all three regimes and compare the results.
**🔖 Remember this run** fixes one path in grey, so that the regime can be changed and the
run repeated; the difference between the two lines is the main result of the chapter.

---

## 9. Imported inflation, $\chi$ — the §5.5 extension

Setting $\chi > 0$ at the **Advanced** level extends the role of the exchange rate beyond
quantities. A movement in $w^r$ then also moves the price index directly, because imported
goods form part of that index.

Consider the example given in the book: **contractionary monetary policy under a float**.
The currency appreciates sharply on impact. With $\chi = 0$ this only reduces net exports,
and the result is a deep contraction ($Y_1 = 0.40$). With $\chi = 0.5$ the appreciation
*also* makes imports cheaper, so inflation falls immediately rather than waiting for the
output gap; and since the central bank observes lower inflation, a smaller contraction is
required ($Y_1 = 0.60$, $\pi_1 = 2.80$).

> **The conclusion of §5.5:** allowing for imported inflation *increases* the effect of
> monetary policy on inflation and *reduces* its effect on output.

Two further points are worth noting:

- **The long run does not move.** Once $w^r$ has stopped changing the $\chi$ term is zero,
  so $\pi^*$ and $\bar Y$ are exactly where they were.
- **Full crowding out becomes partial.** Under a float a fiscal expansion appreciates the
  currency, which now *lowers* measured inflation and allows the central bank to accept
  higher output, so $Y_1 > \bar Y$ rather than exactly $\bar Y$. This is a genuine
  implication of $\chi$, and it is why chapters 4–5.4 — and the table in §6 — are stated
  for $\chi = 0$.

---

### A simplification worth knowing about

The FX curve used here is the horizontal line $r = r^a$, which assumes that investors
expect today's real exchange rate to persist. Book §4.7 and §5.2 relax this assumption. If
investors *anticipate* the real appreciation that a contraction under a peg brings, then
$w^{r,e}_{+1}/w^r > 1$ requires $r > r^a$, so the point $P_o$ without sterilisation lies
**above** the FX curve and further to the left, and the contraction is deeper still. The
book treats this as an important finding: an exchange-rate peg without sterilisation makes
an economy *more* vulnerable to a collapse in demand. This application reproduces the
ranking — the contraction under the hard peg is deeper than under the sterilised peg — but
not the additional amplification.

---

### The five equations, together

$$Y = \omega - \varphi\, r + \psi\, w^r \qquad\text{(IS)}$$
$$r = r' + \lambda_P\,\tilde Y + \lambda_I\,\pi \qquad\text{(MP)}$$
$$r = r^a \qquad\text{(FX — binds except under sterilisation)}$$
$$\pi_{t+1} = \pi_t + \gamma\,\tilde Y_t + \chi\,(w^r_{t+1}-w^r_t) + \eta \qquad\text{(IA)}$$
$$\pi \to \pi^a \quad\text{or}\quad \pi \to \pi^* \qquad\text{(PPP vs. crawling peg)}$$

*Based on the consensus model of Lambsdorff & Giamattei, chapter 5.*
"""

peg_no_ster = """🏛️ **Hard peg — fiscal policy is fully effective:** the money supply
accommodates, so output moves by the full IS multiplier before the real
exchange rate slowly crowds it out."""

peg_ster = """🏛️ **Sterilised peg — fiscal policy is effective but damped:** the bank's own
MP rule raises r as output rises, so the impact is smaller than without
sterilization. Crowding out still arrives via the trade balance, as domestic
prices outrun foreign ones (wʳ ↓)."""

no_peg_nor_ster = """🏛️ **Float — fiscal policy is crowded out:** the currency appreciates (wʳ ↓)
and net exports fall, so output and inflation are unchanged."""

foreign_neutralised_text = """🏛️ **Fixed peg, with sterilization:** the bank sterilises the reserve flows, so
the real economy is insulated — the change in rᵃ does not reach it. Reserves,
however, move continuously (see the warning below)."""

monetary_neutralised_text = """🏛️ **Fixed peg, no sterilization:** monetary policy has no effect — reserve
flows tie r to rᵃ, so the change in r' does not reach the economy."""
