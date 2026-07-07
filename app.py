import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr

st.set_page_config(page_title="RAM Bot v2.6 AI", page_icon="🤖", layout="centered")

# 1. التحقق من الـ API KEY
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error(f"الـ GROQ_KEY ماشي موجود فـ Secrets. الخطأ: {e}")
    st.stop()

recognizer = sr.Recognizer()

# CSS
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v2.6 AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر + كيسمع + كيقرا الصور + كيحل التمارين 🎨🎤🌍</p>
</div>
""", unsafe_allow_html=True)

# جميع اللغات
lang_option = st.selectbox(
    "🌍 اختار اللغة / Choose Language",
    ("ar-MA", "fr-FR", "en-US", "ar", "es-ES", "de-DE"),
    format_func=lambda x: {
        "ar-MA":"الدارجة المغربية", "fr-FR":"Français", "en-US":"English",
        "ar":"العربية الفصحى", "es-ES":"Español", "de-DE":"Deutsch"
    }[x]
)

lang_map_tts = {'ar-MA': 'ar', 'fr-FR': 'fr', 'en-US': 'en', 'ar': 'ar', 'es-ES': 'es', 'de-DE': 'de'}
lang_name = {"ar-MA": "الدارجة المغربية", "fr-FR": "الفرنسية", "en-US": "الإنجليزية", "ar": "العربية", "es-ES": "الإسبانية", "de-DE": "الألمانية"}

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang_map_tts, slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

def speech_to_text(audio_bytes, lang):
    with sr.AudioFile(audio_bytes) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language=lang)
        return text
    except:
        return "ما فهمتش مزيان، عاود"

def generate_image(prompt):
    with st.spinner("كنرسم ليك الصورة... صبر 20 ثانية 🎨"):
        try:
            clean_prompt = prompt.replace("ولد ليا", "").replace("صاوب ليا", "").replace("رسم ليا", "").replace("صورة ديال", "").replace("generate", "").strip()
            enhanced_prompt = f"professional high quality photo of {clean_prompt}, 4k, highly detailed"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&enhance=true"
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                return response.content
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

def get_text_messages():
    text_msgs = []
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"] and "content" in msg:
            text_msgs.append({"role": msg["role"], "content": msg["content"]})
    return text_msgs

def call_groq(messages, model="llama-3.3-70b-versatile"):
    """دالة موحدة باش نكابتو الاخطاء"""
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=0.7,
            max_tokens=2048
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]:
            st.audio(msg["audio"])
        if "image" in msg and msg["image"]:
            st.image(msg["image"])
        st.markdown(msg["content"])

# رفع الصور
uploaded_file = st.file_uploader("📸 صيفط صورة / Upload Image", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

# الصوت
audio_value = st.audio_input("🎤 دوس هنا و هضر / Press and speak")

if audio_value:
    st.audio(audio_value)
    with st.spinner("كنسمعك..."):
        user_text = speech_to_text(audio_value, lang_option)
        st.write(f"نتا قلتي: {user_text}")

        system_prompt = {"role": "system", "content": f"نتا RAM Bot v2.6. المطور ديالك رضا مالكي. جاوب ب {lang_name}. كون قصير و مفيد."}
        messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_text}]
        response, error = call_groq(messages)

        if error:
            st.error(f"خطأ من Groq: {error}")
        else:
            audio_response = text_to_speech(response, lang_option)
            with st.chat_message("assistant"):
                st.markdown(response)
                if audio_response: st.audio(audio_response)
            st.session_state.messages.append({"role": "user", "content": user_text})
            st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

prompt_text_only = st.chat_input("كتب هنا... / Type here... ولا قول 'ولد ليا صورة ديال...'")

if uploaded_file is not None:
    prompt_for_image = st.text_input("كتب السؤال ديال الصورة هنا:", key="img_prompt")
    if st.button("صيفط الصورة"):
        if prompt_for_image:
            image_b64 = encode_image(uploaded_file)
            image_url = f"data:image/jpeg;base64,{image_b64}"
            with st.chat_message("user"):
                st.image(uploaded_file, width=300)
                st.markdown(prompt_for_image)

            with st.chat_message("assistant"):
                with st.spinner("كنقرا الصورة و كنحل..."):
                    system_prompt = {
                        "role": "system",
                        "content": f"نتا RAM Bot v2.6. المطور ديالك رضا مالكي. كتهضر ب {lang_name}. إلا عطاوك صورة وصفها مزيان. إلا كانت فيها تمارين ولا مسائل رياضيات حلها خطوة بخطوة. كون مفيد."
                    }
                    user_content = [{"type": "text", "text": prompt_for_image}, {"type": "image_url", "image_url": {"url": image_url}}]
                    messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
                    response, error = call_groq(messages, model="llama-3.3-70b-versatile") # استعملنا نفس الموديل للصور

                    if error:
                        st.error(f"خطأ من Groq: {error}")
                    else:
                        st.markdown(response)
                        audio_response = text_to_speech(response, lang_option)
                        if audio_response: st.audio(audio_response)
                        st.session_state.messages.append({"role": "user", "content": prompt_for_image})
                        st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
            st.session_state.uploader_key += 1
            st.rerun()
        else:
            st.warning("كتب شنو بغيتي نسول على الصورة")

elif prompt_text_only:
    if any(word in prompt_text_only.lower() for word in ["ولد ليا", "صاوب ليا", "رسم ليا", "صورة ديال", "generate", "draw"]):
        with st.chat_message("user"): st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes, caption="صورة مولدة بالذكاء الاصطناعي")
                st.download_button("📥 تحميل الصورة", image_bytes, "ram_bot_image.png")
                audio_response = text_to_speech("ها هي الصورة ديالك", lang_option)
                if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": f"ها هي الصورة ديال: {prompt_text_only}", "image": image_bytes, "audio": audio_response})
            else:
                st.error(f"ما قدرتش نولد الصورة: {image_bytes}")
    else:
        with st.chat_message("user"): st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            system_prompt = {"role": "system", "content": f"نتا RAM Bot v2.6. المطور ديالك رضا مالكي. جاوب ب {lang_name}. كون مفيد."}
            messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": prompt_text_only}]
            response, error = call_groq(messages)
            if error:
                st.error(f"خطأ من Groq: {error}")
            else:
                audio_response = text_to_speech(response, lang_option)
                st.markdown(response)
                if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

if st.button("🗑️ مسح المحادثة / Clear Chat"):
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
