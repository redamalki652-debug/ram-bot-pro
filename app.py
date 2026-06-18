import streamlit as st

# ==========================================
# كود التحقق ديال Google - ما تحيدوش
# خليتو فاللول قبل set_page_config باش Google يلقاه
# ==========================================
st.html('<meta name="google-site-verification" content="b277554ee20ea754" />')

# SEO Meta Tags
st.html("""
<meta name="description" content="RAM Bot v5.3 by Reda Malki - دردشة ذكية بـ 100+ لغة، توليد صور بالذكاء الاصطناعي، تحويل الصوت لنص">
<meta name="keywords" content="RAM Bot, Reda Malki, ذكاء اصطناعي, دردشة, صور AI, مغربي">
<meta name="author" content="Reda Malki">
<meta property="og:title" content="RAM Bot v5.3 - دردشة ذكية مغربية">
<meta property="og:description" content="أقوى بوت مغربي بالذكاء الاصطناعي - 100+ لغة + صور + صوت">
<meta name="robots" content="index, follow">
""")

st.set_page_config(
    page_title="RAM Bot v5.3 - دردشة ذكية | Reda Malki",
    page_icon="🌍",
    layout="centered"
)

from groq import Groq
import base64
import requests
import io
import urllib.parse
import random
from gtts import gTTS
import re
import time

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
except KeyError:
    st.error("⚠️ GROQ_KEY ناقص! سير Settings > Secrets")
    st.stop()

client = Groq(api_key=GROQ_KEY)

# CSS
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); text-align: center; margin-bottom: 2rem;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
.card p {color: #666; margin: 0.5rem 0;}
.stButton>button {background: #ff4b4b; color: white; font-weight: bold; border-radius: 15px; border: none;}
.stButton>button:hover {background: #ff2b2b;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🌍 RAM Bot v5.3</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>100+ لغة + صوت + صور + مسح مضمون ✅</p>
</div>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_key" not in st.session_state:
    st.session_state.chat_key = random.randint(1000, 99999)

def get_gtts_lang(text):
    text = text.lower()
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    if any(w in text for w in ['the', 'is', 'hello', 'what']):
        return 'en'
    if any(w in text for w in ['le', 'la', 'bonjour']):
        return 'fr'
    return 'ar'

def translate_to_english(text):
    text = text.lower().replace("ولد ليا صورة ديال", "").replace("draw", "").strip()
    dict = {"قط": "cat cute 4k", "غوكو": "Goku Dragon Ball super saiyan anime"}
    for ar, en in dict.items():
        if ar in text:
            return en + ", high quality 4k"
    return text + ", high quality 4k" if text else "beautiful scene 4k"

def generate_image(prompt):
    with st.spinner("كنرسم... 3 ثواني 🎨"):
        eng_prompt = translate_to_english(prompt)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng_prompt)}?width=1024&height=1024&model=flux&nologo=true&seed={random.randint(1,99999)}"
        r = requests.get(url, timeout=30)
        return r.content if r.status_code == 200 else None

def speak(text):
    try:
        lang = get_gtts_lang(text)
        tts = gTTS(text=text[:250], lang=lang)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()
    except:
        tts = gTTS(text=text[:200], lang='ar')
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        return buf.getvalue()

# رسم الرسائل
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image") == "ai":
            st.image(msg["content"], caption=msg.get("prompt"))
        elif msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")
        else:
            st.markdown(msg["content"])

# Widgets
uploaded_file = st.file_uploader("📸 صيفط صورة للحل", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.chat_key}")
audio = st.audio_input("🎤 سجل صوتك بأي لغة", key=f"audio_{st.session_state.chat_key}")
prompt_image = st.chat_input("سول على الصورة...", key=f"img_{st.session_state.chat_key}")
prompt_main = st.chat_input("كتب بأي لغة... ولا 'ولد ليا صورة'", key=f"main_{st.session_state.chat_key}")

# معالجة الصوت
if audio:
    with st.spinner("كنسمعك..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio.getvalue()),
            model="whisper-large-v3",
            response_format="text",
            language=None
        )
        st.session_state.messages.append({"role": "user", "content": transcription})
        st.success(f"سمعتك: {transcription}")
        prompt_main = transcription

# معالجة النص
if prompt_main:
    st.session_state.messages.append({"role": "user", "content": prompt_main})

    if any(k in prompt_main.lower() for k in ["صورة", "draw", "generate"]):
        with st.chat_message("assistant"):
            result = generate_image(prompt_main)
            if result:
                st.image(result, caption="AI Generated")
                audio_bytes = speak("ها هي الصورة ديالك")
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.messages.append({"role": "assistant", "content": result, "image": "ai", "prompt": prompt_main, "audio": audio_bytes})
    else:
        with st.chat_message("assistant"):
            system_msg = "You are RAM Bot v5.3 by Reda Malki. Detect user's language and reply in same language. Short."
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": system_msg}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if isinstance(m.get("content"), str)],
                model="llama-3.3-70b-versatile",
                max_tokens=350
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

# معالجة الصورة
if uploaded_file and prompt_image:
    image_b64 = base64.b64encode(uploaded_file.getvalue()).decode()
    image_url = f"data:image/jpeg;base64,{image_b64}"
    st.session_state.messages.append({"role": "user", "content": prompt_image, "image": uploaded_file})
    with st.chat_message("assistant"):
        with st.spinner("كنقرا الصورة..."):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "Reply in same language as user."},
                         {"role": "user", "content": [{"type": "text", "text": prompt_image}, {"type": "image_url", "image_url": {"url": image_url}}]}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                max_tokens=600
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

# زر المسح
if st.button("🗑️ مسح المحادثة", type="primary", use_container_width=True, key=f"clear_{st.session_state.chat_key}"):
    st.session_state.messages = []
    st.session_state.chat_key = random.randint(1000, 99999)
    st.toast("تم المسح! الصفحة غتعود تتحمل...", icon="✅")
    time.sleep(0.3)
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>Made with ❤️ by Reda Malki</div>", unsafe_allow_html=True)
