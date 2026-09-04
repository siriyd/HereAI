import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

import time
@st.dialog("Auto Enroll")
def auto_enroll_dialog(subject_code):
    student_id = st.session_state['student_data']['student_id']

    res = supabase.table('subjects').select('subject_id,name').eq('subject_code',subject_code).execute()
    if not res.data:
        st.error("Subject code not found")
        if st.button('Close'):
            st.query_params.clear()
            st.rerun()
            return
    subjects = res.data[0]

    check = supabase.table('subject_students').select('*').eq('student_id', student_id).eq('subject_id', subjects['subject_id']).execute()
    if check.data:
        st.info("You are already enrolled in this subject.")
        if st.button('Close'):
            st.query_params.clear()
            st.rerun()
            return  
    else:
        st.markdown(f"Are you sure you want to enroll in {subjects['name']}?")\

        col1,col2=st.columns(2)
        with col1:
            if st.button("No",type='secondary',width='stretch',key='auto_enroll_no_btn'):
                st.query_params.clear()
                st.rerun()
                return
        with col2:
            if st.button("Yes",type='primary',width='stretch',key='auto_enroll_yes_btn'):
                enroll_student_to_subject(subjects['subject_id'], student_id)
                st.success("You are now enrolled in " + subjects['name'])
                st.query_params.clear()
                time.sleep(2)
                st.rerun()
    