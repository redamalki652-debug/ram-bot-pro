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

st.set_page_config(page_title="RAM Bot v2.0 AI", page_icon="🤖", layout="centered")

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
    <h1>🤖 RAM Bot v2.0 AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>فيديو فابور 🎬 + صوت 🎤 + صور 📸</p>
</div>
""", unsafe_allow_html=True)

def translate_to_english(text):
    prompt = f"Translate this Moroccan Darija to English for AI: {text}"
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except:
        return text.replace("ولد ليا", "").replace("فيديو ديال", "").strip()

def generate_video_free(prompt):
    """فيديو فابور - Pollinations LTX"""
    eng_prompt = translate_to_english(prompt)
    st.info(f"Prompt: {eng_prompt}")

    seed = random.randint(1, 999)
    url = f"https://image.pollinations.ai/video/{urllib.parse.quote(eng_prompt)}?model=ltx-video&nologo=true&width=512&height=512&seed={seed}"

    try:
        with st.spinner("كنولد ليك الفيديو... صبر 40 ثانية"):
            response = requests.get(url, timeout=45)

        if response.status_code == 200 and len(response.content) > 50000:
            return response.content, "Pollinations LTX فابور"
        else:
            return None, f"السيرفر مضغوط دابا كود {response.status_code}. عاود من بعد 5 دقايق"

    except requests.exceptions.Timeout:
        return None, "طول بزاف، عاود المحاولة"
    except Exception as e:
        return None, f"خطأ: {str(e)}"

def speak(text):
    tts = gTTS(text=text, lang='ar')
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "video" in msg:
            st.video(msg["video"])
            st.caption(f"المصدر: {msg['source']}")
        elif "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")
        else:
            st.markdown(msg["content"])

audio = mic_recorder(start_prompt="🎤 سجل", stop_prompt="⏹️ وقف", key="recorder")
prompt_text = st.chat_input("كتب هنا... 'ولد ليا فيديو ديال...'")

if audio and audio["bytes"]:
    with st.spinner("كنسمعك..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio["bytes"]),
            model="whisper-large-v3",
            response_format="text",
            language="ar"
        )
        st.success(f"سمعتك: {transcription}")
        prompt_text = transcription

if prompt_text:
    with st.chat_message("user"):
        st.markdown(prompt_text)

    if any(word in prompt_text for word in ["فيديو"]):
        with st.chat_message("assistant"):
            result, source = generate_video_free(prompt_text)
            if isinstance(result, bytes):
                st.video(result)
                st.caption(f"المصدر: {source}")
                audio = speak("ها هو الفيديو ديالك فابور")
                st.audio(audio, format="audio/mp3")
                st.session_state.messages.append({"role": "user", "content": prompt_text})
                st.session_state.messages.append({"role": "assistant", "content": "تم", "video": result, "source": source})
            else:
                st.error(result)
                st.warning("💡 الحل: عاود المحاولة من بعد 5 دقايق ولا بسط البرومت لـ 2 كلمات")

    else:
        with st.chat_message("assistant"):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "نتا RAM Bot v2.0. المطور رضا مالكي. كتهضر بالدارجة."}, {"role": "user", "content": prompt_text}],
                model="llama-3.3-70b-versatile",
                max_tokens=300
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "user", "content": prompt_text})
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
