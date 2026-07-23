import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
from langdetect import detect
import numpy as np
from pydub import AudioSegment
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av

st.set_page_config(page_title="RAM Bot v4.4", page_icon="🤖", layout="centered")

try: client = Groq(api_key=st.secrets["GROQ_KEY"])
except: st.error("🚨 GROQ_KEY"); st.stop()

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);}
.card {background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 20px; text-align: center; backdrop-filter: blur(10px); color:white;}
.voice-ball {width: 200px; height: 200px; margin: 20px auto; background: radial-gradient(circle, #667eea, #764ba2); border-radius: 50%; box-shadow: 0 0 80px #667eea; animation: pulse 2s infinite;}
@keyframes pulse {0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
.mic-btn {width:70px; height:70px; border-radius:50%; background:#667eea; border:none; color:white; font-size:30px; margin:10px auto; display:block;}
.section-title {color: white; font-size: 1.2rem; font-weight: bold; text-align:center; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="card"><h1>🤖 RAM Bot v4.4 Voice + Vision</h1><p>المطور: رضا مالكي</p></div>', unsafe_allow_html=True)

def detect_language(text): 
    try: return 'ar' if detect(text).startswith('ar') else 'en'
    except: return 'ar'

def encode_image(image): return base64.b64encode(image.getvalue()).decode('utf-8')

def tts_fast(text, lang):
    try: return BytesIO(client.audio.speech.create(model="playai-tts", voice="Arman", input=text, response_format="wav").read())
    except: fp=BytesIO(); gTTS(text, lang='ar').write_to_fp(fp); fp.seek(0); return fp

def stt_groq(audio_bytes):
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
    audio_seg = AudioSegment(audio_array.tobytes(), frame_rate=48000, sample_width=2, channels=1)
    wav_io = BytesIO(); audio_seg.export(wav_io, format="wav"); wav_io.seek(0)
    res = client.audio.transcriptions.create(file=("audio.wav", wav_io.read()), model="whisper-large-v3-turbo", language="ar")
    return res.text

def call_groq(messages):
    return client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", max_tokens=200).choices[0].message.content

def generate_image(prompt):
    with st.spinner("كنرسم..."):
        clean_prompt = prompt.replace("ولد ليا", "").strip()
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_prompt)}?width=512&height=512"
        return requests.get(url, timeout=30).content

class AudioProcessor(AudioProcessorBase):
    def __init__(self): self.audio_buffer = BytesIO()
    def recv_audio(self, frame: av.AudioFrame):
        if st.session_state.recording: self.audio_buffer.write(frame.to_ndarray().tobytes())
        return frame

def clear_chat():
    st.session_state.messages = []; st.session_state.uploaded_image = None; st.session_state.uploader_key += 1

if "messages" not in st.session_state: st.session_state.messages = []
if "recording" not in st.session_state: st.session_state.recording = False
if "uploaded_image" not in st.session_state: st.session_state.uploaded_image = None
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"], autoplay=(msg["role"]=="assistant"))
        if "image" in msg and msg["image"]: st.image(msg["image"])
        st.markdown(msg["content"])

st.markdown('<div class="voice-ball"></div>', unsafe_allow_html=True)
st.markdown('<p class="section-title">🎤 المحادثة الصوتية</p>', unsafe_allow_html=True)

webrtc_ctx = webrtc_streamer(key="voice", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor, media_stream_constraints={"video": False, "audio": True})

# ايقونة المايك المدورة بحال واتساب
if st.button("🎤", key="mic", help="ورك باش تهضر"):
    if not st.session_state.recording:
        st.session_state.recording = True
        st.rerun()
    else:
        st.session_state.recording = False
        processor = webrtc_ctx.audio_processor
        if processor and processor.audio_buffer.getbuffer().nbytes > 1000:
            with st.spinner("كنسمعك..."):
                user_text = stt_groq(processor.audio_buffer.getvalue())
                if user_text:
                    st.session_state.messages.append({"role":"user","content":user_text})
                    response = call_groq([{"role":"system","content":"نتا RAM Bot. جاوب قصير بالدارجة"}] + st.session_state.messages)
                    audio_res = tts_fast(response, 'ar')
                    st.session_state.messages.append({"role":"assistant","content":response, "audio":audio_res})
                processor.audio_buffer = BytesIO()
        st.rerun()

st.button("🗑️ مسح المحادثة", on_click=clear_chat)

st.markdown('<p class="section-title">📸 سؤال بالصورة</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("رفع صورة", type=["png","jpg"], key=f"uploader_{st.session_state.uploader_key}")
if uploaded_file: st.session_state.uploaded_image = uploaded_file; st.image(uploaded_file, width=200)

prompt_img = st.chat_input("سول على الصورة...")
if prompt_img and st.session_state.uploaded_image:
    image_b64 = encode_image(st.session_state.uploaded_image)
    messages = [{"role":"system","content":"جاوب على الصورة"}] + st.session_state.messages + [{"role":"user","content":[{"type":"text","text":prompt_img},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{image_b64}"}}]}]
    response = call_groq(messages)
    st.session_state.messages.append({"role":"user","content":prompt_img})
    st.session_state.messages.append({"role":"assistant","content":response})
    st.rerun()

prompt_gen = st.chat_input("كتب 'ولد ليا صورة'...")
if prompt_gen and "ولد ليا" in prompt_gen:
    st.session_state.messages.append({"role":"user","content":prompt_gen})
    img_bytes = generate_image(prompt_gen)
    st.session_state.messages.append({"role":"assistant","content":"تفضل الصورة", "image":img_bytes})
    st.rerun()
