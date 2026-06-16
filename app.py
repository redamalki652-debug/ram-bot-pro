import streamlit as st
import random
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
import io
import datetime
import requests

st.set_page_config(page_title="RAM Bot Ultra", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

# ===== بطاقة الترحيب =====
st.markdown("""
<div dir="rtl" style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    border-radius: 25px;
    color: white;
    text-align: right;
    margin-bottom: 25px;
">
    <h1 style="margin: 0;">🤖 RAM Bot Ultra v6.1</h1>
    <h3>مليار معلومة + بحث فـ النت</h3>
    <p><b>👨‍💻 المطور: رضا مالكي</b></p>
    <p>🎤 صوت + 📸 صور + 🔍 بحث + 💬 محادثة</p>
</div>
""", unsafe_allow_html=True)

KNOWLEDGE_BASE = {
    'سلام': "وعليكم السلام المعلم 👋 مرحبا بيك",
    'شكون انت': "أنا RAM Bot Ultra 🤖 عندي بحث فـ النت + ذكاء. سولني على أي حاجة!",
    'شكرا': "العفو المعلم ❤️"
}

# ===== البحث فـ النت =====
def search_internet(query):
    try:
        url = f"https://api.duckgo.com/?q={query}&format=json&no_html=1"
        r = requests.get(url, timeout=4)
        data = r.json()
        if data.get('AbstractText'):
            return data['AbstractText']
        elif data.get('Answer'):
            return data['Answer']
        return None
    except:
        return None

# ===== دالة الصوت =====
def audio_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="ar-MA")
        return text, None
    except Exception as e:
        if "ffprobe" in str(e):
            return None, "⚠️ خاص ffmpeg فـ packages.txt"
        return None, "ما فهمتش الصوت 🎤"

# ===== الرد الذكي + البحث =====
def get_smart_response(user_msg):
    msg = user_msg.lower().strip()
    
    for key, answer in KNOWLEDGE_BASE.items():
        if key in msg:
            return answer
    
    # أي سؤال فيه أرقام/تاريخ/سعر = قلب فـ النت
    search_keywords = ['شحال', 'عدد', 'تاريخ', 'متى', 'فين', 'من هو', 'كم', 'سعر', '2025', '2026', 'درجة الحرارة']
    if any(word in msg for word in search_keywords):
        with st.spinner("🔍 كنقلب ليك فـ النت..."):
            result = search_internet(user_msg)
        if result:
            return f"🔍 **على حسب البحث:**\n{result}\n\nبغيتي تفاصيل كثر؟"
    
    if 'علاش' in msg:
        return f"سؤال زوين 🤔 علاش {msg.replace('علاش', '')}؟\nكل حاجة عندها سبب. باغي 3 ديال الأسباب؟"
    
    return f"فهمتك المعلم 👌 {msg} موضوع كبير. من وجهة نظري: أي حاجة فالدنيا عندها حل. شنو رأيك نتا؟"

# ===== تهيئة المحادثة =====
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "السلام المعلم 👋 أنا RAM Bot Ultra. عندي مليار معلومة + بحث فـ النت. سولني على أي حاجة!"}]

# ===== الصوت - بلا وميض =====
audio_input = st.audio_input("🎤 هضر معايا")
if audio_input and "last_audio" not in st.session_state:
    st.session_state.last_audio = audio_input.getvalue()
    audio_bytes = st.session_state.last_audio
    
    with st.spinner("كيسمع ليك..."):
        text, error = audio_to_text(audio_bytes)
    
    if error:
        st.error(error)
    else:
        st.session_state.messages.append({"role": "user", "content": f"🎤 {text}"})
        response = get_smart_response(text)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.session_state.last_audio = None
    st.stop()

elif audio_input is None:
    st.session_state.pop("last_audio", None)

# ===== الصور =====
uploaded_file = st.file_uploader("📸 صيفط صورة", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    text = pytesseract.image_to_string(image, lang='ara+eng+fra')
    st.success(f"قريت: {text}")
    st.session_state.messages.append({"role": "assistant", "content": f"من الصورة:\n```\n{text}\n```"})
    st.rerun()

# ===== عرض المحادثة =====
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===== الكتابة =====
if prompt := st.chat_input("سولني على أي حاجة..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("كنفكر..."):
            response = get_smart_response(prompt)
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
