import streamlit as st
import re
from sympy import symbols, Eq, solve
from PIL import Image
import pytesseract

# إعدادات الصفحة
st.set_page_config(
    page_title="رام بوت - المساعد الدراسي",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 رام بوت برو v4.5")
st.header("مطور: رضا مالكي")
st.write("📚 معادلات + نسب % + دين + مواد + دعم نفسي + قراءة الصور")

# دالة حل المعادلات
def solve_equation(eq_text):
    try:
        x = symbols('x')
        eq_text = eq_text.replace("=", "-(") + ")"
        eq = Eq(eval(eq_text), 0)
        solution = solve(eq, x)
        return f"✅ حل المعادلة: x = {solution[0]}"
    except:
        return "❌ ما قدرتش نحل المعادلة، كتبها بهاد الشكل: 2x + 5 = 15"

# دالة الرد ديال البوت
def get_bot_response(message):
    message = message.lower()

    if 'تمرين' in message or 'معادلة' in message:
        return "كتب ليا المعادلة ديالك مثلا: 3x + 7 = 22\nولا صور التمرين من التحت 👇"

    if '=' in message and 'x' in message:
        return solve_equation(message)

    if 'السلام' in message:
        return "وعليكم السلام المعلم رضا مالكي! شنو نقدر نعاونك؟"

    return "ما فهمتكش مزيان 😅 جرب تكتب معادلة ولا صور التمرين"

# حفظ المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة القديمة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# الشات
user_input = st.chat_input("سولني أي حاجة...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = get_bot_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

# فاصل بين الشات والصور
st.divider()

# خاصية رفع الصور وقراءة التمارين
st.subheader("📸 صاور التمرين ونحلو ليك")
uploaded_file = st.file_uploader("طلع الصورة هنا", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="التمرين ديالك", use_column_width=True)

    with st.spinner("كنقرا فـ التمرين..."):
        text = pytesseract.image_to_string(image, lang='ara+eng')

    st.write("**📝 اللي قريت من الصورة:**")
    st.code(text)

    if text.strip():
        st.write("**💡 الحل:**")
        st.write("جرب تكتب المعادلة اللي خرجت ليك فـ الشات الفوق باش نحلها ليك")
    else:
        st.warning("ما قدرتش نقرا الكتابة، صور صورة أوضح")
