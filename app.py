import streamlit as st
from groq import Groq
import base64
import requests
import os
import replicate
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import urllib.parse

st.set_page_config(page_title="RAM Bot v2.2 AI", page_icon="🤖", layout="centered")

# Secrets
GROQ_KEY = st.secrets["GROQ_KEY"]
REPLICATE_TOKEN = st.secrets["REPLICATE_TOKEN"]
client = Groq(api_key=GROQ_KEY)
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

# الواجهة
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

def translate_to_english(text):
    prompt = f"Translate this Moroccan Darija to English for AI image/video generation, only output English: {text}"
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except:
        return text.replace("ولد ليا", "").replace("صاوب ليا", "").replace("رسم ليا", "").replace("صورة ديال", "").replace("فيديو ديال", "").strip()

def generate_image(prompt):
    with st.spinner("كنرسم ليك الصورة... 🎨"):
        try:
            eng_prompt = translate_to_english(prompt)
            st.info(f"Prompt: {eng_prompt}")

            url = f"https://image.pollinations.ai/prompt/{eng_prompt}?width=1024&height=1024&model=flux&enhance=true&nologo=true"
            response = requests.get(url, timeout=45)

            if response.status_code == 200:
                return response.content
            else:
                return f"Error {response.status_code}: {response.text[:100]}"
        except Exception as e:
            return f"Error: {str(e)}"

def generate_video_pollinations(prompt):
    """Backup مجاني 100%"""
    try:
        eng_prompt = translate_to_english(prompt)
        encoded = urllib.parse.quote(eng_prompt)
        url = f"https://image.pollinations.ai/video/{encoded}?model=alegria&nologo=true"

        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return response.content, "Pollinations مجاني"
        else:
            return None, f"Pollinations Error {response.status_code}"
    except Exception as e:
        return None, str(e)

def generate_video(prompt):
    with st.spinner("كنولد الفيديو... صبر 30 ثانية 🎬"):
        eng_prompt = translate_to_english(prompt)
        st.info(f"Prompt: {eng_prompt}")

        # المحاولة 1: Replicate المجاني
        try:
            output = replicate.run(
                "wavespeedai/wan-2.1-i2v-14b-720",
                input={"prompt": eng_prompt, "duration": 5, "fps": 16}
            )
            if output:
                video_url = str(output)
                with st.spinner("كنحمل من Replicate..."):
                    video_response = requests.get(video_url, timeout=60)
                    if video_response.status_code == 200:
                        return video_response.content, "Replicate مجاني"
        except Exception as e:
            st.warning(f"Replicate بلع: {str(e)[:50]}... كنجرب Pollinations")

        # المحاولة 2: Pollinations backup فابور
        video_bytes, source = generate_video_pollinations(prompt)
        if video_bytes:
            return video_bytes, source
        else:
            return f"Error: Replicate و Pollinations بجوج فشلو. {source}", source

def speak(text):
    tts = gTTS(text=text, lang='ar')
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

# الذاكرة
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
                st.image(msg["content"], caption="صورة مولدة")
            elif "video" in msg:
                st.video(msg["video"])
                if "source" in msg:
                    st.caption(f"المصدر: {msg['source']}")
            elif "audio" in msg:
                st.audio(msg["audio"], format="audio/mp3")
            else:
                st.markdown(msg["content"])

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

prompt_with_image = st.chat_input("كتب سؤالك على الصورة هنا...", key="chat_input_img")
prompt_text_only = st.chat_input("كتب سؤالك هنا... ولا قول 'ولد ليا صورة/فيديو ديال...'", key="chat_input_text")

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
    image_b64 = encode_image(uploaded_file)
    image_url = f"data:image/jpeg;base64,{image_b64}"
    with st.chat_message("user"):
        st.image(uploaded_file, width=300)
        st.markdown(prompt_with_image)
    with st.chat_message("assistant"):
        with st.spinner("كنقرا الصورة..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v2.2. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية. إلا عطاوك صورة ديال بطاقة خرج المعلومات."}
            user_content = [{"type": "text", "text": prompt_with_image}, {"type": "image_url", "image_url": {"url": image_url}}]
            messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
            chat_completion = client.chat.completions.create(messages=messages, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, max_tokens=500)
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "user", "content": prompt_with_image, "image": uploaded_file})
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

elif prompt_text_only:
    # صورة
    if any(word in prompt_text_only for word in ["ولد ليا صورة", "صاوب ليا صورة", "رسم ليا", "صورة ديال"]):
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            result = generate_image(prompt_text_only)
            if isinstance(result, bytes):
                st.image(result)
                response = "ها هي الصورة ديالك 🎨"
                audio_bytes = speak(response)
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes, "image": "ai_generated"})
            else:
                st.error(f"خطأ فتوليد الصورة: {result}")

    # فيديو - دابا فيه 2 مصادر
    elif any(word in prompt_text_only for word in ["ولد ليا فيديو", "صاوب ليا فيديو", "فيديو ديال"]):
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            result, source = generate_video(prompt_text_only)
            if isinstance(result, bytes):
                st.video(result)
                st.caption(f"المصدر: {source}")
                response = f"ها هو الفيديو ديالك 🎬 من {source}"
                audio_bytes = speak(response)
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes, "video": result, "source": source})
            else:
                st.error(f"خطأ: {result}")
    else:
        process_text_only(prompt_text_only)

# مسح المحادثة
if st.button("🗑️ مسح المحادثة", use_container_width=True, type="primary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.success("تم مسح المحادثة ✅")
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
