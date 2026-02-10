import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import pandas as pd  # Search feature එකට pandas add කළා (requirements.txt එකට pandas add කරගන්න)

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
        if password == "gnnegombo2025":  # මෙතන ඔයාගේ password එක change කරගන්න
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("වැරදි password!")
    st.stop()

# ------------------ Main App ------------------
st.title("ග්‍රාම නිලධාරි දත්ත ඇතුලත් කිරීම (හවුපේ උතුර 175/B)")
st.subheader("නව පවුල් සාමාජිකයෙකු එකතු කරන්න")

with st.form("member_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        household_id = st.text_input("පවුල් අංකය (Household_ID)", placeholder="GN-001-2025")
        nic = st.text_input("NIC අංකය")
        name = st.text_input("සම්පූර්ණ නම")
        address = st.text_input("ලිපිනය")  # New field
    
    with col2:
        role = st.selectbox("භූමිකාව", [
            "පවුලේ ප්‍රධානි", "බිරිඳ", "ස්වාමිපුරුෂයා", "දරුවා", 
            "මව", "පියා", "සහෝදරයා", "සහෝදරිය", "වෙනත්"
        ])
        job = st.text_input("රැකියාව / වෘත්තිය")
        education = st.text_input("අධ්‍යාපන සුදුසුකම්")  # New field
        email = st.text_input("විද්‍යුත් ලිපිනය (Email)")  # New field

    col3, col4 = st.columns(2)
    
    with col3:
        vehicle1 = st.text_input("වාහන අංකය 1 (optional)")  # New: Vehicle 1
        vehicle2 = st.text_input("වාහන අංකය 2 (optional)")  # New: Vehicle 2
        home_phone = st.text_input("දුරකථන අංකය (නිවස)")  # New: Home Phone
    
    with col4:
        mobile_phone = st.text_input("දුරකථන අංකය (ජංගම)")  # New: Mobile Phone
        gender = st.radio("ලිංගභාවය", ["පිරිමි", "ගැහැණු", "වෙනත්"], horizontal=True)
    
    # Birthday range: 1920 - 2050
    dob = st.date_input(
        "උපන් දිනය",
        value=None,
        min_value=date(1920, 1, 1),
        max_value=date(2050, 12, 31)
    )

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
                vehicle1.strip() if vehicle1 else "",  # Vehicle 1
                vehicle2.strip() if vehicle2 else "",  # Vehicle 2
                gender,
                str(dob) if dob else "",
                address.strip() if address else "",  # Address
                education.strip() if education else "",  # Education
                email.strip() if email else "",  # Email
                home_phone.strip() if home_phone else "",  # Home Phone
                mobile_phone.strip() if mobile_phone else "",  # Mobile Phone
                timestamp
            ]
            worksheet.append_row(new_row)
            st.success(f"සාර්ථකයි! {name} එකතු වුණා ✓ (පවුල් අංකය: {household_id})")
            st.balloons()
        except Exception as e:
            st.error(f"දත්ත එකතු කිරීමේදී ගැටලුවක්: {str(e)}")
            st.info("Service account එක sheet එකට Editor permission තියෙනවද බලන්න.")

# ------------------ Search Feature ------------------
st.subheader("දත්ත සෙවීම")
search_query = st.text_input("පවුල් අංකය හෝ NIC අංකය ඇතුලත් කරන්න")
if st.button("සෙවීම"):
    try:
        data = worksheet.get_all_values()
        if len(data) > 0:
            headers = data[0]
            df = pd.DataFrame(data[1:], columns=headers)
            results = df[(df['පවුල් අංකය'].str.contains(search_query, na=False, case=False)) |
                         (df['NIC අංකය'].str.contains(search_query, na=False, case=False))]
            if not results.empty:
                st.table(results)
            else:
                st.info("කිසිම results නැහැ.")
        else:
            st.info("තවම කිසිම දත්ත නැහැ.")
    except Exception as e:
        st.error(f"සෙවීමේදී ගැටලුවක්: {e}")

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
