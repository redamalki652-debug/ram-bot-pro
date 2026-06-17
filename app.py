import streamlit as st
from groq import Groq
import base64
import requests
import io
import urllib.parse
import time
import random
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS

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
    <p>صوت 🎤 + صور 📸 + فيديو 🎬 بلا فلوس</p>
</div>
""", unsafe_allow_html=True)

def translate_to_english(text):
    prompt = f"Translate this Moroccan Darija to English for AI, only output English: {text}"
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except:
        return text.replace("ولد ليا", "").strip()

def generate_image(prompt):
    with st.spinner("كنرسم ليك الصورة... 🎨"):
        eng_prompt = translate_to_english(prompt)
        st.info(f"Prompt: {eng_prompt}")
        url = f"https://image.pollinations.ai/prompt/{eng_prompt}?width=1024&height=1024&model=flux&nologo=true"
        response = requests.get(url, timeout=45)
        return response.content if response.status_code == 200 else f"Error {response.status_code}"

def generate_video_anything(prompt):
    eng_prompt = translate_to_english(prompt)
    st.info(f"Prompt: {eng_prompt}")
    for attempt in range(3):
        try:
            seed = random.randint(1, 999)
            encoded = urllib.parse.quote(eng_prompt)
            url = f"https://image.pollinations.ai/video/{encoded}?model=ltx-video&nologo=true&width=512&height=512&seed={seed}"
            with st.spinner(f"المحاولة {attempt+1}/3..."):
                response = requests.get(url, timeout=90)
            if response.status_code == 200 and len(response.content) > 50000:
                return response.content, "Pollinations LTX"
            time.sleep(2)
        except:
            time.sleep(2)
    return None, "السيرفر مضغوط. جرب بعد 5 دقايق"

def speak(text):
    tts = gTTS(text=text, lang='ar')
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image" in msg and msg["image"]!= "ai":
            st.image(msg["image"], width=300)
        elif msg.get("image") == "ai":
            st.image(msg["content"])
        elif "video" in msg:
            st.video(msg["video"])
            st.caption(f"المصدر: {msg['source']}")
        elif "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")
        else:
            st.markdown(msg["content"])

# الميكرو + رفع الصور
col1, col2 = st.columns(2)
with col1:
    audio = mic_recorder(start_prompt="🎤 سجل", stop_prompt="⏹️ وقف", key="recorder")
with col2:
    uploaded_file = st.file_uploader("📸 صيفط صورة ديال تمرين", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

# مربع 1: للصورة - بحال التصويرة ديالك
prompt_with_image = st.chat_input("كتب سؤالك على الصورة هنا...", key="chat_input_img")

# مربع 2: للنص العادي - بحال التصويرة ديالك
prompt_text_only = st.chat_input("كتب سؤالك هنا... ولا قول 'ولد ليا صورة/فيديو ديال...'", key="chat_input_text")

# الصوت
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
        prompt_text_only = transcription

# معالجة الصورة + مربع 1
if uploaded_file is not None and prompt_with_image:
    image_b64 = base64.b64encode(uploaded_file.getvalue()).decode()
    image_url = f"data:image/jpeg;base64,{image_b64}"

    with st.chat_message("user"):
        st.image(uploaded_file, width=300)
        st.markdown(prompt_with_image)

    with st.chat_message("assistant"):
        with st.spinner("كنقرا الصورة وكنحل التمرين..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot. المطور رضا مالكي. كتهضر بالدارجة. إلا عطاوك صورة ديال تمرين حلّو خطوة بخطوة."}
            user_content = [{"type": "text", "text": prompt_with_image}, {"type": "image_url", "image_url": {"url": image_url}}]
            chat_completion = client.chat.completions.create(
                messages=[system_prompt, {"role": "user", "content": user_content}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                max_tokens=800
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "user", "content": prompt_with_image, "image": uploaded_file})
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

# معالجة النص فقط + مربع 2
elif prompt_text_only:
    with st.chat_message("user"):
        st.markdown(prompt_text_only)

    if any(word in prompt_text_only for word in ["صورة", "رسم"]):
        with st.chat_message("assistant"):
            result = generate_image(prompt_text_only)
            if isinstance(result, bytes):
                st.image(result)
                audio = speak("ها هي الصورة ديالك")
                st.audio(audio, format="audio/mp3")
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": result, "image": "ai"})
            else:
                st.error(result)

    elif any(word in prompt_text_only for word in ["فيديو"]):
        with st.chat_message("assistant"):
            result, source = generate_video_anything(prompt_text_only)
            if isinstance(result, bytes):
                st.video(result)
                st.caption(f"المصدر: {source}")
                audio = speak("ها هو الفيديو ديالك")
                st.audio(audio, format="audio/mp3")
                st.session_state.messages.append({"role": "user", "user": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": "تم", "video": result, "source": source})
            else:
                st.error(source)

    else:
        with st.chat_message("assistant"):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "نتا RAM Bot v2.2. المطور رضا مالكي. كتهضر بالدارجة المغربية باختصار."}, {"role": "user", "content": prompt_text_only}],
                model="llama-3.3-70b-versatile",
                max_tokens=300
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "user", "content": prompt_text_only})
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

if st.button("🗑️ مسح المحادثة", type="primary"):
    st.session_state.messages = []
    st.session_state.uploader_key += 1
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
