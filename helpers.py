from contextlib import nullcontext

import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import config as c

# ―――― Streamlit Helpers ――――――――――――――――
def session_init(**kwargs):
    """ Initiates the session state for several variables at once"""
    for key, value in kwargs.items():
        if key not in st.session_state:
            st.session_state[key] = value




def panel_header(text, column_to_plot=st):
    """Small caps label at the top of a panel.

    Every column of the model tab is a bordered container carrying one of these,
    which is what makes the row read as one dashboard split into sections rather
    than as unrelated boxes floating next to each other. Keep the styling here —
    if each page styles its own header they drift apart."""
    column_to_plot.markdown(
        f"<div style='font-size:11px; font-weight:600; letter-spacing:.09em; "
        f"text-transform:uppercase; color:#9AA0A6; margin:-4px 0 8px 0;'>{text}</div>",
        unsafe_allow_html=True)


# ―――― Linear Math ――――――――――――――――
def find_line_intersection(slope_1, intercept_1, slope_2, intercept_2):
    if slope_1 == slope_2:
        return None  # parallel (or identical)

    x = (intercept_2 - intercept_1) / (slope_1 - slope_2)
    y = slope_1 * x + intercept_1
    return x, y




# ―――― Plot helpers ――――――――――――――――
def create_linear_plot(x_label="Y", y_label="r"):
    fig = go.Figure()
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label,showlegend=False)
    return fig

def add_line_to_plot(plotly_fig, slope, intercept, x_min=0, x_max=10, n_points=100, name='Name', color='blue', line_width=c.standard_line_width, dash='solid', label_position='right', label_offset=0):
    x = np.linspace(x_min, x_max, n_points)
    y = slope * x + intercept
    df = pd.DataFrame({"x": x, "y": y})

    plotly_fig.add_trace(
        go.Scatter(
            x=df["x"],
            y=df["y"],
            mode="lines",
            name=name,
            line=dict(color=color, width=line_width, dash=dash)
        )
    )

    # label at the right end of the line by default; 'left' places it just INSIDE
    # the left edge (anchored left, nudged up) so it does not hang off the plot and
    # expand the left margin — which would misalign vertically-stacked charts.
    if label_position == 'left':
        label_x, label_y, label_anchor, label_yshift = x[0], y[0], "left", 9
    else:
        label_x, label_y, label_anchor, label_yshift = x[-1], y[-1], "left", 0
    # label_offset separates the labels of two curves that sit on top of each other
    # (an X₁ and an X∞ curve that have not moved apart). Without it the two names
    # print in exactly the same spot and neither is readable.
    label_yshift += label_offset

    plotly_fig.add_annotation(
        x=label_x,
        y=label_y,
        text=name,
        showarrow=False,
        xanchor=label_anchor,
        yshift=label_yshift,
        font=dict(color=color)  # match line color
    )

    return df

def add_vertical_line(plotly_fig, x_value, y_min=None, y_max=None, color="#000000", dash="dash", name="Vertical Line", name_position='top', line_width=None, label_offset=0):
    def _get_y_bounds(fig):
        yaxis = fig.layout.yaxis

        if getattr(yaxis, "range", None) is not None and len(yaxis.range) == 2:
            return float(yaxis.range[0]), float(yaxis.range[1])

        ys = []
        for trace in fig.data:
            if getattr(trace, "y", None) is None:
                continue
            for v in trace.y:
                if v is not None:
                    try:
                        ys.append(float(v))
                    except (TypeError, ValueError):
                        pass

        if not ys:
            return 0.0, 1.0

        y0, y1 = min(ys), max(ys)

        if y0 == y1:
            pad = 1.0 if y0 == 0 else abs(y0) * 0.05
            y0 -= pad
            y1 += pad

        return y0, y1

    axis_y0, axis_y1 = _get_y_bounds(plotly_fig)
    start_y = axis_y0 if y_min is None else y_min
    end_y = axis_y1 if y_max is None else y_max

    plotly_fig.add_shape(
        type="line",
        x0=x_value,
        x1=x_value,
        y0=start_y,
        y1=end_y,
        xref="x",
        yref="y",
        line=dict(color=color, dash=dash,
                  **({} if line_width is None else {"width": line_width})),
    )

    if name_position == "top":
        y_annot = end_y
        yanchor = "bottom"
    else:
        y_annot = start_y
        yanchor = "top"

    plotly_fig.add_annotation(
        x=x_value,
        y=y_annot,
        xref="x",
        yref="y",
        text=name,
        showarrow=False,
        yanchor=yanchor,
        xshift=label_offset,     # vertical curves separate their labels sideways
        font=dict(color=color),
    )

    return plotly_fig


