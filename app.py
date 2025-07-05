import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURATION ---
PASSWORD = "mypassword123"
DATA_FILE = "finance_data.csv"

# --- AUTHENTICATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    password_input = st.text_input("Enter password", type="password")
    login_button = st.button("Login")

    if login_button:
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "category", "amount"])
    return df

df = load_data()

# --- CLEAN DATA ---
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

# --- UI HEADER ---
st.title("💰 Personal Expense & Savings Tracker")
st.success("Login successful!")

# --- METRICS ---
total_expenses = df[df["category"] == "expense"]["amount"].sum()
total_savings = df[df["category"] == "saving"]["amount"].sum()

today = datetime.today().date()
start_of_week = today - timedelta(days=today.weekday())
weekly_df = df[df["date"].dt.date >= start_of_week]
weekly_expenses = weekly_df[weekly_df["category"] == "expense"]["amount"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("📅 Weekly Expenses", f"AED {weekly_expenses:,.2f}")
col2.metric("💸 Total Expenses", f"AED {total_expenses:,.2f}")
col3.metric("💰 Total Savings", f"AED {total_savings:,.2f}")

# --- ADD ENTRY FORM ---
st.markdown("### ➕ Add New Entry")
with st.form("entry_form"):
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["expense", "saving"])
    amount = st.number_input("Amount (AED)", min_value=0.0, step=0.01)
    submitted = st.form_submit_button("Add Entry")

if submitted:
    new_entry = pd.DataFrame([{
        "date": date.strftime("%Y-%m-%d"),
        "category": category,
        "amount": amount
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.to_csv(DATA_FILE, index=False)
    st.success("Entry added successfully!")
    st.experimental_rerun()

# --- SUMMARY VIEW ---
st.markdown("### 📊 Summary Report")
freq = st.selectbox("Group by:", ["Daily", "Weekly", "Monthly", "Yearly"])
freq_map = {
    "Daily": "D",
    "Weekly": "W",
    "Monthly": "M",
    "Yearly": "Y"
}

if not df.empty:
    grouped = df.groupby([pd.Grouper(key="date", freq=freq_map[freq]), "category"])["amount"].sum()
    summary_df = grouped.unstack(fill_value=0)
    summary_df.index = summary_df.index.date  # Show dates without time
    st.dataframe(summary_df)
else:
    st.info("No entries yet. Use the form above to add your first one!")
