import streamlit as st
from src.database.db import create_subject

@st.dialog("Create New Subject")
def create_subject_dialogue(teacher_id):
    st.write("Enter the details of the new subject")
    sub_code=st.text_input("Subject ID",placeholder="CS101")
    subject_name = st.text_input("Subject Name",placeholder="Introduction to Computer Science")
    subject_section=st.text_input("Section",placeholder="A")

    if st.button("Create Subject Now",type="primary",width="stretch",icon=":material/add:"):
        if sub_code and subject_name and subject_section:
            try:
                create_subject(sub_code,subject_name,subject_section,teacher_id)
                st.toast("Subject created successfully!",icon="🎉")
            except Exception as e:
                st.warning("Error creating subject: " + str(e))
        else:
            st.warning("Please fill in all fields.")