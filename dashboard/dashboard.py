import streamlit as st
import requests
import random
import time
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Maintenance", layout="wide")

# ---------------- SOFT MODERN UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #e8f0ff, #f5f7fa);
}

h1, h2, h3 {
    color: #2b2d42;
}

.block-container {
    padding-top: 1rem;
}

.metric-card {
    background: #ffffff;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

/* blinking animation */
@keyframes blink {
    50% { opacity: 0.3; }
}

.blink {
    animation: blink 1s infinite;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN SYSTEM ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")

    st.stop()

# ---------------- HEADER ----------------
st.title("⚙️ AI Predictive Maintenance System")
st.caption("Smart Monitoring | Multi-Machine | Real-Time AI")

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Control Panel")
machines = st.sidebar.slider("Number of Machines", 1, 5, 2)
speed = st.sidebar.slider("Speed", 0.5, 2.0, 1.0)

# ---------------- SESSION ----------------
if "data" not in st.session_state:
    st.session_state.data = []

# ---------------- DATA GENERATOR ----------------
def generate_data(machine_id):
    return {
        "machine": f"Machine-{machine_id}",
        "temperature": random.randint(30, 100),
        "vibration": round(random.uniform(1, 10), 2),
        "current": random.randint(5, 20)
    }

# ---------------- SOUND ALERT ----------------
def play_alarm():
    st.markdown("""
    <audio autoplay>
    <source src="https://www.soundjay.com/button/beep-07.wav" type="audio/wav">
    </audio>
    """, unsafe_allow_html=True)

# ---------------- MAIN LOOP ----------------
placeholder = st.empty()

for _ in range(50):

    new_data = []

    for i in range(1, machines + 1):

        sensor = generate_data(i)

        try:
            res = requests.post("http://127.0.0.1:5000/predict", json=sensor).json()
            sensor["prediction"] = res["prediction"]
            sensor["confidence"] = res["confidence"]
        except:
            sensor["prediction"] = "Error"
            sensor["confidence"] = 0

        new_data.append(sensor)
        st.session_state.data.append(sensor)

    df = pd.DataFrame(st.session_state.data)

    with placeholder.container():

        st.subheader("📊 Multi-Machine Live Metrics")

        cols = st.columns(machines)

        for idx, machine_data in enumerate(new_data):
            with cols[idx]:

                st.markdown(f"""
                <div class="metric-card">
                <b>{machine_data['machine']}</b><br>
                🌡 Temp: {machine_data['temperature']}<br>
                📳 Vib: {machine_data['vibration']}<br>
                ⚡ Curr: {machine_data['current']}
                </div>
                """, unsafe_allow_html=True)

                # -------- GAUGE (SIMULATED) --------
                st.progress(machine_data["temperature"] / 100)

                # -------- STATUS --------
                if "Failure" in machine_data["prediction"]:
                    st.markdown(
                        f"<div class='blink' style='color:red;'>🚨 ALERT ({machine_data['confidence']}%)</div>",
                        unsafe_allow_html=True
                    )
                    play_alarm()
                else:
                    st.success(f"Normal ({machine_data['confidence']}%)")

        # -------- TABLE --------
        st.subheader("📋 Logs")
        st.dataframe(df.tail(10), use_container_width=True)

        # -------- CHART --------
        st.subheader("📈 Temperature Trend")
        st.line_chart(df["temperature"])

    time.sleep(speed)

# ---------------- DOWNLOAD ----------------
if len(st.session_state.data) > 0:
    df = pd.DataFrame(st.session_state.data)

    csv = df.to_csv(index=False).encode('utf-8')

    st.download_button("⬇️ Download Logs", csv, "logs.csv")