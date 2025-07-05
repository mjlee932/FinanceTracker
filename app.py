import streamlit as st

PASSWORD = "mypassword123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔐 Login Required")
    pwd = st.text_input("Enter password", type="password")
    login_clicked = st.button("Login")
    if login_clicked:
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()  # safe here, right after login click
        else:
            st.error("Incorrect password")

if not st.session_state.authenticated:
    login()
    st.stop()

# The rest of your app below...

# --- MAIN APP ---

st.title("💰 Personal Finance Tracker")

# Load data or create empty dataframe
DATA_FILE = "finance_data.csv"

try:
    df = pd.read_csv(DATA_FILE)
    df['date'] = pd.to_datetime(df['date'])
except FileNotFoundError:
    df = pd.DataFrame(columns=['date', 'category', 'type', 'amount', 'notes'])

# --- Add New Entry ---
with st.form("Add New Entry"):
    st.subheader("Add Expense or Saving")
    date = st.date_input("Date", value=datetime.today())
    category = st.text_input("Category (e.g., Food, Transport, Salary)")
    type_ = st.selectbox("Type", ["Expense", "Saving"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    notes = st.text_area("Notes (optional)")
    submitted = st.form_submit_button("Add Entry")

    if submitted:
        if category.strip() == "":
            st.error("Please enter a category.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            new_entry = {
                "date": pd.to_datetime(date),
                "category": category.strip(),
                "type": type_,
                "amount": amount,
                "notes": notes.strip()
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("Entry added successfully!")
            st.experimental_rerun()

# --- Summary Filters ---
st.sidebar.header("Filter & Summary Options")

start_date = st.sidebar.date_input("Start date", value=df['date'].min() if not df.empty else datetime.today())
end_date = st.sidebar.date_input("End date", value=df['date'].max() if not df.empty else datetime.today())

if start_date > end_date:
    st.sidebar.error("Start date must be before or equal to End date.")

freq = st.sidebar.selectbox("Summary Frequency", ["Daily", "Weekly", "Monthly", "Yearly"])

# Filter dataframe by date
mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
filtered_df = df.loc[mask]

# Map freq to pandas freq strings
freq_map = {
    "Daily": "D",
    "Weekly": "W",
    "Monthly": "M",
    "Yearly": "Y"
}

if not filtered_df.empty:
    # Group data by freq and category for expenses and savings separately
    grouped = filtered_df.groupby([
        pd.Grouper(key='date', freq=freq_map[freq]),
        'category',
        'type'
    ])['amount'].sum().unstack(fill_value=0)

    st.subheader(f"{freq} Summary from {start_date} to {end_date}")

    # Show grouped summary table
    st.dataframe(grouped)

    # Totals by type
    total_expenses = filtered_df.loc[filtered_df['type'] == "Expense", 'amount'].sum()
    total_savings = filtered_df.loc[filtered_df['type'] == "Saving", 'amount'].sum()
    st.markdown(f"**Total Expenses:** ${total_expenses:.2f}")
    st.markdown(f"**Total Savings:** ${total_savings:.2f}")

    st.subheader("All Transactions")
    st.dataframe(filtered_df.sort_values(by='date', ascending=False).reset_index(drop=True))
else:
    st.info("No data available for the selected date range.")

