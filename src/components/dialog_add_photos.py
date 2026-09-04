import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time
from PIL import Image

@st.dialog("Capture / Upload Photos")
def add_photos_dialog():
    st.write("Add classroom photos to scan for attendance")

    if "photo_tab" not in st.session_state:
        st.session_state["photo_tab"] = 'camera'

    t1,t2=st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state["photo_tab"] == 'camera' else "tertiary"
        if st.button("Camera", type=type_camera,width='stretch',key='add_photos_camera_btn'):
            st.session_state["photo_tab"] = 'camera'
    with t2:
        type_upload = "primary" if st.session_state["photo_tab"] == 'upload' else "tertiary"
        if st.button("Upload photos", type=type_upload,width='stretch',key='add_photos_upload_btn'):
            st.session_state["photo_tab"] = 'upload'

    if st.session_state["photo_tab"] == 'camera':
        cam_photo = st.camera_input("Take a photo",key='add_photos_camera_input')

        if cam_photo:
            st.session_state['attendance_images'].append(Image.open(cam_photo))
            st.toast("Photo captured!")
            st.rerun()

    elif st.session_state["photo_tab"] == 'upload':
        uploaded_files = st.file_uploader("Choose image files",type=["jpg", "jpeg", "png"], accept_multiple_files=True,key='add_photos_upload_input')

        if uploaded_files:
            for file in uploaded_files:
                st.session_state['attendance_images'].append(Image.open(file))
            st.toast("Photos uploaded!")
            st.rerun()

    st.divider()

    if st.button("Done", type='primary',width='stretch',key='add_photos_done_btn'):
        st.rerun()