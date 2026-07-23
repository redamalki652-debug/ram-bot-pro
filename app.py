import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
from langdetect import detect
import io
import queue
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av

st.set_page_config(page_title="RAM Bot v4.9", page_icon="🤖")

try: client = Groq(api_key=st.secrets["GROQ_KEY"])
except: st.error("🚨 GROQ_KEY ماشي موجود فـ Secrets"); st.stop()

st.markdown("""
<style>
.stApp {background: #0e1117;}
.card {background: #262730; padding: 1rem; border-radius: 15px; text-align: center; color:white; margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="card"><h2>🤖 RAM Bot v4.9 Voice</h2><p>ورك "بدا" مرة وحدة و هضر</p></div>', unsafe_allow_html=True)

def detect_language(text): 
    try: return 'ar' if detect(text).startswith('ar') else 'en'
    except: return 'ar'

def tts_fast(text):
    try: return BytesIO(client.audio.speech.create(model="playai-tts", voice="Arman", input=text, response_format="wav").read())
    except: fp=BytesIO(); gTTS(text, lang='ar').write_to_fp(fp); fp.seek(0); return fp

def stt_groq(audio_bytes):
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.webm"
        res = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3-turbo", language="ar")
        return res.text
    except Exception as e: 
        st.error(f"خطأ STT: {e}")
        return ""

def call_groq(messages):
    res = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", max_tokens=80, temperature=0.7)
    return res.choices[0].message.content

class AudioProcessor(AudioProcessorBase):
    def __init__(self): 
        self.audio_buffer = BytesIO()
        self.last_send = time.time()
    
    def recv_audio(self, frame: av.AudioFrame):
        if time.time() - self.last_send > 2.5:
            self.last_send = time.time()
            if self.audio_buffer.getbuffer().nbytes > 8000:
                st.session_state.audio_q.put(self.audio_buffer.getvalue())
            self.audio_buffer = BytesIO()
        self.audio_buffer.write(frame.to_ndarray().tobytes())
        return frame

def clear_chat(): 
    st.session_state.messages = []

if "messages" not in st.session_state: st.session_state.messages = []
if "audio_q" not in st.session_state: st.session_state.audio_q = queue.Queue()
if "is_bot_speaking" not in st.session_state: st.session_state.is_bot_speaking = False

for msg in st.session_state.messages[-6:]:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"], autoplay=(msg["role"]=="assistant"))
        st.markdown(msg["content"])

# حيدنا auto_start حيت كيدير مشكل
webrtc_ctx = webrtc_streamer(key="voice", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor, media_stream_constraints={"video": False, "audio": True})

if not st.session_state.audio_q.empty() and not st.session_state.is_bot_speaking:
    audio_data = st.session_state.audio_q.get()
    with st.spinner("كنفكر..."):
        st.session_state.is_bot_speaking = True
        user_text = stt_groq(audio_data)
        if user_text and len(user_text) > 2:
            st.session_state.messages.append({"role":"user","content":user_text})
            system = {"role":"system","content":"نتا RAM Bot ديال رضا. جاوب بجملة وحدة قصيرة جدا بالدارجة المغربية. ممنوع تقول نبداو ولا واش"}
            response = call_groq([system] + st.session_state.messages)
            audio_res = tts_fast(response)
            st.session_state.messages.append({"role":"assistant","content":response, "audio":audio_res})
        st.session_state.is_bot_speaking = False
        st.rerun()

st.button("🗑️ مسح المحادثة", on_click=clear_chat)
