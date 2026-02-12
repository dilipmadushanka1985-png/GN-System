import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import pandas as pd

# ------------------ Google Sheets Credentials (common for all users) ------------------
@st.cache_resource
def get_creds():
    creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    return Credentials.from_service_account_info(creds_dict, scopes=scopes)

# ------------------ Multi-User: User to Sheet Mapping ------------------
# මෙතන එක එක user එකට එක එක sheet ID එක දාන්න
USER_SHEETS = {
    "dilip": "1itCCxoIfEWWroY5c3ukjLho9B1V0QM6WwR-6Z2rMORE",  # ඔයාගේ sheet ID
    "user1": "1abcDEF1234567890",  # අලුත් user එකක sheet ID
    "user2": "1xyzABC9876543210",  # තවත් user එකක sheet ID
    # ඔයාට ඕන users එකතු කරන්න මෙතනට
}

# ------------------ Login ------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if not st.session_state.logged_in:
    st.title("GN Data Entry - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # මෙතන simple username-password check එකක් (production එකට change කරන්න)
        if username in USER_SHEETS and password == "gnnegombo2025":  # ඔයාට ඕන password එක දාන්න
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Login සාර්ථකයි! Welcome {username}")
            st.rerun()
        else:
            st.error("වැරදි username හෝ password!")
    st.stop()

# Logged in user එකට එක sheet එකක් assign කරනවා
SHEET_ID = USER_SHEETS.get(st.session_state.username)
if not SHEET_ID:
    st.error("User එකට sheet එකක් assign කරලා නැහැ. Admin එක්ක කතා කරන්න.")
    st.stop()

# User එකට එක sheet එකක් open කරනවා
@st.cache_resource
def get_user_sheet():
    creds = get_creds()
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

worksheet = get_user_sheet()

# ------------------ Title ------------------
st.markdown(f"<h2 style='color: navy;'>හවුපේ උතුර 175/B - {st.session_state.username}</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='color: navy;'>ග්‍රාම නිලධාරි දත්ත ඇතුලත් කිරීම</h1>", unsafe_allow_html=True)

# ------------------ Dashboard ------------------
@st.cache_data(ttl=5)
def load_data():
    data = worksheet.get_all_values()
    if len(data) > 0:
        df = pd.DataFrame(data[1:], columns=data[0])
        df['උපන් දිනය'] = pd.to_datetime(df['උපන් දිනය'], errors='coerce')
        df['Age'] = (datetime.now() - df['උපන් දිනය']).dt.days / 365.25
        if 'මාසික ආදායම' in df.columns:
            df['මාසික ආදායම'] = pd.to_numeric(df['මාසික ආදායම'], errors='coerce')
        return df
    return pd.DataFrame()

df = load_data()

if not df.empty:
    total_families = df['පවුල් අංකය'].dropna().nunique()
    total_members = df['නම'].dropna().count()
    age_groups = {
        '0-18': len(df[(df['Age'].notnull()) & (df['Age'] >= 0) & (df['Age'] <= 18)]),
        '19-35': len(df[(df['Age'].notnull()) & (df['Age'] > 18) & (df['Age'] <= 35)]),
        '36-60': len(df[(df['Age'].notnull()) & (df['Age'] > 35) & (df['Age'] <= 60)]),
        '60+': len(df[(df['Age'].notnull()) & (df['Age'] > 60)])
    }
    st.subheader("Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("මුළු පවුල් ගණන", total_families)
        st.metric("මුළු සාමාජිකයින් ගණන", total_members)
    with col2:
        st.write("වයස් කාණ්ඩ අනුව සාරාංශ:")
        for group, count in age_groups.items():
            st.write(f"{group}: {count}")

# ------------------ Data Entry Form ------------------
st.markdown("<h3 style='color: darkgreen;'>නව පවුල් සාමාජිකයෙකු එකතු කරන්න</h3>", unsafe_allow_html=True)

with st.form("member_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        household_id = st.text_input("පවුල් අංකය", placeholder="GN-001-2025")
        nic = st.text_input("NIC අංකය")
        name = st.text_input("සම්පූර්ණ නම")
        address = st.text_input("ලිපිනය")
    with col2:
        role = st.selectbox("භූමිකාව", ["පවුලේ ප්‍රධානි", "බිරිඳ", "ස්වාමිපුරුෂයා", "දරුවා", "මව", "පියා", "සහෝදරයා", "සහෝදරිය", "වෙනත්"])
        job = st.text_input("රැකියාව / වෘත්තිය")
        education = st.text_input("අධ්‍යාපන සුදුසුකම්")
        email = st.text_input("විද්‍යුත් ලිපිනය")
    col3, col4 = st.columns(2)
    with col3:
        vehicle1 = st.text_input("වාහන අංකය 1")
        vehicle2 = st.text_input("වාහන අංකය 2")
        home_phone = st.text_input("දුරකථන අංකය (නිවස)")
    with col4:
        mobile_phone = st.text_input("දුරකථන අංකය (ජංගම)")
        gender = st.radio("ලිංගභාවය", ["පිරිමි", "ගැහැණු", "වෙනත්"], horizontal=True)
        ethnicity = st.selectbox("ජාතිය", ["සිංහල", "දෙමළ", "මුස්ලිම්", "බර්ගර්", "වෙනත්"])
        monthly_income = st.number_input("මාසික ආදායම (Rs.)", min_value=0.0, step=1000.0)
    dob = st.date_input("උපන් දිනය", value=None, min_value=date(1920, 1, 1), max_value=date(2050, 12, 31))

    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: lightgreen;
        color: red;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    submitted = st.form_submit_button("එකතු කරන්න")

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
                vehicle1.strip() if vehicle1 else "",
                vehicle2.strip() if vehicle2 else "",
                gender,
                str(dob) if dob else "",
                address.strip() if address else "",
                education.strip() if education else "",
                email.strip() if email else "",
                home_phone.strip() if home_phone else "",
                mobile_phone.strip() if mobile_phone else "",
                ethnicity,
                str(monthly_income),
                timestamp
            ]
            worksheet.append_row(new_row)
            st.success(f"සාර්ථකයි! {name} එකතු වුණා ✓ (Sheet: {SHEET_ID})")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"දත්ත එකතු කිරීමේදී ගැටලුවක්: {str(e)}")

# ------------------ Search Feature ------------------
st.subheader("දත්ත සෙවීම")
search_query = st.text_input("පවුල් අංකය, NIC හෝ නම ඇතුලත් කරන්න")
if st.button("සෙවීම"):
    try:
        if not df.empty:
            results = df[(df['පවුල් අංකය'].str.contains(search_query, na=False, case=False)) |
                         (df['NIC අංකය'].str.contains(search_query, na=False, case=False)) |
                         (df['නම'].str.contains(search_query, na=False, case=False))]
            if not results.empty:
                st.write("සෙවුම් ප්‍රතිඵල:")
                for i, row in results.iterrows():
                    if st.checkbox(f"{row['නම']} (NIC: {row['NIC අංකය']})", key=f"select_{i}"):
                        st.table(row)
            else:
                st.info("කිසිම results නැහැ.")
    except Exception as e:
        st.error(f"සෙවීමේදී ගැටලුවක්: {e}")
