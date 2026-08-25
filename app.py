import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from langdetect import detect
import hashlib

st.set_page_config(page_title="RAM Bot v3.9 AI", page_icon="🤖", layout="centered")

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 الـ GROQ_KEY ماشي موجود")
    st.stop()

recognizer = sr.Recognizer()

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 1rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.2rem;}
.section-title {color: white; font-size: 1.5rem; font-weight: bold; margin-top: 1rem;}
.footer {text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v3.9 ⚡ AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
</div>
""", unsafe_allow_html=True)

lang_map_tts = {'ar': 'ar', 'fr': 'fr', 'en': 'en', 'es': 'es', 'de': 'de'}

def detect_language(text):
    try:
        lang = detect(text)
        if lang.startswith('ar'): return 'ar'
        if lang.startswith('fr'): return 'fr'
        return 'en'
    except:
        return 'ar'

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang_map_tts.get(lang, 'ar'))
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None

def speech_to_text(audio_bytes):
    try:
        with sr.AudioFile(audio_bytes) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language='ar-MA')
    except: return ""

def generate_image(prompt):
    with st.spinner("⚡ كنرسم..."):
        try:
            clean_prompt = prompt.replace("ولد ليا", "").strip()
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_prompt)}?width=512&height=512&nologo=true"
            response = requests.get(url, timeout=30)
            return response.content if response.status_code == 200 else f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

def get_text_messages():
    return [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages if "content" in msg and isinstance(msg["content"], str)]

def call_groq(messages):
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="meta-llama/llama-4-scout-17b-16e-instruct", # <<<<<< هذا هو الصح
            temperature=0.7,
            max_tokens=2048
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def clear_chat():
    st.session_state.messages = []
    st.session_state.chat_key += 100

if "messages" not in st.session_state: st.session_state.messages = []
if "chat_key" not in st.session_state: st.session_state.chat_key = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"])
        if "image" in msg and msg["image"]: st.image(msg["image"])
        st.markdown(msg["content"])

st.button("🗑️ مسح المحادثة", on_click=clear_chat)

prompt_text_only = st.chat_input("كتب... ولا 'ولد ليا صورة'")
if prompt_text_only:
    detected_lang = detect_language(prompt_text_only)
    if "ولد ليا" in prompt_text_only:
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                st.session_state.messages.append({"role": "assistant", "content": "تفضل الصورة", "image": image_bytes})
            else: st.error(f"خطأ: {image_bytes}")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v3.9. المطور ديالك رضا مالكي. جاوب بالعربية."}
            messages = [system_prompt] + get_text_messages()
            response, error = call_groq(messages)
            if error: st.error(f"🚨 خطأ: {error}")
            else:
                audio_response = text_to_speech(response, detected_lang)
                st.markdown(response)
                if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

st.markdown('<div class="footer">صنع بـ ❤️ بواسطة رضا مالكي</div>', unsafe_allow_html=True)
