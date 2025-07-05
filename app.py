import streamlit as st
import pandas as pd
from datetime import datetime

# Password for login
PASSWORD = "yourpassword"

# Initialize authentication state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Incorrect password")
    st.stop()

st.title("💰 Personal Finance Tracker")

# Load or initialize DataFrame
@st.cache_data(show_spinner=False)
def load_data():
    try:
        df = pd.read_csv("finance_data.csv", parse_dates=["date"])
        # Ensure date column is datetime
        df["date"] = pd.to_datetime(df["date"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "category", "description", "amount", "type"])
    return df

df = load_data()

# Entry form
with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", datetime.today())
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Savings", "Other"])
    with col2:
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    type_ = st.radio("Type", ["Expense", "Savings"])
    submitted = st.form_submit_button("Add Entry")

if submitted:
    new_entry = {
        "date": pd.to_datetime(date),
        "category": category,
        "description": description,
        "amount": amount,
        "type": type_,
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv("finance_data.csv", index=False)
    st.success("Entry added!")

# Date range selector for summary
st.header("📊 Summary")
start_date = st.date_input("Start date", df["date"].min() if not df.empty else datetime.today())
end_date = st.date_input("End date", df["date"].max() if not df.empty else datetime.today())

if start_date > end_date:
    st.error("Error: Start date must be before end date.")
else:
    mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
    filtered_df = df.loc[mask]

    if filtered_df.empty:
        st.info("No entries for the selected date range.")
    else:
        # Group by date and category, sum amounts separately for Expenses and Savings
        st.subheader("Summary by Category")
        summary_expenses = (
            filtered_df[filtered_df["type"] == "Expense"]
            .groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )
        summary_savings = (
            filtered_df[filtered_df["type"] == "Savings"]
            .groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.markdown("**Expenses:**")
        st.table(summary_expenses)

        st.markdown("**Savings:**")
        st.table(summary_savings)

        st.subheader("Total")
        total_expenses = summary_expenses.sum()
        total_savings = summary_savings.sum()
        st.write(f"Total Expenses: ${total_expenses:.2f}")
        st.write(f"Total Savings: ${total_savings:.2f}")

        # Detailed transactions
        st.subheader("Detailed Transactions")
        st.dataframe(filtered_df.sort_values(by="date", ascending=False))

