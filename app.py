import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ------------------ Google Sheets Connection ------------------
@st.cache_resource
def get_sheet():
    creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
    
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    SHEET_ID = "1itCCxoIfEWWroY5c3ukjLho9B1V0QM6WwR-6Z2rMORE"
    return client.open_by_key(SHEET_ID).sheet1

worksheet = get_sheet()

# ------------------ Simple Login ------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("GN Data Entry - Login")
    password = st.text_input("Password ඇතුලත් කරන්න", type="password")
    if st.button("Login"):
        if password == "gnnegombo2025":  # මෙතන ඔයාට ඕන password එක දාන්න (production එකට change කරන්න)
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("වැරදි password!")
    st.stop()

# ------------------ Main App ------------------
st.title("ග්‍රාම නිලධාරි දත්ත ඇතුලත් කිරීම")
st.subheader("නව පවුල් සාමාජිකයෙකු එකතු කරන්න")

with st.form("member_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        household_id = st.text_input("පවුල් අංකය (Household_ID)", placeholder="GN-001-2025")
        nic = st.text_input("NIC අංකය")
        name = st.text_input("සම්පූර්ණ නම")
    
    with col2:
        role = st.selectbox("භූමිකාව", [
            "පවුලේ ප්‍රධානි", "බිරිඳ", "ස්වාමිපුරුෂයා", "දරුවා", 
            "මව", "පියා", "සහෝදරයා", "සහෝදරිය", "වෙනත්"
        ])
        job = st.text_input("රැකියාව / වෘත්තිය")
        vehicle_id = st.text_input("වාහන අංකය (optional)")

    # මෙතන date range එක දාලා තියෙනවා
    gender = st.radio("ලිංගභාවය", ["පිරිමි", "ගැහැණු", "වෙනත්"], horizontal=True)
    dob = st.date_input(
        "උපන් දිනය",
        value=None,
        min_value=date(1920, 1, 1),
        max_value=date(2050, 12, 31)
    )
    phone = st.text_input("දුරකථන අංකය (optional)")

    submitted = st.form_submit_button("එකතු කරන්න", use_container_width=True)

if submitted:
    if not household_id or not nic or not name:
        st.error("පවුල් අංකය, NIC සහ නම අනිවාර්යයි!")
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
            st.success(f"සාර්ථකයි! {name} එකතු වුණා ✓ (පවුල් අංකය: {household_id})")
            st.balloons()
        except Exception as e:
            st.error(f"දත්ත එකතු කිරීමේදී ගැටලුවක්: {str(e)}")
            st.info("Service account එක sheet එකට Editor permission තියෙනවද බලන්න.")

# ------------------ View Recent Entries ------------------
if st.button("අවසන් ඇතුලත් කිරීම් 5 බලන්න"):
    try:
        data = worksheet.get_all_values()
        if len(data) > 1:
            recent = data[-5:]
            st.table(recent)
        else:
            st.info("තවම කිසිම දත්ත ඇතුලත් වෙලා නැහැ.")
    except Exception as e:
        st.error(f"දත්ත බැලීමේදී ගැටලුවක්: {e}")

