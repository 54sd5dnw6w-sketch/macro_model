import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

def add_vertical_line(plotly_fig, x_value, name="Vertical Line"):
    plotly_fig.add_vline(
        x=x_value,
        line=dict(color="black", dash="dash"),
        annotation_text=name,
        annotation_position="top")

def show_plotly_fig(fig, column_to_plot = st):
    fig.update_layout(margin=dict(t=20, b=40, l=40, r=10))
    column_to_plot.plotly_chart(fig,  config={"displayModeBar": True})