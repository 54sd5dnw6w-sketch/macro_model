import io
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ECB Rates Monitor", layout="wide")
st.title("ECB Key Interest Rates")

SERIES = {
    "Main refinancing operations": "B.U2.EUR.4F.KR.MRR_FR.LEV",
    "Deposit facility": "B.U2.EUR.4F.KR.DFR.LEV",
    "Marginal lending facility": "B.U2.EUR.4F.KR.MLFR.LEV",
}

BASE_URL = "https://data-api.ecb.europa.eu/service/data/FM/{key}?format=csvdata"


@st.cache_data(ttl=3600)
def fetch_series(series_key: str) -> pd.DataFrame:
    url = BASE_URL.format(key=series_key)
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    df = pd.read_csv(io.StringIO(r.text), sep=None, engine="python")
    df.columns = [c.strip().upper() for c in df.columns]

    date_col = next((c for c in df.columns if "TIME_PERIOD" in c or c in {"TIME", "DATE"}), df.columns[0])
    value_col = next((c for c in df.columns if "OBS_VALUE" in c or c in {"VALUE"}), df.columns[1])

    out = df[[date_col, value_col]].copy()
    out.columns = ["date", "value"]
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna().sort_values("date")
    return out


selected = st.multiselect("Rates to show", list(SERIES.keys()), default=list(SERIES.keys()))

# --- metrics in 3 columns ---
cols = st.columns(3)

# --- plotly figure ---
fig = go.Figure()

for i, name in enumerate(selected):
    df = fetch_series(SERIES[name])
    if not df.empty:
        # step-like line
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["value"],
            mode="lines",
            name=name,
            line_shape="hv"
        ))

        latest = df.iloc[-1]

        with cols[i % 3]:
            st.metric(
                name,
                f'{latest["value"]:.2f}%',
                delta=f'Latest date: {latest["date"].date()}'
            )

# layout
fig.update_layout(
    title="ECB key rates",
    xaxis_title="Date",
    yaxis_title="Percent",
    template="plotly_white",
    hovermode="x unified"
    )

st.plotly_chart(fig, use_container_width=True)

st.caption("Data source: ECB Data Portal API")