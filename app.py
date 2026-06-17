import streamlit as st
from groq import Groq
import base64
import requests
import os
import urllib.parse
import io
import time
import random

st.set_page_config(page_title="RAM Bot v2.2 AI", page_icon="🤖", layout="centered")

GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v2.2 AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيولد أي فيديو بلا فلوس 🎬</p>
</div>
""", unsafe_allow_html=True)

def translate_to_english(text):
    prompt = f"Translate this Moroccan Darija to English for AI video generation, only output English: {text}"
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except:
        return text.replace("ولد ليا", "").replace("صاوب ليا", "").replace("فيديو ديال", "").strip()

def generate_image(prompt):
    with st.spinner("كنرسم ليك الصورة... 🎨"):
        eng_prompt = translate_to_english(prompt)
        st.info(f"Prompt: {eng_prompt}")
        url = f"https://image.pollinations.ai/prompt/{eng_prompt}?width=1024&height=1024&model=flux&nologo=true"
        response = requests.get(url, timeout=45)
        if response.status_code == 200:
            return response.content
        return f"Error {response.status_code}"

def generate_video_anything(prompt):
    """كيعاود المحاولة 3 مرات حتى يولد أي فيديو"""
    eng_prompt = translate_to_english(prompt)
    st.info(f"Prompt: {eng_prompt}")

    for attempt in range(3):
        try:
            seed = random.randint(1, 999)
            encoded = urllib.parse.quote(eng_prompt)
            url = f"https://image.pollinations.ai/video/{encoded}?model=ltx-video&nologo=true&width=512&height=512&seed={seed}"

            with st.spinner(f"المحاولة {attempt+1}/3... صبر 25 ثانية"):
                response = requests.get(url, timeout=90)

            if response.status_code == 200 and len(response.content) > 50000:
                return response.content, "Pollinations LTX"
            else:
                st.warning(f"المحاولة {attempt+1} فشلت، كنعاود...")
                time.sleep(2)

        except Exception as e:
            st.warning(f"المحاولة {attempt+1} خطأ، كنعاود...")
            time.sleep(2)

    return None, "السيرفر مضغوط بزاف. جرب بعد 5 دقايق ولا بدل البرومت"

def speak(text):
    from gtts import gTTS
    tts = gTTS(text=text, lang='ar')
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

# الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            if "video" in msg:
                st.video(msg["video"])
                st.caption(f"المصدر: {msg['source']}")
            elif "image" in msg:
                st.image(msg["content"])
            else:
                st.markdown(msg["content"])

prompt_text_only = st.chat_input("كتب: ولد ليا فيديو ديال أي حاجة...")

if prompt_text_only:
    with st.chat_message("user"):
        st.markdown(prompt_text_only)

    if any(word in prompt_text_only for word in ["صورة", "رسم"]):
        with st.chat_message("assistant"):
            result = generate_image(prompt_text_only)
            if isinstance(result, bytes):
                st.image(result)
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": result, "image": result})
            else:
                st.error(result)

    elif any(word in prompt_text_only for word in ["فيديو"]):
        with st.chat_message("assistant"):
            result, source = generate_video_anything(prompt_text_only)
            if isinstance(result, bytes):
                st.video(result)
                st.caption(f"المصدر: {source}")
                st.success("ها هو الفيديو ديالك 🎬 كيف ما كان")
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": "تم", "video": result, "source": source})
            else:
                st.error(source)
                st.info("💡 نصيحة: جرب برومت بسيط 'قط كيجري' ولا صبر 5 دقايق وعاود")
    else:
        with st.chat_message("assistant"):
            st.markdown("قول: ولد ليا فيديو ديال... ولا ولد ليا صورة ديال...")

if st.button("🗑️ مسح المحادثة", type="primary"):
    st.session_state.messages = []
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
