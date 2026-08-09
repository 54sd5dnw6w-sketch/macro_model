import streamlit as st
import pandas as pd
import time
import plotly.express as px

import config as c
import helpers as h

# ―――― Open-economy consensus model ――――――――――――――――
# Five equations (Lambsdorff & Giamattei, ch. 5, eq. 5.1/5.2):
#   IS : Y = ω − φ·r + ψ·wʳ
#   MP : r = r' + λ_P·Ỹ + λ_I·π
#   FX : r = rᵃ                      (UIP, static expectations)
#   IA : π = π₋₁ + γ·Ỹ₋₁ + χ·(wʳ − wʳ₋₁) + η
#   PPP: long-run domestic inflation converges to foreign inflation πᵃ
#
# Under a FLEXIBLE exchange rate the FX line binds (r = rᵃ). Output is therefore
# pinned by MP∩FX and the real exchange rate wʳ adjusts so IS passes through the
# same point. Consequences:
#   • AD (from MP∩FX):  π = (rᵃ − r' + λ_P)/λ_I − λ_P/(λ_I·Ȳ)·Y
#   • π* = (rᵃ − r')/λ_I      ← ω and ψ drop out ⇒ demand shocks fully crowd out
#   • wʳ = (Y − ω + φ·rᵃ)/ψ
#
# ―――― χ: imported inflation (book §5.5) ――――――――――――――――
# χ is the pass-through of a change in the real exchange rate to domestic prices
# (large for a CPI basket, small for the GDP deflator). It is an EXTENSION: every
# headline result of chapters 4–5.4 — full crowding out under a float above all —
# is derived with χ = 0, which is why χ defaults to 0 here and is offered only at
# the Advanced level. Switching it on reproduces §5.5: under a float the exchange
# rate channel makes inflation adjust faster and the output response smaller.
# Because wʳ and π move together, the χ term is solved SIMULTANEOUSLY with next
# period's inflation (see `ia_next`), exactly as eq. (5.2) is written.

# ―――― Fixed pre-shock baseline (period 0 of the charts) ――――――――――――――――
# Default parameters below give the resting point Y=Ȳ, π=πᵃ=3, r=rᵃ=2, wʳ=1.
PHI_BASE, PSI_BASE, OMEGA_BASE = 1.0, 1.0, 2.0
RP_BASE, LP_BASE, LI_BASE, GAMMA_BASE = 0.5, 0.5, 0.5, 0.5
RA_BASE, PIA_BASE = 2.0, 3.0
WR_BASELINE = (c.Y_potential - OMEGA_BASE + PHI_BASE * RA_BASE) / PSI_BASE   # → 1.0

