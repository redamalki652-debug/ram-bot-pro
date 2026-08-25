import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from langdetect import detect

st.set_page_config(page_title="RAM Bot v4.8 AI", page_icon="🤖", layout="centered")

try:
    GROQ_KEY = st.secrets["GROQ_KEY"]
    client = Groq(api_key=GROQ_KEY)
except:
    st.error("🚨 الـ GROQ_KEY ماشي موجود. مشي للـ Settings > Secrets")
    st.stop()

# ====== الإصلاح النهائي: Fallback آمن ======
@st.cache_data
def get_available_models():
    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        st.write("الموديلات اللي لقاهم:", model_ids) # مؤقت باش نشوفو

        text_priority = ["llama-3.3-70b-versatile","llama-3.1-70b-versatile","llama-3.1-8b-instant","llama3-8b-8192","gemma2-9b-it"]
        text_model = next((m for m in text_priority if m in model_ids), model_ids[0] if model_ids else "llama-3.1-8b-instant")

        vision_priority = ["qwen/qwen3.6-27b","qwen/qwen2.5-vl-32b","llama-3.2-11b-vision-preview"]
        vision_model = next((m for m in vision_priority if m in model_ids), None)

        return text_model, vision_model, model_ids
    except Exception as e:
        return "llama-3.1-8b-instant", None, []

TEXT_MODEL, VISION_MODEL, ALL_MODELS = get_available_models()
MAX_TOKENS = 512
# ============================================

#... باقي الكود كامل ديال v4.7 خليه هو هو...
