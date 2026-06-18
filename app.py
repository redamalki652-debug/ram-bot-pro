import streamlit as st
from groq import Groq
import base64
import requests
import io
import urllib.parse
import random
from gtts import gTTS

st.set_page_config(page_title="RAM Bot v5.0", page_icon="🌍", layout="centered")

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
    <h1>🌍 RAM Bot v5.0</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>يفهم 100+ لغة + صوت + صور + مسح مضمون ✅</p>
</div>
""", unsafe_allow_html=True)

# Session state بسيط بزاف
if "messages" not in st.session_state:
    st.session_state.messages = []
if "key" not in st.session_state:
    st.session_state.key = random.randint(1, 999)

def translate_to_english(text):
    text = text.lower().replace("ولد ليا صورة ديال", "").replace("draw", "").strip()
    dict = {"قط": "cat cute 4k", "غوكو": "Goku Dragon Ball super saiyan anime", "كلب": "dog cute running 4k"}
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

def speak(text):
    # gTTS كيعرف 60+ لغة وكيحددها بوحدو
    tts = gTTS(text=text, lang='auto')
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

# رفع الصورة - key كيتبدل ملي نمسحو
uploaded_file = st.file_uploader("📸 صيفط صورة للحل", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.key}")

# الصوت - Whisper كيعرف 99 لغة تلقائيا
audio = st.audio_input("🎤 سجل صوتك بأي لغة - دارجة، إنجليزية، فرنسية...")

# الصناديق
prompt_image = st.chat_input("سول على الصورة...", key=f"img_{st.session_state.key}")
prompt_main = st.chat_input("كتب بأي لغة... ولا 'ولد ليا صورة'", key=f"main_{st.session_state.key}")

# معالجة الصوت
if audio:
    with st.spinner("كنسمعك بأي لغة..."):
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio.getvalue()),
            model="whisper-large-v3",
            response_format="text",
            language=None # None = كيعرف اللغة بوحدو
        )
        st.session_state.messages.append({"role": "user", "content": transcription})
        st.success(f"سمعتك: {transcription}")
        prompt_main = transcription # ندوزو النص للمعالجة

# معالجة النص
if prompt_main:
    st.session_state.messages.append({"role": "user", "content": prompt_main})

    if "صورة" in prompt_main or "draw" in prompt_main.lower() or "generate" in prompt_main.lower():
        with st.chat_message("assistant"):
            result = generate_image(prompt_main)
            if result:
                st.image(result, caption="AI Generated - Flux")
                audio_bytes = speak("ها هي الصورة ديالك")
                st.audio(audio_bytes, format="audio/mp3")
                st.session_state.messages.append({"role": "assistant", "content": result, "image": "ai", "prompt": prompt_main, "audio": audio_bytes})
            else:
                st.error("ما قدرتش نرسم")
    else:
        with st.chat_message("assistant"):
            # النظام: جاوب بنفس اللغة اللي هضر بيها المستخدم - 100+ لغة
            system_msg = "You are RAM Bot v5.0 by Reda Malki. Detect the user's language and reply in the EXACT same language. Keep it short and friendly."
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": system_msg}] + st.session_state.messages,
                model="llama-3.3-70b-versatile",
                max_tokens=400
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

# معالجة الصورة
if uploaded_file and prompt_image:
    image_b64 = base64.b64encode(uploaded_file.getvalue()).decode()
    image_url = f"data:image/jpeg;base64,{image_b64}"
    st.session_state.messages.append({"role": "user", "content": prompt_image, "image": uploaded_file})
    with st.chat_message("assistant"):
        with st.spinner("كنقرا الصورة..."):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are RAM Bot. Detect language and reply in same language. Solve step by step."},
                         {"role": "user", "content": [{"type": "text", "text": prompt_image}, {"type": "image_url", "image_url": {"url": image_url}}]}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                max_tokens=800
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            audio_bytes = speak(response)
            st.audio(audio_bytes, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_bytes})

# زر المسح - الحل المضمون 100%
if st.button("🗑️ مسح المحادثة", type="primary", use_container_width=True):
    st.session_state.clear() # نمسحو كلشي
    st.session_state.key = random.randint(100000, 999) # نبدلو المفتاح
    st.success("تم المسح! الصفحة غتعاود تتحمل...")
    st.stop() # نوقفو هنا باش Streamlit يعاود يبني الصفحة من جديد

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>Made with ❤️ by Reda Malki | 100+ لغات 🌍</div>", unsafe_allow_html=True)
