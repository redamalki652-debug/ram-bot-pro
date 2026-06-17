import streamlit as st
from groq import Groq
import base64
import requests
import os
import replicate
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
from PIL import Image

st.set_page_config(page_title="RAM Bot v2.2 AI", page_icon="🤖", layout="centered")

# Secrets
GROQ_KEY = st.secrets["GROQ_KEY"]
REPLICATE_TOKEN = st.secrets["REPLICATE_TOKEN"]
client = Groq(api_key=GROQ_KEY)
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

# الواجهة ديالك
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v2.2 AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر بالصوت + كيقرا الصور + كيولد تصاور وفيديو 🎨</p>
</div>
""", unsafe_allow_html=True)

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def generate_image(prompt):
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

def generate_video(prompt):
    with st.spinner("كنولد الفيديو... صبر 30 ثانية 🎬"):
        try:
            clean_prompt = prompt.replace("ولد ليا فيديو", "").replace("فيديو ديال", "").strip()
            output = replicate.run("minimax/video-01", input={"prompt": clean_prompt})
            return output
        except Exception as e:
            return f"Error: {str(e)}"

def speak(text):
    tts = gTTS(text=text, lang='ar')
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

# تهيئة الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# عرض المحادثة
for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            if "image" in msg and msg["image"] and msg["image"]!= "ai_generated":
                st.image(msg["image"], width=300)
            elif msg.get("image") == "ai_generated":
                st.image(msg["content"], caption="صورة مولدة")
            elif "audio" in msg:
                st.audio(msg["audio"], format="audio/mp3")
            else:
                st.markdown(msg["content"])

# الميكروفون + رفع الصورة
col1, col2 = st.columns(2)
with col1:
    audio = mic_recorder(start_prompt="🎤 سجل", stop_prompt="⏹️ وقف", key="recorder")
with col2:
    uploaded_file = st.file_uploader("📸 صيفط بطاقة/موطور", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

def get_text_messages():
    text_msgs = []
    for msg in st.session_state.messages:
        if msg["role"] == "user" and "image" not in msg:
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
            system_prompt = {"role": "system", "content": "نتا RAM Bot v2.2. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية باختصار. إلا عطاوك صورة ديال بطاقة خرج المعلومات والتمارين."}
            user_content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": image_url}}]
            messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
            chat_completion = client.chat.completions.create(messages=messages, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, max_tokens=500)
            response = chat_completion.choices[0].message.content
            st.markdown(response)

            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")

            st.session_state.messages.append({"role": "user", "content": prompt, "image": image})
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

def process_text_only(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("كنجاوب..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v2.2. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية باختصار."}
            text_messages = get_text_messages()
            messages = [system_prompt] + text_messages + [{"role": "user", "content": prompt}]
            chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=300)
            response = chat_completion.choices[0].message.content
            st.markdown(response)

            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")

            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

prompt_with_image = st.chat_input("كتب سؤالك على الصورة هنا...")
prompt_text_only = st.chat_input("كتب سؤالك هنا... ولا قول 'ولد ليا صورة/فيديو ديال...'", key="text_only")

# معالجة الصوت
if audio and audio["bytes"]:
    with st.spinner("كنسمعك..."):
        audio_bytes = audio["bytes"]
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model="whisper-large-v3",
            response_format="text",
            language="ar"
        )
        st.success(f"سمعتك: {transcription}")
        process_text_only(transcription)

elif uploaded_file is not None and prompt_with_image:
    process_with_image(uploaded_file, prompt_with_image)
    st.session_state.uploader_key += 1
    st.rerun()

elif prompt_text_only:
    if any(word in prompt_text_only for word in ["ولد ليا صورة", "صاوب ليا صورة", "رسم ليا"]):
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                response = f"ها هي الصورة ديال: {prompt_text_only}"
                audio_bytes = speak(response)
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes, "image": "ai_generated"})
            else:
                st.error("ما قدرتش نولد الصورة")

    elif any(word in prompt_text_only for word in ["ولد ليا فيديو", "صاوب ليا فيديو"]):
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            video_url = generate_video(prompt_text_only)
            if isinstance(video_url, list):
                st.video(video_url[0])
                response = "ها هو الفيديو ديالك 🎬"
                audio_bytes = speak(response)
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})
            else:
                st.error(f"خطأ: {video_url}")
    else:
        process_text_only(prompt_text_only)

# زر مسح المحادثة - مصلح 100%
if st.button("🗑️ مسح المحادثة", use_container_width=True, type="primary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.success("تم مسح المحادثة ✅")
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