# ―――― Fixed-peg adjustment speed (BOTH fixed regimes) ――――――――――――――――
# Whenever the NOMINAL rate is pegged, the REAL rate is not free: by definition
# wʳ = w·pᵃ/p, so with w held fixed
#     wʳ_{t+1} / wʳ_t = (1 + πᵃ) / (1 + π_t)
# i.e. wʳ keeps drifting for as long as domestic inflation differs from foreign
# inflation. Modelled linearly as  wʳ_{t+1} = wʳ_t + κ·(πᵃ − π_t).
#
# CONSEQUENCE (the peg identity): a steady state needs wʳ constant, which is only
# possible when π = πᵃ. A pegged economy therefore CANNOT settle at an inflation
# rate of its own. See the "BOOK DIVERGENCE" note further down for what §5.3 says
# about the sterilised peg, where this model and the book part company.
#
# ―――― Why THETA exists (do not remove it) ――――――――――――――――
# THETA is the WITHIN-period pass-through of the inflation gap to wʳ under the
# hard peg:  wʳ_t = S_t − θ·(π_t − πᵃ), where S is the carried-over state. It is
# not decoration — it is the only source of damping that regime has. Under a hard
# peg r is nailed to rᵃ, so the Taylor rule cannot stabilise anything, and the
# system in (π, wʳ) is
#     M = [[1 − γψθ/Ȳ,  γψ/Ȳ],
#          [   −κ,        1  ]]
# whose determinant is 1 − γψθ/Ȳ + γψκ/Ȳ. With θ = κ (a single PPP law) det = 1
# exactly: a harmonic centre that orbits forever and never converges. With θ = 0
# (a vertical AD) det > 1 and the model explodes. Only θ > κ damps it.
#
# κ is therefore DERIVED, not hand-tuned, from the critical-damping condition
# trace² = 4·det, which gives the fastest monotone (non-oscillating) convergence:
#     hard peg    κ = γ·ψ·θ²/(4·Ȳ)
#     sterilised  κ = γ·φ²·λ_I²/(4·Ȳ·D·ψ),  D = 1 + φ·λ_P/Ȳ
# (The sterilised peg has no θ: it gets its AD slope, and its damping, from the
# CB's own MP rule.) Deriving κ is what keeps the tuning correct when γ, ψ, φ or
# λ are changed at the Advanced level — with the old hard-coded κ the pegs went
# silently under- or over-damped.
#
# NOTE ON SPEED: true PPP arithmetic would give Δwʳ ≈ wʳ·(πᵃ−π)/100, ~2 orders of
# magnitude slower — a real "internal devaluation" takes decades. θ (and hence κ)
# is deliberately fast so the adjustment is visible in a 30-period run; treat a
# period as a long span of time, not a year.
THETA_PEG = 0.8


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
    None: c.placeholder_shock,
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
                          help=("Flexible: r = rᵃ; fiscal is crowded out; monetary/foreign-rate shocks "
                                "end in a crawling peg (π* ≠ πᵃ). "
                                "Fixed – no sterilization: r tied to rᵃ so monetary policy is powerless, "
                                "fiscal is fully effective, and PPP returns π to πᵃ. "
                                "Fixed – with sterilization: the CB keeps its own r, so the economy is "
                                "insulated from rᵃ and fiscal works (damped). The nominal peg still holds, "
                                "so wʳ drifts until π = πᵃ — which leaves r off parity and the peg "
                                "indefensible. NOTE: book §5.3 instead holds wʳ still and ends at "
                                "π* = (rᵃ − r')/λ_I via a crawling peg; see the Theory tab."))

    st.sidebar.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    # ―――― Parameter Inputs ――――――――――――――――
    # Structural defaults (overridden in Advanced)
    phi = PHI_BASE; psi = PSI_BASE; lambda_p = LP_BASE; lambda_i = LI_BASE
    gamma = GAMMA_BASE; pi_foreign = PIA_BASE; eta = 0.0; inflation_shock = 0.0
    omega = OMEGA_BASE; r_init = RP_BASE; r_foreign = RA_BASE; pi_0_override = None
    chi = 0.0                      # imported-inflation pass-through (§5.5) — Advanced only

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
                                    help="One-off shift of the IA-curve (χ·Δwʳ). Positive = imported inflation, negative = imported deflation.")

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
                                          help="One-off exogenous shift of the initial IA level — an import-price "
                                               "jump arriving from abroad. Lands once and is inherited thereafter.")
        chi = st.number_input(r'$\chi$ (imported inflation):', on_change=reset, min_value=0.0, max_value=2.0,
                              step=0.1, value=0.0, key="oe_a_chi",
                              help=r"Pass-through of a change in the real exchange rate to domestic prices, "
                                   r"eq. (5.2): $\pi_{t+1} = \pi_t + \gamma\tilde Y_t + \chi(w^r_{t+1}-w^r_t) + \eta$. "
                                   r"Large for a CPI basket, small for the GDP deflator. This is the §5.5 "
                                   r"extension — chapters 4–5.4 (and full crowding out under a float) assume χ = 0.")
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
AD_slope = -lambda_p / (lambda_i * Ybar)

