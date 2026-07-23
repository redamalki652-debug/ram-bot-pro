import streamlit as st
from groq import Groq
from gtts import gTTS
from io import BytesIO
from langdetect import detect
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="RAM Bot v5.0", page_icon="🤖")

try: client = Groq(api_key=st.secrets["GROQ_KEY"])
except: st.error("🚨 GROQ_KEY"); st.stop()

st.markdown("""
<style>
.stApp {background: #0e1117;}
.card {background: #262730; padding: 1rem; border-radius: 15px; text-align: center; color:white;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="card"><h2>🤖 RAM Bot v5.0</h2><p>ورك على المايك و هضر</p></div>', unsafe_allow_html=True)

def detect_language(text): 
    try: return 'ar' if detect(text).startswith('ar') else 'en'
    except: return 'ar'

def tts_fast(text):
    try: return BytesIO(client.audio.speech.create(model="playai-tts", voice="Arman", input=text, response_format="wav").read())
    except: fp=BytesIO(); gTTS(text, lang='ar').write_to_fp(fp); fp.seek(0); return fp

def stt_groq(audio_bytes):
    try:
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        res = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3-turbo", language="ar")
        return res.text
    except Exception as e: 
        st.error(f"خطأ: {e}")
        return ""

def call_groq(messages):
    res = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", max_tokens=80)
    return res.choices[0].message.content

def clear_chat(): st.session_state.messages = []

if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages[-6:]:
    with st.chat_message(msg["role"]):
        if "audio" in msg: st.audio(msg["audio"], autoplay=(msg["role"]=="assistant"))
        st.markdown(msg["content"])

# هادي هي اللي غادي تعوض webrtc
audio = mic_recorder(start_prompt="🎤 بدا الهضرة", stop_prompt="✅ سيفط", key='recorder')

if audio:
    with st.spinner("كنسمعك..."):
        user_text = stt_groq(audio['bytes'])
        if user_text:
            st.session_state.messages.append({"role":"user","content":user_text})
            system = {"role":"system","content":"نتا RAM Bot ديال رضا. جاوب بجملة وحدة قصيرة بالدارجة المغربية"}
            response = call_groq([system] + st.session_state.messages)
            audio_res = tts_fast(response)
            st.session_state.messages.append({"role":"assistant","content":response, "audio":audio_res})
            st.rerun()

st.button("🗑️ مسح المحادثة", on_click=clear_chat)
