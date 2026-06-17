import streamlit as st
from groq import Groq
import base64
import requests
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import tempfile
import os

st.set_page_config(page_title="RAM Bot v3.1 Voice AI", page_icon="🎤", layout="centered")

GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🎤 RAM Bot v3.1 Voice AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر معاك بالصوت + كيقرا الصور + كيولد تصاور 🎨</p>
</div>
""", unsafe_allow_html=True)

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def generate_image(prompt):
    """توليد صورة مجاني - Pollinations.ai"""
    with st.spinner("كنرسم ليك الصورة... 🎨"):
        try:
            clean_prompt = prompt.replace("ولد ليا", "").replace("صاوب ليا", "").replace("رسم ليا", "").replace("صورة ديال", "").strip()
            url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1024&height=1024&model=flux&enhance=true"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.content
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

def text_to_speech(text):
    """تحويل النص لصوت بالعربية"""
    with st.spinner("كنحضر الصوت... 🔊"):
        tts = gTTS(text=text, lang='ar', slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        return audio_bytes.getvalue()

def speech_to_text(audio_bytes):
    """تحويل الصوت لنص ب Whisper ديال Groq"""
    with st.spinner("كنفهم الهضرة ديالك... 🎤"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, file.read()),
                model="whisper-large-v3",
                response_format="text",
                language="ar"
            )
        os.unlink(tmp_path)
        return transcription

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "current_input" not in st.session_state:
    st.session_state.current_input = None

for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            if "image" in msg and msg["image"] and msg["image"]!= "ai_generated":
                st.image(msg["image"], width=300)
            elif msg.get("image") == "ai_generated":
                st.image(msg["content"], caption="صورة مولدة بالذكاء الاصطناعي")
            else:
                st.markdown(msg["content"])
                if msg.get("play_audio"):
                    st.audio(msg["play_audio"], format="audio/mp3")

uploaded_file = st.file_uploader("📸 صيفط صورة ولا سول عادي", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

def get_text_messages():
    text_msgs = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            text_msgs.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            text_msgs.append({"role": "assistant", "content": msg["content"]})
    return text_msgs

def process_with_image(image, prompt):
    image_b64 = encode_image(image)
    image_url = f"data:image/jpeg;base64,{image_b64}"
    with st.chat_message("user"):
        st.image(image, width=300)
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("كنقرا الصورة..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v3.1. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية. جاوب قصير ومباشر."}
            user_content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": image_url}}]
            messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
            chat_completion = client.chat.completions.create(messages=messages, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, max_tokens=1024)
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio = text_to_speech(response)
            st.audio(audio, format="audio/mp3")
            st.session_state.messages.append({"role": "user", "content": prompt, "image": image})
            st.session_state.messages.append({"role": "assistant", "content": response, "play_audio": audio})

def process_text_only(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("كنجاوب..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v3.1. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية. جاوب قصير ومباشر."}
            text_messages = get_text_messages()
            messages = [system_prompt] + text_messages + [{"role": "user", "content": prompt}]
            chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=512)
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio = text_to_speech(response)
            st.audio(audio, format="audio/mp3")
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response, "play_audio": audio})

# المدخل ديال الكتابة والصوت - مصلح
col1, col2 = st.columns([4,1])
with col1:
    text_input = st.chat_input("كتب سؤالك... ولا قول 'ولد ليا صورة ديال...'")
with col2:
    audio = mic_recorder(start_prompt="🎤 هضر", stop_prompt="⏹️ سكت", key=f"recorder_{st.session_state.uploader_key}")

# الأولوية للكتابة
if text_input:
    st.session_state.current_input = text_input
elif audio and audio["bytes"]:
    transcribed_text = speech_to_text(audio["bytes"])
    if transcribed_text and transcribed_text.strip():
        st.session_state.current_input = transcribed_text

# معالجة المدخل
if uploaded_file is not None and st.session_state.current_input:
    process_with_image(uploaded_file, st.session_state.current_input)
    st.session_state.current_input = None
    st.session_state.uploader_key += 1
    st.rerun()

elif st.session_state.current_input:
    prompt = st.session_state.current_input
    st.session_state.current_input = None

    if any(word in prompt for word in ["ولد ليا", "صاوب ليا", "رسم ليا", "صورة ديال"]):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": f"ها هي الصورة ديال: {prompt}"})
            else:
                st.error("ما قدرتش نولد الصورة دابا. جرب مرة أخرى")
    else:
        process_text_only(prompt)

if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.session_state.current_input = None
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
