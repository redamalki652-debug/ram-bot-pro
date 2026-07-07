import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS # باش يهضر
from io import BytesIO
import speech_recognition as sr # باش يسمعك

st.set_page_config(page_title="RAM Bot v2.3 Voice AI", page_icon="🤖", layout="centered")

GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)
recognizer = sr.Recognizer()

# CSS ناضي
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
.card p {color: #333; font-size: 1.1rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v2.3 Voice AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر + كيسمع + كيولد تصاور + جميع اللغات 🎨🎤🌍</p>
</div>
""", unsafe_allow_html=True)

# اختيار اللغة
lang_option = st.selectbox(
    "🌍 اختار اللغة / Choose Language",
    ("ar-MA", "fr-FR", "en-US", "ar", "es-ES"),
    format_func=lambda x: {"ar-MA":"الدارجة المغربية", "fr-FR":"Français", "en-US":"English", "ar":"العربية الفصحى", "es-ES":"Español"}[x]
)

lang_map_tts = {
    'ar-MA': 'ar',
    'fr-FR': 'fr',
    'en-US': 'en',
    'ar': 'ar',
    'es-ES': 'es'
}

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def text_to_speech(text, lang):
    """كنحولو النص للصوت"""
    try:
        tts = gTTS(text=text, lang=lang_map_tts[lang], slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

def speech_to_text(audio_bytes, lang):
    """كنحولو الصوت للنص"""
    with sr.AudioFile(audio_bytes) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language=lang)
        return text
    except:
        return "ما فهمتش مزيان، عاود / I didn't catch that"

def generate_image(prompt):
    with st.spinner("كنرسم ليك الصورة... صبر 20 ثانية 🎨"):
        try:
            clean_prompt = prompt.replace("ولد ليا", "").replace("صاوب ليا", "").replace("رسم ليا", "").replace("صورة ديال", "").replace("generate", "").replace("draw", "").strip()
            enhanced_prompt = f"professional high quality photo of {clean_prompt}, 4k, highly detailed, studio lighting"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&enhance=true"
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                return response.content
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]:
            st.audio(msg["audio"])
        if "image" in msg and msg["image"]:
            st.image(msg["image"])
        st.markdown(msg["content"])

# زر التسجيل بالصوت
audio_value = st.audio_input("🎤 دوس هنا و هضر / Press and speak")

if audio_value:
    st.audio(audio_value)
    with st.spinner("كنسمعك..."):
        user_text = speech_to_text(audio_value, lang_option)
        st.write(f"نتا قلتي: {user_text}")

        # نجاوبو بالـ Groq
        system_prompt = {"role": "system", "content": f"نتا RAM Bot v2.3. المطور ديالك رضا مالكي. جاوب باللغة {lang_option}. كون مفيد و خفيف الدم."}
        messages = [system_prompt] + [{"role": "user", "content": user_text}]
        chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7)
        response = chat_completion.choices[0].message.content

        # نحولو الجواب للصوت
        audio_response = text_to_speech(response, lang_option)

        with st.chat_message("assistant"):
            st.markdown(response)
            if audio_response:
                st.audio(audio_response)

        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

prompt_text_only = st.chat_input("كتب هنا... / Type here... ولا قول 'ولد ليا صورة ديال...'")

if prompt_text_only:
    # إلا طلب توليد صورة
    if any(word in prompt_text_only.lower() for word in ["ولد ليا", "صاوب ليا", "رسم ليا", "صورة ديال", "generate", "draw", "create image"]):
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes, caption="صورة مولدة بالذكاء الاصطناعي")
                st.download_button("📥 تحميل الصورة", image_bytes, "ram_bot_image.png", "image/png")
                audio_response = text_to_speech("ها هي الصورة ديالك", lang_option)
                if audio_response:
                    st.audio(audio_response)
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": f"ها هي الصورة ديال: {prompt_text_only}", "image": image_bytes, "audio": audio_response})
            else:
                st.error(f"ما قدرتش نولد الصورة: {image_bytes}")
    else:
        # محادثة نصية عادية
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            system_prompt = {"role": "system", "content": f"نتا RAM Bot v2.3. المطور ديالك رضا مالكي. جاوب باللغة {lang_option}. كون مفيد و خفيف الدم."}
            messages = [system_prompt] + [{"role": "user", "content": prompt_text_only}]
            chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7)
            response = chat_completion.choices[0].message.content
            audio_response = text_to_speech(response, lang_option)
            st.markdown(response)
            if audio_response:
                st.audio(audio_response)
            st.session_state.messages.append({"role": "user", "content": prompt_text_only})
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

if st.button("🗑️ مسح المحادثة / Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