# ―――― Exchange-rate regime ――――――――――――――――
# Each regime pins down a DIFFERENT pair of "which price can move": the nominal
# exchange rate, or the domestic interest rate. That choice drives everything.
#
# FLEXIBLE — the nominal rate floats, so UIP binds: r = rᵃ. Output comes from
#   MP∩FX, hence AD: π = (rᵃ − r' + λ_P)/λ_I − λ_P/(λ_I·Ȳ)·Y. ω drops out, so
#   FISCAL IS FULLY CROWDED OUT by the exchange rate. Monetary/foreign-rate shocks
#   are permanent → CRAWLING PEG π* = (rᵃ − r')/λ_I ≠ πᵃ.
#
# FIXED – WITH STERILIZATION — the CB offsets the reserve flows, so it keeps its
#   OWN interest rate: r = r' + λ_P·Ỹ + λ_I·π. Output then comes from IS at that
#   self-chosen r, with wʳ the same pegged STATE as under the hard peg:
#       Y·(1 + φλ_P/Ȳ) = ω − φr' + φλ_P − φλ_I·π + ψ·wʳ_t
#       wʳ_{t+1} = wʳ_t + κ·(πᵃ − π_t)
#   → a STEEPER AD than the float. Fiscal works (ω is in it) and the economy is
#   INSULATED from rᵃ (it never appears). But the nominal peg still holds, so
#   π → πᵃ here TOO — sterilisation changes the interest rate and the speed, not
#   the destination.
#   The catch is T2: in that long run r = r' + λ_I·πᵃ, which only equals rᵃ if r'
#   is unchanged. After a monetary or foreign-rate shock r ≠ rᵃ forever, implying
#   unbounded reserve flows — the peg is NOT sustainable and must break (or become
#   a genuine crawling peg). Flagged in the UI rather than silently simulated.
#
#   *** BOOK DIVERGENCE (§5.3) — the one place this model and the book disagree ***
#   For a MONETARY or FOREIGN-RATE shock under sterilisation, book §5.3 holds wʳ
#   STILL and lets inflation do all the adjusting, landing at
#       P∞:  π* = (rᵃ − r')/λ_I  and  r → rᵃ   — the SAME long run as the float,
#   reachable only by turning the peg into a genuine CRAWLING peg ("The difference
#   between fixed and flexible exchange rates is, therefore, not in the long-run
#   equilibrium but in the adjustment path."). This model instead lets wʳ drift, so
#   π → πᵃ and it is r that ends off-parity. Both are internally consistent; they
#   differ in which variable is assumed to give way while the peg is held. What is
#   simulated here is the WHILE-IT-LASTS path. Reaching the book's P∞ needs a
#   fourth regime (crawling peg) — not implemented; surfaced in the UI and the
#   Theory tab instead of being papered over.
#   NOTE this affects ONLY the sterilised peg after a monetary/foreign-rate shock.
#   For DEMAND shocks the book uses the same wʳ drift (§5.2) and both agree on πᵃ.
#
# FIXED – NO STERILIZATION — reserve flows are left to run, so they drag r to the
#   foreign rate: r = rᵃ and MONETARY POLICY IS POWERLESS (r' never appears).
#   The nominal peg holds, so the REAL rate wʳ is a slow-moving STATE that drifts
#   with the inflation differential (PPP) — which is what returns π to πᵃ:
#       Y   = ω − φ·rᵃ + ψ·wʳ_t − ψθ·(π_t − πᵃ)
#       wʳ_{t+1} = wʳ_t + κ·(πᵃ − π_t)
#   Fiscal is FULLY effective here (full IS multiplier — the largest of the three).
#   (θ is what damps this regime — see the note at the top of the file.)
fixed_regime = regime in ('Fixed – no sterilization', 'Fixed – with sterilization')
peg_no_steril = (regime == 'Fixed – no sterilization')
peg_steril = (regime == 'Fixed – with sterilization')
ppp_regime = fixed_regime           # ANY nominal peg forces π → πᵃ (the peg identity)

# Fixed without sterilization: reserve flows peg r to rᵃ, so domestic monetary
# policy (r') has no effect — neutralise any monetary shock.
monetary_neutralised = peg_no_steril and (r_init != RP_BASE)
if peg_no_steril:
    r_init = RP_BASE

# Under sterilization the foreign rate never reaches the domestic economy.
foreign_neutralised = peg_steril and (r_foreign != RA_BASE)

# ―――― Regime-specific AD curve and long-run inflation ――――――――――――――――
if peg_steril:
    # IS solved together with the CB's own MP rule. wʳ is a pegged STATE, so the
    # AD shifts as that state drifts — this is what pins π at πᵃ in the long run.
    _D = 1 + phi * lambda_p / Ybar
    AD_slope = -_D / (phi * lambda_i)
    pi_eq = pi_foreign                          # the peg identity: π must end at πᵃ
    AD_intercept = None                         # depends on the wʳ state (set per period)
    AD_intercept_sr = None
elif peg_no_steril:
    # r is pegged to rᵃ; wʳ is a state. The AD shifts as that state drifts.
    AD_slope = -1.0 / (psi * THETA_PEG)
    pi_eq = pi_foreign                          # PPP pins the long run
    AD_intercept = None                         # depends on the wʳ state (set per period)
    AD_intercept_sr = None