def add_arrow(fig, x_start, y_start, x_end, y_end):
    fig.add_annotation(
        x=x_end,
        y=y_end,
        ax=x_start,
        ay=y_start,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        text="",
        showarrow=True,
        arrowhead=5,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="red",
        standoff=0,
        startstandoff=0,
        xanchor="center",
        yanchor="middle",
    )
    return fig



def show_plotly_fig(fig, height=400, column_to_plot=st, key=None):
    """Render a figure. Pass a STABLE `key` for charts that are redrawn every
    animation frame: without one Streamlit remounts the whole Plotly component on
    each rerun, which is what makes the animation stutter (noticeably so in
    Firefox). With a key the component is reused and only its data is updated."""
    fig.update_layout(
        height=height,
        margin=dict(t=0, b=0, l=0, r=0),
        hovermode="x unified",
        font=dict(size=12)
    )
    column_to_plot.plotly_chart(
        fig,
        key=key,
        config={"displayModeBar": False,"staticPlot": False,
        },
    )

def add_model_curve(plotly_fig, slope, intercept, x_min, x_max, name, color,
                    line_width=c.standard_line_width, dash='solid', label_position='right',
                    label_offset=0):
    """Draw one model curve. A slope of None means the curve is VERTICAL, in which
    case `intercept` is read as the output level it stands at.

    Vertical curves are drawn as shapes, whose extent is taken from whatever is
    already on the figure — so add the horizontal curves FIRST, or the vertical one
    comes out as a stub spanning a single y value."""
    if slope is None:
        return add_vertical_line(plotly_fig, intercept, name=name, color=color,
                                 dash=dash, line_width=line_width, name_position='top',
                                 label_offset=label_offset)
    return add_line_to_plot(plotly_fig, slope, intercept, x_min, x_max, name=name,
                            color=color, line_width=line_width, dash=dash,
                            label_position=label_position, label_offset=label_offset)


# ―――― Curve sets: initial → short run → long run ―――――――――――――――――――――――――――
# Saturated colour for the curve that is currently LIVE, pale for the ghost it
# left behind. Both pages share this so the two read as one app.
CURVE_COLORS = {
    'IS': ("#4C78A8", "#AEC7E8"),
    'MP': ("#F58518", "#FAD7B0"),
    'IA': ("#54A24B", "#CDEACB"),
    'AD': ("#B279A2", "#E0C6DA"),
    'FX': ("#E45756", "#F5B8B7"),
}

# Pixels each of the two visible labels is pushed, in opposite directions. Applied
# ALWAYS, not only when the curves are close: a threshold would need the axis scale,
# which is not known at draw time, and a fixed nudge is harmless when they are far
# apart and exactly what is needed when they coincide.
LABEL_NUDGE = 11

# Curves are indexed by the period they belong to, not by a ST/LT prefix: X₀ is
# where the curve rested before the shock, X₁ where the shock put it, X∞ where it
# is heading. Plotly renders the <sub> tag, so all three indices come out as real
# subscripts of the same size — plain Unicode has ₀ and ₁ but no subscript ∞,
# which would leave the third label a full-height mismatch.
IDX_INITIAL, IDX_SHORT, IDX_LONG = "<sub>0</sub>", "<sub>1</sub>", "<sub>∞</sub>"


