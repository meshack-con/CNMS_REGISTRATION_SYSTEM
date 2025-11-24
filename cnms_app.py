# cnms_app.py
import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# -------------------------------------
# SUPABASE CONFIGURATION
# -------------------------------------
SUPABASE_URL = "https://pnpjfaalcvetdjbcuadj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBucGpmYWFsY3ZldGRqYmN1YWRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyMjM5NTYsImV4cCI6MjA3ODc5OTk1Nn0.5AmOhm_ATsZTX1Vkg5_XHKEytVVpBsGCfATM4dqWlOo"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------
# DEGREE PROGRAMMES (NEW LIST)
# -------------------------------------
DEGREE_PROGRAMMES = [
    "EDU", "ACTUARIAL", "BIOLOGY", "CHEM", "AAQ", "STAT",
    "MSCANALLY", "MATH", "PHY", "BB", "DFS", "MATH$STAT",
    "MSCBDC", "DFMNC", "APHY", "MSCPHY", "MSCSTAT", "MSCMATH"
]

# -------------------------------------
# DB FUNCTIONS (cnms_users / cnms_students)
# -------------------------------------
def login(username, password):
    try:
        result = (
            supabase.table("cnms_users")
            .select("*")
            .eq("username", username)
            .eq("password_hash", password)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print("Login error:", e)
        return None

def insert_student(data):
    try:
        return supabase.table("cnms_students").insert(data).execute()
    except Exception as e:
        print("Insert student error:", e)
        raise

def get_students():
    try:
        res = supabase.table("cnms_students").select("*").order("id", desc=True).execute()
        rows = res.data or []
        return pd.DataFrame(rows)
    except Exception as e:
        print("Get students error:", e)
        return pd.DataFrame([])

def update_student(student_id, updates):
    try:
        return supabase.table("cnms_students").update(updates).eq("id", student_id).execute()
    except Exception as e:
        print("Update error:", e)
        return None

def delete_student(student_id):
    try:
        return supabase.table("cnms_students").delete().eq("id", student_id).execute()
    except Exception as e:
        print("Delete error:", e)
        return None

# -------------------------------------
# STREAMLIT PAGE CONFIG
# -------------------------------------
st.set_page_config(page_title="CNMS Registration System", layout="wide")

st.markdown("""
    <style>
        body { background-color: black !important; }
        .stApp { background-color: black !important; }
        h1,h2,h3,h4 { color: #ffea00 !important; }
        label, .stTextInput label, .stSelectbox label {
            color: white !important;
            font-weight: 600;
        }
        /* yellow counts styling */
        .cnms-count { color: #ffea00; font-weight:700; }
        /* inputs styling */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div {
            background-color: white !important;
            color: black !important;
            border: 2px solid #ffea00 !important;
            border-radius: 6px;
        }
        div.stButton>button {
            background-color: #ffea00 !important;
            color: black !important;
            font-weight: bold;
            border-radius: 8px;
        }
        .cnms-row-sep { border-bottom:1px solid #ffdf5a; padding:6px 0; color: white; }
        .cnms-header-sep { border-bottom:2px solid #ffdf5a; padding-bottom:6px; font-weight:700; color:#ffea00 }
        .cnms-card { background:#111; padding:12px; border:2px solid #ffea00; border-radius:8px; margin-top:8px; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------
# LOGIN SCREEN
# -------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("<h1 style='color:#ffea00'>CNMS Login</h1>", unsafe_allow_html=True)
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login", key="login_btn"):
        user = login(username, password)
        if user:
            st.session_state.user = user
            st.session_state.students_cache = None
            st.success("Login success!")
            st.rerun()
        else:
            st.error("Wrong username or password")
    st.stop()

# -------------------------------------
# AFTER LOGIN - Main UI
# -------------------------------------
st.markdown("<h1 style='color:#ffea00;text-align:center;'>CNMS Student Registration</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["➕ Register Student", "📋 Student Records"])

# -------------------------------------
# TAB 1: REGISTER STUDENT
# -------------------------------------
with tab1:
    st.markdown("<h2 style='color:#ffea00;'>Student Registration Form</h2>", unsafe_allow_html=True)

    # use keys to avoid duplicate widget ids
    name = st.text_input("Full Name", key="reg_full_name")
    course = st.selectbox("Degree Programme", [""] + DEGREE_PROGRAMMES, key="reg_course")
    years = st.number_input("Years of Study", 1, 6, key="reg_years")
    block = st.text_input("Block", key="reg_block")
    gender = st.selectbox("Gender", ["", "Male", "Female"], key="reg_gender")
    room = st.text_input("Room Number", key="reg_room")
    phone = st.text_input("Phone Number", key="reg_phone")

    electronic_card = st.text_input("Electronic Card Number (Optional)", key="reg_electronic")
    gamba_card = st.text_input("Gamba Card Number (Optional)", key="reg_gamba")

    if st.button("Register Student", key="register_student_btn"):
        if not name.strip() or not course or not gender:
            st.error("Please fill required fields: Full Name, Degree Programme, Gender.")
        else:
            data = {
                "full_name": name.strip(),
                "course": course,
                "years_of_study": int(years),
                "block": block.strip() if block else None,
                "gender": gender,
                "room": room.strip() if room else None,
                "phone_number": phone.strip() if phone else None,
                "electronic_card": electronic_card.strip() if electronic_card else None,
                "gamba_card": gamba_card.strip() if gamba_card else None,
                "created_at": datetime.utcnow().isoformat()
            }
            try:
                insert_student(data)
                st.success("Student registered successfully!")
                st.session_state.students_cache = None
                st.rerun()
            except Exception as e:
                st.error("Failed to register student. Check server logs.")
                print("Insert error:", e)

# -------------------------------------
# TAB 2: STUDENT RECORDS
# -------------------------------------
with tab2:
    st.markdown("<h2 style='color:#ffea00;'>Registered Students</h2>", unsafe_allow_html=True)

    # fetch students with caching
    if "students_cache" not in st.session_state or st.session_state.students_cache is None:
        df = get_students()
        # ensure df is DataFrame
        if df is None:
            df = pd.DataFrame([])
        st.session_state.students_cache = df
    else:
        df = st.session_state.students_cache

    # ensure df is dataframe
    if df is None:
        df = pd.DataFrame([])

    # --------------------- COUNTS ---------------------
    total_count = len(df)
    male_count = 0
    female_count = 0
    years_counts = {y: 0 for y in range(1, 7)}  # Year1..Year6

    if not df.empty:
        if "gender" in df.columns:
            male_count = int((df["gender"].astype(str).str.lower() == "male").sum())
            female_count = int((df["gender"].astype(str).str.lower() == "female").sum())
        if "years_of_study" in df.columns:
            for y in years_counts.keys():
                # handle non-numeric or missing safely
                years_counts[y] = int((df["years_of_study"] == y).sum())

    # show counts with yellow styling
    st.markdown(
        f"""
        <div style="display:flex;gap:24px;align-items:center">
            <div class="cnms-count">Total Students: {total_count}</div>
            <div class="cnms-count">Male: {male_count}</div>
            <div class="cnms-count">Female: {female_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # show year breakdown lines (yellow)
    year_breakdown_html = "<div style='margin-top:6px'>"
    for y in range(1, 7):
        year_breakdown_html += f"<span class='cnms-count' style='margin-right:12px'>YEAR {y}: {years_counts[y]}</span>"
    year_breakdown_html += "</div>"
    st.markdown(year_breakdown_html, unsafe_allow_html=True)

    # --------------------- SEARCH ---------------------
    search = st.text_input("Search student by name or course", key="searchbar")
    filtered_df = df.copy()
    if search and not df.empty:
        q = search.strip().lower()
        filtered_df = df[df.apply(lambda row: q in str(row.get("full_name","")).lower() 
                                            or q in str(row.get("course","")).lower()
                                            or q in str(row.get("phone_number","")).lower(), axis=1)]

    # --------------------- PAGINATION ---------------------
    rows_per_page = 10
    total_pages = max(1, (len(filtered_df) + rows_per_page - 1) // rows_per_page)
    page = st.number_input("Page", 1, total_pages, value=1, key="cnms_page") - 1
    start = page * rows_per_page
    end = start + rows_per_page
    df_show = filtered_df.iloc[start:end] if not filtered_df.empty else filtered_df

    # --------------------- DOWNLOAD CSV ---------------------
    csv_df = df if not df.empty else pd.DataFrame([])
    csv = csv_df.to_csv(index=False).encode("utf-8")
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    st.download_button("Download CSV", csv, f"cnms_students_{ts}.csv", "text/csv", key="cnms_download")

    # --------------------- TABLE DISPLAY ---------------------
    if df_show is None or df_show.empty:
        st.info("No students to show on this page.")
    else:
        # header row
        header_cols = st.columns([3,2,1,1,2,2,1,1,2,2,1])
        headers = ["Full Name","Course","Years","Block","Electronic Card","Gamba Card","Gender","Room","Phone","Registered At","Actions"]
        for col_obj, h in zip(header_cols, headers):
            col_obj.markdown(f"<div class='cnms-header-sep'>{h}</div>", unsafe_allow_html=True)

        # rows
        for _, row in df_show.reset_index(drop=True).iterrows():
            student_id = row.get("id", "")
            full_name = row.get("full_name", "")
            course = row.get("course", "")
            years_val = row.get("years_of_study", "")
            block = row.get("block", "")
            elec = row.get("electronic_card", "") if "electronic_card" in row.index else ""
            gamba = row.get("gamba_card", "") if "gamba_card" in row.index else ""
            gender = row.get("gender", "")
            room = row.get("room", "")
            phone = row.get("phone_number", "")
            created_at = row.get("created_at", "")

            row_cols = st.columns([3,2,1,1,2,2,1,1,2,2,1])

            row_cols[0].markdown(f"<div class='cnms-row-sep'>{full_name}</div>", unsafe_allow_html=True)
            row_cols[1].markdown(f"<div class='cnms-row-sep'>{course}</div>", unsafe_allow_html=True)
            row_cols[2].markdown(f"<div class='cnms-row-sep'>{years_val}</div>", unsafe_allow_html=True)
            row_cols[3].markdown(f"<div class='cnms-row-sep'>{block}</div>", unsafe_allow_html=True)
            row_cols[4].markdown(f"<div class='cnms-row-sep'>{elec}</div>", unsafe_allow_html=True)
            row_cols[5].markdown(f"<div class='cnms-row-sep'>{gamba}</div>", unsafe_allow_html=True)
            row_cols[6].markdown(f"<div class='cnms-row-sep'>{gender}</div>", unsafe_allow_html=True)
            row_cols[7].markdown(f"<div class='cnms-row-sep'>{room}</div>", unsafe_allow_html=True)
            row_cols[8].markdown(f"<div class='cnms-row-sep'>{phone}</div>", unsafe_allow_html=True)
            row_cols[9].markdown(f"<div class='cnms-row-sep'>{created_at}</div>", unsafe_allow_html=True)

            # actions
            with row_cols[10]:
                if st.button("✏ Edit", key=f"edit_{student_id}"):
                    st.session_state.edit_id = student_id
                if st.button("🗑 Delete", key=f"del_{student_id}"):
                    delete_student(student_id)
                    st.success("Student deleted.")
                    st.session_state.students_cache = None
                    st.rerun()

            # inline edit panel for this student
            if "edit_id" in st.session_state and st.session_state.edit_id == student_id:
                st.markdown("<div class='cnms-card'>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:#ffea00'>Edit: {full_name}</h4>", unsafe_allow_html=True)

                new_name = st.text_input("Full Name", value=full_name, key=f"name_{student_id}")
                new_course = st.selectbox("Degree Programme", [""] + DEGREE_PROGRAMMES,
                                          index=(([""]+DEGREE_PROGRAMMES).index(course) if course in DEGREE_PROGRAMMES else 0),
                                          key=f"course_{student_id}")
                # unique number_input key
                new_years = st.number_input("Years", min_value=1, max_value=6,
                                            value=int(years_val) if (str(years_val).isdigit()) else 3,
                                            key=f"years_{student_id}")
                new_block = st.text_input("Block", value=block, key=f"block_{student_id}")
                new_elec = st.text_input("Electronic Card Number (optional)", value=elec, key=f"elec_{student_id}")
                new_gamba = st.text_input("Gamba Card Number (optional)", value=gamba, key=f"gamba_{student_id}")
                new_gender = st.selectbox("Gender", ["", "Male","Female"],
                                          index=(["","Male","Female"].index(gender) if gender in ["Male","Female"] else 0),
                                          key=f"gender_{student_id}")
                new_room = st.text_input("Room Number", value=room, key=f"room_{student_id}")
                new_phone = st.text_input("Phone Number", value=phone, key=f"phone_{student_id}")

                s1, s2 = st.columns(2)
                if s1.button("Save Changes", key=f"save_{student_id}"):
                    updates = {
                        "full_name": new_name.strip(),
                        "course": new_course,
                        "years_of_study": int(new_years),
                        "block": new_block.strip() if new_block else None,
                        "electronic_card": new_elec.strip() if new_elec else None,
                        "gamba_card": new_gamba.strip() if new_gamba else None,
                        "gender": new_gender,
                        "room": new_room.strip() if new_room else None,
                        "phone_number": new_phone.strip() if new_phone else None
                    }
                    update_student(student_id, updates)
                    st.success("Updated successfully.")
                    st.session_state.edit_id = None
                    st.session_state.students_cache = None
                    st.rerun()
                if s2.button("Cancel", key=f"cancel_{student_id}"):
                    st.session_state.edit_id = None
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------
# Logout button
# -------------------------------------
if st.button("Logout", key="cnms_logout"):
    st.session_state.user = None
    st.session_state.students_cache = None
    st.session_state.edit_id = None
    st.rerun()
