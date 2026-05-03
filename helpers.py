import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go



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

def add_line_to_plot(plotly_fig, slope, intercept, x_min=0, x_max=10, n_points=100, name='Name', color='blue', width=3, dash='solid'):
    x = np.linspace(x_min, x_max, n_points)
    y = slope * x + intercept
    df = pd.DataFrame({"x": x, "y": y})

    plotly_fig.add_trace(
        go.Scatter(
            x=df["x"],
            y=df["y"],
            mode="lines",
            name=name,
            line=dict(color=color, width=width, dash=dash)
        )
    )

    plotly_fig.add_annotation(
        x=x[-1],
        y=y[-1],
        text=name,
        showarrow=False,
        xanchor="left",
        font=dict(color=color)  # match line color
    )

    return df

def add_vertical_line(plotly_fig, x_value, y_min=None, y_max=None, color="#000000", dash="dash", name="Vertical Line", name_position='bottom'):
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
        line=dict(color=color, dash=dash),
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
        font=dict(color=color),
    )

    return plotly_fig



def show_plotly_fig(fig, column_to_plot = st):
    fig.update_layout(margin=dict(t=20, b=40, l=40, r=10))
    column_to_plot.plotly_chart(fig,  config={"displayModeBar": True})