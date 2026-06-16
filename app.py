import streamlit as st
import requests
from PIL import Image
import pytesseract

st.set_page_config(page_title="RAM Bot", page_icon="🤖", layout="centered")

st.markdown("""
<div dir="rtl" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 25px; color: white; text-align: right; margin-bottom: 25px;">
    <h1>🤖 RAM Bot v8.0</h1>
    <h3>كيجاوب على أي سؤال</h3>
    <p><b>👨‍💻 رضا مالكي</b></p>
</div>
""", unsafe_allow_html=True)

# ===== عواصم سريعة =====
CAPITALS = {
    'تركيا': 'أنقرة Ankara 🇹🇷', 'المغرب': 'الرباط 🇲🇦', 'مصر': 'القاهرة 🇪🇬',
    'السعودية': 'الرياض 🇸🇦', 'الجزائر': 'الجزائر العاصمة 🇩🇿', 'فرنسا': 'باريس Paris 🇫🇷',
    'امريكا': 'واشنطن دي سي 🇺🇸', 'الصين': 'بكين Beijing 🇨🇳', 'كوريا': 'سيول Seoul 🇰🇷',
    'اليابان': 'طوكيو Tokyo 🇯🇵', 'بريطانيا': 'لندن London 🇬🇧', 'المانيا': 'برلين Berlin 🇩🇪',
}

def get_weather(city="Casablanca"):
    try:
        url = f"https://wttr.in/{city}?format=4&lang=ar"
        r = requests.get(url, timeout=5)
        return f"🌤️ {r.text.strip()}" if r.status_code == 200 else None
    except:
        return None

def search_wikipedia(query):
    try:
        # نحيدو الكلمات الزايدة
        query = query.replace("شنو", "").replace("شحال", "").replace("علاش", "").replace("؟", "").strip()
        query = query.replace(" ", "_")
        url = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            data = r.json()
            extract = data.get('extract', '')
            # نختصرو الجواب
            if len(extract) > 500:
                extract = extract[:500] + "..."
            return f"**{data['title']}**\n\n{extract}"
    except:
        return None

def get_smart_response(user_msg):
    msg = user_msg.lower().strip()
    
    # 1. عواصم - جواب مباشر
    for country, capital in CAPITALS.items():
        if country in msg:
            return f"عاصمة {country} هي **{capital}**"

    # 2. الطقس - جواب مباشر
    if 'حرارة' in msg or 'طقس' in msg or 'سخونية' in msg:
        city = "Casablanca"
        if 'الرباط' in msg: city = "Rabat"
        if 'مراكش' in msg: city = "Marrakech"
        if 'طنجة' in msg: city = "Tangier"
        weather = get_weather(city)
        if weather:
            return weather
        return "ما قدرتش نجيب الطقس دابا 😅"

    # 3. أي سؤال آخر = ويكيبيديا طول بلا نقاش
    with st.spinner("🔍 كنقلب وكنجاوبك دابا..."):
        result = search_wikipedia(user_msg)
    
    if result:
        return f"🔍 {result}\n\nبغيتي تفاصيل كثر قولها ليا"
    
    # 4. إلا والو
    return f"ما لقيتش معلومات على '{user_msg}' دابا المعلم 😔 جرب سؤال آخر"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "السلام المعلم 👋 سولني على أي حاجة وغنجاوبك طول بلا لف ودوران!"}]

# الصور
uploaded_file = st.file_uploader("📸 صيفط صورة", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    try:
        text = pytesseract.image_to_string(image, lang='ara+eng')
        st.success(f"📝 قريت: {text}")
        st.session_state.messages.append({"role": "assistant", "content": f"من الصورة قريت:\n```\n{text}\n```\nهادا هو الجواب ولا نشرحو ليك؟"})
    except:
        st.error("خاص tesseract-ocr فـ packages.txt")
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("سولني على أي حاجة..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        response = get_smart_response(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
