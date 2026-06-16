import streamlit as st
import random
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
import io
import datetime

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
    <h1 style="margin: 0;">🤖 RAM Bot Ultra v6.2</h1>
    <h3>مليار معلومة + بحث حقي</h3>
    <p><b>👨‍💻 المطور: رضا مالكي</b></p>
    <p>🎤 صوت + 📸 صور + 🔍 بحث فـ النت + 💬 محادثة</p>
</div>
""", unsafe_allow_html=True)

# ===== قاعدة المعرفة =====
KNOWLEDGE_BASE = {
    'سلام': "وعليكم السلام المعلم 👋 مرحبا بيك",
    'شكون انت': "أنا RAM Bot Ultra 🤖 عندي بحث فـ النت + ذكاء. سولني على أي حاجة!",
    'شكرا': "العفو المعلم ❤️ راني هنا ديما",
}

# ===== البحث الحقي فـ النت =====
def search_internet(query):
    try:
        search_results = browser.search(
            primary_query={"language_code": "ar", "query": query},
            verbosity_level="high"
        )
        if hasattr(search_results, 'results') and search_results.results:
            top_result = search_results.results[0]
            snippet = top_result.get('snippet', '')
            title = top_result.get('title', '')
            if snippet:
                return f"**{title}**\n{snippet}"
        return None
    except Exception:
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
            return None, "⚠️ خاص ffmpeg فـ packages.txt ودير Reboot"
        return None, "ما فهمتش الصوت، عاود 🎤"

# ===== الرد الذكي + بحث + عواصم =====
def get_smart_response(user_msg):
    msg = user_msg.lower().strip()

    # 1. عواصم ودول مباشرة
    capitals = {
        'عاصمة كوريا': 'عاصمة كوريا الجنوبية هي **سيول Seoul** 🇰🇷',
        'عاصمة المغرب': 'عاصمة المغرب هي **الرباط** 🇲🇦',
        'عاصمة فرنسا': 'عاصمة فرنسا هي **باريس Paris** 🇫🇷',
        'عاصمة اليابان': 'عاصمة اليابان هي **طوكيو Tokyo** 🇯🇵',
        'عاصمة امريكا': 'عاصمة أمريكا هي **واشنطن دي سي** 🇺🇸',
        'عاصمة مصر': 'عاصمة مصر هي **القاهرة** 🇪🇬'
    }
    for key, answer in capitals.items():
        if key in msg:
            return answer

    # 2. قاعدة المعرفة
    for key, answer in KNOWLEDGE_BASE.items():
        if key in msg:
            return answer

    # 3. أي سؤال = قلب فـ النت دغيا
    with st.spinner("🔍 كنقلب ليك فـ النت دابا..."):
        result = search_internet(user_msg)

    if result:
        return f"🔍 **لقيت ليك هاد الجواب:**\n{result}\n\nبغيتي تفاصيل كثر المعلم؟"
    else:
        if 'علاش' in msg:
            return f"🤔 علاش {msg.replace('علاش', '')}؟ كل حاجة عندها سبب وحكمة"
        return f"فهمتك المعلم 👌 {msg} موضوع كبير. شنو بالضبط باغي تعرف؟"

# ===== تهيئة المحادثة =====
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "السلام المعلم 👋 أنا RAM Bot Ultra v6.2. عندي مليار معلومة + بحث فـ النت. سولني على أي حاجة!"}]

# ===== الصوت - بلا وميض =====
audio_input = st.audio_input("🎤 هضر معايا")
if audio_input and "last_audio" not in st.session_state:
    st.session_state.last_audio = audio_input.getvalue()
    audio_bytes = st.session_state.last_audio

    with st.spinner("RAM Bot كيسمع ليك..."):
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

# ===== الصور OCR =====
uploaded_file = st.file_uploader("📸 صيفط صورة تمرين", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    with st.spinner("كنقرا فـ الصورة..."):
        text = pytesseract.image_to_string(image, lang='ara+eng+fra')
    if text.strip():
        st.success(f"📝 قريت من الصورة:\n{text}")
        st.session_state.messages.append({"role": "assistant", "content": f"من الصورة قريت:\n```\n{text}\n```\nشنو ندير بيه المعلم؟"})
    else:
        st.warning("ما قدرتش نقرا والو فـ الصورة 😅")
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
