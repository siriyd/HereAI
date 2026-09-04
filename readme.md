# HereAI

HereAI is an AI-powered attendance tracker for classrooms. It gives students and teachers separate portals and uses face recognition and voice recognition to make attendance, enrollment, and attendance review easier to manage.

The application is built as a Streamlit web app. Supabase stores users, subjects, enrollments, biometric embeddings, and attendance logs.

## Features

### Student portal

- Register with a captured face image.
- Log in using face recognition.
- Optionally enroll a voice profile.
- Join subjects using a subject code or a shared QR/link.
- View enrolled subjects.
- See total classes and attended classes for each subject.
- Unenroll from subjects.
- Log out from the student dashboard.

### Teacher portal

- Register and log in with a username and password.
- Create and manage subjects.
- Share subjects through a generated QR code and join URL.
- Capture classroom photos with a camera or upload multiple images.
- Record classroom audio for voice-based attendance.
- Detect students in classroom images using face recognition.
- Identify speakers in recorded audio using voice recognition.
- Review detected attendance before saving it.
- View attendance summaries for subjects.

### Attendance workflow

1. A teacher selects a subject and supplies classroom images or a recording.
2. HereAI compares faces or voices with enrolled student embeddings.
3. The teacher reviews the attendance results.
4. Confirmed results are saved as attendance logs in Supabase.

## Project structure

```text
Attendance Tracker/
|-- app.py                              # Streamlit entry point and page routing
|-- requirements.txt                    # Python dependencies
|-- readme.md                           # Project documentation
|-- .gitignore                          # Ignored files and folders
|-- .streamlit/
|   `-- secrets.toml                    # Local Supabase secrets
|-- database/                           # Reserved root-level database directory
|-- src/
    |-- components/
    |   |-- dialog_add_photos.py        # Capture or upload attendance photos
    |   |-- dialog_attendance_results.py # Review and save attendance results
    |   |-- dialog_auto_enroll.py        # Enrollment from a join-code URL
    |   |-- dialog_enroll.py             # Manual subject-code enrollment
    |   |-- dialog_share_subject.py      # QR code and subject sharing
    |   |-- dialog_voice_attendance.py   # Audio recording and voice attendance
    |   |-- dialogue_create_subject.py   # Subject creation dialog
    |   |-- footer.py                    # Footer component
    |   |-- header.py                    # HereAI header and branding
    |   `-- subject_card.py              # Subject summary and actions
    |-- database/
    |   |-- config.py                   # Supabase client configuration
    |   `-- db.py                       # Database and authentication helpers
    |-- pipelines/
    |   |-- face_pipeline.py            # Face detection, embeddings, and matching
    |   `-- voice_pipeline.py            # Audio processing, embeddings, and matching
    |-- screens/
    |   |-- home_screen.py              # Student/teacher portal selection
    |   |-- student_screen.py            # Student registration and dashboard
    |   |-- teacher_screen.py            # Teacher dashboard and workflows
    |   `-- com/                        # Reserved screen-related directory
    `-- ui/
        `-- base_layout.py              # Shared Streamlit CSS and layout styling
```

## How it works

- `app.py` initializes Streamlit, maintains the login state, and routes users to the home, student, or teacher screen.
- The face pipeline extracts 128-dimensional face embeddings and uses a cached linear SVM classifier with distance-based matching.
- The voice pipeline converts audio to 16 kHz, creates embeddings with Resemblyzer, compares speakers, and splits classroom audio into speech segments.
- `src/database/db.py` handles password hashing, authentication, user records, subjects, enrollments, and attendance queries.
- Attendance results are shown to the teacher before they are inserted into the database.
- A `join-code` query parameter lets a logged-in student accept an enrollment invitation from a shared subject link.

## Requirements

- Python 3.9 or newer is recommended.
- A Supabase project with the required tables and relationships.
- A working camera or image upload capability for face attendance.
- A microphone or audio upload capability for voice attendance.
- Network access for external branding and font assets used by the interface.
- Some dependencies, especially `dlib`, face-recognition models, and Resemblyzer, can require extra installation time and system resources.

## Installation and setup

1. Clone the repository and open its directory:

   ```bash
   git clone <repository-url>
   cd "Attendance Tracker"
   ```

2. Create and activate a virtual environment. A Conda environment is also suitable:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` and add the Supabase credentials:

   ```toml
   SUPABASE_URL = "your-supabase-project-url"
   SUPABASE_KEY = "your-supabase-anon-key"
   ```

   Keep this file private. It is intended for local Streamlit secrets and should not be committed.

5. Create the Supabase tables described below and configure their foreign-key relationships.

## Supabase data model

The application expects the following tables and fields:

- `teachers`: `teacher_id`, `username`, `password`, `name`
- `students`: `student_id`, `name`, `face_embedding`, `voice_embedding`
- `subjects`: `subject_id`, `subject_code`, `name`, `section`, `teacher_id`
- `subject_students`: `subject_id`, `student_id`
- `attendance_logs`: `student_id`, `subject_id`, `timestamp`, `is_present`

The nested Supabase queries also require the relationships between subjects, students, and attendance records to be configured correctly. Row Level Security policies should be configured for the intended access model before deploying the application.

## Run the application

From the project root, run:

```bash
streamlit run app.py
```

Streamlit normally starts the application at:

```text
http://localhost:8501
```

The current subject-sharing implementation creates join URLs using `http://localhost:8501/`. For a hosted deployment, update that base URL to the public application URL.

## Technologies used

- **Python**: Application and data-processing language.
- **Streamlit**: Web interface, dialogs, session state, camera/audio inputs, and page routing.
- **Supabase**: Hosted database and client API.
- **NumPy**: Numerical operations for biometric embeddings.
- **pandas**: Attendance data handling and summaries.
- **scikit-learn**: Linear SVM face classifier.
- **dlib**: Face detection, facial landmarks, and face recognition model support.
- **face-recognition models**: Pre-trained face recognition model package.
- **Pillow**: Image preprocessing.
- **librosa**: Audio loading and resampling.
- **Resemblyzer**: Voice embedding generation.
- **bcrypt**: Teacher password hashing and verification.
- **Segno**: QR code generation.
- **CSS and external Google Fonts**: Shared visual styling and typography.

## Important notes

- The Supabase schema and migrations are not included in this repository.
- Supabase credentials must be available at import time, so missing secrets prevent startup.
- Face and voice recognition thresholds are defined in the application and are not currently configurable through the UI.
- Biometric data is sensitive. Use appropriate database permissions, Row Level Security, secret management, and privacy practices before using HereAI with real student data.
