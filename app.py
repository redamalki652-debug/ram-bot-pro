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
    st.error("🚨 الـ GROQ_KEY ماشي موجود. مشي للـ Settings > Secrets")
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
        if lang.startswith('es'): return 'es'
        if lang.startswith('de'): return 'de'
        return 'en'
    except:
        return 'ar'

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang_map_tts.get(lang, 'ar'), slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

def speech_to_text(audio_bytes):
    try:
        with sr.AudioFile(audio_bytes) as source:
            audio = recognizer.record(source)
        for l in ['ar-MA', 'fr-FR', 'en-US']:
            try:
                return recognizer.recognize_google(audio, language=l)
            except: continue
        return ""
    except: return ""

def generate_image(prompt):
    with st.spinner("⚡ كنرسم فـ 3 ثواني..."):
        try:
            clean_prompt = prompt.replace("ولد ليا", "").strip()
            encoded_prompt = urllib.parse.quote(clean_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
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
            model="gemma2-9b-it", # <<<<<< الموديل الجديد اللي خدام
            temperature=0.7,
            max_tokens=2048
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def clear_chat():
    st.session_state.messages = []
    st.session_state.uploaded_image = None
    st.session_state.uploader_key += 1
    st.session_state.chat_key += 100
    st.session_state.last_image = None
    st.session_state.last_audio_hash = None

if "messages" not in st.session_state: st.session_state.messages = []
if "uploaded_image" not in st.session_state: st.session_state.uploaded_image = None
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
if "chat_key" not in st.session_state: st.session_state.chat_key = 0
if "last_image" not in st.session_state: st.session_state.last_image = None
if "last_audio_hash" not in st.session_state: st.session_state.last_audio_hash = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"], autoplay=False)
        if "image" in msg and msg["image"]:
            st.image(msg["image"])
            st.session_state.last_image = msg["image"]
        st.markdown(msg["content"])

st.markdown('<p class="section-title">📸❓ سؤال بالصورة</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key=f"uploader_{st.session_state.uploader_key}")

st.markdown('<p class="section-title">🎤 هضر</p>', unsafe_allow_html=True)
audio_value = st.audio_input(" ", label_visibility="collapsed", key=f"audio_{st.session_state.chat_key}")

if audio_value:
    audio_hash = hashlib.md5(audio_value.getvalue()).hexdigest()
    if audio_hash!= st.session_state.last_audio_hash:
        st.session_state.last_audio_hash = audio_hash
        with st.spinner("كنسمعك..."):
            user_text = speech_to_text(audio_value)
            if user_text:
                detected_lang = detect_language(user_text)
                st.session_state.messages.append({"role": "user", "content": user_text})
                system_prompt = {"role": "system", "content": "نتا RAM Bot v3.9. المطور ديالك رضا مالكي. كتشف اللغة و جاوب بنفسها."}
                messages = [system_prompt] + get_text_messages()
                response, error = call_groq(messages)
                if error: st.error(f"🚨 خطأ: {error}")
                else:
                    audio_response = text_to_speech(response, detected_lang)
                    with st.chat_message("assistant"):
                        st.markdown(response)
                        if audio_response: st.audio(audio_response, autoplay=False)
                    st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

st.button("🗑️ مسح المحادثة", on_click=clear_chat, key=f"clear_{st.session_state.chat_key}")

prompt_text_only = st.chat_input("كتب... ولا 'ولد ليا صورة'", key=f"chat_main_{st.session_state.chat_key}")
if prompt_text_only:
    detected_lang = detect_language(prompt_text_only)
    if "ولد ليا" in prompt_text_only:
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                st.session_state.last_image = image_bytes
                st.session_state.messages.append({"role": "assistant", "content": "تفضل الصورة", "image": image_bytes})
            else: st.error(f"خطأ: {image_bytes}")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v3.9. كتشف اللغة و جاوب بنفسها."}
            messages = [system_prompt] + get_text_messages()
            response, error = call_groq(messages)
            if error: st.error(f"🚨 خطأ: {error}")
            else:
                audio_response = text_to_speech(response, detected_lang)
                st.markdown(response)
                if audio_response: st.audio(audio_response, autoplay=False)
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

st.markdown('<div class="footer">صنع بـ ❤️ بواسطة رضا مالكي</div>', unsafe_allow_html=True)
