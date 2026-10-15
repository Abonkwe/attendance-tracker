import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="iSpark Attendance Tracker", layout="wide")

st.sidebar.title("iSpark Inno")
st.sidebar.subheader("Navigation")

# Setup the sidebar menu
menu = ["Programs", "Cohorts", "Trainers & Trainees", "Classes & Attendance", "Reports"]
choice = st.sidebar.radio("Go to", menu)


# programs dashboard
if choice == "Programs":
    st.header("Program Management")
    
    # --- Create a New Program ---
    with st.expander("➕ Create New Program"):
        with st.form("create_program_form"):
            new_name = st.text_input("Program Name")
            new_desc = st.text_area("Description")
            submit_program = st.form_submit_button("Create Program")
            
            if submit_program:
                if new_name:
                    response = requests.post(
                        f"{API_URL}/programs", 
                        json={"name": new_name, "description": new_desc}
                    )
                    if response.status_code == 201:
                        st.success(f"Program '{new_name}' created successfully!")
                    else:
                        st.error(response.json().get("detail", "Error creating program"))
                else:
                    st.warning("Program name is required.")

    # --- List Existing Programs ---
    st.subheader("Existing Programs")
    
    # Fetch programs from FastAPI
    response = requests.get(f"{API_URL}/programs")
    
    if response.status_code == 200:
        programs = response.json()
        if programs:
            # Display as a clean table
            st.dataframe(
                programs, 
                column_config={
                    "id": "ID",
                    "name": "Program Name",
                    "description": "Description",
                    "created_at": st.column_config.DatetimeColumn("Created Date", format="MMM DD, YYYY")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No programs found. Create one above!")
    else:
        st.error("Failed to connect to the backend API. Is FastAPI running?")






# 2. cohorts dashbaord 
elif choice == "Cohorts":
    st.header("Cohort Management")
    
    # First, we must fetch programs so the user can select which program the cohort belongs to
    response = requests.get(f"{API_URL}/programs")
    if response.status_code == 200 and response.json():
        programs = response.json()
        # Create a dictionary mapping the Program Name to its ID for the dropdown
        program_options = {p["name"]: p["id"] for p in programs}
        
        selected_program_name = st.selectbox("Select a Program to view its Cohorts", list(program_options.keys()))
        selected_program_id = program_options[selected_program_name]
        
        # --- Create a New Cohort ---
        with st.expander(f"➕ Create New Cohort in {selected_program_name}"):
            with st.form("create_cohort_form"):
                new_cohort_name = st.text_input("Cohort Name")
                col1, col2 = st.columns(2)
                start_date = col1.date_input("Start Date")
                end_date = col2.date_input("End Date")
                
                if st.form_submit_button("Create Cohort"):
                    res = requests.post(
                        f"{API_URL}/cohorts", 
                        json={
                            "program_id": selected_program_id,
                            "name": new_cohort_name,
                            "start_date": str(start_date),
                            "end_date": str(end_date)
                        }
                    )
                    if res.status_code == 201:
                        st.success("Cohort created successfully!")
                    else:
                        st.error(res.json().get("detail", "Error creating cohort"))

        # --- List Cohorts for the Selected Program ---
        st.subheader(f"Cohorts in {selected_program_name}")
        cohorts_res = requests.get(f"{API_URL}/programs/{selected_program_id}/cohorts")
        if cohorts_res.status_code == 200:
            cohorts = cohorts_res.json()
            if cohorts:
                st.dataframe(
                    cohorts,
                    column_config={"id": "Cohort ID", "program_id": None}, # Hide program_id as it's redundant here
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No cohorts found for this program.")
    else:
        st.warning("Please create a Program first before managing Cohorts.")

# ==========================================
# 3 & 4. USER MANAGEMENT DASHBOARD
# ==========================================
elif choice == "Trainers & Trainees":
    st.header("User Management")
    
    # We use Streamlit tabs to keep the UI clean and organized
    tab1, tab2, tab3 = st.tabs(["Create Trainer", "Create Trainee", "Assign & Enroll"])
    
    with tab1:
        st.subheader("Add a New Trainer")
        with st.form("create_trainer_form"):
            t_name = st.text_input("Trainer Name")
            t_email = st.text_input("Trainer Email")
            if st.form_submit_button("Create Trainer"):
                res = requests.post(f"{API_URL}/trainers", json={"name": t_name, "email": t_email})
                if res.status_code == 201:
                    st.success(f"Trainer {t_name} created with ID: {res.json()['id']}")
                else:
                    st.error(res.json().get("detail", "Error creating trainer"))
                    
    with tab2:
        st.subheader("Add a New Trainee")
        with st.form("create_trainee_form"):
            tr_name = st.text_input("Trainee Name")
            tr_email = st.text_input("Trainee Email")
            if st.form_submit_button("Create Trainee"):
                res = requests.post(f"{API_URL}/trainees", json={"name": tr_name, "email": tr_email})
                if res.status_code == 201:
                    st.success(f"Trainee {tr_name} created with ID: {res.json()['id']}")
                else:
                    st.error(res.json().get("detail", "Error creating trainee"))
                    
    with tab3:
        st.subheader("Assign Users to Cohorts")
        st.info("Enter the relevant IDs to link users to cohorts.")
        col1, col2 = st.columns(2)
        
        with col1:
            with st.form("assign_trainer_form"):
                st.markdown("**Assign Trainer**")
                c_id = st.number_input("Cohort ID", min_value=1, step=1)
                t_id = st.number_input("Trainer ID", min_value=1, step=1)
                if st.form_submit_button("Assign Trainer"):
                    res = requests.post(f"{API_URL}/cohorts/{c_id}/trainers", json={"trainer_id": t_id})
                    if res.status_code == 201:
                        st.success("Trainer successfully assigned!")
                    else:
                        st.error(res.json().get("detail", "Error assigning trainer"))
                        
        with col2:
            with st.form("enroll_trainee_form"):
                st.markdown("**Enroll Trainee**")
                c_id_en = st.number_input("Cohort ID ", min_value=1, step=1)
                tr_id = st.number_input("Trainee ID", min_value=1, step=1)
                if st.form_submit_button("Enroll Trainee"):
                    res = requests.post(f"{API_URL}/cohorts/{c_id_en}/enrollments", json={"trainee_id": tr_id})
                    if res.status_code == 201:
                        st.success("Trainee successfully enrolled!")
                    else:
                        st.error(res.json().get("detail", "Error enrolling trainee"))





# ==========================================
# 5 & 6. CLASSES & ATTENDANCE DASHBOARD
# ==========================================
elif choice == "Classes & Attendance":
    st.header("Classes & Attendance")
    
    # We need context: Select a Program -> Select a Cohort
    programs_res = requests.get(f"{API_URL}/programs")
    if programs_res.status_code == 200 and programs_res.json():
        programs = {p["name"]: p["id"] for p in programs_res.json()}
        selected_prog = st.selectbox("1. Select Program", list(programs.keys()))
        prog_id = programs[selected_prog]
        
        cohorts_res = requests.get(f"{API_URL}/programs/{prog_id}/cohorts")
        if cohorts_res.status_code == 200 and cohorts_res.json():
            cohorts = {c["name"]: c["id"] for c in cohorts_res.json()}
            selected_coh = st.selectbox("2. Select Cohort", list(cohorts.keys()))
            coh_id = cohorts[selected_coh]
            
            st.divider()
            tab1, tab2 = st.tabs(["Schedule a Class", "Record/Update Attendance"])
            
            with tab1:
                st.subheader(f"Schedule Class for {selected_coh}")
                with st.form("schedule_class_form"):
                    col1, col2 = st.columns(2)
                    t_id = col1.number_input("Trainer ID (Must be assigned to cohort)", min_value=1, step=1)
                    c_date = col2.date_input("Class Date")
                    topic = st.text_input("Topic (Optional)")
                    
                    if st.form_submit_button("Schedule Class"):
                        res = requests.post(
                            f"{API_URL}/cohorts/{coh_id}/classes", 
                            json={"trainer_id": t_id, "date": str(c_date), "topic": topic}
                        )
                        if res.status_code == 201:
                            st.success(f"Class scheduled successfully! Class ID: {res.json()['id']}")
                        else:
                            st.error(res.json().get("detail", "Error scheduling class"))
            
            with tab2:
                st.subheader("Record Batch Attendance")
                st.info("If attendance was already recorded, submitting again will safely UPDATE the records.")
                
                # Fetch classes for the dropdown
                classes_res = requests.get(f"{API_URL}/cohorts/{coh_id}/classes")
                if classes_res.status_code == 200 and classes_res.json():
                    classes_data = classes_res.json()
                    class_options = {f"ID: {c['id']} - {c['date']} ({c['topic']})": c['id'] for c in classes_data}
                    selected_class_str = st.selectbox("Select Class", list(class_options.keys()))
                    class_id = class_options[selected_class_str]
                    
                    recording_trainer = st.number_input("Recording Trainer ID", min_value=1, step=1)
                    
                    # Fetch all trainees in this cohort using our report endpoint
                    report_res = requests.get(f"{API_URL}/cohorts/{coh_id}/report")
                    if report_res.status_code == 200 and report_res.json():
                        trainees = report_res.json()
                        
                        with st.form("attendance_form"):
                            st.write("**Mark Status for all Enrolled Trainees:**")
                            attendance_records = []
                            
                            # Dynamically generate a dropdown for every trainee
                            for t in trainees:
                                status = st.selectbox(
                                    f"{t['trainee_name']} (ID: {t['trainee_id']})", 
                                    options=["Present", "Absent", "Late", "Excused"], 
                                    key=f"att_{t['trainee_id']}"
                                )
                                attendance_records.append({"trainee_id": t['trainee_id'], "status": status})
                                
                            if st.form_submit_button("Submit Attendance Roster"):
                                payload = {
                                    "recorded_by_trainer_id": recording_trainer,
                                    "records": attendance_records
                                }
                                att_res = requests.post(f"{API_URL}/classes/{class_id}/attendance", json=payload)
                                if att_res.status_code == 200:
                                    st.success(att_res.json().get("message"))
                                else:
                                    st.error(att_res.json().get("detail", "Error recording attendance"))
                    else:
                        st.warning("No trainees are enrolled in this cohort yet.")
                else:
                    st.info("No classes scheduled for this cohort yet.")
        else:
            st.info("No cohorts found in this program.")
    else:
        st.info("No programs found.")

# ==========================================
# 7. REPORTS DASHBOARD
# ==========================================
elif choice == "Reports":
    st.header("Data Reports & Analytics")
    
    programs_res = requests.get(f"{API_URL}/programs")
    if programs_res.status_code == 200 and programs_res.json():
        programs = {p["name"]: p["id"] for p in programs_res.json()}
        selected_prog = st.selectbox("1. Select Program", list(programs.keys()))
        prog_id = programs[selected_prog]
        
        cohorts_res = requests.get(f"{API_URL}/programs/{prog_id}/cohorts")
        if cohorts_res.status_code == 200 and cohorts_res.json():
            cohorts = {c["name"]: c["id"] for c in cohorts_res.json()}
            selected_coh = st.selectbox("2. Select Cohort", list(cohorts.keys()))
            coh_id = cohorts[selected_coh]
            
            st.divider()
            tab1, tab2, tab3 = st.tabs(["Cohort Report", "Trainee History", "Class Summary"])
            
            with tab1:
                st.subheader(f"Cohort Attendance Report: {selected_coh}")
                report_res = requests.get(f"{API_URL}/cohorts/{coh_id}/report")
                if report_res.status_code == 200 and report_res.json():
                    st.dataframe(
                        report_res.json(),
                        column_config={
                            "trainee_id": "ID",
                            "trainee_name": "Name",
                            "present_count": "Present",
                            "absent_count": "Absent",
                            "late_count": "Late",
                            "excused_count": "Excused",
                            "total_classes_marked": "Total Marked",
                            "attendance_rate_percentage": st.column_config.NumberColumn("Rate (%)", format="%.1f%%"),
                            "is_flagged": "Flagged (<75%)"
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.info("No data available for this cohort.")
                    
            with tab2:
                st.subheader("Individual Trainee History")
                t_id = st.number_input("Enter Trainee ID", min_value=1, step=1, key="hist_tid")
                if st.button("Fetch History"):
                    hist_res = requests.get(f"{API_URL}/cohorts/{coh_id}/trainees/{t_id}/history")
                    if hist_res.status_code == 200 and hist_res.json():
                        st.dataframe(hist_res.json(), hide_index=True, use_container_width=True)
                    else:
                        st.error("No history found or invalid Trainee ID.")
                        
            with tab3:
                st.subheader("Class Summary")
                c_id = st.number_input("Enter Class ID", min_value=1, step=1, key="sum_cid")
                if st.button("Fetch Summary"):
                    sum_res = requests.get(f"{API_URL}/classes/{c_id}/summary")
                    if sum_res.status_code == 200:
                        data = sum_res.json()
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Status Counts**")
                            st.json(data.get("status_counts", {}))
                        with col2:
                            st.markdown("**Unmarked Trainees**")
                            unmarked = data.get("unmarked_trainees", [])
                            if unmarked:
                                for name in unmarked:
                                    st.write(f"- {name}")
                            else:
                                st.success("All trainees have been marked!")
                    else:
                        st.error("Class not found.")
        else:
            st.info("No cohorts found.")
    else:
        st.info("No programs found.")