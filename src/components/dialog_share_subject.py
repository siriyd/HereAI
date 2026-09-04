import streamlit as st

import segno
import io

@st.dialog("Share Class Link")
def share_subject_dialog(subject_name,subject_code):
    app_domain = "http://localhost:8501/"
    join_url = f"{app_domain}?join-code={subject_code}"

    st.header("Scan to Join")

    qr = segno.make(join_url)

    out = io.BytesIO()
    qr.save(out, kind='png', scale=10,border=1)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('### Copy Link')
        st.code(join_url, language='text', line_numbers=False)
        st.code(subject_code, language='text', line_numbers=False)
        st.info("Copy the code and share it with your students")
    with col2:
        st.markdown('### Scan to Join')  
        st.image(out.getvalue(), caption='QRCODE for class joining')