import streamlit as st
import requests
import re

st.set_page_config(page_title="RAM Bot OCR", page_icon="📚", layout="centered")

st.markdown("""
<div dir="rtl" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 35px; border-radius: 30px; color: white; text-align: right; margin-bottom: 30px;">
    <h1>📚 RAM Bot OCR PRO</h1>
    <h3>كيقرا التمارين من الصورة</h3>
    <p>📸 صيفط صورة + 🔍 بحث + 🧮 حاسبة</p>
    <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 20px 0;">
    <p><b>👨‍💻 رضا مالكي</b></p>
</div>
""", unsafe_allow_html=True)

CAPITALS = {
    'تركيا': 'أنقرة 🇹🇷', 'المغرب': 'الرباط 🇲🇦', 'مصر': 'القاهرة 🇪🇬',
    'السعودية': 'الرياض 🇸🇦', 'فرنسا': 'باريس 🇫🇷', 'امريكا': 'واشنطن 🇺🇸',
}

def calculate(expr):
    try:
        expr = expr.replace('شحال', '').replace('=', '').strip()
        expr = expr.replace('÷', '/').replace('×', '*').replace('x', '*')
        expr = re.sub(r'[^\d\+\-\*/\.\(\) ]', '', expr)
        if expr:
            result = eval(expr)
            return f"🧮 **{expr} = {result}** ✅"
    except:
        return None

def search_web(query):
    try:
        query = query.replace("شكون", "").replace("شنو", "").replace("علاش", "").replace("؟", "").strip()
        url = f"https://api.duckgo.com/?q={query}&format=json&no_html=1"
        r = requests.get(url, timeout=8)
        data = r.json()
        abstract = data.get('AbstractText', '')
        heading = data.get('Heading', query)
        if abstract and len(abstract) > 10:
            return f"🔍 **{heading}**\n\n{abstract[:500]}..."
        return None
    except:
        return None

def get_weather(city="Casablanca"):
    try:
        url = f"https://wttr.in/{city}?format=3&lang=ar"
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return f"🌤️ {r.text.strip()}"
    except:
        return None

# ===== OCR بـ OCR.space API - فابور وما كيطيحش =====
def read_image_ocr(image_file):
    try:
        url = "https://api.ocr.space/parse/image"
        payload = {
            'apikey': 'helloworld', # مفتاح فابور للتجربة
            'language': 'ara', # عربي + انجليزي
            'isOverlayRequired': False,
        }
        files = {'file': image_file}
        r = requests.post(url, data=payload, files=files, timeout=15)
        result = r.json()

        if result['IsErroredOnProcessing']:
            return None

        text = result['ParsedResults'][0]['ParsedText']
        return text.strip()
    except:
        return None

def get_response(msg):
    msg_lower = msg.lower().strip()

    calc = calculate(msg)
    if calc: return calc

    if 'طقس' in msg_lower:
        city = "Casablanca"
        if 'الرباط' in msg_lower: city = "Rabat"
        if 'البيضاء' in msg_lower or 'كازا' in msg_lower: city = "Casablanca"
        return get_weather(city)

    for country, capital in CAPITALS.items():
        if country in msg_lower:
            return f"🌍 عاصمة {country} هي **{capital}**"

    result = search_web(msg)
    if result:
        return result

    return f"المعلم '{msg}' ما لقيتلوش جواب دابا 😔"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "السلام المعلم 👋 صيفط ليا صورة التمرين وغنجاوبك"}]

# ===== رفع الصور OCR =====
st.markdown("### 📸 صيفط صورة التمرين")
uploaded_file = st.file_uploader("اختار صورة", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    st.image(uploaded_file, caption="التمرين ديالك", use_column_width=True)

    with st.spinner("🔍 كنقرا الكتابة من الصورة..."):
        text = read_image_ocr(uploaded_file)

        if text and len(text) > 3:
            st.success("✅ قريت التمرين:")
            st.text_area("النص:", text, height=150)
            st.session_state.last_text = text
            st.info("كتب دابا: حل ليا هاد التمرين")
        else:
            st.warning("ما قدرتش نقرا النص مزيان. صور التمرين بخط واضح")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("سولني..."):
    if "حل" in prompt.lower() and "last_text" in st.session_state:
        prompt = f"حل هاد التمرين: {st.session_state.last_text}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        response = get_response(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
