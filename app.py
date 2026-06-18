import streamlit as st
from groq import Groq
import base64
import requests
import io
import urllib.parse
import random
from gtts import gTTS

st.set_page_config(page_title="RAM Bot v4.2 Voice", page_icon="🌍", layout="centered")

# التوكن
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
except KeyError:
    st.error("⚠️ GROQ_KEY ناقص! سير Settings > Secrets وحط التوكن ديالك")
    st.stop()

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
    <h1>🌍 RAM Bot v4.2</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>يفهم جميع اللغات + صوت + صور AI فابور 📚</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def detect_lang(text):
    if any(word in text.lower() for word in ["hello", "hi", "what", "how"]):
        return "en"
    elif any(word in text for word in ["bonjour", "salut", "comment"]):
        return "fr"
    elif any(word in text for word in ["hola", "qué", "cómo"]):
        return "es"
    else:
        return "ar"

def translate_to_english(text):
    text = text.lower().replace("ولد ليا صورة ديال", "").replace("ولد ليا", "").replace("draw", "").replace("generate", "").strip()
    dict = {
        "قط": "cat cute, detailed, 4k",
        "cat": "cat cute, detailed, 4k",
        "كلب": "dog cute, running, detailed",
        "dog": "dog cute, running, detailed",
        "بحر": "ocean waves, sunset, cinematic",
        "sea": "ocean waves, sunset, cinematic",
        "غوكو": "Goku Dragon Ball, flying, super saiyan, anime style",
        "goku": "Goku Dragon Ball, flying, super saiyan, anime style"
    }
    for ar, en in dict.items():
        if ar in text:
            return en + ", high quality, 4k"
    return text + ", high quality, 4k" if text else "beautiful scene, 4k"

def generate_image(prompt):
    with st.spinner("Generating image... 3 ثواني 🎨"):
        eng_prompt = translate_to_english(prompt)
        st.info(f"Prompt: {eng_prompt}")
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng_prompt)}?width=1024&height=1024&model=flux&nologo=true&seed={random.randint(1,9999)}"
        response = requests.get(url, timeout=30)
        return response.content if response.status_code == 200 else None

def speak(text, lang="ar"):
    lang_map = {"ar": "ar", "en": "en", "fr": "fr", "es": "es"}
    tts = gTTS(text=text, lang=lang_map.get(lang, "ar"))
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

# رسم الرسائل القديمة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image") and msg["image"]!= "ai":
            st.image(msg["image"], width=300)
        elif msg.get("image") == "ai":
            st.image(msg["content"], caption=msg.get("prompt"))
        elif msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")
        else:
            st.markdown(msg["content"])

# رفع الصورة
uploaded_file = st.file_uploader("📸 Upload image للحل", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

# الصوت - هادا هو الحل الجديد
audio = st.audio_input("🎤 سجل صوتك هنا - كيعرف جميع اللغات")

# الصندوق الأول: للصور
prompt_image = st.chat_input("Ask about image...", key="input_image")

# الصندوق الثاني: للدردشة والصور
prompt_main = st.chat_input("Write in any language... Ask for image with 'draw...' or 'ولد ليا...'", key="input_main")

# معالجة الصوت الجديد
if audio:
    with st.spinner("كنسمعك وكنحول للكتابة..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio.getvalue()),
            model="whisper-large-v3",
            response_format="text",
            language=None
        )
        prompt_main = transcription
        st.success(f"سمعتك: {prompt_main}")
        st.rerun()

# معالجة الصندوق الثاني
if prompt_main:
    with st.chat_message("user"):
        st.markdown(prompt_main)
    st.session_state.messages.append({"role": "user", "content": prompt_main})

    lang = detect_lang(prompt_main)

    if "صورة" in prompt_main or "draw" in prompt_main.lower() or "generate image" in prompt_main.lower():
        with st.chat_message("assistant"):
            result = generate_image(prompt_main)
            if result:
                st.image(result, caption="AI Generated - Flux")
                audio_bytes = speak("Here's your image" if lang=="en" else "ها هي الصورة ديالك", lang)
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.messages.append({"role": "assistant", "content": result, "image": "ai", "prompt": prompt_main, "audio": audio_bytes})
            else:
                st.error("Failed to generate image")

    else:
        with st.chat_message("assistant"):
            system_msg = f"You are RAM Bot v4.2 by Reda Malki. Answer in the same language as user: {lang}. Be brief and clear."
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt_main}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=400
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response, lang)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

# معالجة الصورة + الصندوق الأول
if uploaded_file is not None and prompt_image:
    image_b64 = base64.b64encode(uploaded_file.getvalue()).decode()
    image_url = f"data:image/jpeg;base64,{image_b64}"
    with st.chat_message("user"):
        st.image(uploaded_file, width=300)
        st.markdown(prompt_image)
    st.session_state.messages.append({"role": "user", "content": prompt_image, "image": uploaded_file})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing image..."):
            lang = detect_lang(prompt_image)
            system_prompt = {"role": "system", "content": f"You are RAM Bot. Answer in {lang}. Solve step by step and explain clearly."}
            user_content = [{"type": "text", "text": prompt_image}, {"type": "image_url", "image_url": {"url": image_url}}]
            chat_completion = client.chat.completions.create(
                messages=[system_prompt, {"role": "user", "content": user_content}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                max_tokens=800
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response, lang)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})
            st.session_state.uploader_key += 1
            st.rerun()

# زر المسح
if st.button("🗑️ Clear Chat", type="primary"):
    st.session_state.messages = []
    st.session_state.uploader_key += 1
    st.success("Cleared!")
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>Made with ❤️ by Reda Malki | Voice + Multilingual 🌍</div>", unsafe_allow_html=True)
