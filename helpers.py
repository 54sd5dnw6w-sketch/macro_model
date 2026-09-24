from contextlib import nullcontext

import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import config as c

# ―――― Streamlit Helpers ――――――――――――――――
def session_init(**kwargs):
    """Set several session-state defaults at once."""
    for key, value in kwargs.items():
        if key not in st.session_state:
            st.session_state[key] = value


def panel_header(text, column_to_plot=st):
    """Small-caps label at the top of a panel."""
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

    # 'left' keeps the label inside the plot so it does not widen the left margin. Base shift 0 in both branches, so a nudged pair straddles the curve evenly; a standalone label that wants clearance passes its own label_offset.
    if label_position == 'left':
        label_x, label_y, label_anchor, label_yshift = x[0], y[0], "left", 0
    else:
        label_x, label_y, label_anchor, label_yshift = x[-1], y[-1], "left", 0
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
        xshift=label_offset,     # vertical curves offset their labels sideways
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
    """Render a figure. Pass a stable `key` for animated charts, or Streamlit
    remounts the Plotly component every rerun and the animation stutters."""
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
    """Draw one curve. slope=None means vertical, with `intercept` as its x value.
    Add the horizontal curves first — a vertical one is sized from what is already
    on the figure."""
    if slope is None:
        return add_vertical_line(plotly_fig, intercept, name=name, color=color,
                                 dash=dash, line_width=line_width, name_position='top',
                                 label_offset=label_offset)
    return add_line_to_plot(plotly_fig, slope, intercept, x_min, x_max, name=name,
                            color=color, line_width=line_width, dash=dash,
                            label_position=label_position, label_offset=label_offset)


# ―――― Curve sets: initial → short run → long run ―――――――――――――――――――――――――――
# (live colour, ghost colour)
CURVE_COLORS = {
    'IS': ("#4C78A8", "#AEC7E8"),
    'MP': ("#F58518", "#FAD7B0"),
    'IA': ("#54A24B", "#CDEACB"),
    'AD': ("#B279A2", "#E0C6DA"),
    'FX': ("#E45756", "#F5B8B7"),
}

# Pixels the two visible labels are pushed apart, so they stay readable when the curves coincide. Always applied — the axis scale is not known at draw time.
LABEL_NUDGE = 11

IDX_INITIAL, IDX_SHORT, IDX_LONG = "<sub>0</sub>", "<sub>1</sub>", "<sub>∞</sub>"


def add_curve_set(plotly_fig, key, x_min, x_max, initial, short, long_=None,
                  show_initial=False, show_long=False, label=None,
                  label_position='right'):
    """Draw one curve in the positions the current phase calls for.

    idle: `initial` alone. After Play: `initial` as a dotted ghost plus `short`.
    After Continue: `short` as the ghost plus `long_`, which drifts each period.

    Either `label_position` straddles the curve evenly: the ghost is nudged below it
    and the live label above. 'left' suits a horizontal curve whose right-edge label
    would collide with the sloped curves' labels."""
    name = key if label is None else label
    solid, pale = CURVE_COLORS[key]

    # A right-edge label sits past the end of the line and needs no clearance; a left-edge one starts ON the line and runs across it, so a lone label there is lifted by the same nudge the live label of a pair gets.
    solo_offset = LABEL_NUDGE if label_position == 'left' else 0

    def _nm(index=""):
        return f"{name}{index}"

    if not show_initial and not show_long:
        return add_model_curve(plotly_fig, *initial, x_min, x_max, name=_nm(),
                               color=solid, line_width=c.standard_line_width,
                               label_position=label_position,
                               label_offset=solo_offset)

    if show_initial:
        add_model_curve(plotly_fig, *initial, x_min, x_max, name=_nm(IDX_INITIAL),
                        color=pale, line_width=c.thin_line_width, dash='dot',
                        label_position=label_position, label_offset=-LABEL_NUDGE)
        return add_model_curve(plotly_fig, *short, x_min, x_max, name=_nm(IDX_SHORT),
                               color=solid, line_width=c.standard_line_width,
                               label_position=label_position, label_offset=LABEL_NUDGE)

    add_model_curve(plotly_fig, *short, x_min, x_max, name=_nm(IDX_SHORT),
                    color=pale, line_width=c.thin_line_width,
                    label_position=label_position, label_offset=-LABEL_NUDGE)
    return add_model_curve(plotly_fig, *long_, x_min, x_max, name=_nm(IDX_LONG),
                           color=solid, line_width=c.standard_line_width,
                           label_position=label_position, label_offset=LABEL_NUDGE)


# ―――― Units ―――――――――――――――――――――――――――――――――
def output_gap(Y, Ybar):
    """Output gap Ỹ, in the same points as r and π."""
    return Y - Ybar


# ―――― Open-economy model ―――――――――――――――――――――――――――――――――――――――――――――――――――
OE_FLOAT, OE_PEG, OE_PEG_STER = 'float', 'hard', 'ster'


class OEParams:
    """Structural parameters of the open-economy model."""

    def __init__(self, omega, phi, psi, r_init, lambda_p, lambda_i,
                 r_foreign, pi_foreign, gamma, Ybar=1.0):
        self.omega, self.phi, self.psi = omega, phi, psi
        self.r_init, self.lambda_p, self.lambda_i = r_init, lambda_p, lambda_i
        self.r_foreign, self.pi_foreign = r_foreign, pi_foreign
        self.gamma, self.Ybar = gamma, Ybar


