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

iteration_count = 40




neg_inflation_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Upward Inflation Shock 📈
</div>

<div style="font-size:13px; color:gray;">
    Usually an external supply shock — a sudden increase in production costs or prices (e.g. the 1970s oil crisis). Inflation rises while output falls below potential.
    <br><br>
    In the short run, the central bank often raises interest rates to control inflation, making borrowing more expensive and reducing demand further. Over time, lower demand helps reduce inflation, and output gradually returns to its potential level.
</div>
"""

pos_monetary_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Expansionary Monetary Shock 🏦
</div>

<div style="font-size:13px; color:gray;">
    An unexpected expansionary monetary policy shock — the central bank lowers nominal interest rates. Borrowing becomes cheaper, and in the short run the real interest rate also decreases. Investment and consumption increase, pushing output above potential.
    <br><br>
    In the long run, higher demand increases inflation, which gradually raises the real interest rate again and brings output back to the potential level.
</div>
"""

pos_demand_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Expansionary Demand Shock 🛒
</div>

<div style="font-size:13px; color:gray;">
    A sudden increase in aggregate demand caused by higher consumption, investment, government spending, or exports.
    <br><br>
    In the short run, output rises above potential. As demand increases, inflation also rises. The central bank responds by increasing interest rates, slowing economic activity and gradually bringing output back to its potential level.
</div>
"""

pos_inflation_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Downward Inflation Shock 📉
</div>

<div style="font-size:13px; color:gray;">
    A favourable supply-side development — falling commodity prices, a technological improvement, or easing supply-chain pressures — pushes inflation below its equilibrium level while output rises above potential.
    <br><br>
    The central bank, seeing inflation below target, typically lowers interest rates to support demand. Over time, rising demand gradually brings inflation back to the equilibrium level.
</div>
"""

neg_monetary_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Contractionary Monetary Shock 🏦
</div>

<div style="font-size:13px; color:gray;">
    An unexpected contractionary monetary policy shock — the central bank raises the nominal interest rate. Borrowing becomes more expensive, and in the short run the real interest rate also increases. Investment and consumption fall, pushing output below potential.
    <br><br>
    In the long run, weaker demand reduces inflation, which gradually lowers the real interest rate again and brings output back to the potential level.
</div>
"""

neg_demand_shock = """
<div style="text-align:center; font-size:17px; font-weight:700;">
    Contractionary Demand Shock 🛒
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

# ―――― Open-economy consensus model ――――――――――――――――
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
A one-off jump in import prices from abroad passes straight into domestic prices — the χ·Δwʳ term of eq. (5.2) — shifting the IA-curve up <b>even with no output gap</b>. It is modelled here as an exogenous one-off shift of IA; it lands once and is then inherited by later periods.
<br><br>
Inflation jumps above foreign inflation πᵃ. Output falls below potential, and the negative output gap brings inflation back down to πᵃ.
<br><br>
<i>Reading the wʳ chart:</i> the line you see is the economy's <b>response</b>, not the shock. Higher inflation with the interest rate tied to rᵃ means the currency must strengthen (wʳ ↓) — under a peg because domestic prices outrun foreign ones, under a float because the currency appreciates. The shock itself comes from abroad and is not drawn.
</div>""",
    'Imported Deflation Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Imported Deflation Shock 📉</div>
<div style="font-size:13px; color:gray;">
A one-off fall in import prices from abroad passes straight into domestic prices — the χ·Δwʳ term of eq. (5.2) — shifting the IA-curve down <b>even with no output gap</b>. It is modelled here as an exogenous one-off shift of IA; it lands once and is then inherited by later periods.
<br><br>
Inflation drops below foreign inflation πᵃ. Output rises above potential, and the positive output gap brings inflation back up to πᵃ.
<br><br>
<i>Reading the wʳ chart:</i> the line you see is the economy's <b>response</b>, not the shock — lower inflation with r tied to rᵃ means the currency weakens (wʳ ↑). The shock itself comes from abroad and is not drawn.
</div>""",
    'Expansionary Fiscal Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Expansionary Fiscal Shock 🏛️</div>
