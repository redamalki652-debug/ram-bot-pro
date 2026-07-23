import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
from langdetect import detect
import queue
import time
import wave
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av

st.set_page_config(page_title="RAM Bot v4.3 AI", page_icon="🤖", layout="centered")

# ========= 1. الاتصال بـ Groq =========
try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 الـ GROQ_KEY ماشي موجود. مشي للـ Settings > Secrets")
    st.stop()

# ========= 2. الستايل =========
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 1rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.2rem;}
.section-title {color: white; font-size: 1.5rem; font-weight: bold; margin-top: 1rem; margin-bottom: 0.5rem;}
.footer {text-align: center; color: white; font-size: 1.1rem; margin: 1rem 0; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="card"><h1>🤖 RAM Bot v4.3 ⚡ AI LIVE</h1><p><b>المطور:</b> رضا مالكي</p></div>""", unsafe_allow_html=True)

# ========= 3. دوال الـ AI =========
lang_map_tts = {'ar': 'ar', 'fr': 'fr', 'en': 'en', 'es': 'es', 'de': 'de'}

def detect_language(text):
    try:
        lang = detect(text)
        if lang.startswith('ar'): return 'ar'
        if lang.startswith('fr'): return 'fr'
        if lang.startswith('es'): return 'es'
        if lang.startswith('de'): return 'de'
        return 'en'
    except: return 'ar'

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def text_to_speech(text, lang):
    try:
        res = client.audio.speech.create(model="playai-tts", voice="Arman", input=text, response_format="wav")
        fp = BytesIO(res.read()); fp.seek(0); return fp
    except:
        fp = BytesIO(); gTTS(text=text, lang=lang_map_tts.get(lang, 'ar'), slow=False).write_to_fp(fp); fp.seek(0); return fp

def speech_to_text(audio_bytes):
    # نبنيو ملف wav صحيح 16khz mono s16
    wav_buffer = BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_bytes)
    wav_buffer.seek(0)
    wav_buffer.name = "audio.wav"

    res = client.audio.transcriptions.create(
        file=wav_buffer,
        model="whisper-large-v3-turbo",
        language="ar",
        prompt="دارجة مغربية"
    )
    return res.text

def generate_image(prompt):
    with st.spinner("⚡ كنرسم فـ 3 ثواني..."):
        try:
            clean_prompt = prompt.replace("ولد ليا", "").replace("generate", "").replace("draw", "").strip()
            encoded_prompt = urllib.parse.quote(clean_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
            response = requests.get(url, timeout=30)
            return response.content if response.status_code == 200 else f"Error: {response.status_code}"
        except Exception as e: return f"Error: {str(e)}"

def get_text_messages():
    return [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages if "content" in msg]

def call_groq(messages, max_tokens=2048):
    try:
        chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=max_tokens)
        return chat_completion.choices[0].message.content, None
    except Exception as e: return None, str(e)

# ========= 4. معالج الصوت اللحظي =========
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = BytesIO()
        self.last_send = time.time()

    def recv_audio(self, frame: av.AudioFrame):
        # نديرو resampling من 48k -> 16k و mono
        resampled_frame = frame.reformat(format='s16', rate=16000, layout='mono')
        self.audio_buffer.write(resampled_frame.to_bytes())

        if time.time() - self.last_send > 2.5:
            self.last_send = time.time()
            if self.audio_buffer.getbuffer().nbytes > 16000:
                st.session_state.audio_q.put(self.audio_buffer.getvalue())
            self.audio_buffer = BytesIO()
        return frame

def clear_chat():
    st.session_state.messages = []
    st.session_state.uploaded_image = None
    st.session_state.uploader_key += 1
    st.session_state.chat_key += 100
    st.session_state.last_image = None
    st.session_state.last_audio_hash = None

# ========= 5. حالة التطبيق =========
for key, default in [("messages",[]),("uploaded_image",None),("uploader_key",0),("chat_key",0),("last_image",None),("last_audio_hash",None),("audio_q",queue.Queue()),("is_bot_speaking",False)]:
    if key not in st.session_state: st.session_state[key] = default

# ========= 6. الواجهة =========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg and msg["audio"]: st.audio(msg["audio"], autoplay=(msg["role"]=="assistant"))
        if "image" in msg and msg["image"]: st.image(msg["image"]); st.session_state.last_image = msg["image"]
        st.markdown(msg["content"])

# القسم 1: سؤال بالصورة
st.markdown('<p class="section-title">📸❓ القسم 1: سؤال بالصورة</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key=f"uploader_{st.session_state.uploader_key}")
st.caption("PNG, JPG")
if uploaded_file:
    st.session_state.uploaded_image = uploaded_file
    st.session_state.last_image = uploaded_file
    st.image(uploaded_file, width=200)

# القسم 2: محادثة صوتية لحظية
st.markdown('<p class="section-title">🎤 القسم 2: محادثة صوتية</p>', unsafe_allow_html=True)
webrtc_ctx = webrtc_streamer(key="voice", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor, media_stream_constraints={"video": False, "audio": True})

if not st.session_state.audio_q.empty() and not st.session_state.is_bot_speaking:
    audio_data = st.session_state.audio_q.get()
    with st.spinner("كنفكر..."):
        st.session_state.is_bot_speaking = True
        try:
            user_text = speech_to_text(audio_data)
            if user_text and len(user_text) > 2:
                detected_lang = detect_language(user_text)
                st.session_state.messages.append({"role": "user", "content": user_text})
                system_prompt = {"role": "system", "content": "نتا RAM Bot v4.3. المطور ديالك رضا مالكي. كتشف اللغة و جاوب بنفسها. رد قصير جدا بجملة وحدة بالدارجة."}
                response, error = call_groq([system_prompt] + get_text_messages(), max_tokens=80)
                if not error:
                    audio_response = text_to_speech(response, detected_lang)
                    st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
        except Exception as e:
            st.error(f"خطأ فـ الصوت: {e}")
        st.session_state.is_bot_speaking = False
        st.rerun()

st.button("🗑️ مسح المحادثة", on_click=clear_chat, key=f"clear_{st.session_state.chat_key}")

# القسم 3: سول على الصورة
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
                system_prompt = {"role": "system", "content": "نتا RAM Bot v4.3. كتشف اللغة و جاوب بنفسها. إلا كانت تمارين حلها خطوة بخطوة."}
                user_content = [{"type": "text", "text": prompt_image_question}, {"type": "image_url", "image_url": {"url": image_url}}]
                messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
                response, error = call_groq(messages)
                if error: st.error(f"🚨 خطأ: {error}")
                else:
                    st.markdown(response)
                    audio_response = text_to_speech(response, detected_lang)
                    if audio_response: st.audio(audio_response, autoplay=True)
                    st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})
        st.session_state.uploaded_image = None
        st.session_state.uploader_key += 1
        st.session_state.chat_key += 1
        st.rerun()
    else: st.warning("⚠️ رفع صورة الاول ولا سول على اخر صورة تولدات")

# القسم 4: النص العادي + توليد الصور
prompt_text_only = st.chat_input("كتب بأي لغة... ولا 'ولد ليا صورة ديال قط'", key=f"chat_main_{st.session_state.chat_key}")
if prompt_text_only:
    detected_lang = detect_language(prompt_text_only)
    if any(word in prompt_text_only.lower() for word in ["ولد ليا", "generate", "draw", "صاوب ليا"]):
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes)
                st.session_state.last_image = image_bytes
                st.download_button("📥 تحميل الصورة", image_bytes, "ram_bot_image.png")
                audio_response = text_to_speech("تفضل الصورة ديالك", detected_lang)
                if audio_response: st.audio(audio_response, autoplay=True)
                st.session_state.messages.append({"role": "assistant", "content": "تفضل الصورة", "image": image_bytes, "audio": audio_response})
            else: st.error(f"خطأ: {image_bytes}")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text_only})
        with st.chat_message("assistant"):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v4.3. المطور ديالك رضا مالكي. كتشف اللغة و جاوب بنفسها. رد قصير ومباشر."}
            response, error = call_groq([system_prompt] + get_text_messages())
            if error: st.error(f"🚨 خطأ: {error}")
            else:
                audio_response = text_to_speech(response, detected_lang)
                st.markdown(response)
                if audio_response: st.audio(audio_response, autoplay=True)
                st.session_state.messages.append({"role": "assistant", "content": response, "audio": audio_response})

st.markdown('<div class="footer">صنع بـ ❤️ بواسطة رضا مالكي</div>', unsafe_allow_html=True)