def oe_ppp_next(p, wr, pi):
    """wʳ = wʳ₋₁·(1+πᵃ)/(1+π), with inflation in per cent."""
    return wr * (1.0 + p.pi_foreign / 100.0) / (1.0 + pi / 100.0)


def oe_baseline_wr(p):
    """Pre-shock real exchange rate: IS solved at Y = Ȳ and r = rᵃ."""
    return (p.Ybar - p.omega + p.phi * p.r_foreign) / p.psi


def oe_fx_rate(p, regime, pi):
    """Level of the FX curve — the real rate interest parity demands.

    Float: no move in wʳ is expected, so r = rᵃ. Peg: the nominal rate is fixed, so
    wʳ,ᵉ₊₁/wʳ = (1+πᵃ)/(1+π) and to first order r = rᵃ + (πᵃ − π). Under
    sterilisation the relation is absorbed by the reserve flow and constrains nothing,
    so this level is not drawn — it is kept only for the regimes where it binds."""
    if regime == OE_FLOAT:
        return p.r_foreign
    return p.r_foreign + (p.pi_foreign - pi)


def oe_peg_root(p):
    """Dominant eigenvalue of the unsterilised peg, as a growth factor per period.

    Linearising (wʳ, π) around the rest point gives a matrix with determinant
    1 + γφ·100/Ȳ, which exceeds 1 for any φ > 0 — so this regime never settles,
    whatever the other parameters are. ψ changes how fast, never whether."""
    a = oe_baseline_wr(p) / 100.0        # 100 converts π from per cent, not Ȳ
    b = p.gamma * p.psi
    c = p.gamma * p.phi
    tr, det = 2.0 + c - a * b, 1.0 + c
    disc = tr * tr - 4.0 * det
    if disc < 0:
        return det ** 0.5                      # complex pair, modulus √det
    return (abs(tr) + disc ** 0.5) / 2.0


def oe_operating_point(p, regime, pi, wr_state):
    """(Y, r, wʳ) this period, given predetermined π and the carried-over wʳ.

    Float: MP ∩ FX, then wʳ jumps to whatever makes IS pass through that point.
    Sterilised peg: IS ∩ MP at the pegged wʳ. Hard peg: IS ∩ FX at the pegged wʳ."""
    if regime == OE_FLOAT:
        # rᵃ = r' + λ_P·Ỹ + λ_I·π  solved for the gap, then for Y
        gap = (p.r_foreign - p.r_init - p.lambda_i * pi) / p.lambda_p
        Y = p.Ybar + gap
        return Y, p.r_foreign, (Y - p.omega + p.phi * p.r_foreign) / p.psi

    wr = wr_state
    if regime == OE_PEG_STER:
        D = 1.0 + p.phi * p.lambda_p
        Y = (p.omega - p.phi * p.r_init + p.phi * p.lambda_p * p.Ybar
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


def oe_next_inflation(p, pi, Y):
    """IA curve:  π₊₁ = π + γ·Ỹ.
    η, the exogenous inflation shock of the thesis's (3.10), is applied once to
    π₀ by the page rather than carried as a term here — it is zero in every other
    period, so the update itself is the plain output-gap rule."""
    return pi + p.gamma * output_gap(Y, p.Ybar)


def oe_ad_curve(p, regime, wr_state):
    """AD in π–Y space as (slope, intercept).

    Float: MP ∩ FX, so ω drops out. Sterilised peg: IS ∩ MP at the pegged wʳ.
    Hard peg: IS ∩ FX, which slopes UPWARD (+1/φ) because parity ties r to πᵃ − π,
    so more inflation means a lower real rate and more demand."""
    if regime == OE_FLOAT:
        return (-p.lambda_p / p.lambda_i,
                (p.r_foreign - p.r_init + p.lambda_p * p.Ybar) / p.lambda_i)
    if regime == OE_PEG_STER:
        D = 1.0 + p.phi * p.lambda_p
        return (-D / (p.phi * p.lambda_i),
                (p.omega - p.phi * p.r_init + p.phi * p.lambda_p * p.Ybar
                 + p.psi * wr_state) / (p.phi * p.lambda_i))
    # Y = ω − φ·(rᵃ + πᵃ − π) + ψ·wʳ, solved for π
    return (1.0 / p.phi,
            (p.r_foreign + p.pi_foreign) - (p.omega + p.psi * wr_state) / p.phi)


def oe_is_intercept(p, wr):
    """IS intercept in the r–Y diagram at a given real exchange rate."""
    return (p.omega + p.psi * wr) / p.phi


def oe_longrun(p, regime):
    """(π*, r*, wʳ*) where the economy comes to rest.
    Under either peg wʳ only stops moving at π = πᵃ; under a float the Taylor rule
    sets π* instead. For the unsterilised peg this is where the economy WOULD rest,
    not where it goes — the rest point is unstable (oe_peg_root > 1)."""
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
    """Simulation settings, shared by the Settings page and the in-page popover.
    `key_prefix` keeps the widget keys distinct between the two; `stacked` puts the
    inputs one above the other for a narrow popover."""
    current_speed = st.session_state.get("setting_speed", c.speed)
    current_label = min(SPEED_LABELS, key=lambda k: abs(SPEED_LABELS[k] - current_speed))
    saved_iters = st.session_state.get("setting_iterations", c.iteration_count)

    # nullcontext stands in for a column so both layouts share one `with` block
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
    """Right-aligned Settings popover. Give it its own row ABOVE the tab bar —
    putting the tabs in a column confines everything drawn inside them to it."""
    _, right = st.columns(ratio, vertical_alignment="top")
    with right.popover(label, width="stretch"):
        settings_controls(key_prefix=key_prefix, stacked=True)
