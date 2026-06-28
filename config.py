# Letters to copy: 𝜓 ç 𝜔


markdown_text = r"""
## Model Overview

This model describes a closed economy through four curves that jointly determine output $Y$ and inflation $\pi$ in each period. The economy starts at a long-run equilibrium, is hit by a shock in period 1, and then adjusts back to equilibrium over time.

---

### Curve Definitions

**IS curve** — *Investment–Savings*

Describes the goods market: output $Y$ is a decreasing function of the real interest rate $r$. Higher rates discourage investment and consumption, reducing output.
$$
Y = \omega - \phi \, r \qquad \phi > 0
$$

| Parameter | Meaning |
|-----------|---------|
| $\omega$ | Autonomous demand (shifts IS right/left) |
| $\phi$ | Sensitivity of output to the interest rate |

---

**MP curve** — *Monetary Policy*

The central bank sets the real interest rate in response to the output gap $\tilde{Y} = \frac{Y - \bar{Y}}{\bar{Y}}$ and inflation $\pi$. Higher output or higher inflation leads to a higher rate.
$$
r = r' + \lambda_P \tilde{Y} + \lambda_I \pi \qquad r' > 0,\ \lambda_P \ge 0,\ \lambda_I \ge 0
$$

| Parameter | Meaning |
|-----------|---------|
| $r'$ | Baseline (neutral) real interest rate |
| $\lambda_P$ | Response to output gap |
| $\lambda_I$ | Response to inflation |

---

**IA curve** — *Inflation Adjustment*

The IA curve captures the current level of inflation expectations and price stickiness. In the **short run** (period 1), it is a horizontal line at the shocked inflation level $\pi_0$ — prices do not immediately adjust to the new economic conditions:
$$
\pi_t = \pi_0 \qquad \text{(short run, } t = 1\text{)}
$$

In the **long run**, the IA curve shifts each period based on the output gap and any persistent exogenous price shock — if output exceeds potential, firms raise prices and inflation increases; if output is below potential, inflation falls:
$$
\boxed{\pi_{t+1} = \pi_t + \gamma \cdot \tilde{Y}_t + \eta = \pi_t + \gamma \cdot \frac{Y_t - \bar{Y}}{\bar{Y}} + \eta}
$$

| Parameter | Meaning |
|-----------|---------|
| $\gamma$ | Speed of inflation adjustment (higher $\gamma$ → faster convergence) |
| $\tilde{Y}_t$ | Output gap in period $t$ |
| $\eta$ | Exogenous price shock — price changes not driven by producer or worker behaviour (e.g. crop failures, raw material shortages, VAT changes). Applied persistently each period. |

The IA curve shifts **upward** when $Y_t > \bar{Y}$ or $\eta > 0$, and **downward** when $Y_t < \bar{Y}$ or $\eta < 0$. It stops moving only when both $Y_t = \bar{Y}$ and $\eta = 0$, which defines the long-run equilibrium.

**Phillips Curve** — *IA with current output gap*

The IA equation uses the *previous* period's output gap — by the time we draw the diagram, next-period inflation is already determined, so the IA appears as a **horizontal line**. The Phillips curve is the same equation, but asks: *if current output were $Y$, what would next-period inflation be?*

$$
\pi_{t+1} = \pi_t + \gamma \cdot \frac{Y - \bar{Y}}{\bar{Y}}
$$

Rearranging as a function of $Y$:

$$
\pi_{t+1} = \underbrace{\frac{\gamma}{\bar{Y}}}_{\text{slope}} \cdot Y + \underbrace{(\pi_t - \gamma)}_{\text{intercept}}
$$

This is an **upward-sloping line** in $\pi$–$Y$ space, anchored at $(\bar{Y},\, \pi_t)$: when output equals potential there is no gap, so inflation is unchanged. The IA curve is simply the Phillips curve *evaluated at last period's $Y$* and then frozen — the horizontal line shows the value the Phillips curve delivered one period ago.

Toggling the Phillips curve in the diagram lets you see both: the sloped curve shows the full relationship between current output and future inflation, while the horizontal IA shows the single point on that curve that the economy actually delivered.

---

**AD curve** — *Aggregate Demand*

Derived by combining the IS and MP curves, the AD curve expresses inflation as a function of output. It captures how monetary policy transmits demand conditions into inflationary pressure, and has a **negative slope** — higher output is associated with lower inflation (the central bank raises rates to cool demand).

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

The economy returns to equilibrium when $\pi_{t+1} = \pi_t$, which requires $Y_t = \bar{Y}$. The long-run equilibrium inflation $\pi^*$ is the value at which the AD curve crosses the potential output line $Y = \bar{Y}$:
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

iteration_count = 30




neg_inflation_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Negative Inflation Shock 📈
</div>

<div style="font-size:13px; color:gray;">
    Usually an external supply shock — a sudden increase in production costs or prices (e.g. the 1970s oil crisis). Inflation rises while output falls below potential.
    <br><br>
    In the short run, the central bank often raises interest rates to control inflation, making borrowing more expensive and reducing demand further. Over time, lower demand helps reduce inflation, and output gradually returns to its potential level.
</div>
"""

pos_monetary_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Positive Monetary Shock 🏦
</div>

