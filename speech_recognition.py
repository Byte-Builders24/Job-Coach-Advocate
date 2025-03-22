import os
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
from resume_service import generate_resume
from embedding_service import generate_embedding, store_embedding
from azure_blob_storage import AzureBlobStorage
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from search_service import search_candidates

# result_data = search_candidates(query_text="Who makes a good engineer??")
# # Show answers
# for ans in result_data["semantic_answers"]:
#     print(f"Semantic Answer (score={ans['score']}): {ans['highlights'] or ans['text']}")

# # Show documents
# for doc in result_data["documents"]:
#     print(doc["id"], doc["reranker_score"], doc["content"][:100], doc["caption"])

# Instantiate AzureBlobStorage

blob_storage = AzureBlobStorage()

def recognize_from_microphone():
    """
    1. Listen to speech for candidate info.
    2. Translate/detect language to English (existing behavior, left unchanged).
    """
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get('SPEECH_KEY'),
        region=os.environ.get('SPEECH_REGION')
    )
    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    st.write("Speak into your microphone.")
    st.info("Listening...")

    # Perform speech recognition asynchronously and wait for the result
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    # Check the result of the speech recognition
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        st.session_state.recognized_text = speech_recognition_result.text
        st.success("Recognized Speech:")
        st.write(st.session_state.recognized_text)
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        st.error("No speech could be recognized.")
        st.write(speech_recognition_result.no_match_details)
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        st.error("Speech Recognition canceled.")
        st.write(f"Reason: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            st.error("Error details:")
            st.write(cancellation_details.error_details)
            st.warning("Did you set the speech resource key and region values?")

# Streamlit UI
st.markdown(
    """
    <style>
    .header-title {
        font-size: 2.5rem;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="header-title">Job Coach AI Speech Recognition & Resume Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Transform your client’s spoken words into a professional resume effortlessly, then embed it for future searches.</div>', unsafe_allow_html=True)

st.title("Speech Recognition and Resume Generator")

# Option 1: Manually enter candidate info
st.write("### Option 1: Enter Candidate Information Manually")
manual_text = st.text_area(
    "Enter candidate information (e.g. career stories, achievements, and contact details):",
    height=200,
    key="manual_text",
    placeholder="Ensure to ask for contact info and general career stories no matter how 'small'."
)

# Option 2: Use Speech Recognition
st.write("### Option 2: Use Speech Recognition")
if st.button("Start Speech Recognition"):
    recognize_from_microphone()

# Always show email and phone inputs, with default fallback
st.write("### Candidate Contact Info (Optional)")
email = st.text_input("Email address:", value="jobcoach@resume.com", key="email_input")
phone = st.text_input("Phone number:", value="12345678", key="phone_input")

# Button to generate resume
if st.button("Generate Resume", key="generate_resume_button"):
    input_text = st.session_state.get("recognized_text", "") or st.session_state.get("manual_text", "")
    if not input_text:
        st.error("No input text found. Please perform speech recognition or enter text manually.")
    else:
        try:
            # Generate the resume
            resume_text = generate_resume(input_text, email=email, phone=phone)

            if resume_text.strip():
                # 1. Store the plain-text resume in Blob Storage
                blob_storage.store_resume(email, resume_text)

                # 2. Generate and store the embedding for future searches
                embedding = generate_embedding(resume_text)
                store_embedding(email=email, embedding=embedding, resume_url="")

            st.session_state.generated_resume = resume_text
            st.success("Resume Generated Successfully!")
        except Exception as e:
            st.error(f"Failed to generate resume: {e}")

# Display the generated resume if it exists
if "generated_resume" in st.session_state:
    st.write("### Generated Resume")
    edited_resume = st.text_area(
        "Edit the Generated Resume",
        st.session_state.generated_resume,
        height=300,
        key="edited_resume"
    )

    st.download_button(
        label="Download Edited Resume",
        data=edited_resume,
        file_name="edited_resume.txt",
        mime="text/plain"
    )

    