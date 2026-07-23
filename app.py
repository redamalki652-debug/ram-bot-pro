import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
import hashlib
from langdetect import detect
from pydub import AudioSegment
import time
import queue
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av

st.set_page_config(page_title="RAM Bot v4.1 Live", page_icon="🤖", layout="centered")

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 الـ GROQ_KEY ماشي موجود. مشي للـ Settings > Secrets")
    st.stop()

# CSS ديال الكورة الزرقة بحال ChatGPT
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);}
.card {background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 20px; margin-bottom: 1rem; text-align: center; backdrop-filter: blur(10px);}
.card h1 {color: white; margin: 0; font-size: 2rem;}
.voice-ball {
    width: 220px; height: 220px; margin: 30px auto;
    background: radial-gradient(circle at 30% 30%, #a0c4ff, #667eea 70%);
    border-radius: 50%;
    box-shadow: 0 0 60px rgba(102, 126, 234, 0.6);
    animation: pulse 2s infinite ease-in-out;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.08); }
}
.section-title {color: white; font-size: 1.2rem; font-weight: bold; text-align:center;}
.footer {text-align: center; color: #aaa; font-size: 1rem; margin: 1rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v4.1 ⚡ Live Voice</h1>
    <p style="color:#ccc"><b>المطور:</b> رضا مالكي</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="voice-ball"></div>', unsafe_allow_html=True)

lang_map_tts = {'ar': 'ar', 'fr': 'fr', 'en': 'en', 'es': 'es', 'de': 'de'}

def detect_language(text):
    try:
        lang = detect(text)
        if lang.startswith('ar'): return 'ar'
        if lang.startswith('fr'): return 'fr'
        return 'en'
    except: return 'ar'

def text_to_speech_fast(text, lang):
    try:
        voice = "Arman" if lang == "ar" else "Celeste"
        response = client.audio.speech.create(model="playai-tts", voice=voice, input=text, response_format="wav")
        return BytesIO(response.read())
    except:
        tts = gTTS(text=text, lang=lang_map_tts.get(lang, 'ar'))
        fp = BytesIO(); tts.write_to_fp(fp); fp.seek(0); return fp

def speech_to_text_groq(audio_bytes):
    try:
        audio = AudioSegment.from_file(audio_bytes)
        wav_io = BytesIO(); audio.export(wav_io, format="wav"); wav_io.seek(0)
        transcription = client.audio.transcriptions.create(file=("audio.wav", wav_io.read()), model="whisper-large-v3-turbo")
        return transcription.text
    except: return ""

def call_groq(messages):
    try:
        chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=200)
        return chat_completion.choices[0].message.content, None
    except Exception as e: return None, str(e)

def get_text_messages():
    return [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages if "content" in msg]

def process_audio(audio_bytes):
    if st.session_state.is_bot_speaking: return # ما نسمعش ملي البوت كيهضر

    user_text = speech_to_text_groq(audio_bytes)
    if user_text and len(user_text) > 2:
        detected_lang = detect_language(user_text)
        st.session_state.messages.append({"role": "user", "content": user_text})

        system_prompt = {"role": "system", "content": f"نتا RAM Bot v4.1. كتهضر فمكالمة. جاوب قصير جدا 1-2 جمل باللغة: {detected_lang}"}
        messages = [system_prompt] + get_text_messages()
        response, error = call_groq(messages)

        if not error:
            st.session_state.is_bot_speaking = True
            audio_response = text_to_speech_fast(response, detected_lang)
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
            st.session_state.last_audio = audio_response
            st.session_state.is_bot_speaking = False
            st.rerun()

class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.audio_buffer = BytesIO()

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        # كنخزنو الصوت
        if st.session_state.is_recording:
            self.audio_buffer.write(audio.tobytes())
        return frame

if "messages" not in st.session_state: st.session_state.messages = []
if "is_bot_speaking" not in st.session_state: st.session_state.is_bot_speaking = False
if "is_recording" not in st.session_state: st.session_state.is_recording = False
if "last_audio" not in st.session_state: st.session_state.last_audio = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"], autoplay=(msg["role"]=="assistant"))
        st.markdown(msg["content"])

if st.session_state.last_audio:
    st.audio(st.session_state.last_audio, autoplay=True)
    st.session_state.last_audio = None

st.markdown('<p class="section-title">هضر دابا... أنا كنسمعك</p>', unsafe_allow_html=True)

webrtc_ctx = webrtc_streamer(
    key="voice-call",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
    async_processing=True,
)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎤 بدا المكالمة"):
        st.session_state.is_recording = True
with col2:
    if st.button("🛑 وقف"):
        st.session_state.is_recording = False

# إلا كان كيسجل و تسد المايك نعالجو
if not webrtc_ctx.state.playing and st.session_state.is_recording:
    processor = webrtc_ctx.audio_processor
    if processor and processor.audio_buffer.getbuffer().nbytes > 0:
        process_audio(processor.audio_buffer)
        processor.audio_buffer = BytesIO() # نفرغوه

st.markdown('<div class="footer">صنع بـ ❤️ بواسطة رضا مالكي</div>', unsafe_allow_html=True)
