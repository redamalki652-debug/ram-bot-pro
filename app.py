import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from langdetect import detect

st.set_page_config(page_title="RAM Bot v3.7 AI", page_icon="🤖", layout="centered")

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 الـ GROQ_KEY ماشي موجود. مشي للـ Settings > Secrets")
    st.stop()

recognizer = sr.Recognizer()

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 1rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.2rem;}
.section-title {color: white; font-size: 1.5rem; font-weight: bold; margin-top: 1rem;}
.footer {text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v3.7 ⚡ AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
</div>
""", unsafe_allow_html=True)

lang_map_tts = {'ar': 'ar', 'fr': 'fr', 'en': 'en', 'es': 'es', 'de': 'de'}

def detect_language(text):
    try:
        lang = detect(text)
        if lang.startswith('ar'): return 'ar'
        if lang.startswith('fr'): return 'fr'
        if lang.startswith('es'): return 'es'
        if lang.startswith('de'): return 'de'
        return 'en'
    except:
        return 'ar'

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang_map_tts.get(lang, 'ar'), slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except:
        return None

def speech_to_text(audio_bytes):
    with sr.AudioFile(audio_bytes) as source:
        audio = recognizer.record(source)
    try:
        for l in ['ar-MA', 'fr-FR', 'en-US']:
            try:
                return recognizer.recognize_google(audio, language=l)
            except: continue
        return ""
    except:
        return ""

def generate_image(prompt):
    with st.spinner("⚡ كنرسم فـ 3 ثواني..."):
        try:
            clean_prompt = prompt.replace("ولد ليا", "").replace("generate", "").strip()
            encoded_prompt = urllib.parse.quote(clean_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
            response = requests.get(url, timeout=30)
            return response.content if response.status_code == 200 else f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

def get_text_messages():
    return [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages if "content" in msg]

def call_groq(messages):
    try:
        chat_completion = client.chat.completions.create(
            messages=messages, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=2048
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

def clear_chat():
    st.session_state.messages = []
    st.session_state.uploaded_image = None
    st.session_state.uploader_key += 1
    st.session_state.chat_key += 1
    st.session_state.last_image = None

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "chat_key" not in st.session_state:
    st.session_state.chat_key = 0
if "last_image" not in st.session_state:
    st.session_state.last_image = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"])
        if "image" in msg and msg["image"]:
            st.image(msg["image"])
            st.session_state.last_image = msg["image"] # حفظ اخر صورة
        st.markdown(msg["content"])

# القسم 1: سؤال بالصورة
st.markdown('<p class="section-title">📸❓ سؤال بالصورة</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key=f"uploader_{st.session_state.uploader_key}")
st.caption("200MB per file • PNG, JPG")
if uploaded_file:
    st.session_state.uploaded_image = uploaded_file
    st.session_state.last_image = uploaded_file
    st.image(uploaded_file, width=200)

# القسم 2: هضر
st.markdown('<p class="section-title">🎤 هضر</p>', unsafe_allow_html=True)
audio_value = st.audio_input(" ", label_visibility="collapsed")

if audio_value:
    st.audio(audio_value)
    with st.spinner("..."):
        user_text = speech_to_text(audio_value)
        if user_text:
            detected_lang = detect_language(user_text)
            st.session_state.messages.append({"role": "user", "content": user_text})
            system_prompt = {"role": "system", "content": f"نتا RAM Bot v3.7. المطور ديالك رضا مالكي. كتشف اللغة و جاوب بنفسها."}
            messages = [system_prompt] + get_text_messages()
            response, error = call_groq(messages)
            if error: st.error(f"🚨 خطأ: {error}")
            else:
                audio_response = text_to_speech(response, detected_lang)
                with st.chat_message("assistant"):
                    st.markdown(response)
                    if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

st.button("🗑️ مسح المحادثة", on_click=clear_chat)

# الخانة 1 الفوقانية: سول على الصورة - ديما باينة
prompt_image_question = st.chat_input("سول على الصورة...", key=f"chat_img_{st.session_state.chat_key}")
if prompt_image_question:
    image_to_use = st.session_state.uploaded_image if st.session_state.uploaded_image else st.session_state.last_image
    if image_to_use:
        image_b64 = encode_image(image_to_use)
        image_url = f"data:image/jpeg;base64,{image_b64}"
        st.session_state.messages.append({"role": "user", "content": f"[صورة] {prompt_image_question}"})
        with st.chat_message("assistant"):
            with st.spinner("كنقرا الصورة..."):
                detected_lang = detect_language(prompt_image_question)
                system_prompt = {"role": "system", "content": f"نتا RAM Bot v3.7. كتشف اللغة و جاوب بنفسها. إلا كانت تمارين حلها خطوة بخطوة."}
                user_content = [{"type": "text", "text": prompt_image_question}, {"type":":image_url", "image_url": {"url": image_url}}]
                messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
                response, error = call_groq(messages)
                if error: st.error(f"🚨 خطأ: {error}")
                else:
                    st.markdown(response)
                    audio_response = text_to_speech(response, detected_lang)
                    if audio_response: st.audio(audio_response)
                    st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
        st.session_state.uploaded_image = None
        st.session_state.uploader_key += 1
        st.session_state.chat_key += 1
        st.rerun()
    else:
        st.warning("⚠️ رفع صورة الاول ولا سول على اخر صورة تولدات")

# FOOTER
st.markdown('<div class="footer">صنع بـ ❤️ بواسطة رضا مالكي</div>', unsafe_allow_html=True)

# الخانة 2 التحانية: العادية - ديما باينة
prompt_text_only = st.chat_input("كتب بأي لغة... ولا 'ولد ليا صورة'", key=f"chat_main_{st.session_state.chat_key}")

if prompt_text_only:
    detected_lang = detect_language(prompt_text_only)
    if any(word in prompt_text_only.lower() for word in ["ولد ليا", "generate", "draw", "صاوب ليا"]):
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                st.session_state.last_image = image_bytes
                st.download_button("📥 تحميل", image_bytes, "image.png")
                audio_response = text_to_speech("تفضل الصورة ديالك", detected_lang)
                if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "assistant", "content": "تفضل الصورة", "image": image_bytes, "audio": audio_response})
            else:
                st.error(f"خطأ: {image_bytes}")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            system_prompt = {"role": "system", "content": f"نتا RAM Bot v3.7. كتشف اللغة و جاوب بنفسها."}
            messages = [system_prompt] + get_text_messages()
            response, error = call_groq(messages)
            if error: st.error(f"🚨 خطأ: {error}")
            else:
                audio_response = text_to_speech(response, detected_lang)
                st.markdown(response)
                if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