<div style="font-size:13px; color:gray;">
Higher government demand shifts the IS-curve right (↑ω). What happens next depends entirely on the <b>exchange-rate regime</b>:
<br><br>
<b>Flexible:</b> the currency appreciates (wʳ ↓), net exports fall, and output is <b>fully crowded out</b> — Y and π are unchanged.
<br><br>
<b>Fixed peg:</b> the nominal rate cannot move, so fiscal policy is <b>effective</b> — output jumps above potential (fully without sterilization, damped with it). Crowding out then arrives slowly through the trade balance as domestic prices outrun foreign ones (wʳ ↓), and inflation returns to πᵃ.
</div>""",
    'Contractionary Fiscal Shock': """
<div style="text-align:center; font-size:17px; font-weight:700;">Contractionary Fiscal Shock 🏛️</div>
<div style="font-size:13px; color:gray;">
Lower government demand shifts the IS-curve left (↓ω). The effect depends on the <b>exchange-rate regime</b>:
<br><br>
<b>Flexible:</b> the currency depreciates (wʳ ↑), net exports rise, and the demand cut is <b>fully crowded out</b> — Y and π are unchanged.
<br><br>
<b>Fixed peg:</b> fiscal policy is <b>effective</b> — output falls below potential, then real depreciation (wʳ ↑) slowly restores it and inflation returns to πᵃ.
</div>""",
    None: placeholder_shock,
}


MARKDOWN_THEORY = r"""
## The Open Economy — a guided tour

In the **closed** economy, a country trades with nobody. Everything it produces, it
consumes itself. That is a useful simplification, but no real country works that way.

Once you **open** the economy, two new doors appear in the wall:

- **A goods door** — we can sell things abroad (exports) and buy things from abroad
  (imports).
- **A money door** — savers can move their money abroad chasing a better interest
  rate, and foreigners can move money in.

Almost everything interesting in this model comes from one question:
**what happens at those two doors when something changes?**

---

## 1. The exchange rate is the hero of this story

Before anything else, meet the variable that does most of the work: the **real
exchange rate**, written $w^r$.

Think of $w^r$ as *"how expensive foreign goods are for us."*

| If $w^r$ goes **up** | If $w^r$ goes **down** |
|---|---|
| Our currency is **weaker** (depreciation) | Our currency is **stronger** (appreciation) |
| Foreign goods look expensive to us | Foreign goods look cheap to us |
| Foreigners find our goods cheap → **exports rise** | Foreigners find our goods dear → **exports fall** |
| **Demand for our output rises** | **Demand for our output falls** |

> **The one sentence to remember:** a *weaker* currency ($w^r \uparrow$) *boosts*
> demand for what we make; a *stronger* currency ($w^r \downarrow$) *dampens* it.

There are two different exchange rates hiding in that one symbol, and the difference
matters enormously later:

- The **nominal** rate — the number on the currency-exchange board. A central bank
  can pin this one down by decree if it wants to.
- The **real** rate $w^r$ — the nominal rate *adjusted for prices at home and abroad*.
  Even if the nominal rate is frozen, $w^r$ still moves whenever our inflation
  differs from theirs. **You can freeze a price. You cannot freeze a price
  difference.** That single fact drives the whole second half of this page.

---

## 2. The five building blocks

The model is five relationships. Read each as a sentence first; the algebra is just
the same sentence written compactly.

#### IS — where does demand come from?

*"We produce more when borrowing is cheap and when our currency is weak."*

$$Y = \omega - \varphi\, r + \psi\, w^r$$

| Symbol | Plain meaning |
|---|---|
| $Y$ | Output (GDP) — how much we produce |
| $\omega$ | Baseline demand. **Government spending lives here** — this is our fiscal-policy lever |
| $\varphi$ | How strongly high interest rates choke off investment |
| $\psi$ | How strongly a weak currency boosts net exports |

The $\psi\, w^r$ term is the **only** new piece versus the closed economy — but it
changes everything.

#### MP — what does the central bank do?

