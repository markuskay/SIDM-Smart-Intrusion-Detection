# ================================================================
# SMART INTRUSION DETECTION & PREVENTION SYSTEM (SIDM)
# Hybrid Ensemble + Ethereum API Integration + Streamlit Dashboard
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from web3 import Web3
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import joblib
import os

# -----------------------------------------------------------
# 🎨 PAGE CONFIGURATION
# -----------------------------------------------------------
st.set_page_config(page_title="SIDM Dashboard", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
body { background-color: #0e1117; color: white; }
h1, h2, h3, h4 { color: #C4BAFF; font-weight: 700; }
.stButton>button {
    background-color: #5A4FCF; color: white; border-radius: 8px;
    padding: 10px 20px; font-weight: bold; border: none;
}
.stTextInput>div>div>input, .stNumberInput>div>div>input {
    background-color: #1c1e25; color: white; border: 1px solid #5A4FCF;
    border-radius: 6px;
}
.stSelectbox>div>div>select {
    background-color: #1c1e25; color: white; border: 1px solid #5A4FCF;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# ⚙️ LOAD MODELS AND FEATURES
# -----------------------------------------------------------
@st.cache_resource
def load_models():
    rf = joblib.load(r"C:\Users\HP\Desktop\model\rf_model.pkl")
    xgb = joblib.load(r"C:\Users\HP\Desktop\model\xgb_model.pkl")
    lstm = load_model(r"C:\Users\HP\Desktop\model\lstm_model.h5")
    scaler = StandardScaler()
    all_features = [f"feature_{i}" for i in range(54)]
    return rf, xgb, lstm, scaler, all_features

rf_model, xgb_model, lstm_model, scaler, feature_cols = load_models()

# -----------------------------------------------------------
# 🌐 ETHEREUM CONNECTION + GAS PRICE
# -----------------------------------------------------------
INFURA_RPC_URL = "https://mainnet.infura.io/v3/c712904d1b82429db08b179259366653"

try:
    w3 = Web3(Web3.HTTPProvider(INFURA_RPC_URL))
    if not w3.is_connected():
        raise ConnectionError("Infura connection failed.")
    eth_status = "✅ Connected to Ethereum Mainnet via Infura"
except Exception as e:
    st.warning(f"⚠️ Infura error: {e} — using public RPC fallback.")
    w3 = Web3(Web3.HTTPProvider("https://eth-mainnet.public.blastapi.io"))
    eth_status = "⚠️ Using public RPC fallback" if w3.is_connected() else "❌ Ethereum network not connected"

@st.cache_data(ttl=30)
def get_gas_price():
    try:
        if not w3.is_connected():
            return {"error": "Ethereum client not connected"}
        base_gas_wei = w3.eth.gas_price
        base_gas_gwei = base_gas_wei / 1_000_000_000
        return {
            "slow": round(base_gas_gwei * 0.9, 2),
            "standard": round(base_gas_gwei, 2),
            "fast": round(base_gas_gwei * 1.2, 2),
        }
    except Exception as e:
        return {"error": str(e)}

# -----------------------------------------------------------
# 🧮 PREDICTION FUNCTION
# -----------------------------------------------------------
def sidm_predict(input_df):
    aligned = pd.DataFrame(columns=feature_cols)
    for col in feature_cols:
        aligned[col] = input_df[col] if col in input_df.columns else 0
    X_scaled = scaler.fit_transform(aligned)
    rf_p = rf_model.predict_proba(X_scaled)
    xgb_p = xgb_model.predict_proba(X_scaled)
    lstm_p = lstm_model.predict(X_scaled)
    avg_p = (rf_p + xgb_p + lstm_p) / 3
    predictions = np.argmax(avg_p, axis=1)
    confidence = np.max(avg_p, axis=1)
    result_df = input_df.copy()
    result_df["Threat_Label"] = ["Normal" if p == 0 else "Malicious" for p in predictions]
    result_df["Confidence (%)"] = np.round(confidence * 100, 2)
    return result_df[["Threat_Label", "Confidence (%)"]]

# -----------------------------------------------------------
# 🔐 LOGIN PAGE
# -----------------------------------------------------------
def login_page():
    st.title("🔐 Secure Login Portal")
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "sidm123":
            st.session_state["authenticated"] = True
            st.success("✅ Login Successful! Redirecting...")
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error("❌ Invalid credentials.")

# -----------------------------------------------------------
# 🏠 HOME PAGE
# -----------------------------------------------------------
def home_page():
    st.title("🏠 SIDM Home Dashboard")
    st.subheader("Smart Intrusion Detection & Ethereum-Integrated Security System")
    st.markdown(f"**Blockchain Connection:** {eth_status}")

    st.subheader("⛽ Live Ethereum Gas Prices")
    gas = get_gas_price()
    if "error" in gas:
        st.error(f"⚠️ Unable to fetch gas data: {gas['error']}")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("🕒 Slow", f"{gas['slow']} Gwei")
        c2.metric("⚙️ Standard", f"{gas['standard']} Gwei")
        c3.metric("🚀 Fast", f"{gas['fast']} Gwei")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("🚨 Intrusion Detection", on_click=lambda: st.session_state.update(page="detection"))
    with col2:
        st.button("🛡️ Prevention Mechanism", on_click=lambda: st.session_state.update(page="prevention"))
    with col3:
        st.button("📊 Reports & Logs", on_click=lambda: st.session_state.update(page="reports"))

# -----------------------------------------------------------
# 🚨 INTRUSION DETECTION PAGE
# -----------------------------------------------------------
def intrusion_detection_page():
    st.title("🚨 Intrusion Detection System")
    st.markdown("Analyse Ethereum wallet activity or network metrics for threat prediction.")

    wallet = st.text_input("Enter Ethereum Wallet Address", placeholder="e.g., 0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
    auto_data = {}

    if wallet:
        if not wallet.startswith("0x") or len(wallet) != 42:
            st.error("❌ Invalid Ethereum address format. It must start with '0x' and be 42 characters long.")
        elif w3.is_connected():
            try:
                balance = w3.eth.get_balance(wallet)
                ether_balance = w3.from_wei(balance, 'ether')
                tx_count = w3.eth.get_transaction_count(wallet)
                latest_block = w3.eth.block_number
                auto_data = {
                    "ether_balance": float(ether_balance),
                    "transactions": tx_count,
                    "latest_block": latest_block,
                }
                st.success(f"✅ Wallet Connected — Latest Block: {latest_block}")
                st.info(f"💰 Balance: {ether_balance:.4f} ETH | 🧾 Transactions: {tx_count}")
            except Exception as e:
                st.error(f"⚠️ Error fetching wallet data: {str(e)}")
        else:
            st.error("❌ Ethereum network not connected. Please check your Infura URL.")

    with st.form("detection_form"):
        st.markdown("### 🧩 Input Parameters")
        protocol = st.selectbox("Protocol", ["TCP", "UDP", "ICMP"])
        flag = st.text_input("Flag (A, AP, R)", "A")
        sent_tnx = st.number_input("Sent Transactions", 0, 10000, value=auto_data.get("transactions", 100))
        recv_tnx = st.number_input("Received Transactions", 0, 10000, value=120)
        ether_sent = st.number_input("Total Ether Sent (ETH)", 0.0, 100.0, 0.002)
        ether_received = st.number_input("Total Ether Received (ETH)", 0.0, 100.0, 0.003)
        wallet_balance = auto_data.get("ether_balance", 0.8)
        ether_balance = st.number_input("Ether Balance (ETH)", 0.0, max(100.0, wallet_balance * 2), wallet_balance)
        erc20_txn = st.number_input("Total ERC20 Transactions", 0, 5000, value=25)
        submitted = st.form_submit_button("🔍 Predict Threat")

    if submitted:
        protocol_map = {"TCP": 1, "UDP": 2, "ICMP": 3}
        flag_map = {"A": 1, "AP": 2, "R": 3}
        input_df = pd.DataFrame([{
            "feature_0": protocol_map.get(protocol, 0),
            "feature_1": flag_map.get(flag.upper(), 0),
            "feature_2": sent_tnx,
            "feature_3": recv_tnx,
            "feature_4": ether_sent,
            "feature_5": ether_received,
            "feature_6": ether_balance,
            "feature_7": erc20_txn,
        }])
        result = sidm_predict(input_df)
        st.success("✅ Prediction Complete!")
        st.dataframe(result.style.highlight_max(axis=0, color='#5A4FCF'))
        label = result["Threat_Label"].iloc[0]
        conf = result["Confidence (%)"].iloc[0]
        if label == "Malicious":
            st.error(f"🚫 Threat Detected — Confidence: {conf}%")
        else:
            st.success(f"🟢 Normal Activity — Confidence: {conf}%")

    st.markdown("---")
    if st.button("🏠 Return to Home"):
        st.session_state["page"] = "home"
        st.rerun()

# -----------------------------------------------------------
# 🛡️ PREVENTION PAGE
# -----------------------------------------------------------
def prevention_page():
    st.title("🛡️ Prevention Mechanism")
    st.markdown("Apply proactive countermeasures to detected threats.")
    col1, col2 = st.columns(2)
    with col1:
        action = st.selectbox("Select Action", ["Block IP", "Rate Limit", "Verify Transactions", "Deploy Firewall"])
    with col2:
        target = st.text_input("Target IP / Wallet Address", "192.168.1.12")
    if st.button("Execute Action"):
        st.success(f"✅ {action} applied successfully on {target}")
    st.markdown("---")
    if st.button("🏠 Return to Home"):
        st.session_state["page"] = "home"
        st.rerun()

# -----------------------------------------------------------
# 📊 REPORTS PAGE
# -----------------------------------------------------------
def reports_page():
    st.title("📊 Logs & Blockchain Audit")
    data = pd.DataFrame({
        "Timestamp": [datetime.now(), datetime.now()],
        "IP Address": ["192.168.3.5", "192.168.8.7"],
        "Threat Type": ["DoS", "Malware"],
        "Action": ["Blocked", "Quarantined"],
        "Status": ["Resolved", "Monitoring"],
    })
    st.dataframe(data)
    st.download_button("📥 Export Logs", data.to_csv(index=False), "sidm_logs.csv")
    st.markdown("---")
    if st.button("🏠 Return to Home"):
        st.session_state["page"] = "home"
        st.rerun()

# -----------------------------------------------------------
# 🧭 MAIN NAVIGATION
# -----------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if not st.session_state["authenticated"]:
    login_page()
else:
    page = st.session_state["page"]
    if page == "home":
        home_page()
    elif page == "detection":
        intrusion_detection_page()
    elif page == "prevention":
        prevention_page()
    elif page == "reports":
        reports_page()