else:
    # Flexible float: the original MP∩FX construction.
    AD_slope = -lambda_p / (lambda_i * Ybar)
    AD_intercept = (r_foreign - r_init + lambda_p) / lambda_i
    AD_intercept_sr = AD_intercept
    pi_eq = (r_foreign - r_init) / lambda_i     # crawling peg

# Fixed pre-shock equilibrium — charts start here (period 0).
PI_BASELINE = pi_foreign


def peg_ad_intercept(wr_state):
    """AD intercept for a peg, given the current real-exchange-rate state."""
    if peg_steril:
        # r comes from the CB's own MP rule; wʳ enters through IS.
        K = omega - phi * r_init + phi * lambda_p + psi * wr_state
        return K / (phi * lambda_i)
    A = omega - phi * r_foreign + psi * wr_state
    return pi_foreign + A / (psi * THETA_PEG)


def peg_kappa():
    """Carry-over drift speed of the real exchange rate under whichever peg is
    selected: wʳ_{t+1} = wʳ_t + κ·(πᵃ − π_t).

    DERIVED from the model's own parameters instead of hard-coded, so the tuning
    stays correct when γ, ψ, φ or λ are changed at the Advanced level. (With a
    fixed κ the pegs silently went under- or over-damped as soon as a slider moved.)

    The SCALE is the critical-damping value of each regime's (π, wʳ) system, i.e.
    the κ solving trace² = 4·det:
        hard peg    κ_c = γ·ψ·θ²/(4·Ȳ)                    → 0.080 at the defaults
        sterilised  κ_c = γ·φ²·λ_I²/(4·Ȳ·D·ψ),  D = 1+φλ_P/Ȳ → 0.021 at the defaults
    See the note at the top of the file for why the pegs need damping at all.

    The MULTIPLIER is a display-speed calibration. κ_c minimises the asymptotic
    decay rate, but the pegs are nowhere near their asymptote after 30 periods, so
    the transient is what the user actually sees. Measured over all eight shocks,
    worst-case distance from equilibrium at the last plotted period:
        hard peg    ×1: 0.017   ×2: 0.003   ×3: 0.005   (overshoot 0.08/0.15/0.20)
        sterilised  ×1: 0.445   ×2: 0.111   ×3: 0.066   (overshoot 0.05/0.08/0.10)
    The hard peg is already damped by θ and settles at ×1; the sterilised peg has
    only the Taylor rule to lean on and needs ×3 to finish inside the chart. Both
    stay comfortably stable (ρ ≈ 0.92)."""
    if peg_steril:
        # Damping comes from the CB's own MP rule (there is no θ here).
        D = 1 + phi * lambda_p / Ybar
        return 3.0 * gamma * phi ** 2 * lambda_i ** 2 / (4 * Ybar * D * psi)
    # Hard peg: damping comes from θ, the within-period pass-through.
    return gamma * psi * THETA_PEG ** 2 / (4 * Ybar)


# ―――― T2: is the peg actually defensible? ――――――――――――――――
# In the sterilised long run r = r' + λ_I·πᵃ. If that differs from rᵃ, capital
# flows never stop, reserves move without bound, and the peg must eventually be
# abandoned. Sterilisation postpones the reckoning; it does not remove it.
peg_lr_rate = r_init + lambda_i * pi_foreign if peg_steril else r_foreign
peg_unsustainable = peg_steril and abs(peg_lr_rate - r_foreign) > 1e-6

# Real exchange rate implied by the long run. Defined for EVERY regime: in the long
# run Y = Ȳ, so IS gives wʳ* = (Ȳ − ω + φ·r*)/ψ with r* the regime's long-run rate.
# Used as the reference line on the wʳ time series (the old wʳ₀ line pointed at the
# pre-shock level, which is not where any shocked run ends up).
WR_LONGRUN = (Ybar - omega + phi * peg_lr_rate) / psi

# Regime outcome summary (shown in the right column).
if ppp_regime:
    regime_outcome = (f"<b>{regime}</b><br><span style='color:gray;'>Long-run: π → πᵃ = "
                      f"{pi_foreign:.2f}. Under a nominal peg the real exchange rate must do the "
                      f"adjusting (wʳ → {WR_LONGRUN:.2f}) — inflation cannot settle anywhere else."
                      f"</span>")
    if peg_steril:
        regime_outcome += ("<br><span style='color:#999; font-size:12px;'>Book §5.3 instead holds wʳ "
                           f"still after a monetary/foreign-rate shock and ends at π* = "
                           f"{(r_foreign - r_init) / lambda_i:.2f} via a crawling peg — see Theory §4.</span>")