*"Raise rates when the economy overheats or inflation climbs."*

$$r = r' + \lambda_P \tilde{Y} + \lambda_I \pi$$

where $\tilde{Y} = (Y - \bar{Y})/\bar{Y}$ is the **output gap** — how far we are from
what the economy can sustainably produce, $\bar{Y}$. The lever $r'$ is the bank's
overall stance: **lower $r'$ = looser policy**.

#### FX — why can't we choose our own interest rate?

*"Money chases the best return, so our rate gets dragged to the world rate."*

$$r = r^a$$

If our rate sat above the world rate $r^a$, foreign money would flood in until
something gave. This is the **capital-mobility** constraint. Whether it truly binds
turns out to depend on the exchange-rate regime — that is section 4.

#### IA — how does inflation move?

*"Inflation is sticky today, and drifts based on whether we're running hot or cold."*

$$\pi_{t+1} = \pi_t + \gamma \tilde{Y}_t + \chi\,(w^r_{t+1} - w^r_t) + \eta$$

Two crucial features:

1. **Inflation is predetermined.** Today's inflation was set by yesterday's
   conditions. It cannot leap the instant a shock lands — wages and contracts are
   already signed. This is why *output* moves first and *inflation* follows.
2. **The output gap is the engine.** Running above capacity ($\tilde{Y}>0$) pushes
   inflation up; running below pushes it down. Inflation only stops moving when
   output is back at potential.

The $\chi$ term is **imported inflation** (§5.5): when the currency weakens, imports
cost more and that feeds straight into the price index, with no output gap needed.
$\chi$ is large for a consumer price index (which contains imported final goods) and
small for the GDP deflator (which does not). It is an **extension** — every headline
result below is derived with $\chi = 0$, which is why it defaults to zero and appears
only at the Advanced level. Section 9 explains what changes when you switch it on.

#### PPP — where does inflation eventually settle?

*"In the long run, a fixed currency forces your inflation to match theirs."*

Purchasing Power Parity is the anchor $\pi^a$ (foreign inflation) shown as the grey
dashed line. Whether your inflation actually returns to it is **exactly** what
separates the three regimes.

---

## 3. Reading the two diagrams

**Top chart — the $r$–$Y$ diagram (interest rates)**

Where IS, MP and FX meet tells you output and the interest rate. Watch the
<span style="color:#4C78A8;">**IS**</span> line slide sideways: that movement *is*
the exchange rate doing its job.

**Bottom chart — the $\pi$–$Y$ diagram (inflation)**

- The <span style="color:#B279A2;">**AD**</span> curve (downward sloping) is the whole
  top diagram compressed into one line: *for each inflation rate, what output results
  once the central bank and the exchange rate have reacted?*
- The <span style="color:#54A24B;">**IA**</span> curve is flat because inflation is
  predetermined — it is *today's* inflation, and it cannot move today.

**So a run reads like this:** the shock hits, AD shifts, and the economy jumps
**sideways** along the flat IA line (output moves, inflation cannot). Then, period by
period, the output gap drags IA up or down, and the economy **slides along AD** until
output is back at $\bar{Y}$.

Once a run starts, the faint pale curves are the **short-run** position (period 1) and
the bright ones are **where things stand now** — so you can always see how far the
economy has travelled.

---

## 4. The three regimes — you can't have everything

Here is the central idea of open-economy macro, and the reason for the regime switch
in the sidebar. A country wants three things:

1. A **stable exchange rate**
2. **Free movement of capital** across borders
3. An **independent monetary policy** (setting rates for domestic needs)

**You can only ever have two.** This is the *impossible trinity*. Each regime in this
app is a different choice about which one to sacrifice.

### 🌊 Flexible — give up the stable exchange rate

Let the currency float. Capital moves freely, so $r = r^a$ binds.

The currency becomes a **shock absorber** — and it is *so* good at its job that it
completely neutralises fiscal policy. Spend more, and the resulting inflow makes the
currency stronger, exports fall by exactly what the spending added.
**Fiscal policy is fully crowded out.**

### 🔒 Fixed, no sterilization — give up monetary independence

