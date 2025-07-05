import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

PASSWORD = "mypassword123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    st.title("Login")
    pwd = st.text_input("Enter password:", type="password")
    login_clicked = st.button("Login")
    return pwd, login_clicked

# --- LOGIN FLOW ---

if not st.session_state.authenticated:
    pwd, login_clicked = login_page()
    if login_clicked:
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()  # Rerun once after successful login
        else:
            st.error("Incorrect password")
    st.stop()  # Stop here until authenticated

# --- MAIN APP BELOW ---

# Load or initialize data
DATA_FILE = "transactions.csv"

@st.cache_data(show_spinner=False)
def load_data():
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    except FileNotFoundError:
        df = pd.DataFrame(columns=["date", "category", "type", "amount", "notes"])
    return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# Add new entry
st.header("Add New Transaction")

with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", value=datetime.today())
        category = st.text_input("Category (e.g., Food, Rent, Salary)")
    with col2:
        type_ = st.selectbox("Type", ["Expense", "Saving"])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        notes = st.text_input("Notes (optional)")
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if not category.strip():
            st.error("Please enter a category.")
        elif amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            new_entry = {
                "date": pd.to_datetime(date),
                "category": category.strip(),
                "type": type_,
                "amount": amount,
                "notes": notes.strip(),
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)
            st.success("Entry added successfully!")
            st.experimental_rerun()

# Current week summary
st.header("Current Week Summary")

today = datetime.today()
start_of_week = today - timedelta(days=today.weekday())  # Monday
end_of_week = start_of_week + timedelta(days=6)

mask_week = (df["date"] >= pd.Timestamp(start_of_week.date())) & (df["date"] <= pd.Timestamp(end_of_week.date()))
df_week = df.loc[mask_week]

total_expenses_week = df_week.loc[df_week["type"] == "Expense", "amount"].sum()
total_savings_week = df_week.loc[df_week["type"] == "Saving", "amount"].sum()

st.markdown(f"**Total Expenses this week (Mon-Sun):** AED {total_expenses_week:.2f}")
st.markdown(f"**Total Savings this week (Mon-Sun):** AED {total_savings_week:.2f}")

# Summary options
st.header("View Summary")

freq_map = {
    "Daily": "D",
    "Weekly": "W-MON",
    "Monthly": "M",
    "Yearly": "Y"
}

summary_type = st.selectbox("Summary Frequency", ["Daily", "Weekly", "Monthly", "Yearly", "Custom Date Range"])

if summary_type == "Custom Date Range":
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=df["date"].min() if not df.empty else datetime.today())
    with col2:
        end_date = st.date_input("End Date", value=datetime.today())
    if start_date > end_date:
        st.error("Start Date must be before or equal to End Date")
        st.stop()

    mask_custom = (df["date"] >= pd.Timestamp(start_date)) & (df["date"] <= pd.Timestamp(end_date))
    df_filtered = df.loc[mask_custom]

    if df_filtered.empty:
        st.info("No transactions found in this date range.")
    else:
        summary_df = df_filtered.groupby(["type", "category"])["amount"].sum().unstack(fill_value=0)
        st.subheader(f"Summary from {start_date} to {end_date}")
        st.dataframe(summary_df)
else:
    if df.empty:
        st.info("No transactions to summarize.")
    else:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        grouped = df.groupby([pd.Grouper(key="date", freq=freq_map[summary_type]), "type", "category"])["amount"].sum()
        summary_df = grouped.unstack(level=[1, 2], fill_value=0)

        st.subheader(f"{summary_type} Summary")
        st.dataframe(summary_df)

# Show all transactions
st.header("All Transactions")

if df.empty:
    st.info("No transactions recorded yet.")
else:
    df_sorted = df.sort_values(by="date", ascending=False)
    df_display = df_sorted.copy()
    df_display["date"] = df_display["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(df_display.reset_index(drop=True))
