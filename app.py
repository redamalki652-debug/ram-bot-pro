import streamlit as st
import re
from PIL import Image

st.set_page_config(page_title="RAM Bot", page_icon="🤖", layout="centered")

st.markdown("""
<div dir="rtl" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 25px; color: white; text-align: right; margin-bottom: 25px;">
    <h1>🤖 RAM Bot v1</h1>
    <h3>كيجاوب على أي سؤال</h3>
    <p><b>👨‍💻 رضا مالكي</b></p>
</div>
""", unsafe_allow_html=True)

CAPITALS = {
    'تركيا': 'أنقرة Ankara 🇹🇷', 'المغرب': 'الرباط 🇲🇦', 'مصر': 'القاهرة 🇪🇬',
    'الصين': 'بكين Beijing 🇨🇳', 'امريكا': 'واشنطن دي سي 🇺🇸', 'فرنسا': 'باريس Paris 🇫🇷',
    'الجزائر': 'الجزائر العاصمة 🇩🇿', 'السعودية': 'الرياض 🇸🇦',
}

def calculate(expr):
    try:
        expr = expr.replace('شحال', '').replace('=', '').strip()
        expr = expr.replace('÷', '/').replace('×', '*').replace('x', '*')
        expr = re.sub(r'[^\d\+\-\*/\.\(\) ]', '', expr)
        if expr:
            result = eval(expr)
            return f"**{expr} = {result}** ✅"
    except:
        return None

def ai_answer(q):
    q = q.lower()
    if 'goku' in q:
        return "🔍 **Goku** هو البطل ديال Dragon Ball 🐉\nسايان من كوكب فيجيتا، كيتحول لـ Super Saiyan."
    if 'نيوتن' in q:
        return "🔍 **إسحاق نيوتن** عالم فيزياء إنجليزي 🏛️\nاكتشف قانون الجاذبية."
    if 'شكون انت' in q:
        return "أنا RAM Bot v1 🤖 صنعني رضا مالكي. كنحسب وكنجاوب على أي سؤال."
    if 'علاش السماء' in q:
        return "🔍 **علاش السماء زرقاء؟**\nحيت ضوء الشمس كيتفرق فـ الغلاف الجوي واللون الأزرق كيتشتت كثر."
    return None

def get_response(msg):
    msg_lower = msg.lower().strip()
    calc = calculate(msg)
    if calc: return calc
    for country, capital in CAPITALS.items():
        if country in msg_lower:
            return f"عاصمة {country} هي **{capital}**"
    ai = ai_answer(msg)
    if ai: return ai
    return f"المعلم سؤال '{msg}' ما عرفتش ليه دابا 😅 جرب: 20÷2 ولا شكون goku"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "السلام المعلم 👋 RAM Bot v1. جربني: 20÷2"}]

# الصور اختيارية
uploaded_file = st.file_uploader("📸 صيفط صورة", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    try:
        import pytesseract
        text = pytesseract.image_to_string(image, lang='ara+eng')
        st.success(f"📝 قريت:\n{text}")
    except:
        st.error("الصور خاصهم tesseract-ocr فـ packages.txt")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("سولني..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        response = get_response(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