def add_curve_set(plotly_fig, key, x_min, x_max, initial, short, long_=None,
                  show_initial=False, show_long=False, label=None):
    """Draw one model curve in whichever positions the current phase calls for.

    Each position is a (slope, intercept) pair; a slope of None means the curve is
    vertical and the second element is the output level it stands at.

        idle            one bold curve at `initial` — the pre-shock resting point
        after Play      `initial` stays as a dotted ghost (X₀), so it is obvious
                        WHICH curves the shock moved, and `short` is live as X₁
        after Continue  X₀ drops out, `short` fades to the pale X₁ ghost, and
                        `long_` emerges on top of it as X∞ and drifts away period
                        by period. X∞ marks where the curve is HEADING; it only
                        actually gets there at the end of the run.

    Only ever two curves carry a label at once, so nudging them apart by a fixed
    ±LABEL_NUDGE is enough to keep both readable when they overlap."""
    name = key if label is None else label
    solid, pale = CURVE_COLORS[key]

    if not show_initial and not show_long:
        return add_model_curve(plotly_fig, *initial, x_min, x_max, name=name,
                               color=solid, line_width=c.standard_line_width)

    if show_initial:
        add_model_curve(plotly_fig, *initial, x_min, x_max, name=f"{name}{IDX_INITIAL}",
                        color=pale, line_width=c.thin_line_width, dash='dot',
                        label_offset=-LABEL_NUDGE)
        return add_model_curve(plotly_fig, *short, x_min, x_max, name=f"{name}{IDX_SHORT}",
                               color=solid, line_width=c.standard_line_width,
                               label_offset=LABEL_NUDGE)

    add_model_curve(plotly_fig, *short, x_min, x_max, name=f"{name}{IDX_SHORT}",
                    color=pale, line_width=c.thin_line_width, label_offset=-LABEL_NUDGE)
    return add_model_curve(plotly_fig, *long_, x_min, x_max, name=f"{name}{IDX_LONG}",
                           color=solid, line_width=c.standard_line_width,
                           label_offset=LABEL_NUDGE)


# ―――― Units ―――――――――――――――――――――――――――――――――
# Y is an INDEX with potential Ȳ = 100, so one unit of Y is one per cent of
# potential output. r, π and the output gap are all in PERCENTAGE POINTS, and the
# real exchange rate is an index at 100 too.
#
# This is what makes the coefficients readable: φ = 1 means "a 1 pp rise in the
# real interest rate costs 1 % of potential output", λ_P = 0.5 is the textbook
# Taylor weight on a gap measured in per cent, γ = 0.4 is the Phillips slope in
# points of inflation per point of gap, and ψ = 0.25 means "a 1 % real
# depreciation adds 0.25 % to output".
#
# The gap therefore has to be scaled: Ỹ = 100·(Y − Ȳ)/Ȳ, NOT (Y − Ȳ)/Ȳ. Anywhere
# a slope is taken with respect to Y, that same factor of 100/Ȳ appears.

def output_gap(Y, Ybar):
    """Output gap in percentage points of potential."""
    return 100.0 * (Y - Ybar) / Ybar


def gap_per_Y(Ybar):
    """turns a coefficient on the gap into a slope in Y."""
    return 100.0 / Ybar


