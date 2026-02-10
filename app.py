import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import os
from datetime import datetime

# ------------------ Google Sheets Connection (cached) ------------------
@st.cache_resource
def get_sheet():
    # Streamlit Cloud secrets වල GOOGLE_CREDENTIALS key එක තියෙන්න ඕන (full JSON string)
    if "GOOGLE_CREDENTIALS" in os.environ:
        creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    else:
        # Local testing වලදි credentials.json file එක use කරන්න (gitignore කරලා තියන්න!)
        try:
            with open("credentials.json", "r") as f:
                creds_dict = json.load(f)
        except FileNotFoundError:
            st.error("Local credentials.json file නැහැ. Streamlit Cloud වලදි secrets දාලා තියෙනවද බලන්න.")
            st.stop()

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    # ඔයාගේ Sheet ID එක මෙතන දාලා තියෙනවා
    SHEET_ID = "1itCCxoIfEWWroY5c3ukjLho9B1V0QM6WwR-6Z2rMORE"
    sheet = client.open_by_key(SHEET_ID).sheet1  # sheet1 = first tab (gid=0)
    
    return sheet

worksheet = get_sheet()

# ------------------ Simple Login (GN use කරන්න) ------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("GN Data Entry System - Login")
    password = st.text_input("Password ඇතුලත් කරන්න", type="password")
    if st.button("Login"):
        if password == "gnnegombo2025":  # ඔයාට ඕන password එක change කරන්න!
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("වැරදි password! නැවත උත්සාහ කරන්න.")
    st.stop()

# ------------------ Main Data Entry Form ------------------
st.title("ග්‍රාම නිලධාරි දත්ත ඇතුලත් කිරීම")
st.subheader("නව පවුල් සාමාජිකයෙකු එකතු කරන්න")

with st.form("member_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        household_id = st.text_input("පවුල් අංකය (Household_ID)", placeholder="GN-001-2025")
        nic = st.text_input("NIC අංකය")
        name = st.text_input("සම්පූර්ණ නම")
    
    with col2:
        role = st.selectbox("භූමිකාව (Role)", ["පවුලේ ප්‍රධානි", "බිරිඳ", "ස්වාමිපුරුෂයා", "දරුවා", "මව", "පියා", "සහෝදරයා", "සහෝදරිය", "වෙනත්"])
        job = st.text_input("රැකියාව / වෘත්තිය")
        vehicle_id = st.text_input("වාහන අංකය (optional)")

    # Extra fields (ඔයාගේ sheet එකට columns add කරලා තියෙනවා නම් මේවාත් append කරන්න)
    gender = st.radio("ලිංගභාවය", ["පිරිමි", "ගැහැණු", "වෙනත්"], horizontal=True)
    dob = st.date_input("උපන් දිනය", value=None)
    phone = st.text_input("දුරකථන අංකය (optional)")

    submitted = st.form_submit_button("එකතු කරන්න", use_container_width=True)

if submitted:
    if not household_id or not nic or not name:
        st.error("පවුල් අංකය, NIC සහ නම **අනිවාර්යයි**!")
    else:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [
                household_id.strip(),
                nic.strip(),
                name.strip(),
                role,
                job.strip() if job else "",
                vehicle_id.strip() if vehicle_id else "",
                gender,
                str(dob) if dob else "",
                phone.strip() if phone else "",
                timestamp
            ]
            worksheet.append_row(new_row)
            st.success(f"සාර්ථකයි! **{name}** එකතු වුණා ✓ (පවුල් අංකය: {household_id})")
            st.balloons()  # fun effect :)
        except gspread.exceptions.APIError as api_err:
            st.error(f"Google Sheets API ගැටලුවක්: {api_err}")
            st.info("Service account එක sheet එකට Editor permission තියෙනවද බලන්න.")
        except Exception as e:
            st.error(f"අනපේක්ෂිත error එකක්: {str(e)}")

# Optional: Recent entries බලන්න button
if st.button("අවසන් ඇතුලත් කිරීම් 5 බලන්න"):
    try:
        all_data = worksheet.get_all_values()
        if len(all_data) > 1:
            recent_rows = all_data[-5:]  # last 5 rows
            st.table(recent_rows)
        else:
            st.info("තවම කිසිම data ඇතුලත් වෙලා නැහැ.")
    except Exception as e:
        st.error(f"Data බැලීමේදී error: {e}")
