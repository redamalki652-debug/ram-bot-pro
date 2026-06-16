import streamlit as st
import random
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
import io
import datetime
from duckduckgo_search import DDGS

st.set_page_config(page_title="RAM Bot Ultra", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<div dir="rtl" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 25px; color: white; text-align: right; margin-bottom: 25px;">
    <h1>🤖 RAM Bot Ultra v6.3</h1>
    <h3>كيقلب فـ النت بصح</h3>
    <p><b>👨‍💻 رضا مالكي</b></p>
</div>
""", unsafe_allow_html=True)

KNOWLEDGE_BASE = {
    'سلام': "وعليكم السلام المعلم 👋",
    'عاصمة الصين': 'عاصمة الصين هي **بكين Beijing** 🇨🇳',
    'عاصمة كوريا': 'عاصمة كوريا الجنوبية هي **سيول Seoul** 🇰🇷',
}

# ===== البحث الحقي ب duckduckgo_search =====
def search_internet(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=1)
            if results:
                r = results[0]
                return f"**{r['title']}**\n{r['body']}\n🔗 {r['href']}"
        return None
    except Exception:
        return None

# ===== الصوت =====
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
        return None, f"خطأ: {e}"

# ===== الرد الذكي =====
def get_smart_response(user_msg):
    msg = user_msg.lower().strip()

    # عواصم
    for key, answer in KNOWLEDGE_BASE.items():
        if key in msg:
            return answer

    # أي سؤال = قلب فـ النت دغيا بلا شروط
    with st.spinner("🔍 كنقلب فـ Google دابا..."):
        result = search_internet(user_msg)

    if result:
        return f"🔍 **لقيت ليك هاد الجواب:**\n{result}"
    else:
        return f"ما لقيتش جواب دقيق المعلم 😅 عاود بصيغة أخرى"

# ===== المحادثة =====
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "السلام المعلم 👋 أنا RAM Bot Ultra v6.3. دابا كنقلب فـ النت بصح. جربني!"}]

# الصوت
audio_input = st.audio_input("🎤 هضر معايا")
if audio_input and "last_audio" not in st.session_state:
    st.session_state.last_audio = audio_input.getvalue()
    text, error = audio_to_text(st.session_state.last_audio)
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

# الصور
uploaded_file = st.file_uploader("📸 صيفط صورة", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    text = pytesseract.image_to_string(image, lang='ara+eng+fra')
    st.success(f"قريت: {text}")
    st.session_state.messages.append({"role": "assistant", "content": f"من الصورة:\n```\n{text}\n```"})
    st.rerun()

# عرض الرسائل
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# الكتابة
if prompt := st.chat_input("سولني على أي حاجة..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("كنقلب..."):
            response = get_smart_response(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
