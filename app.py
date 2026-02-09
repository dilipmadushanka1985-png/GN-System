import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Page Configuration
st.set_page_config(page_title="GN Data System", layout="wide")
st.title("🏡 ග්‍රාම නිලධාරී - පවුල් දත්ත පද්ධතිය")

# 1. Google Sheets Connection
# ---------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

# දත්ත කියවීම (Read Data)
try:
    # ttl=5 මගින් දත්ත ඉක්මනින් refresh වේ
    existing_data = conn.read(ttl=5)
    
    # හිස් පේළි අයින් කිරීම සහ දත්ත නැත්නම් DataFrame එකක් සෑදීම
    if existing_data.empty:
        existing_data = pd.DataFrame(columns=["Household_ID", "NIC", "Name", "Role", "Job", "Vehicle"])
except Exception as e:
    st.error(f"Google Sheet සම්බන්ධ දෝෂයක්: {e}")
    existing_data = pd.DataFrame(columns=["Household_ID", "NIC", "Name", "Role", "Job", "Vehicle"])

# 2. Data Entry Form
# ---------------------------------------------------------
with st.expander("➕ අලුත් සාමාජිකයෙක් හෝ පවුලක් ඇතුලත් කරන්න", expanded=False):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            h_id = st.text_input("🏠 ගෘහ මූලික අංකය (Household ID)")
            nic = st.text_input("🆔 NIC අංකය")
            name = st.text_input("👤 සම්පූර්ණ නම")
        
        with col2:
            role = st.selectbox("🔗 ගෘහ මූලිකයාට ඇති නෑකම", ["ගෘහ මූලිකයා", "බිරිඳ/සැමියා", "දරුවා", "දෙමාපියන්", "වෙනත්"])
            job = st.text_input("💼 රැකියාව")
            vehicle = st.text_input("🚗 වාහන විස්තර (නැත්නම් 'නැත')")

        submitted = st.form_submit_button("දත්ත සුරකින්න (Save to Sheet)")

        if submitted:
            if h_id and nic and name:
                # අලුත් පේළිය හදාගැනීම
                new_data = {
                    "Household_ID": h_id, 
                    "NIC": nic, 
                    "Name": name, 
                    "Role": role, 
                    "Job": job, 
                    "Vehicle": vehicle
                }
                new_row = pd.DataFrame([new_data])
                
                # පරණ ඩේටා වලට අලුත් එක එකතු කිරීම
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                
                # Google Sheet එක Update කිරීම
                conn.update(data=updated_df)
                
                st.success(f"✅ {name} ගේ විස්තර සාර්ථකව Google Sheet එකට ඇතුලත් කරන ලදී!")
                st.rerun() # Refresh to show new data (Updated from experimental_rerun)
            else:
                st.error("⚠️ කරුණාකර ගෘහ අංකය, NIC සහ නම අනිවාර්යයෙන් ඇතුලත් කරන්න.")

# 3. Search & View Data
# ---------------------------------------------------------
st.divider()
st.subheader("🔍 පවුලේ විස්තර සොයන්න (From Google Sheet)")

col_search, col_display = st.columns([1, 2])

with col_search:
    search_hid = st.text_input("සොයන්න අවශ්‍ය ගෘහ අංකය:")
    search_nic = st.text_input("හෝ NIC අංකය:")

with col_display:
    results = pd.DataFrame()
    
    if search_hid:
        # Data type ප්‍රශ්න මගහරවා ගැනීමට astype(str) භාවිතා කරයි
        results = existing_data[existing_data['Household_ID'].astype(str) == search_hid]
    elif search_nic:
        person = existing_data[existing_data['NIC'].astype(str) == search_nic]
        if not person.empty:
            found_hid = person.iloc[0]['Household_ID']
            results = existing_data[existing_data['Household_ID'] == found_hid]
            st.info(f"මෙම පුද්ගලයා අයත් වන ගෘහ අංකය: {found_hid}")

    if not results.empty:
        st.success(f"සාමාජිකයින් ගණන: {len(results)}")
        st.dataframe(results, use_container_width=True)
    elif (search_hid or search_nic):
        st.warning("❌ දත්ත හමු නොවිණි.")
