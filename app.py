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

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")

    data = [df.columns.values.tolist()] + df.values.tolist()
    worksheet.update(data)
    st.success(f"Exported {len(df)} rows to Google