else:
    regime_outcome = (f"<b>{regime}</b><br><span style='color:gray;'>Long-run: <b>crawling peg</b> — "
                      f"π* = {pi_eq:.2f} ≠ πᵃ = {pi_foreign:.2f}; the nominal exchange rate crawls at "
                      f"π − πᵃ ≈ {pi_eq - pi_foreign:+.2f}%/period.</span>")

# Fiscal policy enters through ω. It is now handled by each regime's own AD (it is
# absent from the float's AD → crowded out; present in both pegs → effective), so
# no separate adjustment is needed.
fiscal_shock = omega - OMEGA_BASE

def output_at(pi, ad_intercept=None, wr_state_=None):
    """Output on the regime's AD-curve at inflation π. Under EITHER peg the AD
    intercept depends on the current real-exchange-rate state."""
    if fixed_regime:
        intercept = peg_ad_intercept(WR_BASELINE if wr_state_ is None else wr_state_)
    else:
        intercept = AD_intercept if ad_intercept is None else ad_intercept
    return (pi - intercept) / AD_slope


def rate_at(y, pi):
    """Domestic real interest rate. Sterilization is exactly what frees the CB to
    set its own rate; otherwise capital flows tie r to the foreign rate."""
    if peg_steril:
        return r_init + lambda_p * (y - Ybar) / Ybar + lambda_i * pi
    return r_foreign


def realfx_at(y, pi, state):
    """Real exchange rate wʳ at an operating point. Under a float it jumps so IS
    passes through (Y, rᵃ); under EITHER peg the nominal rate is fixed, so wʳ is
    driven by the carried-over state `state`.

    `state` is passed EXPLICITLY rather than read from the session: the frozen
    period-1 curves must be evaluated at the period-1 state (WR_BASELINE), while
    the live curves use the current one. Reading a module-level state here made
    the pale 'short-run' IS line drift across the diagram as the run advanced."""
    if peg_steril:
        return state
    if peg_no_steril:
        return state - THETA_PEG * (pi - pi_foreign)
    return (y - omega + phi * r_foreign) / psi


def is_intercept_at(y, pi, state):
    """IS intercept for the r/Y diagram, given the wʳ that goes with this point."""
    return (omega + psi * realfx_at(y, pi, state)) / phi


def next_wr_coeffs(state_next):
    """Next period's realised wʳ written as W + b·π₊₁, given the peg state that
    will apply then. Needed because eq. (5.2)'s χ(wʳ₊₁ − wʳ) term is contemporaneous
    with π₊₁ — the two have to be solved together, not sequentially."""
    if peg_steril:
        return state_next, 0.0                       # wʳ is the state; π does not move it
    if peg_no_steril:
        return state_next + THETA_PEG * pi_foreign, -THETA_PEG
    # Float: wʳ = (Y(π) − ω + φrᵃ)/ψ with Y(π) = (π − AD_intercept)/AD_slope.
    return ((-AD_intercept / AD_slope - omega + phi * r_foreign) / psi,
            1.0 / (psi * AD_slope))


def ia_next(pi_now, y_now, wr_now, state_next):
    """IA curve, eq. (5.2):  π₊₁ = π + γ·Ỹ + χ·(wʳ₊₁ − wʳ) + η.

    With χ = 0 (the default, and all of chapters 4–5.4) this is the plain
    output-gap rule. With χ > 0 the imported-inflation channel of §5.5 is live and
    the equation is implicit in π₊₁, so it is solved in closed form."""
    base = pi_now + gamma * (y_now - Ybar) / Ybar + eta
    if chi == 0:
        return base
    W, b = next_wr_coeffs(state_next)
    return (base + chi * (W - wr_now)) / (1 - chi * b)


def peg_state_next(state, pi):
    """PPP drift of the pegged real exchange rate: wʳ_{t+1} = wʳ_t + κ(πᵃ − π_t)."""
    return state + peg_kappa() * (pi_foreign - pi) if fixed_regime else state


# Initial (period-1) inflation: predetermined at πᵃ, moved by the one-off imported
# price shock and — when χ > 0 — by the impact jump in the real exchange rate.
if chi == 0:
    pi_0 = pi_foreign + inflation_shock
else:
    _W1, _b1 = next_wr_coeffs(WR_BASELINE)
    pi_0 = (pi_foreign + inflation_shock + chi * (_W1 - WR_BASELINE)) / (1 - chi * _b1)

