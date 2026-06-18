import streamlit as st
from groq import Groq
import base64
import requests
import io
import urllib.parse
import random
from gtts import gTTS

st.set_page_config(page_title="RAM Bot v4.5", page_icon="🌍", layout="centered")

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
except KeyError:
    st.error("⚠️ GROQ_KEY ناقص! سير Settings > Secrets")
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
    <h1>🌍 RAM Bot v4.5</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>صوت + كتابة + مسح مضمون ✅</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = random.randint(1, 9999)
if "process_now" not in st.session_state:
    st.session_state.process_now = None

def detect_lang(text):
    return "en" if any(w in text.lower() for w in ["hello", "hi"]) else "ar"

def translate_to_english(text):
    text = text.lower().replace("ولد ليا صورة ديال", "").replace("draw", "").strip()
    dict = {"قط": "cat cute 4k", "غوكو": "Goku Dragon Ball super saiyan anime"}
    for ar, en in dict.items():
        if ar in text:
            return en + ", high quality 4k"
    return text + ", high quality 4k" if text else "beautiful scene 4k"

def generate_image(prompt):
    with st.spinner("كنرسم... 3 ثواني 🎨"):
        eng_prompt = translate_to_english(prompt)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng_prompt)}?width=1024&height=1024&model=flux&nologo=true&seed={random.randint(1,9999)}"
        r = requests.get(url, timeout=30)
        return r.content if r.status_code == 200 else None

def speak(text, lang="ar"):
    tts = gTTS(text=text, lang="en" if lang=="en" else "ar")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

# رسم الرسائل
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image") == "ai":
            st.image(msg["content"], caption=msg.get("prompt"))
        elif msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")
        else:
            st.markdown(msg["content"])

# رفع الصورة
uploaded_file = st.file_uploader("📸 صيفط صورة", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

# الصوت
audio = st.audio_input("🎤 سجل صوتك هنا")

# الصناديق
prompt_image = st.chat_input("سول على الصورة...", key="input_image")
prompt_main = st.chat_input("كتب سؤالك...", key="input_main")

# الحل ديال الصوت: نعالجو دغيا بلا ما نوقفو
if audio and st.session_state.process_now!= "audio":
    st.session_state.process_now = "audio"
    with st.spinner("كنسمعك..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio.getvalue()),
            model="whisper-large-v3",
            response_format="text"
        )
        st.session_state.messages.append({"role": "user", "content": transcription})
        st.session_state.process_now = transcription # نخزن النص باش نعالجو لتحت
        st.success(f"سمعتك: {transcription}")

# نجمعو البرومبت
final_prompt = st.session_state.process_now if st.session_state.process_now and st.session_state.process_now!= "audio" else prompt_main

# معالجة الجواب
if final_prompt:
    lang = detect_lang(final_prompt)

    # إلا كان صورة
    if "صورة" in final_prompt or "draw" in final_prompt.lower():
        with st.chat_message("assistant"):
            result = generate_image(final_prompt)
            if result:
                st.image(result, caption="AI Generated")
                audio_bytes = speak("ها هي الصورة", lang)
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.messages.append({"role": "assistant", "content": result, "image": "ai", "prompt": final_prompt, "audio": audio_bytes})

    # إلا كان كلام عادي
    else:
        with st.chat_message("assistant"):
            system_msg = f"You are RAM Bot by Reda Malki. Answer in {lang}. Short, Moroccan dialect."
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": system_msg}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if isinstance(m.get("content"), str)],
                model="llama-3.3-70b-versatile",
                max_tokens=300
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response, lang)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

    st.session_state.process_now = None # نصفر باش ما يعاودش

# معالجة الصورة
if uploaded_file and prompt_image:
    image_b64 = base64.b64encode(uploaded_file.getvalue()).decode()
    image_url = f"data:image/jpeg;base64,{image_b64}"
    st.session_state.messages.append({"role": "user", "content": prompt_image, "image": uploaded_file})
    with st.chat_message("assistant"):
        with st.spinner("كنقرا الصورة..."):
            lang = detect_lang(prompt_image)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": f"Answer in {lang}"},
                         {"role": "user", "content": [{"type": "text", "text": prompt_image}, {"type": "image_url", "image_url": {"url": image_url}}]}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                max_tokens=600
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response, lang)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})
            st.session_state.uploader_key = random.randint(1000, 9999)

# زر المسح - الحل المضمون بلا switch_page
if st.button("🗑️ مسح المحادثة", type="primary", use_container_width=True, key="clear_btn"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.toast("تم المسح! ✅", icon="🗑️")
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>Made with ❤️ by Reda Malki</div>", unsafe_allow_html=True)
