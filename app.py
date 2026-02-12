import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import pandas as pd

# Google Sheets connection
@st.cache_resource
def get_sheet():
    creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    SHEET_ID = "1itCCxoIfEWWroY5c3ukjLho9B1V0QM6WwR-6Z2rMORE"
    return client.open_by_key(SHEET_ID).sheet1

worksheet = get_sheet()

# Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("GN Data Entry - Login")
    password = st.text_input("Password ඇතුලත් කරන්න", type="password")
    if st.button("Login"):
        if password == "gnnegombo2025":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("වැරදි password!")
    st.stop()

# Title
st.markdown("<h2 style='color: navy;'>හවුපේ උතුර 175/B</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='color: navy;'>ග්‍රාම නිලධාරි දත්ත ඇතුලත් කිරීම</h1>", unsafe_allow_html=True)

# Dashboard
@st.cache_data(ttl=60)
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
    # මුළු පවුල් ගණන = unique පවුල් අංකය count
    total_families = df['පවුල් අංකය'].dropna().nunique()

    # මුළු සාමාජිකයින් ගණන = සම්පූර්ණ නම තියෙන row ගණන (empty name skip කරලා)
    total_members = df['නම'].dropna().count()   # හෝ len(df[df['නම'].notna()])

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

# Data Entry Form
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
            st.success(f"සාර්ථකයි! {name} එකතු වුණා ✓")
            st.balloons()
        except Exception as e:
            st.error(f"දත්ත එකතු කිරීමේදී ගැටලුවක්: {str(e)}")

# Search Feature
st.subheader("දත්ත සෙවීම")
search_query = st.text_input("පවුල් අංකය, NIC හෝ නම ඇතුලත් කරන්න", placeholder="ඔයාගේ සෙවුම් වචනය ඇතුලත් කරන්න")
if st.button("සෙවීම"):
    try:
        if not df.empty:
            results = df[(df['පවුල් අංකය'].str.contains(search_query, na=False, case=False)) |
                         (df['NIC අංකය'].str.contains(search_query, na=False, case=False)) |
                         (df['නම'].str.contains(search_query, na=False, case=False))]
            if not results.empty:
                st.write("සෙවුම් ප්‍රතිඵල:")
                selected_rows = []
                for i, row in results.iterrows():
                    if st.checkbox(f"{row['නම']} (NIC: {row['NIC අංකය']}, පවුල් අංකය: {row['පවුල් අංකය']})", key=f"select_{i}"):
                        selected_rows.append(row)
                if selected_rows:
                    selected_df = pd.DataFrame(selected_rows)
                    st.table(selected_df)
            else:
                st.info("කිසිම results නැහැ.")
    except Exception as e:
        st.error(f"සෙවීමේදී ගැටලුවක්: {e}")

