import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
PASSWORD = "mypassword123"
DATA_FILE = "finance_data.csv"

# --- AUTH ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# --- DATA FUNCTIONS ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["date", "category", "amount"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- SESSION DATA ---
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# --- HEADER ---
st.title("💰 Personal Finance Tracker")
st.success("Login successful!")

# --- METRICS ---
total_expenses = df[df["category"] == "expense"]["amount"].sum()
total_savings = df[df["category"] == "saving"]["amount"].sum()

today = datetime.today().date()
start_week = today - timedelta(days=today.weekday())
weekly_df = df[df["date"].dt.date >= start_week]
weekly_expenses = weekly_df[weekly_df["category"] == "expense"]["amount"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("📅 Weekly Expenses", f"AED {weekly_expenses:,.2f}")
col2.metric("💸 Total Expenses", f"AED {total_expenses:,.2f}")
col3.metric("💰 Total Savings", f"AED {total_savings:,.2f}")

# --- ADD ENTRY FORM ---
st.markdown("### ➕ Add New Entry")
with st.form("add_entry"):
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["expense", "saving"])
    amount = st.number_input("Amount (AED)", min_value=0.0, step=0.01)
    submitted = st.form_submit_button("Add Entry")

if submitted:
    new_entry = {
        "date": pd.to_datetime(date),
        "category": category,
        "amount": amount
    }
    st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_entry])], ignore_index=True)
    save_data(st.session_state.df)
    st.success("Entry added!")
    st.rerun()

# --- CUSTOM DATE RANGE SUMMARY ---
st.markdown("### 📊 Summary View by Date Range")

if not df.empty:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = col2.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

    if start_date > end_date:
        st.warning("⚠️ Start date must be before end date.")
    else:
        filtered_df = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]

        freq = st.selectbox("Group by", ["Daily", "Weekly", "Monthly", "Yearly"])
        freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M", "Yearly": "Y"}

        if not filtered_df.empty:
            grouped = filtered_df.groupby([pd.Grouper(key="date", freq=freq_map[freq]), "category"])["amount"].sum()
            summary_df = grouped.unstack(fill_value=0
