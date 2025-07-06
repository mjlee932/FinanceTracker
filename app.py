import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import json

import gspread
from google.oauth2.service_account import Credentials

PASSWORD = "mypassword123"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Google Sheets helper functions
def get_gsheet_client():
    creds_json = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
    creds_dict = json.loads(creds_json)  # parse string to dict
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def export_to_gsheet(df, spreadsheet_name="Finance Transactions", worksheet_name="Transactions"):
    client = get_gsheet_client()

    try:
        spreadsheet = client.open(spreadsheet_name)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(spreadsheet_name)
        # Optional: share spreadsheet to your email here if needed
        # spreadsheet.share('your-email@example.com', perm_type='user', role='writer')

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")

    data = [df.columns.values.tolist()] + df.values.tolist()
    worksheet.update(data)
    st.success(f"Exported {len(df)} rows to Google Sheet: {spreadsheet_name} / {worksheet_name}")

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

DATA_FILE = "transactions.csv"
try:
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["date", "category", "type", "amount", "notes"])

with st.form("entry_form"):
    st.markdown("### Add New Transaction")
