import streamlit as st
from groq import Groq
from io import BytesIO
from langdetect import detect
from gtts import gTTS
import time
import webrtcvad
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import collections

st.set_page_config(page_title="RAM Bot v4.2 Live", page_icon="🤖", layout="centered")

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 الـ GROQ_KEY ماشي موجود")
    st.stop()

# CSS الكورة الزرقة
st.markdown("""
<style>
.stApp {background: #000;}
.voice-ball {width: 220px; height: 220px; margin: 30px auto; background: radial-gradient(circle, #667eea, #764ba2); border-radius: 50%; box-shadow: 0 0 80px #667eea; animation: pulse 1.5s infinite;}
@keyframes pulse {0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="voice-ball"></div>', unsafe_allow_html=True)

def detect_language(text): return 'ar' if 'ا' in text else 'en'

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

class VADProcessor(AudioProcessorBase):
    def __init__(self):
        self.vad = webrtcvad.Vad(3) # 3 = حساسية عالية
        self.frames = collections.deque()
        self.speaking = False

    def recv_audio(self, frame: av.AudioFrame):
        audio_bytes = frame.to_ndarray().tobytes()
        is_speech = self.vad.is_speech(audio_bytes, 48000)
        
        if is_speech:
            self.frames.append(audio_bytes)
            self.speaking = True
        elif self.speaking: # سكت
            self.speaking = False
            if len(self.frames) > 10: # باش ما ياخدش كلمة وحدة
                audio_data = b''.join(self.frames)
                st.session_state.audio_queue.put(audio_data)
            self.frames.clear()
        return frame

if "audio_queue" not in st.session_state: st.session_state.audio_queue = queue.Queue()
if "messages" not in st.session_state: st.session_state.messages = []

webrtc_ctx = webrtc_streamer(
    key="voice",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=VADProcessor,
    media_stream_constraints={"video": False, "audio": True},
)

# المعالجة فالخلفية
if not st.session_state.audio_queue.empty():
    audio_data = st.session_state.audio_queue.get()
    with st.spinner("كنفكر..."):
        user_text = stt_groq(audio_data)
        if user_text:
            st.session_state.messages.append({"role":"user","content":user_text})
            response = call_llm([{"role":"system","content":"جاوب قصير بالدارجة"}] + st.session_state.messages)
            audio_res = tts_fast(response, 'ar')
            st.session_state.messages.append({"role":"assistant","content":response})
            st.audio(audio_res, autoplay=True)
            st.rerun()

for msg in st.session_state.messages[-4:]: # غير اخر 4 رسائل
    with st.chat_message(msg["role"]): st.write(msg["content"])
