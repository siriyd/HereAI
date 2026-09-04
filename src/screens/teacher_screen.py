import streamlit as st
import numpy as np
import pandas as pd

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.dialogue_create_subject import create_subject_dialogue
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photos import add_photos_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.database.config import supabase

import time
from datetime import datetime
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subjects, get_teacher_attendance_records

def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if 'teacher_data' in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()

def teacher_dashboard():
    teacher_data = st.session_state['teacher_data']

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {teacher_data['name']} !", text_alignment='center')

        if st.button("Logout", type='secondary', key='teacher_login_back_btn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state['teacher_data']
            st.rerun()

    st.space()
    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state["current_teacher_tab"] = 'take_attendance'
    tab1,tab2,tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state["current_teacher_tab"] == 'take_attendance' else "tertiary"
        if st.button("Take Attendance", type=type1,width="stretch",icon=":material/ar_on_you:"):
            st.session_state["current_teacher_tab"] = 'take_attendance'
            st.rerun()
    with tab2:
        type2 = "primary" if st.session_state["current_teacher_tab"] == 'manage_subjects' else "tertiary"
        if st.button("Manage Subjects", type=type2,width="stretch",icon=":material/description:"):
                    st.session_state["current_teacher_tab"] = 'manage_subjects'
                    st.rerun()
    with tab3:
        type3 = "primary" if st.session_state["current_teacher_tab"] == 'attendance_records' else "tertiary"
        if st.button("Attendance Records", type=type3,width="stretch",icon=":material/dashboard:"):
                    st.session_state["current_teacher_tab"] = 'attendance_records'
                    st.rerun()

    if st.session_state["current_teacher_tab"] == 'take_attendance':
        teacher_take_attendance()
    elif st.session_state["current_teacher_tab"] == 'manage_subjects':
        teacher_manage_subjects()
    elif st.session_state["current_teacher_tab"] == 'attendance_records':
        teacher_attendance_records()


    footer_dashboard()

def teacher_take_attendance():
    teacher_id = st.session_state['teacher_data']['teacher_id']
    st.header("Take AI Attendance")

    if 'attendance_images' not in st.session_state:
        st.session_state['attendance_images'] = []

    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning("No subjects found. Please add a subject first.")
        return
    subject_options = {f"{subject['name']} - {subject['subject_code']} ": subject['subject_id'] for subject in subjects}

    col1,col2=st.columns([3,1])
    with col1:
        subject_code = st.selectbox('Select Subject', options=list(subject_options.keys()))
    with col2:
        if st.button("Add Photos", type='primary', key='teacher_add_photos_btn',icon=':material/add:',width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[subject_code]

    st.divider()

    if st.session_state.attendance_images:
        st.header("Added Images")
        gallery_cols = st.columns(4)
        for idx, image in enumerate(st.session_state.attendance_images): 
            with gallery_cols[idx%4]:           
                st.image(image, caption=f"Image {idx+1}")
                st.divider()

    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("Take AI Attendance",width='stretch',icon=":material/ar_on_you:"):
            with st.spinner("Taking Attendance..."):
                has_photos = bool(st.session_state.attendance_images)
                if not has_photos:
                    st.warning("No photos added. Please add photos first.")
                else:
                    all_detected_id={}
                    for idx, image in enumerate(st.session_state.attendance_images):
                        img_np=np.array(image.convert('RGB'))
                        detected,_,_ = predict_attendance(img_np)
                        if detected:
                            for sid in detected.keys():
                                student_id = int(sid)

                                all_detected_id.setdefault(student_id,[]).append(f"Photo {idx+1}")

                    enrolled_response = supabase.table('subject_students').select('*, students(*)').eq('subject_id', selected_subject_id).execute()
                    enrolled_students = enrolled_response.data
                    if not enrolled_students:
                        st.warning("No students enrolled in this course.")
                    else:
                        results, attendance_to_log = [],[]

                        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        for student in enrolled_students:
                            student_id = student['student_id']
                            student_info = student['students']
                            sources = all_detected_id.get(int(student_id),[])
                            is_present = len(sources) > 0
                            results.append({
                                "Name" : student_info['name'],
                                "ID": student_id,
                                "Sources" : ", ".join(sources) if is_present else "-",
                                "Status" : "Present" if is_present else "Absent"
                            })
                            attendance_to_log.append({
                                "student_id": student_id,
                                "subject_id": selected_subject_id,
                                "timestamp": current_timestamp,
                                "is_present": bool(is_present)
                            })

                        attendance_result_dialog(pd.DataFrame(results), attendance_to_log)
                        
        
    with c2:
        if st.button("Clear all photos",width='stretch', type='secondary', key='teacher_take_attendance_clear_btn',icon=':material/delete:'):
            st.session_state.attendance_images = []
            st.rerun()
    with c3:
        if st.button("Use Voice Attendance",type='primary',key='teacher_take_attendance_submit_btn',icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)



def teacher_manage_subjects():
    teacher_id = st.session_state['teacher_data']['teacher_id']
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.header("Manage Subjects")
    with col2:
        if st.button("Add Subject", type='primary', key='teacher_add_subject_btn',icon=':material/add:',width='stretch'):
            create_subject_dialogue(teacher_id)

    # LIST ALL SUBJECTS OF THE TEACHER
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for subject in subjects:
            stats= [
                ("Students", subject['total_students']),
                ("Classes", subject['total_classes'])
            ]
            def share_btn():
                if st.button(f"Share code: {subject['name']}",key=f"share_subject_{subject['subject_code']}",type='secondary',width='stretch',icon=":material/share:"):
                    share_subject_dialog(subject['name'],subject['subject_code'])
                st.space()

            subject_card(
                name = subject['name'],
                code = subject['subject_code'],
                section = subject['section'],
                stats = stats,
                footer_callback=share_btn
            )
    else:
        st.info("No subjects found.")

def teacher_attendance_records():
    st.header("Attendance Records")

    teacher_id=st.session_state['teacher_data']['teacher_id']
    records=get_teacher_attendance_records(teacher_id)

    if not records:
        return

    data=[]

    for record in records:
        ts = record.get('timestamp')
        data.append({
            "ts_group":ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "NA",
            "Subject":record['subjects']['name'],
            "Subject Code":record['subjects']['subject_code'],
            "is_present":bool(record.get("is_present", False))
        })

    df=pd.DataFrame(data)

    summary=(
        df.groupby(['ts_group','Time','Subject','Subject Code'])
        .agg(
            Present_Count=("is_present", "sum"),
            Total_count=("is_present", "count")
        ).reset_index()
    )

    summary["Attendance Stats"] = (
        "✅" + summary['Present_Count'].astype(str) + " / " + summary['Total_count'].astype(str) +
        ' Students'
    )

    display_df = (summary.sort_values(by='ts_group', ascending=False)
                   [["Time", "Subject","Subject Code","Attendance Stats"]]
                  )
    st.dataframe(display_df,width='stretch',hide_index=True)
    



def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='teacher_login_back_btn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            teacher = teacher_login(teacher_username, teacher_pass)
            if teacher:
                st.toast("Welcome back, " + teacher['name'] + "!", icon="🎉")
                time.sleep(2)
                st.session_state.user_role = 'teacher'
                st.session_state['teacher_data'] = teacher
                st.session_state.is_logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()

def register_teacher(username, name, password, password_confirm):
    if not username or not name or not password or not password_confirm:
        return False, "Please fill in all fields."
    if check_teacher_exists(username):
        return False, "Username already exists. Please choose a different username."
    if password != password_confirm:
        return False, "Passwords do not match. Please try again." 
    try:
        create_teacher(username, password,name)
        return True, "Teacher registered successfully!"
    except Exception as e:
        return False, f"An unexpected error occurred"
    

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='teacher_register_back_btn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success,message = register_teacher(teacher_username,teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                time.sleep(2)
                st.session_state.teacher_login_type = 'login'
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()