<div style="font-size:13px; color:gray;">
    An unexpected expansionary monetary policy shock — the central bank lowers nominal interest rates. Borrowing becomes cheaper, and in the short run the real interest rate also decreases. Investment and consumption increase, pushing output above potential.
    <br><br>
    In the long run, higher demand increases inflation, which gradually raises the real interest rate again and brings output back to the potential level.
</div>
"""

pos_demand_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Positive Demand Shock 🛒
</div>

<div style="font-size:13px; color:gray;">
    A sudden increase in aggregate demand caused by higher consumption, investment, government spending, or exports.
    <br><br>
    In the short run, output rises above potential. As demand increases, inflation also rises. The central bank responds by increasing interest rates, slowing economic activity and gradually bringing output back to its potential level.
</div>
"""

pos_inflation_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Positive Inflation Shock 📉
</div>

<div style="font-size:13px; color:gray;">
    A favourable supply-side development — falling commodity prices, a technological improvement, or easing supply-chain pressures — pushes inflation below its equilibrium level while output rises above potential.
    <br><br>
    The central bank, seeing inflation below target, typically lowers interest rates to support demand. Over time, rising demand gradually brings inflation back to the equilibrium level.
</div>
"""

neg_monetary_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Negative Monetary Shock 🏦
</div>

<div style="font-size:13px; color:gray;">
    An unexpected contractionary monetary policy shock — the central bank raises the nominal interest rate. Borrowing becomes more expensive, and in the short run the real interest rate also increases. Investment and consumption fall, pushing output below potential.
    <br><br>
    In the long run, weaker demand reduces inflation, which gradually lowers the real interest rate again and brings output back to the potential level.
</div>
"""

neg_demand_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Negative Demand Shock 🛒
</div>

<div style="font-size:13px; color:gray;">
    A sudden fall in aggregate demand caused by lower consumer confidence, reduced investment, fiscal austerity, or a drop in exports.
    <br><br>
    In the short run, output falls below potential. As demand weakens, inflation also falls. The central bank responds by cutting interest rates, stimulating economic activity and gradually bringing output back to its potential level.
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
    Either an external positive supply shock or a government increase in public spending or reduction in taxes.
</div>
"""

omega_text_res = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Negative Supply Shock (ω < 4) 🏛️
</div>

<div style="font-size:13px; color:gray;">
    Either a negative external event leading to an increase in world prices or a government reduction in aggregate demand through lower spending or higher taxes.
</div>
"""


# ---------- Monetary Policy (r) ----------
r_text_con = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Contractionary Monetary Policy (r > 2.3) 💰
</div>

<div style="font-size:13px; color:gray;">
    The central bank raises interest rates and tightens financial conditions.
    Borrowing and investment decline, slowing inflation and aggregate demand.
</div>
"""

r_text_exp = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Expansionary Monetary Policy (r < 1.7) 💰
</div>

<div style="font-size:13px; color:gray;">
    The central bank lowers interest rates and increases liquidity in the economy.
    Credit conditions improve, stimulating consumption, investment, and output.
</div>
"""


# ---------- Inflation Shock (pi) ----------
pi_text_inf = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Upward Inflation Shock (η > 0) 📈
</div>

<div style="font-size:13px; color:gray;">
    Inflation starts above its long-run equilibrium — caused by supply disruptions, rising
    production costs, or commodity price increases. Inflation accelerates while real
    purchasing power declines. The economy adjusts back as the central bank tightens policy.
</div>
"""

pi_text_def = """
<div style="font-size:17px; font-weight:700; color:#222;">
    Downward Inflation Shock (η < 0) 📉
</div>

<div style="font-size:13px; color:gray;">
    Inflation starts below its long-run equilibrium — caused by weak demand or falling costs.
    Economic activity may weaken as firms reduce production and investment.
    The economy adjusts back as monetary policy eases.
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


# \frac{\omega}{\phi} - \frac{1}{\phi} Y = r' - \lambda_P \bar{Y} + \lambda_I \pi + \lambda_P Y  \\
# \lambda_I \pi = - r' + \lambda_P \bar{Y}  - \lambda_P Y + \frac{\omega}{\phi} - \frac{1}{\phi} Y \\
# \pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} - \frac{\lambda_P}{\lambda_I} Y
#               + \frac{\omega}{\phi \lambda_I} - \frac{1}{\phi \lambda_I} Y \ \
#  \
#     \pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} + \frac{\omega}{\phi \lambda_I} - \frac{\lambda_P}{\lambda_I} Y - \frac{1}{\phi \lambda_I} Y \\
#
# \pi = - \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y}  + \frac{\omega}{\phi \lambda_I} + (- \frac{\lambda_P}{\lambda_I} - \frac{1}{\phi \lambda_I}) Y\\
#
#
# \pi =\underbrace{\left(- \frac{r'}{\lambda_I} + \frac{\lambda_P}{\lambda_I}\bar{Y} + \frac{\omega}{\phi \lambda_I}\right)}_{\text{intercept}} +
# \underbrace{\left( - \frac{\lambda_P}{\lambda_I} - \frac{1}{\phi \lambda_I}\right)}_{\text{slope}} \cdot Y
