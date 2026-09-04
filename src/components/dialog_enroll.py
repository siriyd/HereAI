import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time

@st.dialog("Enroll in Subject")
def enroll_dialog():
    st.write("Enter the subject code provided by your teacher to enroll")
    join_code = st.text_input("Subject Code", placeholder="eg. CS101")

    if st.button("Enroll Now", type="primary", width="stretch", icon=":material/add:"):
        if join_code:
            res = supabase.table('subjects').select('subject_id,name,subject_code').eq('subject_code', join_code).execute()
            if res.data:
                subject = res.data[0]
                student_id = st.session_state['student_data']['student_id']
                check = supabase.table('subject_students').select('*').eq('student_id', student_id).eq('subject_id', subject['subject_id']).execute()
                if check.data:
                    st.warning("You are already enrolled in this subject.")
                else:
                    enroll_student_to_subject(subject['subject_id'], student_id)
                    st.success("You are now enrolled in " + subject['name'])
                    time.sleep(2)
                    st.rerun()
