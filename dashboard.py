import streamlit as st
import pandas as pd
import threading
import asyncio
import websockets
import time
from datetime import datetime
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

PI_IP = "127.0.0.1"   # change to Pi IP later
PORT = 8765
WS_URL = f"ws://{PI_IP}:{PORT}"

st.set_page_config(page_title="Sensor Dashboard", layout="wide")

# =========================
# AUTO REFRESH (SAFE)
# =========================
st_autorefresh(interval=1000, key="datarefresh")

# =========================
# DARK THEME (LIKE IMAGE)
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: #e6edf3;
}

.panel {
    background: #161b22;
    border-radius: 10px;
    padding: 12px 12px 0px 12px;
    border: 1px solid #30363d;
    margin-bottom: 20px;
}

.pump-on {
    background: #1f6f4a;
    color: #d2ffd9;
    padding: 14px;
    border-radius: 10px;
    text-align: center;
    font-weight: 600;
    font-size: 18px;
}

.pump-off {
    background: #6e1f1f;
    color: #ffd6d6;
    padding: 14px;
    border-radius: 10px;
    text-align: center;
    font-weight: 600;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

st.title("Sensor Dashboard")

# =========================
# SHARED DATA
# =========================
@st.cache_resource
def get_shared_values():
    return {
        "soil_flags": [],
        "soil_values": [],
        "air_humidity": []
    }

data = get_shared_values()

# =========================
# WEBSOCKET THREAD
# =========================
def websocket_worker():
    async def listen():
        while True:
            try:
                async with websockets.connect(WS_URL) as ws:
                    while True:
                        msg = await ws.recv()
                        ts = datetime.now()

                        parts = msg.split(",")

                        if len(parts) == 3:
                            sf = float(parts[0])
                            sv = float(parts[1])
                            ah = float(parts[2])

                            data["soil_flags"].append((ts, sf))
                            data["soil_values"].append((ts, sv))
                            data["air_humidity"].append((ts, ah))

                            for k in data:
                                del data[k][:-200]

            except:
                time.sleep(2)

    asyncio.run(listen())

if "ws_started" not in st.session_state:
    threading.Thread(target=websocket_worker, daemon=True).start()
    st.session_state["ws_started"] = True

# =========================
# DARK CHART FUNCTION
# =========================
def dark_chart(df, label):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[label],
        mode="lines",
        line=dict(width=2),
        name=label
    ))

    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=10, r=10, t=20, b=10),
        height=250,
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font=dict(color="#e6edf3"),
        xaxis=dict(showgrid=True, gridcolor="#30363d"),
        yaxis=dict(showgrid=True, gridcolor="#30363d"),
        legend=dict(orientation="h", y=1.02),
        uirevision="keep"
    )
    return fig

# =========================
# PUMP STATUS
# =========================
st.markdown("### Pump Status")

if data["soil_flags"]:
    latest_flag = data["soil_flags"][-1][1]
    if latest_flag == 1:
        st.markdown('<div class="pump-on">💧 Pump ON</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pump-off">Pump OFF</div>', unsafe_allow_html=True)
else:
    st.info("No data yet")

# =========================
# GRAPH PANELS
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### Soil Flag")
    if data["soil_flags"]:
        df = pd.DataFrame(data["soil_flags"], columns=["Time","Soil Flag"]).set_index("Time")
        st.plotly_chart(dark_chart(df,"Soil Flag"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### Soil Moisture")
    if data["soil_values"]:
        df = pd.DataFrame(data["soil_values"], columns=["Time","Soil Moisture"]).set_index("Time")
        st.plotly_chart(dark_chart(df,"Soil Moisture"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("#### Air Humidity")
    if data["air_humidity"]:
        df = pd.DataFrame(data["air_humidity"], columns=["Time","Air Humidity"]).set_index("Time")
        st.plotly_chart(dark_chart(df,"Air Humidity"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
