import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV

import streamlit as st

from src.database.db import get_all_students

@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector() # how many faces are in the image

    #shape predictor
    sp = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())

    #face recognition model
    facerec = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())

    return detector, sp, facerec

def get_face_embedding(image_np):
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np,1)

    embeddings = []
    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape,1) # 128 embeddings
        embeddings.append(np.array(face_descriptor)) 
    return embeddings 

@st.cache_resource
def get_trained_model():
    students = get_all_students()
    X = []
    y = []
    if students is None:
        return None
    
    for student in students:
        if 'face_embedding' in student and student['face_embedding']:
            X.append(np.array(student['face_embedding']))
            y.append(student['student_id'])
    if len(X) == 0:
        return None

    unique_classes = set(y)
    clf = None

    if len(unique_classes) >= 2:
        # clf = SVC(kernel='linear', probability=True, class_weight='balanced')
        base_clf = SVC(probability=False , kernel='linear', class_weight='balanced')  # no longer need probability=True here
        clf = CalibratedClassifierCV(base_clf, ensemble=False)
        try:
            clf.fit(X, y)
        except ValueError:
            clf = None  # fitting failed, fall back to distance-only matching

    return {'clf': clf, 'X': X, 'y': y}

def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_img_np):
    encodings = get_face_embedding(class_img_np)

    detected_students = {}
    model_data = get_trained_model()

    if not model_data:
        return detected_students, [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))
    resemblance_threshold = 0.6

    for face_encoding in encodings:
        predicted_id = None

        # make a prediction
        if clf is not None and len(all_students) >= 2:
            predicted_id = int(clf.predict([face_encoding])[0])
        else:
            # Single-student case (or classifier unavailable): verify by distance
            known_encoding = X_train[0]
            distance = np.linalg.norm(np.array(known_encoding) - np.array(face_encoding))
            if distance < resemblance_threshold:
                predicted_id = int(all_students[0]) if all_students else None

        if predicted_id is None:
            continue

        # Re-verify classifier's prediction against the actual stored embedding
        try:
            student_embedding = X_train[y_train.index(predicted_id)]
        except ValueError:
            student_embedding = None

        best_match_score = (
            np.linalg.norm(np.array(face_encoding) - np.array(student_embedding))
            if student_embedding is not None else None
        )

        if best_match_score is not None and best_match_score < resemblance_threshold:
            detected_students[predicted_id] = True

    return detected_students, all_students, len(encodings)