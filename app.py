import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

PASSWORD = "mypassword123"

# --- Session state setup ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

# --- Login Page ---
if not st.session_state.authenticated:
    st.title("Login")
    password_input = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
        else:
            st.session_state.login_attempted = True
    if st.session_state.login_attempted and not st.session_state.authenticated:
        st.error("Incorrect password")
    st.stop()

# --- Main App ---
st.title("💰 Personal Finance Tracker")

# Data handling
DATA_FILE = "transactions.csv"
try:
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["date", "category", "type", "amount", "notes"])

# Entry form
with st.form("entry_form"):
    st.markdown("### Add New Transaction")

    trans_type = st.selectbox("Type", ["Expense", "Saving"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    notes = st.text_area("Notes", height=80)
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than 0.")
        elif not category.strip():
            st.error("Category cannot be empty.")
        else:
            timestamp = datetime.now()  # full date + time
            new_entry = {
                "date": timestamp,
                "category": category.strip(),
                "type": trans_type,
                "amount": amount,
                "notes": notes.strip()
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Transaction added on {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


# Current week summary
st.subheader("📆 Current Week Summary")
today = datetime.today()
start_of_week = today - timedelta(days=today.weekday())
end_of_week = start_of_week + timedelta(days=6)

week_df = df[(df["date"] >= start_of_week) & (df["date"] <= end_of_week)]
weekly_expense = week_df[week_df["type"] == "Expense"]["amount"].sum()
weekly_saving = week_df[week_df["type"] == "Saving"]["amount"].sum()

st.markdown(f"**Total Weekly Expenses:** AED {weekly_expense:.2f}")
st.markdown(f"**Total Weekly Savings:** AED {weekly_saving:.2f}")

# Summary viewer
# Summary viewer
st.subheader("📊 Summary by Period")

freq_options = {
    "Daily": "D",
    "Weekly": "W-MON",
    "Monthly": "M",
    "Yearly": "Y"
}

summary_type = st.selectbox("Select summary type", list(freq_options.keys()) + ["Custom Date Range"])

# Let user choose date range for all summary types
start_date = st.date_input("Start date", datetime.today() - timedelta(days=30))
end_date = st.date_input("End date", datetime.today())

# Make sure dates are valid
if pd.to_datetime(start_date) > pd.to_datetime(end_date):
    st.error("Start date must be before end date.")
else:
    filtered_df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

    if filtered_df.empty:
        st.info("No records in selected range.")
    elif summary_type == "Custom Date Range":
        grouped = filtered_df.groupby(["type", "category"])["amount"].sum().unstack(fill_value=0)
        st.dataframe(grouped)
    else:
        df["date"] = pd.to_datetime(df["date"])  # ensure it's datetime
        grouped = filtered_df.groupby([
            pd.Grouper(key="date", freq=freq_options[summary_type]),
            "type",
            "category"
        ])["amount"].sum()

        summary_df = grouped.unstack(level=[1, 2]).fillna(0)
        st.dataframe(summary_df)

st.subheader("📋 All Transactions")
if df.empty:
    st.info("No transactions found.")
else:
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))