# ―――― Open-economy model ―――――――――――――――――――――――――――――――――――――――――――――――――――
# Five equations, nothing calibrated and no free coefficients:
#
#   IS   Y = ω − φ·r + ψ·wʳ
#   MP   r = r' + λ_P·Ỹ + λ_I·π
#   FX   1+r = (1+rᵃ)·wʳ,ᵉ₊₁/wʳ                  (eq. 3.9, real interest parity)
#   IA   π = π₋₁ + γ·Ỹ₋₁ + χ·(wʳ − wʳ₋₁)
#   PPP  wʳ = wʳ₋₁·(1+πᵃ)/(1+π)                  (nominal exchange rate pegged)
#
# The PPP line is the whole peg mechanism: with the nominal rate w held fixed,
# wʳ = w·pᵃ/p, so the real rate keeps moving for as long as domestic inflation
# differs from foreign inflation. It is ONE law — the same equation supplies both
# the within-period response of wʳ to π and the carry-over drift between periods.
# Do not split it into separate within-period and drift coefficients: tuning them
# apart is what previously turned an exact identity into a fitted parameter.
#
# CONSEQUENCE: how well the adjustment behaves depends entirely on what stabilises
# demand in each regime.
#   • Float          — the Taylor rule works, so π converges geometrically.
#   • Sterilised peg — the bank keeps its rule, so output returns to potential
#                      quickly while prices grind back over a much longer span.
#   • Hard peg       — the Taylor rule is abandoned and the FX MARKET sets r. The
#                      nominal rate is pegged, so the expected real appreciation
#                      IS the inflation differential and eq. 3.9 collapses to
#                      r = rᵃ + (πᵃ − π) — identically i = iᵃ with r = i − π, which
#                      is how the book writes it for a currency union (§5.4). The
#                      real rate therefore moves AGAINST inflation: a slump that
#                      lowers π RAISES r and deepens the slump. AD slopes UPWARD
#                      and the rest point is unstable — see oe_peg_root.

OE_FLOAT, OE_PEG, OE_PEG_STER = 'float', 'hard', 'ster'


class OEParams:
    """Structural parameters of the open-economy model."""

    def __init__(self, omega, phi, psi, r_init, lambda_p, lambda_i,
                 r_foreign, pi_foreign, gamma, chi=0.0, Ybar=1.0):
        self.omega, self.phi, self.psi = omega, phi, psi
        self.r_init, self.lambda_p, self.lambda_i = r_init, lambda_p, lambda_i
        self.r_foreign, self.pi_foreign = r_foreign, pi_foreign
        self.gamma, self.chi, self.Ybar = gamma, chi, Ybar


def oe_ppp_next(p, wr, pi):
    """Exact PPP: wʳ = wʳ₋₁·(1+πᵃ)/(1+π) — the nominal rate is pegged, so the real
    rate drifts with the inflation differential. Inflation is in percent."""
    return wr * (1.0 + p.pi_foreign / 100.0) / (1.0 + pi / 100.0)


def oe_baseline_wr(p):
    """Pre-shock real exchange rate: IS solved at Y = Ȳ and r = rᵃ."""
    return (p.Ybar - p.omega + p.phi * p.r_foreign) / p.psi


def oe_fx_rate(p, regime, pi):
    """The FX-curve level: the real interest rate the FX market imposes, eq. 3.9
    1+r = (1+rᵃ)·wʳ,ᵉ₊₁/wʳ.

    Float — the book's baseline assumption is wʳ,ᵉ₊₁ = wʳ (§4.7), so r = rᵃ.
    Peg — the NOMINAL rate is fixed, so wʳ = w·pᵃ/p is expected to move with the
    inflation differential alone: wʳ,ᵉ₊₁/wʳ = (1+πᵃ)/(1+π), which to first order
    gives r = rᵃ + (πᵃ − π). The book states exactly this twice: "with a fixed
    exchange rate, nominal interest rates must be equal (i = iᵃ). The fall in
    domestic prices then implies a higher real interest rate than abroad" (§5.2),
    and "r = i − π^ES < r₀ … r = i − π^DE > r₀" for a currency union (§5.4).

    Under a peg this is the position of the FX CURVE in the r–Y diagram, whether or
    not the bank sterilises. With sterilisation the bank holds its own r and the
    distance to this line is the reserve flow it has to absorb; without it, the
    line IS the operating point."""
    if regime == OE_FLOAT:
        return p.r_foreign
    return p.r_foreign + (p.pi_foreign - pi)


