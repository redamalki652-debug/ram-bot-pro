import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from langdetect import detect

st.set_page_config(page_title="RAM Bot v2.9 AI", page_icon="🤖", layout="centered")

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
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v2.9 ⚡ AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>سريع 3s + كيهضر + كيقرا الصور 🎨🎤</p>
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
            enhanced_prompt = f"{clean_prompt}, high quality"
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            # رجعناها سريعة 512 بلا flux
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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"])
        if "image" in msg and msg["image"]: st.image(msg["image"])
        st.markdown(msg["content"])

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📸❓ سؤال بالصورة", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")
with col2:
    audio_value = st.audio_input("🎤 هضر")

if audio_value:
    st.audio(audio_value)
    with st.spinner("..."):
        user_text = speech_to_text(audio_value)
        if user_text:
            detected_lang = detect_language(user_text)
            st.session_state.messages.append({"role": "user", "content": user_text})

            system_prompt = {"role": "system", "content": f"نتا RAM Bot v2.9. المطور ديالك رضا مالكي. كتشف اللغة ديال المستخدم و جاوب بنفس اللغة تماما. كون طبيعي و قصير."}
            messages = [system_prompt] + get_text_messages()
            response, error = call_groq(messages)

            if error:
                st.error(f"🚨 خطأ من Groq: {error}")
            else:
                audio_response = text_to_speech(response, detected_lang)
                with st.chat_message("assistant"):
                    st.markdown(response)
                    if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

prompt_text_only = st.chat_input("كتب هنا... / Type here... ولا قول 'ولد ليا صورة ديال...'")

if uploaded_file is not None:
    prompt_for_image = st.text_input("❓ كتب السؤال ديال الصورة:", key="img_prompt")
    if st.button("📤 صيفط الصورة"):
        if prompt_for_image:
            image_b64 = encode_image(uploaded_file)
            image_url = f"data:image/jpeg;base64,{image_b64}"
            st.session_state.messages.append({"role": "user", "content": f"[صورة] {prompt_for_image}"})

            with st.chat_message("assistant"):
                with st.spinner("كنقرا الصورة..."):
                    detected_lang = detect_language(prompt_for_image)
                    system_prompt = {"role": "system", "content": f"نتا RAM Bot v2.9. كتشف اللغة و جاوب بنفسها. إلا كانت تمارين حلها خطوة بخطوة."}
                    user_content = [{"type": "text", "text": prompt_for_image}, {"type": "image_url", "image_url": {"url": image_url}}]
                    messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
                    response, error = call_groq(messages)

                    if error:
                        st.error(f"🚨 خطأ من Groq: {error}")
                    else:
                        st.markdown(response)
                        audio_response = text_to_speech(response, detected_lang)
                        if audio_response: st.audio(audio_response)
                        st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
            st.session_state.uploader_key += 1
            st.rerun()

elif prompt_text_only:
    detected_lang = detect_language(prompt_text_only)
    if any(word in prompt_text_only.lower() for word in ["ولد ليا", "generate", "draw", "صاوب ليا", "رسم ليا"]):
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                st.download_button("📥 تحميل", image_bytes, "image.png")
                audio_response = text_to_speech("تفضل الصورة ديالك", detected_lang)
                if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "assistant", "content": "تفضل الصورة", "image": image_bytes, "audio": audio_response})
            else:
                st.error(f"خطأ: {image_bytes}")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            system_prompt = {"role": "system", "content": f"نتا RAM Bot v2.9. كتشف اللغة و جاوب بنفسها."}
            messages = [system_prompt] + get_text_messages()
            response, error = call_groq(messages)
            if error:
                st.error(f"🚨 خطأ من Groq: {error}")
            else:
                audio_response = text_to_speech(response, detected_lang)
                st.markdown(response)
                if audio_response: st.audio(audio_response)
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
