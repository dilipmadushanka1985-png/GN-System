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
