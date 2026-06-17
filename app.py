import streamlit as st
import os
import replicate
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
from groq import Groq
import io

# قراية الـ Secrets
GROQ_KEY = st.secrets["GROQ_KEY"]
REPLICATE_TOKEN = st.secrets["REPLICATE_TOKEN"]

# ربط API
client = Groq(api_key=GROQ_KEY)
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

st.set_page_config(page_title="Ram Bot Pro", page_icon="🤖")
st.title("🤖 Ram Bot Pro - بوت الصور والفيديو")

# 1. الشات بالميكروفون
audio = mic_recorder(start_prompt="🎤 سجل", stop_prompt="⏹️ وقف", key="recorder")

if audio:
    st.audio(audio["bytes"])
    # هنا تقدر تزيد تحويل الصوت لنص إلا بغيتي

# 2. الشات بالكتابة
prompt = st.text_input("كتب ليا شنو بغيتي:")

col1, col2, col3 = st.columns(3)

# زر الصورة
with col1:
    if st.button("🖼️ ولد صورة"):
        if prompt:
            with st.spinner("كنولد الصورة..."):
                output = replicate.run(
                    "black-forest-labs/flux-schnell",
                    input={"prompt": prompt}
                )
                st.image(output[0])

# زر الفيديو - هنا صلحنا الموديل
with col2:
    if st.button("🎬 ولد فيديو"):
        if prompt:
            with st.spinner("كنولد الفيديو... صبر 30 ثانية"):
                output = replicate.run(
                    "minimax/video-01", # هادا الموديل اللي مفتوح ومضمون
                    input={"prompt": prompt}
                )
                st.video(output)

# زر الهضرة
with col3:
    if st.button("🔊 هضر"):
        if prompt:
            with st.spinner("كنهضر..."):
                tts = gTTS(text=prompt, lang='ar')
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                st.audio(buf.getvalue(), format="audio/mp3")

# 3. شات Groq العادي
if prompt and not st.button:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    st.write(response.choices[0].message.content)
