import os
import azure.cognitiveservices.speech as speechsdk
import streamlit as st
import requests
from azure_blob_storage import AzureBlobStorage

# Initialize Azure Blob Storage
blob_storage = AzureBlobStorage()

def recognize_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
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
        # Store the recognized text in session state
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

def generate_resume():
    # Check if recognized_text or manually entered text exists
    input_text = st.session_state.get("recognized_text", "") or st.session_state.get("manual_text", "")
    if not input_text:
        st.error("No input text found. Please perform speech recognition or enter text manually.")
        return

    # Collect additional candidate information
    email = st.session_state.get("email", "")
    phone = st.session_state.get("phone", "")

    # Append additional information to the input text
    additional_info = f"""
    Candidate Contact Information:
    - Email: {email}
    - Phone: {phone}
    """
    input_text += "\n\n" + additional_info

    # Azure OpenAI API endpoint, key, and deployment name
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")  # Deployment name

    # Validate environment variables
    if not endpoint or not api_key or not deployment_name:
        st.error("Azure OpenAI environment variables are not set correctly.")
        return

    # Define the prompt for generating a resume
    prompt = f"""
    You are a professional resume writer and Job Coach. Based on the following input, create a structured resume in plain text format:
    
    Input: {input_text}
    
    Resume Format:
    - Name:
    - Professional Summary:
    - Key Skills:
    - Work Experience:
    - Education:
    - Certifications:
    - Technical Skills:
    """

    # Azure OpenAI API request
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": prompt}
        ],
        "model": deployment_name,  # Use deployment name here
        "temperature": 0.7
    }

    # Construct the full API URL
    api_url = f"{endpoint}openai/deployments/{deployment_name}/chat/completions?api-version=2025-01-01-preview"

    response = requests.post(
        api_url,
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        # Extract the generated resume
        resume_text = response.json()["choices"][0]["message"]["content"]
        st.session_state.generated_resume = resume_text  # Store the generated resume in session state
        st.success("Resume Generated Successfully!")

        # Upload the resume to Azure Blob Storage
        try:
            container_name = "resumes"
            file_name = f"resume_{st.session_state.get('email', 'unknown')}.txt"
            upload_message = blob_storage.upload_resume(container_name, file_name, resume_text)
            st.info(upload_message)
        except Exception as e:
            st.error(f"Failed to upload resume to Azure Blob Storage: {e}")
    else:
        st.error("Failed to generate resume.")
        st.write(f"Error: {response.status_code} - {response.text}")

# Streamlit app with a descriptive header
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
st.markdown('<div class="header-subtitle">Transform your clients spoken words into a professional resume effortlessly to empower them for their next role /br be sure to followup with each one for check-ins every 3-6 months to offer support.</div>', unsafe_allow_html=True)

st.title("Speech Recognition and Resume Generator")

# Option to manually enter text
st.write("### Option 1: Enter Candidate Information Manually")
manual_text = st.text_area(
    "Enter candidate information (e.g., career stories, achievements, and contact details):",
    height=200,
    key="manual_text",
    placeholder="Ensure to ask for contact info and general career stories no matter how 'small'."
)

# Option to use speech recognition
st.write("### Option 2: Use Speech Recognition")
if st.button("Start Speech Recognition"):
    recognize_from_microphone()

# Button to generate resume
if st.button("Generate Resume"):
    generate_resume()

# Display the generated resume if it exists
if "generated_resume" in st.session_state:
    st.write("### Generated Resume")
    edited_resume = st.text_area("Edit the Generated Resume", st.session_state.generated_resume, height=300, key="edited_resume")

    # Add a download button for the edited resume
    st.download_button(
        label="Download Edited Resume",
        data=edited_resume,
        file_name="edited_resume.txt",
        mime="text/plain"
    )