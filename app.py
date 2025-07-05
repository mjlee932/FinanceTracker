import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

PASSWORD = "mypassword123"

# --- Authentication ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔐 Login Required")
    pwd = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()  # rerun only after successful login
        else:
            st.error("Incorrect password")
            # DO NOT call st.experimental_rerun() here or it loops infinitely

if not st.session_state.authenticated:
    login()
    st.stop()

# --- Main App ---
st.title("💰 Personal Finance Tracker")

# Load or initialize data
@st.cache_data(show_spinner=False)
def load_data():
    try:
        df = pd.read_csv("finance_data.csv", parse_dates=["date"])
        df["date"] = pd.to_datetime(df["date"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "category", "description", "amount", "type"])
    return df

df = load_data()

# Add new entry form
with st.form("add_entry_form", clear_on_submit=True):
    st.subheader("Add Expense or Saving")
    entry_date = st.date_input("Date", datetime.today())
    entry_type = st.selectbox("Type", ["Expense", "Saving"])
    category = st.text_input("Category")
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")

    submitted = st.form_submit_button("Add Entry")

if submitted:
    if category.strip() == "" or amount <= 0:
        st.error("Please provide valid Category and Amount > 0.")
    else:
        new_entry = {
            "date": pd.to_datetime(entry_date),
            "type": entry_type,
            "category": category.strip(),
            "description": description.strip(),
            "amount": amount,
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv("finance_data.csv", index=False)
        st.success(f"{entry_type} added!")
        st.experimental_rerun()

# Date range selector for summary
st.subheader("View Summary")
min_date = df["date"].min() if not df.empty else datetime.today()
max_date = df["date"].max() if not df.empty else datetime.today()
start_date = st.date_input("Start date", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.date_input("End date", min_value=min_date, max_value=max_date, value=max_date)

if start_date > end_date:
    st.error("Start date must be before or equal to End date.")
    st.stop()

freq_map = {
    "Daily": "D",
    "Weekly": "W",
    "Monthly": "M",
    "Yearly": "Y",
}
freq = st.selectbox("Summary Frequency", list(freq_map.keys()))

# Filter dataframe to date range
df_filtered = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

# Calculate current week total expenses and total savings (based on today)
today = pd.to_datetime(datetime.today().date())
week_start = today - pd.Timedelta(days=today.weekday())  # Monday
week_end = week_start + pd.Timedelta(days=6)
week_filter = (df["date"] >= week_start) & (df["date"] <= week_end)
week_expenses = df[(week_filter) & (df["type"] == "Expense")]["amount"].sum()
total_savings = df[df["type"] == "Saving"]["amount"].sum()

st.markdown(f"### Current Week's Total Expenses: ${week_expenses:.2f}")
st.markdown(f"### Total Savings: ${total_savings:.2f}")

if df_filtered.empty:
    st.info("No data for selected date range.")
else:
    # Group by date freq and type and sum amounts
    grouped = df_filtered.groupby(
        [pd.Grouper(key="date", freq=freq_map[freq]), "type"]
    )["amount"].sum().unstack(fill_value=0)

    st.subheader(f"{freq} Summary from {start_date} to {end_date}")
    st.dataframe(grouped.style.format("${:,.2f}"))

    st.subheader("All Transactions")
    # Sort by date descending
    st.dataframe(df_filtered.sort_values(by="date", ascending=False).reset_index(drop=True))
