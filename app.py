import streamlit as st
import pandas as pd
from datetime import datetime

# Load or initialize data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('finance_data.csv', parse_dates=['date'])
    except FileNotFoundError:
        df = pd.DataFrame(columns=['date', 'category', 'amount'])
    return df

df = load_data()

st.title("💰 My Expense & Savings Tracker")

# Input form
with st.form("entry_form"):
    date = st.date_input("Date", datetime.today())
    category = st.selectbox("Category", ["expense", "saving"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    submitted = st.form_submit_button("Add Entry")

if submitted:
    new_entry = {'date': date, 'category': category, 'amount': amount}
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv('finance_data.csv', index=False)
    st.success("Entry added!")

# Display summary options
freq = st.selectbox("View Summary By:", ["Daily", "Monthly", "Yearly"])
freq_map = {"Daily": "D", "Monthly": "M", "Yearly": "Y"}

if not df.empty:
    summary = df.groupby([pd.Grouper(key='date', freq=freq_map[freq]), 'category'])['amount'].sum().unstack().fillna(0)
    st.write(f"### {freq} Summary")
    st.dataframe(summary)
else:
    st.info("No data yet. Add some entries!")
