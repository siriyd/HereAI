import streamlit as st
import numpy as np
import time

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.pipelines.face_pipeline import predict_attendance, get_face_embedding, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_enrolled_subjects, get_student_logs

from src.components.dialog_enroll import enroll_dialog
from src.database.db import unenroll_student_to_subject
from src.components.subject_card import subject_card

from PIL import Image

def student_screen():
    style_background_dashboard()
    style_base_layout()

    
    if 'student_data' in st.session_state:
        student_dashboard()
    elif 'student_login_type' not in st.session_state or st.session_state.student_login_type=="login":
        student_screen_login()
    elif st.session_state.student_login_type == "register":
        student_screen_register()

def student_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='student_login_back_btn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()
    photo_source= st.camera_input("Position your face in the center", key="student_face_input")

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button("Login", type='primary', shortcut='control+enter', width='stretch'):
            if photo_source:
                img = np.array(Image.open(photo_source))\
                
                with st.spinner("AI is scanning..."):
                    detected,all_ids,num_faces = predict_attendance(img)

                    if num_faces==0:
                        st.warning("No face detected.")
                    elif num_faces>1:
                        st.warning("Multiple faces detected. Please ensure only your face is visible.")
                    else:
                        if detected:
                            student_id = next(iter(detected))
                            all_students = get_all_students()
                            s = next((student for student in all_students if student['student_id'] == student_id), None)

                            if s:
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = s
                                st.toast("Welcome back, " + s['name'] + "!", icon="🎉")
                                time.sleep(2)
                                st.rerun()
                        else:
                            st.info("Face not recognized. Please try again.")


    with btnc2:
        if st.button("Register", type='secondary', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            st.session_state.student_login_type = "register"
            st.rerun()



    footer_dashboard()


def student_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='student_register_back_btn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    photo_source= st.camera_input("Position your face in the center", key="student_face_input")

    
    st.header('Register your student profile')

    st.space()
    st.space()

    
    new_name = st.text_input("Enter your name", placeholder='Ananya Roy')

    st.subheader("Optional : Voice Enrollment")
    st.info("Enroll your voice for attendace")

    audio_data = None

    try: 
        audio_data = st.audio_input("Record a short phrase like 'I am present', 'My name is Akash'", key="student_audio_input")
    except:
        st.error("Audio recording error. Please try again.")


    btnc1, btnc2 = st.columns(2)
    with btnc1:
        if st.button("Create Account", type='primary'):
            if new_name and photo_source:
                with st.spinner("Creating profile..."):
                    img = np.array(Image.open(photo_source))
                    encodings = get_face_embedding(img)
                    if encodings:
                        face_emb = encodings[0].tolist()

                        voice_emb = None
                        if audio_data:
                            voice_emb = get_voice_embedding(audio_data.getvalue())

                        response_data = create_student(new_name, face_embedding = face_emb, voice_embedding =voice_emb)

                        if response_data:
                            train_classifier()
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = response_data[0]
                            st.toast(f"Profile created! Hi {new_name} !", icon="🎉")
                            time.sleep(2)
                            st.session_state
                            st.rerun()
                    else:
                        st.error("Face not recognized. Please try again.")
                            
                    
            else:
                st.warning("Please enter your name and take a photo.")

    with btnc2:
        if st.button("Login instead", type='secondary'):
            st.session_state.student_login_type="login"
            st.rerun()


    footer_dashboard()

def student_dashboard():
    student_data = st.session_state['student_data']
    student_id = student_data['student_id']
    
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']} !", text_alignment='center')

        if st.button("Logout", type='secondary', key='student_login_back_btn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state['student_data']
            st.rerun()

    st.space()
    st.space()

    c1,c2=st.columns(2)
    with c1:
        st.header("Your Enrolled Subjects")
    with c2:
        if st.button("Enroll in Subject", type="primary",width='stretch',key='student_enroll_subject_btn',icon=':material/add:'):
            enroll_dialog()

    st.divider()

    with st.spinner("Loading your subjects.."):
        subjects = get_enrolled_subjects(student_id)
        logs = get_student_logs(student_id)

        stats_map={}

        for log in logs:
            sid = log['subject_id']

            if sid not in stats_map:
                stats_map[sid]={"total":0,"attended":0}
            stats_map[sid]['total']+=1

            if log['is_present']:
                stats_map[sid]['attended']+=1

    cols = st.columns(2)

    if not subjects:
        st.info("You are not enrolled in any subjects yet. Enroll in a subject to get started.")
    else:
        for i,sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub_node['subject_id']
            stats = stats_map.get(sid,{"total":0,"attended":0})

            stats = [
                ("Total Classes", stats['total']),
                ("Classes Attended", stats['attended']),
            ]

            def unenroll_btn():
                if st.button(f"Unenroll from {sub['name']}",key=f"unenroll_subject_{sub['subject_code']}",type='tertiary',width='stretch',icon=":material/delete:"):
                    unenroll_student_to_subject(sub['subject_id'],student_id)
                    st.toast(f"You are no longer enrolled in {sub['name']}")
                    st.rerun()

            with cols[i%2]:
                subject_card(
                    name = sub['name'],
                    code = sub['subject_code'],
                    section = sub['section'],
                    stats = stats,
                    footer_callback= unenroll_btn
                )



    footer_dashboard()