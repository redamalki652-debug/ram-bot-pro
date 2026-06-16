import streamlit as st
import requests
from PIL import Image
import pytesseract

st.set_page_config(page_title="RAM Bot", page_icon="🤖", layout="centered")

st.markdown("""
<div dir="rtl" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 25px; color: white; text-align: right; margin-bottom: 25px;">
    <h1>🤖 RAM Bot v7.1</h1>
    <h3>كتابة + بحث + صور 📸</h3>
    <p><b>👨‍💻 رضا مالكي</b></p>
</div>
""", unsafe_allow_html=True)

CAPITALS = {
    'عاصمة الصين': 'عاصمة الصين هي **بكين Beijing** 🇨🇳',
    'عاصمة كوريا': 'عاصمة كوريا الجنوبية هي **سيول Seoul** 🇰🇷',
    'عاصمة المغرب': 'عاصمة المغرب هي **الرباط** 🇲🇦',
}

def get_weather(city="Casablanca"):
    try:
        url = f"https://wttr.in/{city}?format=4&lang=ar"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return f"🌤️ {r.text.strip()}"
        return None
    except:
        return "ما قدرتش نجيب الطقس دابا 😅"

def search_wikipedia(query):
    try:
        query = query.replace(" ", "_")
        url = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return f"🔍 **{data['title']}**\n{data['extract']}"
        return None
    except:
        return None

def get_smart_response(user_msg):
    msg = user_msg.lower().strip()
    for key, answer in CAPITALS.items():
        if key in msg:
            return answer
    if 'حرارة' in msg or 'طقس' in msg:
        city = "Casablanca"
        if 'الرباط' in msg: city = "Rabat"
        if 'مراكش' in msg: city = "Marrakech"
        return get_weather(city)
    with st.spinner("🔍 كنقلب..."):
        result = search_wikipedia(user_msg)
    if result:
        return result
    return f"المعلم سولني: عاصمة؟ طقس؟ ولا شي موضوع عام 👌"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "السلام المعلم 👋 دابا فيه الصور. صيفط صورة تمرين وغادي نقراها ليك!"}]

# ===== الصور OCR =====
uploaded_file = st.file_uploader("📸 صيفط صورة تمرين", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    with st.spinner("كنقرا فـ الصورة..."):
        try:
            text = pytesseract.image_to_string(image, lang='ara+eng')
            if text.strip():
                st.success(f"📝 قريت من الصورة:\n{text}")
                st.session_state.messages.append({"role": "assistant", "content": f"من الصورة قريت:\n```\n{text}\n```\nشنو ندير بيه المعلم؟"})
            else:
                st.warning("ما قدرتش نقرا والو فـ الصورة 😅")
        except Exception as e:
            st.error("خاص `tesseract-ocr` فـ packages.txt ودير Reboot")
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("سولني على أي حاجة..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("كنفكر..."):
            response = get_smart_response(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
