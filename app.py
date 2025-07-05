import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURE PASSWORD ---
PASSWORD = "mypassword123"  # 🔐 Change this to your own password

# --- LOGIN SCREEN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    password_input = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# --- MAIN APP CONTENT ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('finance_data.csv')
    except FileNotF
