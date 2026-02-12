# GN-System - ග්‍රාම නිලධාරි දත්ත ඇතුලත් කිරීමේ පද්ධතිය

හවුපේ උතුර 175/B ග්‍රාම නිලධාරි කොට්ඨාශය සඳහා විශේෂයෙන් නිර්මාණය කරන ලද **web-based data entry application** එකක්.

මෙම app එක භාවිතා කරලා ඔබට පහසුවෙන් පවුල් තොරතුරු ඇතුලත් කරන්න, සංස්කරණය කරන්න, සෙවීම් කරන්න සහ dashboard එකකින් සාරාංශ බලන්න පුළුවන්.

## Features

- **පවුල් සාමාජිකයින් ඇතුලත් කිරීම** (නව record add කිරීම)
- **දත්ත සංස්කරණය** (NIC අංකයෙන් record එක load කරලා update කිරීම)
- **සෙවීම්** (පවුල් අංකය, NIC හෝ නමෙන් search කිරීම + multiple select කරලා view)
- **Dashboard**  
  - මුළු පවුල් ගණන  
  - මුළු සාමාජිකයින් ගණන  
  - වයස් කාණ්ඩ අනුව සාරාංශය (0-18, 19-35, 36-60, 60+)
- **සිංහල භාෂා සහය** (UI සම්පූර්ණයෙන්ම සිංහලෙන්)
- **Google Sheets integration** (දත්ත real-time එකතු වෙනවා + update වෙනවා)
- **ආරක්ෂිත login** (password එකක් භාවිතයෙන්)

## Tech Stack

- **Frontend**: Streamlit (Python-based web app framework)
- **Backend**: gspread + Google Sheets API
- **Authentication**: Google Service Account (secrets.toml)
- **Data Handling**: pandas
- **Deployment**: Streamlit Cloud

## Installation & Setup (Local Development)

1. Clone the repository
   ```bash
   git clone https://github.com/dilipmadushanka1985/GN-System.git
   cd GN-System

   python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

[GOOGLE_CREDENTIALS]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
# ... full JSON content here

streamlit run app.py

Deployment to Streamlit Cloud

GitHub repo එක connect කරන්න Streamlit Cloud එකට
secrets.toml එකේ credentials ඔයාගේ Streamlit Cloud app එකේ Secrets section එකට දාන්න
Main branch එක deploy කරන්න

Sheet Setup

Google Sheet URL: https://docs.google.com/spreadsheets/d/1itCCxoIfEWWroY5c3ukjLho9B1V0QM6WwR-6Z2rMORE/edit
Service account email එකට Editor permission දෙන්න:
gn-editor@gn-system-486911.iam.gserviceaccount.com
පළමු row එකේ headings මෙහෙම තියෙන්න ඕන (A1 සිට Q1 දක්වා):textපවුල් අංකය | NIC අංකය | නම | භූමිකාව | රැකියාව | වාහන අංකය 1 | වාහන අංකය 2 | ලිංගභාවය | උපන් දිනය | ලිපිනය | අධ්‍යාපන සුදුසුකම් | විද්‍යුත් ලිපිනය | දුරකථන අංකය (නිවස) | දුරකථන අංකය (ජංගම) | ජාතිය | මාසික ආදායම | ඇතුලත් කළ වෙලාව

Future Improvements (ඔයාට ඕන නම් එකතු කරන්න පුළුවන්)

User authentication improve කිරීම (multiple users)
PDF export feature
Charts (matplotlib/seaborn) dashboard එකට එකතු කිරීම
Mobile responsive design improve කිරීම

Contact
Developed by: Dilip
GitHub: https://github.com/dilipmadushanka1985/GN-System
Email: [agdmadushanka@gmail.com]
Star දාලා support කරන්නකෝ! ⭐
