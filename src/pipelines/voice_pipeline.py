from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import streamlit as st
import io
import librosa

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000) # sr = sample rate of 16000 Hz
        wav = preprocess_wav(audio)

        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()  # 256-dimensional embedding vector
    except Exception as e:
        st.error("Voice recognition error. - " + str(e))
        return None

def identify_speaker(new_embedding, candidates_dict,threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    best_sid=None
    best_score=-1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding)
            if similarity > best_score:
                best_score = similarity
                best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score
    return None, best_score

def process_bulk_audio(audio_bytes,candidates_dict,threshold=0.65):
    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000) # sr = sample rate of 16000 Hz
        segments = librosa.effects.split(audio, top_db=38)  # Split audio into segments based on silence - top_db = sensitivity threshold - anything quieter than 38dB below peak volume counts as silence, splitting the audio ther

        identified_results = {}

        for start, end in segments:
            if(end-start)<sr*0.5: #start and end come from librosa.effects.split(), and they're sample indices, not seconds. So end - start = number of samples in that segment, not its duration in seconds.  #If this segment has fewer than 8000 samples (i.e., is shorter than half a second), skip it — it's probably noise, a cough, or a false detection, not an actual meaningful utterance."
                continue
            # samples = seconds × sample_rate
            # 0.5 sec × 16000 samples/sec = 8000 samples
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)  
            embedding = encoder.embed_utterance(wav)
            sid, score = identify_speaker(embedding, candidates_dict,threshold)
            if sid:
                if sid not in identified_results or score>identified_results[sid]:
                    identified_results[sid]=score

        return identified_results

    except Exception as e:
        st.error("Bulk process error - " + str(e))
        return {}