# pi_cur / wr_state: the animation's two state variables. Inflation is a state in
# every regime; the real exchange rate is only a state under a peg.
if st.session_state.oe_pi_prev is None:
    st.session_state.oe_pi_prev = pi_0
if st.session_state.oe_wr_prev is None:
    st.session_state.oe_wr_prev = WR_BASELINE
pi_cur = st.session_state.oe_pi_prev
wr_state = st.session_state.oe_wr_prev


# Current period (animated) operating point.
# While IDLE the diagrams draw the pre-shock resting equilibrium, so the readouts
# must report that same point — otherwise the panel shows shocked numbers next to
# unshocked curves (which is what made the values look wrong after a Reset).
_cur_ad = AD_intercept_sr if phase == "short_term_paused" else AD_intercept
if phase == "idle":
    Y_cur, pi_cur, r_cur, wr_cur = Ybar, PIA_BASE, RA_BASE, WR_BASELINE
else:
    Y_cur = output_at(pi_cur, _cur_ad, wr_state)
    r_cur = rate_at(Y_cur, pi_cur)
    wr_cur = realfx_at(Y_cur, pi_cur, wr_state)
IS_intercept_cur = is_intercept_at(Y_cur, pi_cur, wr_state if phase != "idle" else WR_BASELINE)
MP_intercept_cur = r_init - lambda_p + lambda_i * pi_cur

# Shocked (period-1) operating point — the short-run impact jump. Evaluated at the
# PERIOD-1 state (WR_BASELINE), never the live one, so the pale short-run curves
# stay frozen where the shock actually put them while the run advances.
Y_shock = output_at(pi_0, AD_intercept_sr, WR_BASELINE)
r_shock = rate_at(Y_shock, pi_0)
wr_shock = realfx_at(Y_shock, pi_0, WR_BASELINE)
IS_intercept_shock = is_intercept_at(Y_shock, pi_0, WR_BASELINE)
MP_intercept_shock = r_init - lambda_p + lambda_i * pi_0


def spectral_radius():
    """Largest eigenvalue modulus of the dynamic system actually being simulated.

    Replaces the old check γ < 2·Ȳ·|AD_slope|, which was derived for the float —
    a one-state system in π. Both pegs carry a SECOND state, the real exchange
    rate, so a 1-D criterion cannot see their stability at all. ρ < 1 ⇔ the run
    converges."""
    if not fixed_regime:
        if AD_slope == 0:
            return 0.0
        d = 1 - chi / (psi * AD_slope)
        return abs((1 + gamma / (Ybar * AD_slope) - chi / (psi * AD_slope)) / d)
    # Peg: (π, wʳ) system  M = [[a, b], [−κ, 1]]
    k = peg_kappa()
    if peg_steril:
        D = 1 + phi * lambda_p / Ybar
        a = 1 - gamma * phi * lambda_i / (Ybar * D) - chi * k
        b = gamma * psi / (Ybar * D)
    else:
        a = 1 - gamma * psi * THETA_PEG / Ybar - chi * k
        b = gamma * psi / Ybar
    tr, det = a + 1.0, a + b * k
    disc = tr * tr - 4 * det
    if disc >= 0:
        root = disc ** 0.5
        return max(abs((tr + root) / 2), abs((tr - root) / 2))
    return abs(det) ** 0.5


convergence_ok = spectral_radius() < 1.0