Promise to hold the exchange rate and let money flow. To defend the peg the central
bank must buy and sell currency, which changes the domestic money supply — and the
domestic interest rate gets dragged to $r^a$ whether the bank likes it or not.

**Monetary policy becomes completely powerless.** Change $r'$ and *nothing happens* —
the app will tell you so.

But now the currency can no longer absorb anything, so **fiscal policy becomes
maximally powerful** — the full effect lands on output.

Adjustment happens through the *real* rate. If our inflation runs above theirs, our
goods slowly become expensive, exports slowly fall, and output slowly cools — until
inflation is back at $\pi^a$. **PPP wins in the end.** It is slow, because it works
through price differences accumulating, not through a rate that can jump.

### 🛡️ Fixed, with sterilization — try to have all three

Here the bank defends the peg **and** cancels out the money-supply side effects
("sterilises" them) so it can still set its own interest rate.

For a while this works: the exchange rate is stable and monetary policy still bites.
The economy is even **insulated from foreign interest-rate shocks** — change $r^a$ and
nothing happens to output or inflation at home.

But the peg is still a peg, and that has an unavoidable consequence:

> **The peg identity.** By definition $w^r = w\,p^a/p$. If the nominal rate $w$ is
> held fixed and our inflation exceeds theirs, $w^r$ *must* keep falling — forever.
> Things can only come to rest when $w^r$ stops moving, and that happens only when
> $\pi = \pi^a$. **A pegged country cannot end up with an inflation rate of its own,**
> sterilised or not.

So in *this model* sterilisation changes the interest rate and the *speed* of
adjustment — not the destination. Inflation still returns to $\pi^a$, and crowding out
still arrives, just through the **trade balance** rather than through the exchange rate
jumping.

And you cannot cheat the trinity forever. In the long run the bank's own rule leaves
$r = r' + \lambda_I \pi^a$. If it changed $r'$ (or if $r^a$ moved), that is *not* equal
to $r^a$ — so capital keeps flowing and reserves drain without limit. The peg must
eventually break, or become a genuine **crawling peg**. The app warns you when the
scenario you have chosen is in that position.

