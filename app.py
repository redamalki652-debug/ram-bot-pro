import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from langdetect import detect

st.set_page_config(page_title="RAM Bot v4.7 AI", page_icon="🤖", layout="centered")

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 الـ GROQ_KEY ماشي موجود. مشي للـ Settings > Secrets")
    st.stop()

# ====== اختيار ذكي للموديلات المتاحة ======
@st.cache_data
def get_available_models():
    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data]

        # الأولوية للنص: نختارو الأحسن اللي فيه 70b
        text_priority = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        text_model = next((m for m in text_priority if m in model_ids), None)

        # الأولوية للـ Vision
        vision_priority = [
            "qwen/qwen3.6-27b",
            "qwen/qwen2.5-vl-32b",
            "llama-3.2-11b-vision-preview",
            "llama-3.2-90b-vision-preview"
        ]
        vision_model = next((m for m in vision_priority if m in model_ids), None)

        return text_model, vision_model, model_ids
    except Exception as e:
        st.error(f"خطأ فجلب الموديلات: {e}")
        return None, None, []

TEXT_MODEL, VISION_MODEL, ALL_MODELS = get_available_models()
MAX_TOKENS = 512 # جميع الموديلات دابا 512
# ============================================================

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
    <h1>🤖 RAM Bot v4.7 ⚡ AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