# ―――― Medium: concise dynamic description ――――――――――――――――
if level == 'Medium':
    forces = []
    if omega > OMEGA_BASE + 0.05:   forces.append("expansionary demand (↑ω)")
    elif omega < OMEGA_BASE - 0.05: forces.append("contractionary demand (↓ω)")
    if r_init < RP_BASE - 0.05:     forces.append("looser monetary policy (↓r')")
    elif r_init > RP_BASE + 0.05:   forces.append("tighter monetary policy (↑r')")
    if r_foreign > RA_BASE + 0.05:  forces.append("higher foreign rate (↑rᵃ)")
    elif r_foreign < RA_BASE - 0.05: forces.append("lower foreign rate (↓rᵃ)")
    if inflation_shock > 0:         forces.append("imported inflation (IA ↑, one-off)")
    elif inflation_shock < 0:       forces.append("imported deflation (IA ↓, one-off)")

    if not forces:
        text_to_show = c.empty_placeholder_moderate_level_shock
    else:
        demand_only = all("demand" in f for f in forces)
        if demand_only and not fixed_regime:
            note = ("<br><i style='color:#888;'>Under a float, a pure demand shock is fully crowded "
                    "out by the exchange rate — output and inflation are unchanged.</i>")
        elif demand_only:
            note = ("<br><i style='color:#888;'>Under a fixed peg, fiscal/demand policy is effective — "
                    "output moves on impact before real-exchange-rate adjustment crowds it out "
                    "(fully without sterilization, damped by the CB's own rate with it).</i>")
        else:
            note = (f"<br><i style='color:#888;'>New long-run inflation π* = {pi_eq:.2f} "
                    f"(foreign inflation πᵃ = {pi_foreign:.2f}).</i>")
        text_to_show = f"""
<div style="font-size:17px; font-weight:700; color:#222;">Open-Economy Shock 🌍</div>
<div style="font-size:13px; color:gray; margin-top:4px;"><b>{' + '.join(forces)}</b>{note}</div>"""

# ―――― Continue: advance from short_term_paused to adjusting ――――――――――――――――
if continue_clicked and phase == "short_term_paused":
    # Under EITHER peg the real exchange rate drifts with the inflation differential.
    _state_next = peg_state_next(WR_BASELINE, pi_0)
    st.session_state.oe_pi_prev = ia_next(pi_0, Y_shock, wr_shock, _state_next)
    if fixed_regime:
        st.session_state.oe_wr_prev = _state_next
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
    sAD_slope, sAD_int = -LP_BASE / (LI_BASE * Ybar), (RA_BASE - RP_BASE + LP_BASE) / LI_BASE
    sIA, sY = PIA_BASE, Ybar
else:
    sIS_slope, sIS_int = IS_slope, IS_intercept_shock
    sMP_slope, sMP_int = MP_slope, MP_intercept_shock
    # The FX curve is the INTEREST-PARITY constraint r = rᵃ, not the operating
    # point. Drawing it at the CB's own (sterilised) rate made the constraint
    # appear to move to meet Pₛ, hiding the very gap that generates the reserve
    # flows the sterilisation story is about (§4.5, §5.3). It is always rᵃ.
    sFX = r_foreign
    # Short-run (shocked) AD. Under either peg the AD sits where the PERIOD-1
    # real-exchange-rate state puts it.
    sAD_slope = AD_slope
    sAD_int = peg_ad_intercept(WR_BASELINE) if fixed_regime else AD_intercept_sr
    sIA, sY = pi_0, Y_shock

# Under sterilisation the CB holds r away from rᵃ: the operating point is OFF the
# FX line and reserves flow without limit. Reported next to the diagram.
parity_gap = (r_cur - r_foreign) if peg_steril and phase != "idle" else 0.0

# ―――― Tabs ――――――――――――――――
tab1, tab2 = st.tabs(["📊 Model", "📖 Theory"])

