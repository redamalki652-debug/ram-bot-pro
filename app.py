import streamlit as st
from groq import Groq
import base64
import requests
import io
import urllib.parse
import random
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import replicate
import os

st.set_page_config(page_title="RAM Bot v3.0", page_icon="🤖", layout="centered")

GROQ_KEY = st.secrets["GROQ_KEY"]
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
client = Groq(api_key=GROQ_KEY)

st.markdown("<style>.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}</style>", unsafe_allow_html=True)
st.markdown("<div style='background:white;padding:2rem;border-radius:20px;text-align:center'><h1>🤖 RAM Bot v3.0</h1><p>المطور: رضا مالكي</p></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

def translate_to_english(text):
    text = text.lower().replace("ولد ليا فيديو ديال", "").replace("ولد ليا صورة ديال", "").replace("ولد ليا", "").strip()
    dict = {"قط": "cat running cute", "كلب": "dog running", "بحر": "ocean waves", "غوكو": "Goku Dragon Ball flying"}
    for ar, en in dict.items():
        if ar in text:
            return en + ", smooth motion, 4k"
    return text + ", smooth motion, 4k" if text else "beautiful scene, 4k"

def generate_video_replicate(prompt):
    eng_prompt = translate_to_english(prompt)
    st.info(f"DEBUG Prompt: {eng_prompt}") # باش نشوفو واش واصل
    try:
        with st.spinner("كنولد الفيديو... 20 ثانية ⚡"):
            output = replicate.run("wan-video/wan-2.2-a14b", input={"prompt": eng_prompt, "duration": 5, "aspect_ratio": "1:1", "fps": 16})
        video_url = output[0] if isinstance(output, list) else output
        video_bytes = requests.get(video_url).content
        return video_bytes, "Replicate Wan 2.2", None
    except Exception as e:
        return None, None, str(e)

def speak(text):
    tts = gTTS(text=text, lang='ar')
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("video"):
            st.video(msg["video"])
            st.caption(f"المصدر: {msg['source']}")
        elif msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")
        else:
            st.markdown(msg["content"])

uploaded_file = st.file_uploader("📸 صيفط صورة", type=["png", "jpg", "jpeg"], key="uploader")

col1, col2 = st.columns(2)
with col1:
    prompt_image = st.chat_input("كتب سؤالك على الصورة هنا...", key="input1")
with col2:
    prompt_main = st.chat_input("كتب سؤالك هنا... ولا 'ولد ليا فيديو/صورة ديال...'", key="input2")

# معالجة الصندوق الثاني
if prompt_main:
    with st.chat_message("user"):
        st.markdown(prompt_main)
    st.session_state.messages.append({"role": "user", "content": prompt_main})

    if "فيديو" in prompt_main:
        with st.chat_message("assistant"):
            video, source, error = generate_video_replicate(prompt_main)
            if video:
                st.video(video)
                st.caption(f"المصدر: {source}")
                audio = speak("ها هو الفيديو ديالك")
                st.audio(audio, format="audio/mp3")
                st.session_state.messages.append({"role": "assistant", "video": video, "source": source, "audio": audio})
            else:
                st.error(f"خطأ: {error}")
                st.warning("شوف الكريدت ديالك فـ replicate.com/account/billing")

    elif "صورة" in prompt_main:
        with st.chat_message("assistant"):
            st.info("كنرسم الصورة...")
            # كود الصورة هنا...

    else:
        with st.chat_message("assistant"):
            response = client.chat.completions.create(messages=[{"role": "system", "content": "نتا RAM Bot. المطور رضا مالكي."}, {"role": "user", "content": prompt_main}], model="llama-3.3-70b-versatile", max_tokens=300).choices[0].message.content
            st.markdown(response)
            audio = speak(response)
            st.audio(audio, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio})

# معالجة الصورة
if uploaded_file and prompt_image:
    # كود الصورة هنا...

if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.rerun()
