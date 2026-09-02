import streamlit as st
import numpy as np

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout

from PIL import Image

def student_screen():
    style_background_dashboard()
    style_base_layout()
    
    if 'teacher_data' in st.session_state:
        student_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        student_screen_login()
    elif st.session_state.teacher_login_type == "register":
        student_screen_register()

def student_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()
    photo_source= st.camera_input("Position your face in the center", key="student_face_input")

    if photo_source:
        np.array(Image.open(photo_source))

    footer_dashboard()

def student_screen_register():
    pass

def student_dashboard():
    pass