with tab2:
    st.markdown(MARKDOWN_THEORY, unsafe_allow_html=True)

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
    h.show_plotly_fig(r_Y_fig, column_to_plot=cols[0], key="oe_rY")

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
    h.show_plotly_fig(pi_Y_fig, column_to_plot=cols[0], key="oe_piY")

    # ―――― Advanced: equation display ――――――――――――――――
    if level == 'Advanced':
        _fx_line = (f'<b style="color:#E45756;">FX:</b> r set by the CB (sterilised) = {r_cur:.2f}'
                    if peg_steril else
                    f'<b style="color:#E45756;">FX:</b> r = rᵃ = {r_foreign:.2f}')
        text_to_show = f"""
            <b style="color:#4C78A8;">IS:</b> Y = {omega:.1f} − {phi:.1f}·r + {psi:.1f}·wʳ<br>
            <b style="color:#F58518;">MP:</b> r = {MP_slope:.2f}·Y + {MP_intercept_cur:.2f}<br>
            {_fx_line}<br>
            <b style="color:#B279A2;">AD:</b> 𝜋 = {sAD_slope:.2f}·Y + {sAD_int:.2f}<br>
            <b style="color:#54A24B;">IA:</b> 𝜋 = {pi_0:.2f}<br>
            <hr style="margin:4px 0; border:none; border-top:1px solid #ddd;">
            <b style="color:black;">π* (LR eq.):</b> {pi_eq:.2f} &nbsp; <span style="color:gray;">(πᵃ = {pi_foreign:.1f})</span><br>
            <b style="color:black;">Output gap (Y − Ȳ):</b> {output_gap:.2f}<br>
            <b style="color:black;">Real exchange rate wʳ:</b> {wr_cur:.2f}
        """

    # ―――― Right column ――――――――――――――――
    with cols[1].container(border=True):
        if not convergence_ok:
            st.warning(f"⚠️ These parameters do not converge (spectral radius "
                       f"{spectral_radius():.2f} ≥ 1). Try reducing γ"
                       + (" or χ." if chi else "."))

        if parity_gap:
            st.info(f"💱 **Off interest parity by {parity_gap:+.2f}pp** (r = {r_cur:.2f} vs "
                    f"rᵃ = {r_foreign:.2f}). The operating point sits away from the red FX line — "
                    f"that gap is exactly what drives the reserve flows the CB is sterilising.")

        if monetary_neutralised:
            st.info("🏛️ **Fixed peg, no sterilization:** monetary policy is powerless — reserve "
                    "flows tie r to rᵃ, so the change in r' has no effect.")

        if foreign_neutralised:
            st.info("🏛️ **Fixed peg, with sterilization:** the CB sterilises the reserve flows, so "
                    "the real economy is insulated — the change in rᵃ does not reach it. Reserves, "
                    "however, move continuously (see the warning below).")

        if peg_unsustainable:
            st.warning(
                f"⚠️ **This peg cannot be defended indefinitely.** In the long run the CB's own rule "
                f"leaves r = {peg_lr_rate:.2f} while the foreign rate is rᵃ = {r_foreign:.2f}. With free "
                f"capital mobility that gap means never-ending flows and unbounded reserve "
                f"gains/losses. Sterilisation only postpones the reckoning: the country must "
                f"eventually abandon sterilisation (→ the flat paths of the hard peg) or move to a "
                f"**crawling peg** (→ the flexible-regime outcome). The path shown is the "
                f"*while-it-lasts* adjustment.")

        if fiscal_shock != 0:
            if peg_no_steril:
                st.info("🏛️ **Hard peg — fiscal policy is fully effective:** the money supply "
                        "accommodates, so output moves by the full IS multiplier before the real "
                        "exchange rate slowly crowds it out.")
            elif peg_steril:
                st.info("🏛️ **Sterilised peg — fiscal policy is effective but damped:** the CB's own "
                        "MP rule raises r as output rises, so the impact is smaller than without "
                        "sterilization. Crowding out still arrives via the trade balance, as domestic "
                        "prices outrun foreign ones (wʳ ↓).")
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
            h.show_plotly_fig(fig, height=190, key=f"oe_ts_{y_col}")

        _series_chart("Output",    "Y - Output",           "Y",  Ybar,        "Ȳ")
        _series_chart("Inflation", "𝜋 - inflation",        "𝜋",  pi_eq,       "𝜋*")
        # Reference is the LONG-RUN wʳ, not the pre-shock one: most shocks move
        # the real exchange rate permanently, so wʳ₀ was the wrong target line.
        _series_chart("RealFX",    "wʳ - real exch. rate", "wʳ", WR_LONGRUN,  "wʳ*")
        # r is pegged to rᵃ in every regime except 'fixed with sterilization', where
        # the CB sets its own rate — that is what makes the two pegs differ.
        _series_chart("Rate",      "r - interest rate",    "r",
                      rate_at(Ybar, pi_eq) if peg_steril else r_foreign, "r*")

    # ―――― Animation step ――――――――――――――――
    if phase == "adjusting":
        new_row_idx = len(st.session_state.oe_iteration_df)
        st.session_state.oe_iteration_df.loc[new_row_idx] = [
            st.session_state.oe_iter_counter, Y_cur, pi_cur, wr_cur, r_cur
        ]
        # Under a peg the real exchange rate drifts toward PPP (πᵃ − π), which is what
        # eventually closes the output gap and returns inflation to foreign inflation.
        _state_next = peg_state_next(wr_state, pi_cur)
        st.session_state.oe_pi_prev = ia_next(pi_cur, Y_cur, wr_cur, _state_next)
        if fixed_regime:
            st.session_state.oe_wr_prev = _state_next
        st.session_state.oe_iter_counter += 1

        if st.session_state.oe_iter_counter >= iteration_count:
            st.session_state.oe_phase = "done"

        time.sleep(sim_speed)
        st.rerun()