def oe_peg_root(p):
    """Dominant eigenvalue of the unsterilised peg, as a growth factor per period.

    State (wʳ, π) with r = rᵃ + (πᵃ − π), the gap in points (Ỹ = 100·(Y−Ȳ)/Ȳ):
        wʳₜ  = wʳₜ₋₁ − (wʳ*/100)·(πₜ − πᵃ)      exact PPP, linearised
        πₜ₊₁ = πₜ + γ·(100/Ȳ)·(φ·(πₜ − πᵃ) + ψ·(wʳₜ − wʳ*))
    The determinant of that matrix is 1 + γφ·100/Ȳ. It exceeds 1 for ANY φ > 0, so the
    rest point is unstable no matter how the other parameters are set: the trade
    channel (ψ) changes how fast the shock is amplified, never whether it is. That
    is the book's own conclusion — "instead of a convergence of living conditions,
    the analysis shows the opposite, i.e. a divergence" (§5.4). With r pinned at rᵃ
    instead, the determinant would be exactly 1 — the knife-edge case that swings
    forever and settles never."""
    g = gap_per_Y(p.Ybar)
    a = oe_baseline_wr(p) / 100.0
    b = p.gamma * p.psi * g
    c = p.gamma * p.phi * g
    tr, det = 2.0 + c - a * b, 1.0 + c
    disc = tr * tr - 4.0 * det
    if disc < 0:
        return det ** 0.5                      # complex pair, modulus √det
    return (abs(tr) + disc ** 0.5) / 2.0


def oe_out_of_range(p, Y, pi, wr):
    """Has the run left the range in which the model says anything?

    Not a model equation and not a damping device: a display guard. The
    unsterilised peg amplifies without limit, and once output is 8 % away from
    potential (deeper than any post-war recession), inflation is 10 points away from
    the world rate, or the real exchange rate has moved by more than a third, the
    linear IS curve is describing nothing real. In the book that is where the peg goes: the UK gave up
    on Black Wednesday rather than raise the interest rate the parity condition was
    demanding (§4.6)."""
    return (abs(output_gap(Y, p.Ybar)) > 8.0
            or abs(pi - p.pi_foreign) > 10.0
            or abs(wr / oe_baseline_wr(p) - 1.0) > 0.35)


def oe_operating_point(p, regime, pi, wr_state):
    """(Y, r, wʳ) for the current period, given predetermined inflation π and the
    carried-over real exchange rate.

    Float — the nominal rate is free, so FX binds (r = rᵃ) and output comes from
    MP ∩ FX. wʳ then jumps to whatever makes IS pass through that point.
    Sterilised peg — the bank offsets the reserve flows and keeps its own rule, so
    output comes from IS ∩ MP at the pegged wʳ.
    Hard peg — reserve flows are left to run, the Taylor rule is abandoned and the
    FX market sets r, so output comes from IS ∩ FX at the pegged wʳ. FX is eq. 3.9
    at a fixed nominal rate, r = rᵃ + (πᵃ − π), so r is NOT rᵃ whenever domestic
    inflation differs from foreign: below πᵃ the currency is appreciating in real
    terms, investors have to be paid for that, and the real rate rises."""
    if regime == OE_FLOAT:
        # rᵃ = r' + λ_P·Ỹ + λ_I·π  solved for the gap, then for Y
        gap = (p.r_foreign - p.r_init - p.lambda_i * pi) / p.lambda_p
        Y = p.Ybar * (1.0 + gap / 100.0)
        return Y, p.r_foreign, (Y - p.omega + p.phi * p.r_foreign) / p.psi

    wr = wr_state
    if regime == OE_PEG_STER:
        D = 1.0 + p.phi * p.lambda_p * gap_per_Y(p.Ybar)
        Y = (p.omega - p.phi * p.r_init + p.phi * p.lambda_p * 100.0
             - p.phi * p.lambda_i * pi + p.psi * wr) / D
        r = p.r_init + p.lambda_p * output_gap(Y, p.Ybar) + p.lambda_i * pi
        return Y, r, wr

    r = oe_fx_rate(p, regime, pi)
    return p.omega - p.phi * r + p.psi * wr, r, wr


