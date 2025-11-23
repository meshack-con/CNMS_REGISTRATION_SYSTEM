import streamlit as st
from supabase import create_client
import pandas as pd

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
# LOGIN FUNCTION
# -------------------------------------
def login(username, password):
    try:
        result = (
            supabase.table("cnms_users")
            .select("*")
            .eq("username", username)
            .eq("password_hash", password)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None
    except:
        return None

# -------------------------------------
# INSERT STUDENT
# -------------------------------------
def insert_student(data):
    supabase.table("cnms_students").insert(data).execute()

# -------------------------------------
# GET STUDENTS
# -------------------------------------
def get_students():
    result = supabase.table("cnms_students").select("*").order("id", desc=True).execute()
    return pd.DataFrame(result.data)

# -------------------------------------
# UPDATE STUDENT
# -------------------------------------
def update_student(student_id, updates):
    supabase.table("cnms_students").update(updates).eq("id", student_id).execute()

# -------------------------------------
# DELETE STUDENT
# -------------------------------------
def delete_student(student_id):
    supabase.table("cnms_students").delete().eq("id", student_id).execute()

# -------------------------------------
# STREAMLIT PAGE CONFIG
# -------------------------------------
st.set_page_config(page_title="CNMS Registration System", layout="wide")

st.markdown("""
    <style>
        body { background-color: black !important; }
        .stApp { background-color: black !important; }
        label, .stTextInput label, .stSelectbox label {
            color: white !important;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------
# LOGIN SCREEN
# -------------------------------------
if "user" not in st.session_state:
    st.markdown("<h1 style='color:#ffea00'>CNMS Login</h1>", unsafe_allow_html=True)
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        user = login(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Wrong username or password")
    st.stop()

# -------------------------------------
# AFTER LOGIN
# -------------------------------------
st.markdown("<h1 style='color:#ffea00;text-align:center;'>CNMS Student Registration</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["➕ Register Student", "📋 Student Records"])

# -------------------------------------
# TAB 1: REGISTRATION
# -------------------------------------
with tab1:
    st.markdown("<h2 style='color:#ffea00;'>Student Registration Form</h2>", unsafe_allow_html=True)

    name = st.text_input("Full Name")
    course = st.selectbox("Degree Programme", DEGREE_PROGRAMMES)
    years = st.number_input("Years of Study", 1, 6, key="reg_years")
    block = st.text_input("Block")
    gender = st.selectbox("Gender", ["Male", "Female"])
    room = st.text_input("Room Number")
    phone = st.text_input("Phone Number")

    electronic_card = st.text_input("Electronic Card Number (Optional)")
    gamba_card = st.text_input("Gamba Card Number (Optional)")

    if st.button("Register Student"):
        data = {
            "full_name": name,
            "course": course,
            "years_of_study": years,
            "block": block,
            "gender": gender,
            "room": room,
            "phone_number": phone,
            "electronic_card": electronic_card,
            "gamba_card": gamba_card
        }
        insert_student(data)
        st.success("Student registered successfully!")

# -------------------------------------
# TAB 2: STUDENT RECORDS
# -------------------------------------
with tab2:
    st.markdown("<h2 style='color:#ffea00;'>Registered Students</h2>", unsafe_allow_html=True)

    df = get_students()

    # SEARCH BAR
    search = st.text_input("Search student by name or course", key="searchbar")

    if search:
        df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]

    # PAGINATION
    rows_per_page = 10
    total_pages = len(df) // rows_per_page + 1
    page = st.number_input("Page", 1, total_pages, key="pagination") - 1
    df_show = df.iloc[page * rows_per_page : (page + 1) * rows_per_page]

    # DOWNLOAD CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "cnms_students.csv", "text/csv")

    # TABLE DISPLAY
    for idx, row in df_show.iterrows():
        st.markdown(
            "<div style='border:1px solid #ffea00;padding:10px;margin-top:10px;border-radius:6px;'>",
            unsafe_allow_html=True
        )

        cols = st.columns(10)
        fields = [
            "id","full_name","course","years_of_study","block","gender","room",
            "phone_number","electronic_card","gamba_card"
        ]

        # DISPLAY VALUES WITH YELLOW LINES
        for i, c in enumerate(fields):
            cols[i].markdown(
                f"<div style='border-bottom:1px solid #ffea00;padding:4px 0;color:white'>{row[c]}</div>",
                unsafe_allow_html=True
            )

        # EDIT + DELETE BUTTONS
        edit_col, del_col = st.columns(2)

        if edit_col.button("✏️ Edit", key=f"edit_{row['id']}"):
            st.session_state.edit_id = row["id"]

        if del_col.button("🗑 Delete", key=f"del_{row['id']}"):
            delete_student(row["id"])
            st.success("Student deleted.")
            st.rerun()

        # EDIT FORM POPUP
        if "edit_id" in st.session_state and st.session_state.edit_id == row["id"]:
            st.markdown(
                "<div style='background:#111;padding:15px;border:2px solid #ffea00;border-radius:8px;margin-top:10px;'>",
                unsafe_allow_html=True
            )
            st.markdown("<h3 style='color:#ffea00;'>Edit Student</h3>", unsafe_allow_html=True)

            new_name = st.text_input("Full Name", value=row["full_name"], key=f"name_{row['id']}")
            new_course = st.selectbox(
                "Programme", DEGREE_PROGRAMMES,
                index=DEGREE_PROGRAMMES.index(row["course"]),
                key=f"course_{row['id']}"
            )
            new_years = st.number_input(
                "Years", 1, 6, value=row["years_of_study"], key=f"years_{row['id']}"
            )
            new_block = st.text_input("Block", value=row["block"], key=f"block_{row['id']}")
            new_gender = st.selectbox(
                "Gender", ["Male","Female"],
                index=["Male","Female"].index(row["gender"]),
                key=f"gender_{row['id']}"
            )
            new_room = st.text_input("Room", value=row["room"], key=f"room_{row['id']}")
            new_phone = st.text_input("Phone Number", value=row["phone_number"], key=f"phone_{row['id']}")

            new_elec = st.text_input("Electronic Card Number", value=row["electronic_card"], key=f"elec_{row['id']}")
            new_gamba = st.text_input("Gamba Card Number", value=row["gamba_card"], key=f"gamba_{row['id']}")

            s1, s2 = st.columns(2)

            if s1.button("Save", key=f"save_{row['id']}"):
                updates = {
                    "full_name": new_name,
                    "course": new_course,
                    "years_of_study": new_years,
                    "block": new_block,
                    "gender": new_gender,
                    "room": new_room,
                    "phone_number": new_phone,
                    "electronic_card": new_elec,
                    "gamba_card": new_gamba
                }
                update_student(row["id"], updates)
                st.session_state.edit_id = None
                st.success("Updated successfully!")
                st.rerun()

            if s2.button("Cancel", key=f"cancel_{row['id']}"):
                st.session_state.edit_id = None
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
