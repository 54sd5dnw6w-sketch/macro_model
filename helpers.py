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


# ―――― Open-economy model ―――――――――――――――――――――――――――――――――――――――――――――――――――
# Five equations, nothing calibrated and no free coefficients:
#
#   IS   Y = ω − φ·r + ψ·wʳ
#   MP   r = r' + λ_P·Ỹ + λ_I·π
#   FX   r = rᵃ                                  (static exchange-rate expectations)
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
#   • Hard peg       — r is pinned to rᵃ and the Taylor rule is abandoned, so
#                      nothing damps the cycle. Output overshoots and the run does
#                      not settle. That is a property of the regime, not a defect
#                      in the code: with a vertical AD there is no stabiliser left.

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


def oe_operating_point(p, regime, pi, wr_state):
    """(Y, r, wʳ) for the current period, given predetermined inflation π and the
    carried-over real exchange rate.

    Float — the nominal rate is free, so FX binds (r = rᵃ) and output comes from
    MP ∩ FX. wʳ then jumps to whatever makes IS pass through that point.
    Sterilised peg — the bank offsets the reserve flows and keeps its own rule, so
    output comes from IS ∩ MP at the pegged wʳ.
    Hard peg — reserve flows drag r to rᵃ and the Taylor rule is abandoned, so
    output is read straight off IS at the pegged wʳ."""
    if regime == OE_FLOAT:
        # rᵃ = r' + λ_P·(Y−Ȳ)/Ȳ + λ_I·π  solved for Y
        Y = p.Ybar + p.Ybar * (p.r_foreign - p.r_init - p.lambda_i * pi) / p.lambda_p
        return Y, p.r_foreign, (Y - p.omega + p.phi * p.r_foreign) / p.psi

    wr = wr_state
    if regime == OE_PEG_STER:
        D = 1.0 + p.phi * p.lambda_p / p.Ybar
        Y = (p.omega - p.phi * p.r_init + p.phi * p.lambda_p
             - p.phi * p.lambda_i * pi + p.psi * wr) / D
        r = p.r_init + p.lambda_p * (Y - p.Ybar) / p.Ybar + p.lambda_i * pi
        return Y, r, wr

    Y = p.omega - p.phi * p.r_foreign + p.psi * wr
    return Y, p.r_foreign, wr


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
    base = pi + p.gamma * (Y - p.Ybar) / p.Ybar
    if p.chi == 0.0:
        return base

    if regime == OE_FLOAT:
        # wʳ₊₁ is linear in π₊₁: Y(π) off the float's AD, then IS solved for wʳ.
        b = -p.Ybar * p.lambda_i / (p.lambda_p * p.psi)
        W0 = (p.Ybar + p.Ybar * (p.r_foreign - p.r_init) / p.lambda_p
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
    Hard peg — r cannot respond and wʳ is fixed within the period, so demand does
    not depend on current inflation at all: AD is vertical. Every bit of the
    adjustment has to come through accumulated price differences, which is what
    makes this regime both slow and badly exposed to a shock."""
    if regime == OE_FLOAT:
        return (-p.lambda_p / (p.lambda_i * p.Ybar),
                (p.r_foreign - p.r_init + p.lambda_p) / p.lambda_i)
    if regime == OE_PEG_STER:
        D = 1.0 + p.phi * p.lambda_p / p.Ybar
        return (-D / (p.phi * p.lambda_i),
                (p.omega - p.phi * p.r_init + p.phi * p.lambda_p
                 + p.psi * wr_state) / (p.phi * p.lambda_i))
    return (None, p.omega - p.phi * p.r_foreign + p.psi * wr_state)


def oe_is_intercept(p, wr):
    """IS intercept in the r–Y diagram at a given real exchange rate."""
    return (p.omega + p.psi * wr) / p.phi


def oe_longrun(p, regime):
    """(π*, r*, wʳ*) where the economy comes to rest.

    Under EITHER peg the nominal rate is fixed, so wʳ is at rest only when
    π = πᵃ — a pegged economy cannot hold an inflation rate of its own. Under a
    float the Taylor rule sets π* instead, and ω is absent from it."""
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


def settings_popover(label="⚙️", key_prefix="", ratio=(6, 1)):
    """Right-aligned Settings popover, meant to sit on its own row ABOVE a tab bar.

    Deliberately NOT wrapped around the tabs. Putting the tabs inside a column —
    st.columns([6,1]) with cols[0].tabs(...) — confines every diagram, panel and
    chart drawn inside those tabs to that column's width, which is what makes the
    page stop short of the vertical border instead of running to the edge. The
    settings control gets a column; the tabs stay at full width."""
    _, right = st.columns(ratio, vertical_alignment="top")
    with right.popover(label, width="stretch"):
        settings_controls(key_prefix=key_prefix, stacked=True)
