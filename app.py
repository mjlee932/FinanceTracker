import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- PASSWORD SETUP ---
PASSWORD = "mypassword123"

# Initialize session state for authentication and data storage
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["date", "category", "type", "amount", "description"])

# --- LOGIN FUNCTION ---
def login():
    st.title("🔐 Login Required")
    pwd = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Incorrect password")

# --- MAIN APP FUNCTION ---
def main_app():
    st.title("💰 Expense & Savings Tracker")

    # --- Input Form ---
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.today())
        category = st.text_input("Category (e.g. Food, Rent, Salary)")
        entry_type = st.selectbox("Type", ["Expense", "Saving"])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        description = st.text_input("Description (optional)")
        submitted = st.form_submit_button("Add Entry")

        if submitted:
            if not category or amount <= 0:
                st.error("Please enter a valid category and amount > 0.")
            else:
                new_row = {
                    "date": pd.to_datetime(date),
                    "category": category.strip(),
                    "type": entry_type,
                    "amount": amount,
                    "description": description.strip()
                }
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Entry added!")

    df = st.session_state.data.copy()
    if df.empty:
        st.info("No entries yet. Add your first expense or saving!")
        return

    # --- Filter by date range ---
    st.subheader("Filter & Summary")
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    start_date = st.date_input("Start date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input("End date", min_value=min_date, max_value=max_date, value=max_date)
    if start_date > end_date:
        st.error("Start date must be before or equal to End date.")
        return

    mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    filtered = df.loc[mask]

    if filtered.empty:
        st.info("No data for the selected date range.")
        return

    # --- Weekly total (current week) ---
    today = datetime.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)
    mask_week = (df["date"].dt.date >= week_start.date()) & (df["date"].dt.date <= week_end.date())
    current_week = df.loc[mask_week]
    week_expense = current_week.loc[current_week["type"] == "Expense", "amount"].sum()
    week_saving = current_week.loc[current_week["type"] == "Saving", "amount"].sum()

    st.markdown(f"### Current Week Totals ({week_start.date()} to {week_end.date()}):")
    st.write(f"- **Expenses:** ${week_expense:.2f}")
    st.write(f"- **Savings:** ${week_saving:.2f}")

    # --- Summary Table ---
    st.markdown(f"### Summary from {start_date} to {end_date}")
    summary = filtered.groupby(["type", "category"])["amount"].sum().unstack(fill_value=0)
    st.dataframe(summary.style.format("${:,.2f}"))

    # --- Detailed transactions ---
    st.markdown("### Transaction Details")
    st.dataframe(filtered.sort_values("date", ascending=False).reset_index(drop=True))

# --- APP RUN ---
if not st.session_state.authenticated:
    login()
    st.stop()
else:
    main_app()
