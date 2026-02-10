import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime

# --- Google Sheets Setup (secrets or local file) ---
if "GOOGLE_CREDENTIALS" in os.environ:
    creds_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
else:
    creds_info = json.load(open("credentials.json"))  # local dev

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
client = gspread.authorize(creds)

SHEET_ID = "YOUR_GOOGLE_SHEET_ID_HERE"  # Sheet URL එකෙන් ID එක copy කරගන්න[](https://docs.google.com/spreadsheets/d/SHEET_ID/edit)
sheet = client.open_by_key(SHEET_ID).sheet1  # or .worksheet("GN_Database")

# --- Simple login for security (GN use කරන්න) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("GN Data Entry - Login")
    password = st.text_input("Password ඇතුලත් කරන්න", type="password")
    if st.button("Login"):
        if password == "gn123negombo":  # ඔයාට ඕන password එකක් දාන්න (later change කරන්න)
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("වැරදි password!")
    st.stop()

# --- Main App ---
st.title("ග්‍රාම නිලධාරි දත්ත ඇතුලත් කිරීම (GN Data Entry)")
st.subheader("නව පවුල් සාමාජිකයෙකු එකතු කරන්න")

with st.form("household_member_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        household_id = st.text_input("පවුල් අංකය (Household_ID)", placeholder="GN-001-2025")
        nic = st.text_input("ජාතික හැඳුනුම්පත් අංකය (NIC)")
        name = st.text_input("සම්පූර්ණ නම")
    
    with col2:
        role = st.selectbox("භූමිකාව (Role)", ["පවුලේ ප්‍රධානි", "බිරිඳ/ස්වාමිපුරුෂයා", "දරුවා", "මව/පියා", "සහෝදරයා/සහෝදරිය", "වෙනත්"])
        job = st.text_input("රැකියාව / වෘත්තිය (Job)")
        vehicle_id = st.text_input("වාහන අංකය (Vehicle_ID, optional)")

    # Extra fields (ඔයාට ඕන නම් add කරන්න)
    gender = st.radio("ලිංගභාවය", ["පිරිමි", "ගැහැණු", "වෙනත්"])
    dob = st.date_input("උපන් දිනය (Date of Birth)", value=None)
    phone = st.text_input("දුරකථන අංකය")

    submitted = st.form_submit_button("පවුල් සාමාජිකයා එකතු කරන්න")

if submitted:
    if not household_id or not nic or not name:
        st.error("පවුල් අංකය, NIC සහ නම අනිවාර්යයි!")
    else:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [
                household_id,
                nic,
                name,
                role,
                job,
                vehicle_id,
                gender,
                str(dob) if dob else "",
                phone,
                timestamp
            ]
            sheet.append_row(row)
            st.success(f"සාර්ථකයි! {name} එකතු වුණා ✓ (Household: {household_id})")
        except Exception as e:
            st.error(f"දත්ත එකතු කිරීමේදී ගැටලුවක්: {str(e)}")

# Optional: View recent data
if st.button("අවසන් ඇතුලත් කිරීම් 10 බලන්න"):
    data = sheet.get_all_values()
    if len(data) > 1:
        recent = data[-10:]  # last 10 rows
        st.table(recent)
    else:
        st.info("තවම data නැහැ.")
