import streamlit as st
import os
import replicate
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
from groq import Groq
import io
from PIL import Image
import pytesseract

# قراية الـ Secrets
GROQ_KEY = st.secrets["GROQ_KEY"]
REPLICATE_TOKEN = st.secrets["REPLICATE_TOKEN"]

client = Groq(api_key=GROQ_KEY)
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_TOKEN

st.set_page_config(page_title="Ram Bot Pro", page_icon="🤖")
st.title("🤖 Ram Bot Pro - بوت الصور والفيديو والقراية")

# الميكروفون
audio = mic_recorder(start_prompt="🎤 سجل", stop_prompt="⏹️ وقف", key="recorder")
if audio:
    st.audio(audio["bytes"])

prompt = st.text_input("كتب ليا شنو بغيتي:")

# هنا الأيقونات/الأزرار
col1, col2, col3, col4 = st.columns(4)

# زر الصورة
with col1:
    if st.button("🖼️ ولد صورة"):
        if prompt:
            with st.spinner("كنولد الصورة..."):
                output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                st.image(output[0])

# زر الفيديو
with col2:
    if st.button("🎬 ولد فيديو"):
        if prompt:
            with st.spinner("كنولد الفيديو..."):
                output = replicate.run("minimax/video-01", input={"prompt": prompt})
                st.video(output)

# زر الهضرة
with col3:
    if st.button("🔊 هضر"):
        if prompt:
            tts = gTTS(text=prompt, lang='ar')
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            st.audio(buf.getvalue(), format="audio/mp3")

# زر قراية الصورة - هادي الجديدة
with col4:
    st.button("📄 قرا صورة", key="ocr_btn")

# رفع الصورة + قرايتها
uploaded_file = st.file_uploader("رفع بطاقة التعريف ولا أي صورة فيها كتابة", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة اللي رفعتي")

    if st.button("استخرج التمارين/النص"):
        with st.spinner("كنقرا الصورة..."):
            text = pytesseract.image_to_string(image, lang='ara+eng')
            st.success("هاهو النص اللي لقيت:")
            st.text_area("النص المستخرج", text, height=200)

            # يخرج تمارين من النص
            if "موطور" in text or "سياقة" in text:
                st.info("بغيتي نخرج ليك أسئلة من بطاقة التعريف ديال الموطور؟")
                questions = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"خرج ليا 5 أسئلة امتحان من هاد النص: {text}"}],
                    model="llama-3.1-8b-instant",
                )
                st.write(questions.choices[0].message.content)

# شات Groq العادي
if prompt:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    st.write(response.choices[0].message.content)
