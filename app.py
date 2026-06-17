import streamlit as st
from groq import Groq
import base64
import requests
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import tempfile
import os
import time

st.set_page_config(page_title="RAM Bot v4.0 Video AI", page_icon="🎬", layout="centered")

if "initialized" not in st.session_state:
    st.session_state.initialized = True

GROQ_KEY = st.secrets.get("GROQ_KEY")
DID_KEY = st.secrets.get("DID_KEY", "") # زيدو فـ Secrets إلا عندك
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
    <h1>🎬 RAM Bot v4.0 Video AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر + كيسمع + كيولد صور + كيولد فيديو هاضر 🎤🎨🎬</p>
</div>
""", unsafe_allow_html=True)

def text_to_speech(text):
    tts = gTTS(text=text, lang='ar', slow=False)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    return audio_bytes.getvalue()

def generate_video_did(text, voice="ar-EG-Salma"):
    """توليد فيديو هاضر ب D-ID API"""
    if not DID_KEY:
        return None, "ما كاينش DID_KEY فـ Secrets. زيدو ولا استعمل الوضع التجريبي"

    with st.spinner("كنولد ليك الفيديو الهاضر... كيدير 1-2 دقيقة ⏳"):
        try:
            # 1. نولدو الصوت
            audio_data = text_to_speech(text)

            # 2. نطلبو من D-ID يولد الفيديو
            url = "https://api.d-id.com/talks"
            payload = {
                "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Emma_f_square.png", # وجه افتراضي
                "script": {
                    "type": "text",
                    "input": text,
                    "provider": {"type": "microsoft", "voice_id": voice}
                }
            }
            headers = {"Authorization": f"Basic {DID_KEY}", "Content-Type": "application/json"}

            response = requests.post(url, json=payload, headers=headers)
            if response.status_code!= 201:
                return None, f"Error D-ID: {response.text}"

            talk_id = response.json()['id']

            # 3. نسناو حتى يوجّد الفيديو
            status_url = f"https://api.d-id.com/talks/{talk_id}"
            for _ in range(60): # 2 دقايق max
                time.sleep(2)
                status = requests.get(status_url, headers=headers).json()
                if status['status'] == 'done':
                    return status['result_url'], "تم!"
                elif status['status'] == 'error':
                    return None, "فشل توليد الفيديو"
            return None, "تأخر الفيديو بزاف"
        except Exception as e:
            return None, str(e)

# باقي الكود ديال الصور والمحادثة... نفس v3.2
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "current_input" not in st.session_state:
    st.session_state.current_input = None

for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            if msg.get("video"):
                st.video(msg["video"])
            elif "image" in msg and msg["image"] and msg["image"]!= "ai_generated":
                st.image(msg["image"], width=300)
            elif msg.get("image") == "ai_generated":
                st.image(msg["content"], caption="صورة مولدة")
            else:
                st.markdown(msg["content"])
                if msg.get("play_audio"):
                    st.audio(msg["play_audio"], format="audio/mp3")

uploaded_file = st.file_uploader("📸 صورة ولا فيديو", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

col1, col2 = st.columns([4,1])
with col1:
    text_input = st.chat_input("كتب 'ولد فيديو: السلام عليكم' باش تجرب")
with col2:
    audio = mic_recorder(start_prompt="🎤 هضر", stop_prompt="⏹️ سكت", key=f"recorder_{st.session_state.uploader_key}")

if text_input:
    st.session_state.current_input = text_input
elif audio and audio["bytes"]:
    with st.spinner("كنفهم الهضرة..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            tmp_path = tmp.name
        with open(tmp_path, "rb") as file:
            transcribed = client.audio.transcriptions.create(file=(tmp_path, file.read()), model="whisper-large-v3", response_format="text", language="ar")
        os.unlink(tmp_path)
        st.session_state.current_input = transcribed

if st.session_state.current_input:
    prompt = st.session_state.current_input
    st.session_state.current_input = None

    # كشف طلب الفيديو
    if prompt.startswith("ولد فيديو:") or "ولد ليا فيديو" in prompt:
        text_to_say = prompt.replace("ولد فيديو:", "").replace("ولد ليا فيديو", "").strip()
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            if DID_KEY:
                video_url, status = generate_video_did(text_to_say)
                if video_url:
                    st.video(video_url)
                    st.success(status)
                    st.session_state.messages.append({"role": "assistant", "content": text_to_say, "video": video_url})
                else:
                    st.error(status)
            else:
                # وضع تجريبي
                st.info("🔧 وضع تجريبي: ما كاينش D-ID Key. هادا فيديو تجريبي + الصوت")
                audio_data = text_to_speech(text_to_say)
                st.audio(audio_data, format="audio/mp3")
                st.video("https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4")
                st.session_state.messages.append({"role": "assistant", "content": text_to_say, "play_audio": audio_data})
    else:
        # باقي الكود العادي ديال النص والصور
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("كنجاوب..."):
                system_prompt = {"role": "system", "content": "نتا RAM Bot v4.0. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية."}
                messages = [system_prompt] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m["role"] in ["user", "assistant"]] + [{"role": "user", "content": prompt}]
                chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=512)
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                audio = text_to_speech(response)
                st.audio(audio, format="audio/mp3")
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": response, "play_audio": audio})

if st.button("🗑️ مسح المحادثة", use_container_width=True):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