def oe_wr_next(p, regime, wr, pi_next, Y_next=None):
    """The real exchange rate that will apply next period."""
    if regime == OE_FLOAT:
        return (Y_next - p.omega + p.phi * p.r_foreign) / p.psi
    return oe_ppp_next(p, wr, pi_next)


def oe_next_inflation(p, regime, pi, Y, wr):
    """IA curve:  π₊₁ = π + γ·Ỹ + χ·(wʳ₊₁ − wʳ).

    With χ = 0 (the default) this is the plain output-gap rule. With χ > 0 the
    imported-inflation channel is live; wʳ₊₁ is contemporaneous with π₊₁, so the
    two have to be solved together rather than in sequence."""
    base = pi + p.gamma * output_gap(Y, p.Ybar)
    if p.chi == 0.0:
        return base

    if regime == OE_FLOAT:
        # wʳ₊₁ is linear in π₊₁: Y(π) off the float's AD, then IS solved for wʳ.
        b = -(p.Ybar / 100.0) * p.lambda_i / (p.lambda_p * p.psi)
        W0 = (p.Ybar * (1.0 + (p.r_foreign - p.r_init) / (100.0 * p.lambda_p))
              - p.omega + p.phi * p.r_foreign) / p.psi
        return (base + p.chi * (W0 - wr)) / (1.0 - p.chi * b)

    # Peg: wʳ₊₁ = wr·(1+πᵃ)/(1+π₊₁). Substituting into the IA curve and clearing
    # the denominator gives a quadratic in π₊₁; take the root nearest `base`.
    k = 1.0 + p.pi_foreign / 100.0
    b_ = 100.0 - base + p.chi * wr
    c_ = -100.0 * (base + p.chi * wr * (k - 1.0))
    disc = b_ * b_ - 4.0 * c_
    if disc < 0:
        return base
    root = disc ** 0.5
    r1, r2 = (-b_ + root) / 2.0, (-b_ - root) / 2.0
    return r1 if abs(r1 - base) <= abs(r2 - base) else r2


def oe_ad_curve(p, regime, wr_state):
    """AD in π–Y space as (slope, intercept). A slope of None means the curve is
    VERTICAL, returned instead as (None, Y).

    Float — AD is MP ∩ FX, so ω drops out entirely and fiscal policy is fully
    crowded out.
    Sterilised peg — AD is IS ∩ MP at the pegged wʳ, steeper than the float's, and
    it shifts as wʳ drifts. ω is present, so fiscal policy works.
    Hard peg — AD is IS ∩ FX at the pegged wʳ. Interest parity ties r to πᵃ − π,
    so higher inflation means a LOWER real rate and MORE demand: the curve slopes
    UPWARD, with slope 1/φ, the mirror image of the float's −λ_P/λ_I. An
    upward-sloping AD against a horizontal IA is what an unstable equilibrium looks
    like in this diagram — the operating point runs away from Ȳ instead of towards
    it. It is not the Taylor-rule AD the book draws as AD₁ in Figure 5.3: that one
    is the sterilised peg's curve, and the whole point of Figure 5.3 is that Pₒ sits
    off it, "because the central bank has left its MP-curve" (§5.2)."""
    g = gap_per_Y(p.Ybar)
    if regime == OE_FLOAT:
        return (-p.lambda_p * g / p.lambda_i,
                (p.r_foreign - p.r_init + p.lambda_p * 100.0) / p.lambda_i)
    if regime == OE_PEG_STER:
        D = 1.0 + p.phi * p.lambda_p * g
        return (-D / (p.phi * p.lambda_i),
                (p.omega - p.phi * p.r_init + p.phi * p.lambda_p * 100.0
                 + p.psi * wr_state) / (p.phi * p.lambda_i))
    # Y = ω − φ·(rᵃ + πᵃ − π) + ψ·wʳ, solved for π.
    return (1.0 / p.phi,
            (p.r_foreign + p.pi_foreign) - (p.omega + p.psi * wr_state) / p.phi)