</div>
""", unsafe_allow_html=True)

# عرض الموديلات المختارة
if TEXT_MODEL:
    st.success(f"🧠 **Text Model**: `{TEXT_MODEL}`")
else:
    st.error("🚨 ما لقيناش Text Model متاح")

if VISION_MODEL:
    st.success(f"👁️ **Vision Model**: `{VISION_MODEL}`")
else:
    st.warning("⚠️ ما كاينش Vision Model متاح. تحليل الصور معطل")

with st.expander("📋 شوف جميع الموديلات المتاحة عندك"):
    if ALL_MODELS:
        st.code("\n".join(ALL_MODELS))
    else:
        st.write("ما قدرتش نجيب الموديلات")

lang_map_tts = {'ar': 'ar', 'fr': 'fr', 'en': 'en'}

def detect_language(text):
    try:
        lang = detect(text)
        if lang.startswith('ar'): return 'ar'
        if lang.startswith('fr'): return 'fr'
        return 'en'
    except: return 'ar'

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang_map_tts.get(lang, 'ar'), slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except: return None

def speech_to_text(audio_bytes):
    try:
        with sr.AudioFile(audio_bytes) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio, language='ar-MA')
    except: return ""

def encode_image(image):
    image_bytes = image.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = image.type or "image/jpeg"
    return image_base64, mime_type

def generate_image(prompt):
    with st.spinner("⚡ كنرسم فـ 3 ثواني..."):
        try:
            clean_prompt = prompt.replace("ولد ليا", "").strip()
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_prompt)}?width=512&height=512&nologo=true"
            response = requests.get(url, timeout=30)
            return response.content if response.status_code == 200 else f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

def call_groq_text(messages):
    if not TEXT_MODEL: return None, "ما كاينش Text Model متاح"
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=TEXT_MODEL,
            temperature=0.7,
            max_tokens=MAX_TOKENS
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e) # كنرجعو الخطأ كامل

def call_groq_vision(user_question, image_base64, mime_type):
    if not VISION_MODEL:
        return None, "ما كاينش Vision Model متاح للـ API key ديالك"
    try:
        messages_with_image = [{
            "role": "user",
            "content": [
                {"type": "text", "text": user_question},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}}
            ]
        }]
        chat_completion = client.chat.completions.create(
            messages=messages_with_image,
            model=VISION_MODEL,
            temperature=0.7,
            max_tokens=MAX_TOKENS
        )
        return chat_completion.choices[0].message.content, None
    except Exception as e:
        return None, str(e) # كنرجعو الخطأ كامل

def clear_chat():
    st.session_state.messages = []
    st.session_state.uploaded_image = None
    st.session_state.uploader_key += 1
    st.session_state.chat_key += 100
    st.rerun()

if "messages" not in st.session_state: st.session_state.messages = []
if "uploaded_image" not in st.session_state: st.session_state.uploaded_image = None
if "uploader_key" not in st.session_state: st.session_state.uploader_key = 0
if "chat_key" not in st.session_state: st.session_state.chat_key = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"], autoplay=False)
        if "image" in msg and msg["image"]: st.image(msg["image"])
        st.markdown(msg["content"])

st.markdown('<p class="section-title">📸❓ رفع الصورة وسول عليها</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload PNG, JPG, WebP", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed", key=f"uploader_{st.session_state.uploader_key}")

if uploaded_file:
    st.session_state.uploaded_image = uploaded_file
    st.image(uploaded_file, width=250, caption="الصورة مرفوعة. هضر أو كتب سؤالك")

st.markdown('<p class="section-title">🎤 هضر</p>', unsafe_allow_html=True)
audio_value = st.audio_input(" ", label_visibility="collapsed", key=f"audio_{st.session_state.chat_key}")

if audio_value:
    with st.spinner("كنسمعك..."):
        user_text = speech_to_text(audio_value)
        if user_text:
            detected_lang = detect_language(user_text)
            if st.session_state.uploaded_image is not None:
                with st.spinner("كنحلل الصورة بالصوت..."):
                    image_base64, mime_type = encode_image(st.session_state.uploaded_image)
                    response, error = call_groq_vision(user_text, image_base64, mime_type)
                    if error: st.error(f"🚨 خطأ Vision: {error}") # عرض الخطأ كامل
                    else:
                        audio_response = text_to_speech(response, detected_lang)
                        st.session_state.messages.append({"role": "user", "content": f"[صوت على صورة] {user_text}"})
                        st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
                        with st.chat_message("assistant"):
                            st.markdown(response)
                            if audio_response: st.audio(audio_response, autoplay=False)
                        st.session_state.uploaded_image = None
                        st.rerun()
            else:
                st.session_state.messages.append({"role": "user", "content": user_text})
                system_prompt = {"role": "system", "content": "نتا RAM Bot v4.7. المطور ديالك رضا مالكي. جاوب بالعربية المغربية باختصار."}
                response, error = call_groq_text([system_prompt] + st.session_state.messages)
                if error: st.error(f"🚨 خطأ Text: {error}") # عرض الخطأ كامل
                else:
                    audio_response = text_to_speech(response, detected_lang)
                    with st.chat_message("assistant"):
                        st.markdown(response)
                        if audio_response: st.audio(audio_response, autoplay=False)
                    st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

st.button("🗑️ مسح المحادثة", on_click=clear_chat)

prompt_text_only = st.chat_input("كتب سؤالك... ولا 'ولد ليا صورة'")
if prompt_text_only:
    detected_lang = detect_language(prompt_text_only)

    if any(word in prompt_text_only for word in ["ولد ليا", "generate", "draw"]):
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                st.download_button("📥 تحميل", image_bytes, "ram-bot-image.png")
                st.session_state.messages.append({"role": "assistant", "content": "تفضل الصورة ديالك", "image": image_bytes})
            else: st.error(f"خطأ: {image_bytes}")

    elif st.session_state.uploaded_image is not None:
        with st.spinner("كنحلل الصورة..."):
            image_base64, mime_type = encode_image(st.session_state.uploaded_image)
            response, error = call_groq_vision(prompt_text_only, image_base64, mime_type)
            if error: st.error(f"🚨 خطأ Vision: {error}") # عرض الخطأ كامل
            else:
                audio_response = text_to_speech(response, detected_lang)
                st.session_state.messages.append({"role": "user", "content": f"[صورة] {prompt_text_only}"})
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
                with st.chat_message("assistant"):
                    st.markdown(response)
                    if audio_response: st.audio(audio_response, autoplay=False)
                st.session_state.uploaded_image = None
                st.rerun()

    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v4.7. جاوب بالعربية المغربية باختصار."}
            response, error = call_groq_text([system_prompt] + st.session_state.messages)
            if error: st.error(f"🚨 خطأ Text: {error}") # عرض الخطأ كامل
            else:
                audio_response = text_to_speech(response, detected_lang)
                st.markdown(response)
                if audio_response: st.audio(audio_response, autoplay=False)
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

st.markdown('<div class="footer">صنع بـ ❤️ بواسطة رضا مالكي</div>', unsafe_allow_html=True)
