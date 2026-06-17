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
import pytesseract

st.set_page_config(page_title="RAM Bot v2.2 AI", page_icon="🤖", layout="centered")

# Secrets
GROQ_KEY = st.secrets["GROQ_KEY"]
REPLICATE_TOKEN = st.secrets["REPLICATE_TOKEN"]
client = Groq(api_key=GROQ_KEY)
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

# الواجهة ديالك بالضبط
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
    <p>كيهضر بالدارجة + كيقرا الصور + كيولد تصاور وفيديو مجاني 🎨</p>
</div>
""", unsafe_allow_html=True)

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def generate_image(prompt):
    """توليد صورة مجاني بلا Credits - Pollinations.ai"""
    with st.spinner("كنرسم ليك الصورة... صبر شوية 🎨"):
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
    """توليد فيديو"""
    with st.spinner("كنولد الفيديو... صبر 30 ثانية 🎬"):
        try:
            clean_prompt = prompt.replace("ولد ليا فيديو", "").replace("فيديو ديال", "").strip()
            output = replicate.run("minimax/video-01", input={"prompt": clean_prompt})
            return output
        except Exception as e:
            return f"Error: {str(e)}"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            if "image" in msg and msg["image"] and msg["image"]!= "ai_generated":
                st.image(msg["image"], width=300)
            elif msg.get("image") == "ai_generated":
                st.image(msg["content"], caption="صورة مولدة بالذكاء الاصطناعي")
            else:
                st.markdown(msg["content"])

# الميكروفون + رفع الصورة
col1, col2 = st.columns(2)
with col1:
    audio = mic_recorder(start_prompt="🎤 سجل", stop_prompt="⏹️ وقف", key="recorder")
    if audio:
        st.audio(audio["bytes"])
with col2:
    uploaded_file = st.file_uploader("📸 صيفط بطاقة/موطور", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

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
            system_prompt = {"role": "system", "content": "نتا RAM Bot v2.2. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية. إلا عطاوك صورة ديال بطاقة ولا موطور خرج الاسم والتمارين خطوة بخطوة."}
            user_content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": image_url}}]
            messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
            chat_completion = client.chat.completions.create(messages=messages, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, max_tokens=2048)
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "user", "content": prompt, "image": image})
            st.session_state.messages.append({"role": "assistant", "content": response})

def process_text_only(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("كنجاوب..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v2.2. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية."}
            text_messages = get_text_messages()
            messages = [system_prompt] + text_messages + [{"role": "user", "content": prompt}]
            chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=1024)
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response})

prompt_with_image = st.chat_input("كتب سؤالك على الصورة هنا...")
prompt_text_only = st.chat_input("كتب سؤالك هنا... ولا قول 'ولد ليا صورة/فيديو ديال...'", key="text_only")

if uploaded_file is not None and prompt_with_image:
    process_with_image(uploaded_file, prompt_with_image)
    st.session_state.uploader_key += 1
    st.rerun()

elif prompt_text_only:
    # صورة
    if any(word in prompt_text_only for word in ["ولد ليا صورة", "صاوب ليا صورة", "رسم ليا"]):
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": f"ها هي الصورة ديال: {prompt_text_only}", "image": "ai_generated"})
            else:
                st.error("ما قدرتش نولد الصورة دابا")

    # فيديو
    elif any(word in prompt_text_only for word in ["ولد ليا فيديو", "صاوب ليا فيديو"]):
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            video_url = generate_video(prompt_text_only)
            if isinstance(video_url, list):
                st.video(video_url[0])
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": "ها هو الفيديو ديالك 🎬"})
            else:
                st.error(f"خطأ فالفيديو: {video_url}")

    # هضرة
    elif prompt_text_only.startswith("قول") or prompt_text_only.startswith("هضر"):
        tts = gTTS(text=prompt_text_only.replace("قول", "").replace("هضر", ""), lang='ar')
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        st.audio(buf.getvalue(), format="audio/mp3")
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        st.session_state.messages.append({"role": "assistant", "content": "سمع الهضرة 🔊"})

    else:
        process_text_only(prompt_text_only)

if st.button("🗑️ مسح المحادثة", use_container_width=True):
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