> ⚠️ **Where this app and the book differ — read this before quoting a long run.**
> For a **monetary** (or foreign-rate) shock under the **sterilised peg**, book §5.3
> gives a *different* long run from the one simulated here. The book holds $w^r$ still,
> lets inflation do all the adjusting, and lands at
> $$P_\infty:\quad \pi^* = \frac{r^a - r'}{\lambda_I},\qquad r \to r^a$$
> — i.e. **the same long run as the float**, reached only by converting the peg into a
> crawling peg. Its words: *"The difference between fixed and flexible exchange rates
> is, therefore, not in the long-run equilibrium but in the adjustment path."*
>
> This app instead lets $w^r$ drift (the peg identity above), so inflation returns to
> $\pi^a$ and it is the *interest rate* that ends up off-parity. Both are internally
> consistent; they differ in **which variable is assumed to give way** while the peg is
> held. What you see here is the *while-the-peg-lasts* path. The book's $P_\infty$
> needs a fourth regime — a genuine crawling peg — which is not implemented yet.
>
> Note this affects **only** the sterilised peg after a monetary or foreign-rate shock.
> For demand shocks the book uses the same $w^r$ drift this app does (§5.2), and both
> agree that inflation returns to $\pi^a$.

---

## 5. The crawling peg

This is the idea the model is really built to show, so it is worth being precise.

Suppose our inflation settles at 3.6% and the world's stays at 3%. Every year our
goods get about 0.6% more expensive relative to theirs. If the nominal rate were truly
frozen, our exports would be slowly strangled.

So the central bank lets the nominal exchange rate **depreciate by exactly that 0.6%
per year** — it *crawls*. The real exchange rate then holds perfectly still, and
competitiveness is preserved forever.

$$\pi^* = \frac{r^a - r'}{\lambda_I} \neq \pi^a \qquad \text{nominal rate crawls at } \pi^* - \pi^a$$

> **The punchline:** with a crawling peg, a country **keeps its own inflation rate
> permanently**, different from the world's. Monetary policy has a *lasting* effect on
> inflation — it does not get dragged back to $\pi^a$. That is exactly what "monetary
> policy ends in a crawling peg" means.

This is the crucial distinction from a *fixed* peg. Under a genuine nominal peg the
peg identity above forces $\pi \to \pi^a$; only by letting the nominal rate move — a
float, or a crawl — can a country hold on to an inflation rate of its own. In this
model the **Flexible** regime is the one that ends in a crawling peg; both fixed
regimes end at $\pi^a$ — with the caveat in the box above, since book §5.3 puts the
sterilised peg's monetary-shock long run here at $\pi^*$ too, not at $\pi^a$.

Look for the **π\*** reference line in the inflation chart: under a float it sits
*away* from the grey PPP line, and inflation converges to it rather than to $\pi^a$.

---

## 6. Which policy works where?

Same shock, three regimes, three completely different outcomes. Try these yourself —
the period-1 output numbers below are exactly what the app produces.

| | 🌊 Flexible | 🔒 Fixed, no steril. | 🛡️ Fixed, sterilised |
|---|---|---|---|
| **Fiscal policy** (spend more) | ❌ Fully crowded out — nothing happens | ✅ **Strongest of all** | ⚠️ Works, but damped |
| *period-1 output* | $1.00$ (unchanged) | $1.50$ | $1.33$ |
| **Monetary policy** (cut rates) | ✅ Works, permanently | ❌ **Powerless** | ✅ Works, permanently |
| *period-1 output* | $1.60$ | $1.00$ (nothing) | $1.20$ |
| **Foreign rate rises** | Expansionary $(1.60)$ | **Contractionary** $(0.70)$ | Insulated $(1.00)$ |
| **Inflation ends at** | crawling peg $\pi^* \neq \pi^a$ | $\pi^a$ (the peg identity) | $\pi^a$ here — but see the box in §4; book §5.3 puts it at $\pi^*$, and the peg is not sustainable either way |

One more row is worth adding, because it is the whole point of the sterilised peg:

| | 🌊 Flexible | 🔒 Fixed, no steril. | 🛡️ Fixed, sterilised |
|---|---|---|---|
| **Is the regime sustainable?** | yes | yes | **only until reserves run out** |

Three results usually surprise people, and all are worth pausing on:

- **Fiscal and monetary policy are mirror images.** Whichever regime makes one
  powerful makes the other useless. A floating currency kills fiscal policy; a hard
  peg kills monetary policy.
- **A foreign rate rise flips sign between regimes.** Floating, our currency weakens
  and exports boom, so output *rises*. Pegged, the currency cannot weaken — we simply
  import the higher interest rate and output *falls*.
- **Sterilisation changes the journey, not the destination.** Because the nominal rate
  is still pegged, inflation ends at $\pi^a$ just as it does under the hard peg. What
  sterilisation buys is a temporarily independent interest rate — and the price is that
  the peg eventually becomes indefensible.

---

## 7. The shocks, one by one

**🏛️ Fiscal (↑ or ↓ $\omega$)** — the government spends more or less. IS shifts.
Effect depends entirely on the regime; see the table above.

**🏦 Monetary (↓ or ↑ $r'$)** — the central bank loosens or tightens. Under a float or
a sterilised peg it moves output now and inflation permanently. Under a hard peg,
nothing at all.

**🌍 Foreign interest rate (↑ or ↓ $r^a$)** — the rest of the world changes its rate.
Note the sign flip described above, and that sterilisation blocks it entirely.

**📈📉 Imported inflation / deflation** — a one-off jump in import prices pushes
inflation up (or down) *directly*, with no output gap needed. This is the one shock
that hits the IA curve first rather than the AD curve. Output then dips and the gap
slowly squeezes inflation back down.

Careful when reading the $w^r$ chart for these two: the line is the economy's
**response**, not the shock. The shock arrives from abroad and is applied to the IA
curve; the currency then *strengthens* ($w^r \downarrow$) because higher inflation with
$r$ tied to $r^a$ can only be reconciled by a stronger real exchange rate. If you want
the exchange rate itself to be the *source* of the price shock, that is the $\chi$
channel in §9.

---

## 8. How a simulation unfolds

| Stage | What you are looking at |
|---|---|
| **Period 0** | The calm before. $Y = \bar{Y}$, $\pi = \pi^a$, $r = r^a$ — everything at rest. |
| **Period 1** — *the impact* | The shock lands. **Output jumps, inflation does not** (it is predetermined). The app pauses here on purpose so you can study the short run. |
| **Adjustment** | Press **Continue**. The output gap pushes inflation each period; the economy slides along AD. |
| **Long run** | Output returns to $\bar{Y}$. Inflation settles at $\pi^a$ under a hard peg, or at the crawling peg $\pi^*$ otherwise. |

**Getting the most out of it:** run the *same* shock in all three regimes and compare.
Use **🔖 Remember this run** to freeze one path in grey, switch regime, and run
again — the difference between the two lines is the whole lesson of this chapter.

---

## 9. Imported inflation, $\chi$ — the §5.5 extension

Set $\chi > 0$ at the **Advanced** level and the exchange rate stops being only a
quantity story. Now a movement in $w^r$ also moves the price index directly, because
imported goods are *in* that index.

Take the book's own example: a **contractionary monetary policy under a float**. The
currency appreciates sharply on impact. With $\chi = 0$ that only cuts net exports, and
you get a deep depression ($Y_1 = 0.40$). With $\chi = 0.5$ the appreciation *also*
makes imports cheaper, so inflation falls immediately instead of waiting for the output
gap — and because the central bank sees lower inflation, it does not need as deep a
slump ($Y_1 = 0.60$, $\pi_1 = 2.80$).

> **§5.5's conclusion:** recognising imported inflation *increases* the impact of
> monetary policy on inflation and *reduces* its impact on output.

Two things worth noticing when you turn it on:

- The **long run does not move.** Once $w^r$ stops changing, the $\chi$ term is zero, so
  $\pi^*$ and $\bar Y$ are exactly where they were.
- **Full crowding out becomes partial.** Under a float a fiscal expansion appreciates
  the currency, which now *lowers* measured inflation, which lets the central bank
  tolerate more output. So $Y_1 > \bar Y$ instead of exactly $\bar Y$. This is a real
  implication of $\chi$, and it is why chapters 4–5.4 — and the table in §6 — are stated
  for $\chi = 0$.

---

### A simplification worth knowing about

The FX curve here is $r = r^a$ flat, i.e. investors expect today's real exchange rate to
persist. Book §4.7 and §5.2 relax this. If investors *anticipate* the real appreciation
that a slump under a peg will bring, then $w^{r,e}_{+1}/w^r > 1$ requires $r > r^a$, so
the no-sterilisation point $P_o$ sits **above** the FX curve and further left — the
depression is deeper still. The book calls this an important finding: an exchange rate
peg without sterilisation makes an economy *more* vulnerable to a demand collapse. This
app reproduces the ranking (the hard peg's slump is deeper than the sterilised one) but
not the extra amplification.

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

peg_ster = """🏛️ **Sterilised peg — fiscal policy is effective but damped:** the CB's own 
MP rule raises r as output rises, so the impact is smaller than without 
sterilization. Crowding out still arrives via the trade balance, as domestic 
prices outrun foreign ones (wʳ ↓)."""

no_peg_nor_ster = """🏛️ **Float — fiscal policy is crowded out:** the currency appreciates (wʳ ↓)
and net exports fall, so output and inflation are unchanged."""

foreign_neutralised_text = """🏛️ **Fixed peg, with sterilization:** the CB sterilises the reserve flows, so 
the real economy is insulated — the change in rᵃ does not reach it. Reserves, 
however, move continuously (see the warning below)."""

monetary_neutralised_text = """🏛️ **Fixed peg, no sterilization:** monetary policy is powerless — reserve
flows tie r to rᵃ, so the change in r' has no effect."""