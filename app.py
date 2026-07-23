import streamlit as st
from groq import Groq
from io import BytesIO
from langdetect import detect
from gtts import gTTS
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import queue

st.set_page_config(page_title="RAM Bot v4.2 Live", page_icon="🤖", layout="centered")

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 الـ GROQ_KEY ماشي موجود")
    st.stop()

# CSS الكورة الزرقة بحال ChatGPT
st.markdown("""
<style>
.stApp {background: #000;}
.card {text-align:center; color:white;}
.voice-ball {width: 220px; height: 220px; margin: 30px auto; background: radial-gradient(circle at 30% 30%, #a0c4ff, #667eea); border-radius: 50%; box-shadow: 0 0 80px #667eea; animation: pulse 2s infinite;}
@keyframes pulse {0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="card"><h1>🤖 RAM Bot v4.2 Voice</h1></div>', unsafe_allow_html=True)
st.markdown('<div class="voice-ball"></div>', unsafe_allow_html=True)

def detect_language(text): 
    try: return 'ar' if detect(text).startswith('ar') else 'en'
    except: return 'ar'

def tts_fast(text, lang):
    try:
        res = client.audio.speech.create(model="playai-tts", voice="Arman", input=text, response_format="wav")
        return BytesIO(res.read())
    except:
        fp = BytesIO(); gTTS(text, lang='ar').write_to_fp(fp); fp.seek(0); return fp

def stt_groq(audio_bytes):
    res = client.audio.transcriptions.create(file=("audio.webm", audio_bytes), model="whisper-large-v3-turbo")
    return res.text

def call_llm(messages):
    res = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", max_tokens=150)
    return res.choices[0].message.content

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = BytesIO()
    def recv_audio(self, frame: av.AudioFrame):
        if st.session_state.recording:
            self.audio_buffer.write(frame.to_ndarray().tobytes())
        return frame

if "audio_q" not in st.session_state: st.session_state.audio_q = queue.Queue()
if "messages" not in st.session_state: st.session_state.messages = []
if "recording" not in st.session_state: st.session_state.recording = False

webrtc_ctx = webrtc_streamer(key="voice", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor, media_stream_constraints={"video": False, "audio": True})

col1, col2 = st.columns(2)
with col1:
    if st.button("🎤 بدا الهضرة"): st.session_state.recording = True
with col2:
    if st.button("✅ سيفط"): 
        st.session_state.recording = False
        processor = webrtc_ctx.audio_processor
        if processor: st.session_state.audio_q.put(processor.audio_buffer.getvalue())

# المعالجة
if not st.session_state.audio_q.empty():
    audio_data = st.session_state.audio_q.get()
    with st.spinner("كنفكر..."):
        user_text = stt_groq(BytesIO(audio_data))
        if user_text:
            st.session_state.messages.append({"role":"user","content":user_text})
            response = call_llm([{"role":"system","content":"نتا RAM Bot. جاوب قصير جدا بالدارجة المغربية"}] + st.session_state.messages)
            audio_res = tts_fast(response, 'ar')
            st.session_state.messages.append({"role":"assistant","content":response})
            st.audio(audio_res, autoplay=True)
            st.rerun()

for msg in st.session_state.messages[-4:]:
    with st.chat_message(msg["role"]): st.write(msg["content"])
