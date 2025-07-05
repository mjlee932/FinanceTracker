import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

PASSWORD = "mypassword123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    password_input = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Incorrect password")
    st.stop()

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('finance_data.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['date', 'category', 'amount'])
    return df

df = load_data()

# Convert 'date' to datetime, coerce errors to NaT, then drop invalid dates
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])

st.title("💰 My Expense & Savings Tracker")

total_savings = df[df['category'] == 'saving']['amount'].sum()
total_expenses = df[df['category'] == 'expense']['amount'].sum()

today = datetime.today().date()
start_of_week = today - timedelta(days=today.weekday())
this_week_df = df[df['date'].dt.date >= start_of_week]
weekly_expenses = this_week_df[this_week_df['category'] == 'expense']['amount'].sum()

st.markdown("### 📊 Summary")
col1, col2, col3 = st.columns(3)
col1.metric("This Week's Expenses", f"AED {weekly_expenses:,.2f}")
col2.metric("Total Expenses", f"AED {total_expenses:,.2f}")
col3.metric("Total Savings", f"AED {total_savings:,.2f}")

st.markdown("### ➕ Add New Entry")
with st.form("entry_form"):
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["expense", "saving"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    submitted = st.form_submit_button("Add Entry")

if submitted:
    new_entry = {
        'date': date.strftime("%Y-%m-%d"),
        'category': category,
        'amount': amount
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df.to_csv('finance_data.csv', index=False)
    st.success("Entry added!")
    st.experimental_rerun()

st.markdown("### 📅 Time-Based Summary")
freq = st.selectbox("View Summary By:", ["Daily", "Monthly", "Yearly"])
freq_map = {"Daily": "D", "Monthly": "M", "Yearly": "Y"}

if not df.empty:
    summary = df.groupby(
        [pd.Grouper(key='date', freq=freq_map[freq]), 'category']
    )['amount'].sum().unstack().fillna(0)
    st.dataframe(summary)
else:
    st.info("No data yet. Add some entries!")
