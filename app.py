import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
from langdetect import detect
import io
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av

st.set_page_config(page_title="RAM Bot v4.5", page_icon="🤖")

try: client = Groq(api_key=st.secrets["GROQ_KEY"])
except: st.error("🚨 GROQ_KEY"); st.stop()

st.markdown("""<style>.stApp{background:#000}.card{background:rgba(255,255,255,0.05);padding:1.5rem;border-radius:20px;text-align:center;color:white}.voice-ball{width:200px;height:200px;margin:20px auto;background:radial-gradient(circle,#667eea,#764ba2);border-radius:50%;box-shadow:0 0 80px #667eea;animation:pulse 2s infinite}@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}</style>""",unsafe_allow_html=True)
st.markdown('<div class="card"><h1>🤖 RAM Bot v4.5 Voice + Vision</h1></div><div class="voice-ball"></div>', unsafe_allow_html=True)

def detect_language(text): 
    try: return 'ar' if detect(text).startswith('ar') else 'en'
    except: return 'ar'

def encode_image(image): return base64.b64encode(image.getvalue()).decode('utf-8')

def tts_fast(text):
    return BytesIO(client.audio.speech.create(model="playai-tts", voice="Arman", input=text, response_format="wav").read())

def stt_groq(audio_bytes):
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.webm"
    res = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3-turbo", language="ar")
    return res.text

def call_groq(messages):
    return client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", max_tokens=200).choices[0].message.content

def generate_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt.replace('ولد ليا',''))}?width=512&height=512"
    return requests.get(url, timeout=30).content

class AudioProcessor(AudioProcessorBase):
    def __init__(self): self.audio_buffer = BytesIO()
    def recv_audio(self, frame: av.AudioFrame):
        if st.session_state.recording: self.audio_buffer.write(frame.to_ndarray().tobytes())
        return frame

def clear_chat(): st.session_state.messages = []; st.session_state.uploader_key += 1

if "messages" not in st.session_state: st.session_state.messages = []
if "recording" not in st.session_state: st.session_state.recording = False
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg: st.audio(msg["audio"], autoplay=(msg["role"]=="assistant"))
        if "image" in msg: st.image(msg["image"])
        st.markdown(msg["content"])

webrtc_ctx = webrtc_streamer(key="voice", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor, media_stream_constraints={"video": False, "audio": True})

if st.button("🎤 بدا/وقف الهضرة"):
    st.session_state.recording = not st.session_state.recording
    if not st.session_state.recording:
        processor = webrtc_ctx.audio_processor
        if processor and processor.audio_buffer.getbuffer().nbytes > 1000:
            with st.spinner("كنسمعك..."):
                user_text = stt_groq(processor.audio_buffer.getvalue())
                if user_text:
                    st.session_state.messages.append({"role":"user","content":user_text})
                    response = call_groq([{"role":"system","content":"نتا RAM Bot. جاوب قصير بالدارجة"}] + st.session_state.messages)
                    audio_res = tts_fast(response)
                    st.session_state.messages.append({"role":"assistant","content":response, "audio":audio_res})
                processor.audio_buffer = BytesIO()
    st.rerun()

st.button("🗑️ مسح", on_click=clear_chat)

uploaded_file = st.file_uploader("📸 رفع صورة", type=["png","jpg"], key=f"uploader_{st.session_state.uploader_key}")
prompt_img = st.chat_input("سول على الصورة...")
if prompt_img and uploaded_file:
    image_b64 = encode_image(uploaded_file)
    messages = [{"role":"system","content":"جاوب على الصورة"}] + st.session_state.messages + [{"role":"user","content":[{"type":"text","text":prompt_img},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{image_b64}"}}]}]
    response = call_groq(messages)
    st.session_state.messages.append({"role":"user","content":prompt_img})
    st.session_state.messages.append({"role":"assistant","content":response})
    st.rerun()

prompt_gen = st.chat_input("ولد ليا صورة...")
if prompt_gen and "ولد ليا" in prompt_gen:
    img_bytes = generate_image(prompt_gen)
    st.session_state.messages.append({"role":"user","content":prompt_gen})
    st.session_state.messages.append({"role":"assistant","content":"تفضل", "image":img_bytes})
    st.rerun()
