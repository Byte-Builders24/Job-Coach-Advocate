
import streamlit as st
import openai
import assemblyai as aai
import numpy as np
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

st.title("AI Job Profile Generator")

# Input method selection
input_method = st.radio("Choose input method:", ["Text", "Audio"])

candidate_info = None

if input_method == "Text":
    candidate_info = st.text_area("Enter candidate information:", height=200)
else:
    st.write("Click start to begin recording")
    
    if 'audio_buffer' not in st.session_state:
        st.session_state.audio_buffer = []
    
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    start = st.button("Start Recording")
    stop = st.button("Stop Recording")
    
    from streamlit_webrtc import webrtc_streamer
    import av
    
    # Create placeholders for audio visualization and transcription
    audio_display = st.empty()
    transcription_container = st.container()
    transcription_text = transcription_container.empty()
    edit_text = transcription_container.empty()
    
    if 'current_transcription' not in st.session_state:
        st.session_state.current_transcription = ""

    class AudioProcessor:
        def __init__(self):
            self.text_buffer = ""
            self.transcriber = aai.Transcriber()
            self.audio_chunks = []

        def process(self, frame):
            try:
                audio_data = frame.to_ndarray()
                if audio_data.size > 0:
                    # Update audio visualization
                    amplitude = np.abs(audio_data).mean()
                    audio_display.progress(min(1.0, amplitude * 20))
                    
                    # Save audio chunk
                    self.audio_chunks.append(audio_data)
                    
                    # Every 2 seconds, transcribe accumulated audio
                    if len(self.audio_chunks) >= 20:  # Assuming 10 frames per second
                        combined_audio = np.concatenate(self.audio_chunks)
                        temp_path = Path("temp.wav")
                        combined_audio.tofile(str(temp_path))
                        
                        result = self.transcriber.transcribe(str(temp_path))
                        if result.text and result.text != self.text_buffer:
                            self.text_buffer = result.text
                            st.session_state.current_transcription = result.text
                            transcription_text.markdown(f"**Current transcription:**\n{result.text}")
                            st.session_state.candidate_info = result.text
                        
                        temp_path.unlink()
                        self.audio_chunks = []
                return frame
            except Exception as e:
                st.error(f"Error processing audio: {str(e)}")
                return frame
    
    processor = AudioProcessor()
    
    def audio_frame_callback(frame):
        return processor.process(frame)
            
    # Add editable transcription
    if st.session_state.current_transcription:
        edited_text = edit_text.text_area(
            "Edit transcription if needed:",
            value=st.session_state.current_transcription,
            key="transcript_editor"
        )
        if edited_text != st.session_state.current_transcription:
            st.session_state.candidate_info = edited_text
            
    webrtc_streamer(
        key="audio-recorder",
        audio_frame_callback=audio_frame_callback,
        frontend_rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        server_rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True},
        async_processing=True
    )
    
    if 'candidate_info' in st.session_state:
        candidate_info = st.session_state.candidate_info

if candidate_info and st.button("Generate Profile"):
    client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
    
    system_prompt = """You are a professional job profile writer. Create a structured profile with the following sections:
    1. Professional Summary
    2. Key Skills
    3. Work Experience
    4. Education
    5. Certifications (if any)
    6. Technical Skills (if applicable)
    
    Format the output in markdown."""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a structured job profile from this information: {candidate_info}"}
        ]
    )
    
    st.markdown(response.choices[0].message.content)
    
    # Add download button for the profile
    st.download_button(
        label="Download Profile",
        data=response.choices[0].message.content,
        file_name="job_profile.md",
        mime="text/markdown"
    )