# Edit Feature (දැන් full එකතු කළා)
st.subheader("දත්ත සංස්කරණය")
edit_nic = st.text_input("සංස්කරණයට NIC අංකය ඇතුලත් කරන්න")
if st.button("Load කරන්න"):
    if not df.empty:
        match = df[df['NIC අංකය'] == edit_nic]
        if not match.empty:
            row_data = match.iloc[0]
            row_index = match.index[0] + 2
            
            st.write("සංස්කරණයට දත්ත load වුණා:")
            
            with st.form("edit_form", clear_on_submit=True):
                household_id_edit = st.text_input("පවුල් අංකය", value=row_data.get('පවුල් අංකය', ''))
                nic_edit = st.text_input("NIC අංකය", value=row_data.get('NIC අංකය', ''), disabled=True)
                name_edit = st.text_input("නම", value=row_data.get('නම', ''))
                role_edit = st.selectbox("භූමිකාව", options=["පවුලේ ප්‍රධානි", "බිරිඳ", "ස්වාමිපුරුෂයා", "දරුවා", "මව", "පියා", "සහෝදරයා", "සහෝදරිය", "වෙනත්"], index=["පවුලේ ප්‍රධානි", "බිරිඳ", "ස්වාමිපුරුෂයා", "දරුවා", "මව", "පියා", "සහෝදරයා", "සහෝදරිය", "වෙනත්"].index(row_data.get('භූමිකාව', 'වෙනත්')) if row_data.get('භූමිකාව') in ["පවුලේ ප්‍රධානි", "බිරිඳ", "ස්වාමිපුරුෂයා", "දරුවා", "මව", "පියා", "සහෝදරයා", "සහෝදරිය", "වෙනත්"] else 8)
                job_edit = st.text_input("රැකියාව", value=row_data.get('රැකියාව', ''))
                vehicle1_edit = st.text_input("වාහන අංකය 1", value=row_data.get('වාහන අංකය 1', ''))
                vehicle2_edit = st.text_input("වාහන අංකය 2", value=row_data.get('වාහන අංකය 2', ''))
                gender_edit = st.radio("ලිංගභාවය", options=["පිරිමි", "ගැහැණු", "වෙනත්"], horizontal=True, index=["පිරිමි", "ගැහැණු", "වෙනත්"].index(row_data.get('ලිංගභාවය', 'පිරිමි')) if row_data.get('ලිංගභාවය') in ["පිරිමි", "ගැහැණු", "වෙනත්"] else 0)
                
                # DOB safe handling
                dob_value = None
                if row_data.get('උපන් දිනය') and pd.notna(row_data['උපන් දිනය']):
                    try:
                        dob_value = date.fromisoformat(row_data['උපන් දිනය'])
                    except (ValueError, TypeError):
                        dob_value = None
                
                dob_edit = st.date_input("උපන් දිනය", value=dob_value, min_value=date(1920, 1, 1), max_value=date(2050, 12, 31))
                
                address_edit = st.text_input("ලිපිනය", value=row_data.get('ලිපිනය', ''))
                education_edit = st.text_input("අධ්‍යාපන සුදුසුකම්", value=row_data.get('අධ්‍යාපන සුදුසුකම්', ''))
                email_edit = st.text_input("විද්‍යුත් ලිපිනය", value=row_data.get('විද්‍යුත් ලිපිනය', ''))
                home_phone_edit = st.text_input("දුරකථන අංකය (නිවස)", value=row_data.get('දුරකථන අංකය (නිවස)', ''))
                mobile_phone_edit = st.text_input("දුරකථන අංකය (ජංගම)", value=row_data.get('දුරකථන අංකය (ජංගම)', ''))
                ethnicity_edit = st.selectbox("ජාතිය", options=["සිංහල", "දෙමළ", "මුස්ලිම්", "බර්ගර්", "වෙනත්"], index=["සිංහල", "දෙමළ", "මුස්ලිම්", "බර්ගර්", "වෙනත්"].index(row_data.get('ජාතිය', 'සිංහල')) if row_data.get('ජාතිය') in ["සිංහල", "දෙමළ", "මුස්ලිම්", "බර්ගර්", "වෙනත්"] else 0)
                monthly_income_edit = st.number_input("මාසික ආදායම", value=float(row_data.get('මාසික ආදායම', 0)) if pd.notnull(row_data.get('මාසික ආදායම', 0)) else 0.0, min_value=0.0, step=1000.0)

                if st.form_submit_button("Update කරන්න"):
                    updated_row = [
                        household_id_edit,
                        nic_edit,
                        name_edit,
                        role_edit,
                        job_edit,
                        vehicle1_edit,
                        vehicle2_edit,
                        gender_edit,
                        str(dob_edit) if dob_edit else "",
                        address_edit,
                        education_edit,
                        email_edit,
                        home_phone_edit,
                        mobile_phone_edit,
                        ethnicity_edit,
                        str(monthly_income_edit),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                    worksheet.update(f'A{row_index}:Q{row_index}', [updated_row])
                    st.success("සංස්කරණය සාර්ථකයි!")
                    st.rerun()
        else:
            st.error("NIC අංකය නැහැ.")

