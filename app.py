import streamlit as st
from streamlit_mic_recorder import mic_recorder
from gradio_client import Client, handle_file

# Initialize the Gradio Client
client = Client("mrfakename/E2-F5-TTS")

# Set page configuration
st.set_page_config(page_title="Voice Cloning App", layout="centered", initial_sidebar_state="expanded")

# Initialize session state for audio inputs
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "audio_source" not in st.session_state:
    st.session_state.audio_source = None
if "uploaded_audio" not in st.session_state:
    st.session_state.uploaded_audio = None

# App Header
st.title("🎙️ Voice Cloning App")
st.write("Clone a voice by providing a reference audio and text, and generate new speech in the cloned voice!")

# Sidebar for parameters
st.sidebar.header("Voice Cloning Parameters")
remove_silence = st.sidebar.radio("Remove Silence", options=[True, False], index=1)
cross_fade_duration = st.sidebar.slider("Cross-Fade Duration (s)", min_value=0.0, max_value=1.0, value=0.15, step=0.01)
speed = st.sidebar.slider("Speed Multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

# Audio Input Section
st.subheader("1️⃣ Provide Reference Audio")
col1, col2 = st.columns(2)

with col1:
    st.write("### Upload Audio")
    uploaded_audio = st.file_uploader("Upload Reference Audio File:", type=["wav", "mp3", "m4a"])
    if uploaded_audio:
        st.session_state.audio_source = "upload"
        st.session_state.audio_bytes = uploaded_audio.read()
        st.session_state.uploaded_audio = uploaded_audio.name
        st.audio(st.session_state.audio_bytes, format="audio/wav")

with col2:
    st.write("### Record Audio")
    recording = mic_recorder(
        start_prompt="🎙️ Start Recording",
        stop_prompt="🛑 Stop Recording",
        just_once=False,
        use_container_width=False
    )
    if recording["bytes"]:
        st.session_state.audio_source = "record"
        st.session_state.audio_bytes = recording["bytes"]
        st.session_state.uploaded_audio = None
        st.audio(st.session_state.audio_bytes, format="audio/wav")

# Ensure audio source selection is clear
if not st.session_state.audio_bytes:
    st.warning("Please upload or record audio to proceed.")

# Text Input Section
st.subheader("2️⃣ Provide Reference Text and Text to Generate")
ref_text = st.text_input("Enter Reference Text:", value="Hello, this is my voice reference!")
gen_text = st.text_area("Enter Text to Generate Speech:", value="This is the text I want to generate in the cloned voice.")

# Voice cloning process
if st.button("🔄 Clone Voice"):
    if st.session_state.audio_bytes and ref_text and gen_text:
        st.write("⏳ Cloning voice, please wait...")

        # Save audio bytes temporarily based on input type
        temp_file_name = "temp_audio.wav"
        with open(temp_file_name, "wb") as f:
            f.write(st.session_state.audio_bytes)

        # Call the Gradio API
        result = client.predict(
            ref_audio_input=handle_file(temp_file_name),
            ref_text_input=ref_text,
            gen_text_input=gen_text,
            remove_silence=remove_silence,
            cross_fade_duration_slider=cross_fade_duration,
            speed_slider=speed,
            api_name="/basic_tts"
        )

        # Display results
        synthesized_audio_path = result[0]
        st.subheader("3️⃣ Synthesized Audio")
        st.audio(synthesized_audio_path, format="audio/wav")

        # Download button
        with open(synthesized_audio_path, "rb") as file:
            st.download_button(
                label="📥 Download Synthesized Audio",
                data=file,
                file_name="synthesized_audio.wav",
                mime="audio/wav"
            )
    else:
        st.error("Please provide all required inputs (audio, reference text, and generation text).")

# Footer
st.markdown("---")
st.markdown("🚀 Powered by Streamlit, Gradio, and Hugging Face")