def oe_is_intercept(p, wr):
    """IS intercept in the r–Y diagram at a given real exchange rate."""
    return (p.omega + p.psi * wr) / p.phi


def oe_longrun(p, regime):
    """(π*, r*, wʳ*) where the economy comes to rest.

    Under EITHER peg the nominal rate is fixed, so wʳ is at rest only when
    π = πᵃ — a pegged economy cannot hold an inflation rate of its own. Under a
    float the Taylor rule sets π* instead, and ω is absent from it.

    For the unsterilised peg this is where the economy WOULD come to rest, not
    where it goes: the rest point is unstable (oe_peg_root > 1), so a shock moves
    the economy away from it."""
    if regime == OE_FLOAT:
        pi_star = (p.r_foreign - p.r_init) / p.lambda_i
        r_star = p.r_foreign
    else:
        pi_star = p.pi_foreign
        r_star = (p.r_init + p.lambda_i * p.pi_foreign
                  if regime == OE_PEG_STER else p.r_foreign)
    return pi_star, r_star, (p.Ybar - p.omega + p.phi * r_star) / p.psi


# ―――― Settings ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
SPEED_LABELS = {"Slow": 0.2, "Normal": 0.04, "Fast": 0.02, "Very Fast": 0.01}


def settings_controls(key_prefix="", stacked=False):
    """The simulation settings, rendered wherever they are wanted.

    Lives here so the Settings PAGE and the in-page Settings popover show one set
    of controls instead of two that can drift apart. `key_prefix` keeps the widget
    keys distinct between the two — Streamlit raises a duplicate-key error if the
    same widget is rendered twice in one run. `stacked` puts the inputs one above
    the other, which is what a narrow popover needs."""
    current_speed = st.session_state.get("setting_speed", c.speed)
    current_label = min(SPEED_LABELS, key=lambda k: abs(SPEED_LABELS[k] - current_speed))
    saved_iters = st.session_state.get("setting_iterations", c.iteration_count)

    # A narrow popover stacks the inputs; nullcontext stands in for a column so
    # both layouts run through the same `with` block (the st module itself is not
    # a context manager).
    holders = (nullcontext(), nullcontext()) if stacked else st.columns(2)
    with holders[0]:
        iterations = st.number_input(
            "Number of iterations", min_value=5, max_value=200, step=1, value=saved_iters,
            key=f"{key_prefix}set_iterations",
            help="How many periods the model runs after the initial shock.")
    with holders[1]:
        speed_choice = st.select_slider(
            "Animation speed", options=list(SPEED_LABELS.keys()), value=current_label,
            key=f"{key_prefix}set_speed",
            help="Controls the delay between animation steps.")

    changed = (iterations != saved_iters or SPEED_LABELS[speed_choice] != current_speed)
    if st.button("Save settings", type="primary", disabled=not changed,
                 key=f"{key_prefix}set_save", width="stretch"):
        st.session_state.setting_iterations = iterations
        st.session_state.setting_speed = SPEED_LABELS[speed_choice]
        st.rerun()
    return changed


def settings_popover(label="⚙️", key_prefix="", ratio=(4, 1)):
    """Right-aligned Settings popover, meant to sit on its own row ABOVE a tab bar.

    Deliberately NOT wrapped around the tabs. Putting the tabs inside a column —
    st.columns([6,1]) with cols[0].tabs(...) — confines every diagram, panel and
    chart drawn inside those tabs to that column's width, which is what makes the
    page stop short of the vertical border instead of running to the edge. The
    settings control gets a column; the tabs stay at full width."""
    _, right = st.columns(ratio, vertical_alignment="top")
    with right.popover(label, width="stretch"):
        settings_controls(key_prefix=key_prefix, stacked=True)
