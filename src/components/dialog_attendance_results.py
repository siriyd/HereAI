import streamlit as st
import time
import pandas as pd
from src.database.db import create_attendance

def show_results(df,logs):
    st.write("Please review the attendace before confirming")
    st.dataframe(df,hide_index=True,width='stretch')

    col1,col2= st.columns(2)
    with col1:
        if st.button("Discard",type="primary",width="stretch",icon=":material/delete:"):
            st.session_state.voice_attendance_results=None
            st.rerun()
    with col2:
        if st.button("Corfirm and save",type="primary",width="stretch",icon=":material/check:"):
            try:
                create_attendance(logs)
                st.toast("Attendance saved successfully!",icon="🎉")
                st.session_state.attedance_images=[]
                st.session_state.voice_attendance_results=None
                st.rerun()
            except Exception as e:
                st.error("Error saving attendance " )

@st.dialog("Attendance Reports")
def attendance_result_dialog(df,logs):
     show_results(df,logs)
    