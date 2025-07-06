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
st.subheader("📊 Summary")

view_option = st.selectbox("View summary by", ["Monthly", "Custom Date Range"])

if view_option == "Monthly":
    years = sorted(df["date"].dt.year.unique(), reverse=True)
    selected_year = st.selectbox("Select Year", years)

    months = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    selected_month_name = st.selectbox("Select Month", list(months.keys()))
    selected_month = months[selected_month_name]

    # Filter the data for selected year and month
    filtered_df = df[
        (df["date"].dt.year == selected_year) &
        (df["date"].dt.month == selected_month)
    ]

else:
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=30))
    end_date = st.date_input("End Date", datetime.today())
    if start_date > end_date:
        st.error("Start date must be before end date.")
        filtered_df = pd.DataFrame()
    else:
        filtered_df = df[
            (df["date"] >= pd.to_datetime(start_date)) &
            (df["date"] <= pd.to_datetime(end_date))
        ]

# Display summary if data exists
if filtered_df.empty:
    st.info("No records found in the selected period.")
else:
    # Totals
    total_expense = filtered_df[filtered_df["type"] == "Expense"]["amount"].sum()
    total_saving = filtered_df[filtered_df["type"] == "Saving"]["amount"].sum()

    st.markdown(f"**Total Expenses:** AED {total_expense:.2f}")
    st.markdown(f"**Total Savings:** AED {total_saving:.2f}")

    # Grouped summary
    grouped = filtered_df.groupby(["type", "category"])["amount"].sum().unstack(fill_value=0)
    st.dataframe(grouped)


st.subheader("📋 All Transactions")
if df.empty:
    st.info("No transactions found.")
else:
    st.dataframe(df.sort_values("date", ascending=False).reset_index(drop=True))
