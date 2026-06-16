import streamlit as st
import re
from sympy import symbols, Eq, solve
from PIL import Image
import pytesseract
from spellchecker import SpellChecker

st.set_page_config(page_title="رام بوت - المساعد الدراسي", page_icon="🤖", layout="centered")

st.title("🤖 رام بوت برو v4.7")
st.header("مطور: رضا مالكي") # سميتك غير هنا
st.write("📚 معادلات + دردشة + تصحيح + قراءة الصور")

spell = SpellChecker(language='fr')
spell_ar = SpellChecker()

def correct_spelling(text):
    words = text.split()
    corrected = []
    for word in words:
        if any('\u0600' <= c <= '\u06FF' for c in word):
            corrected.append(spell_ar.correction(word) or word)
        else:
            corrected.append(spell.correction(word) or word)
    return ' '.join(corrected)

def detect_lang(text):
    if any('\u0600' <= c <= '\u06FF' for c in text):
        return 'ar'
    elif re.search(r'[a-zA-Z]', text):
        return 'en'
    return 'ar'

def solve_equation(eq_text):
    try:
        x = symbols('x')
        eq_text = eq_text.replace("=", "-(") + ")"
        eq = Eq(eval(eq_text), 0)
        solution = solve(eq, x)
        return f"✅ Solution: x = {solution[0]}"
    except:
        return "❌ ما قدرتش نحلها. كتبها: 2x + 5 = 15"

# هنا زدنا المحادثة العادية بلا سميتك
def get_bot_response(message):
    msg_lower = message.lower().strip()
    lang = detect_lang(message)

    # محادثة عادية - كلام خفيف
    greetings_ar = ['سلام', 'السلام عليكم', 'مرحبا', 'أهلا']
    greetings_en = ['hello', 'hi', 'hey', 'salam']

    if any(g in msg_lower for g in greetings_ar):
        return "وعليكم السلام ورحمة الله 👋\nكيف نقدر نعاونك فـ الدراسة؟"

    if any(g in msg_lower for g in greetings_en):
        return "Hello! 👋 How can I help you with your studies?"

    if 'شكون نتا' in msg_lower or 'من انت' in msg_lower or 'who are you' in msg_lower:
        return "أنا رام بوت 🤖 مساعدك الدراسي\nكنعاونك فـ المعادلات، النسب، والتمارين. صور ليا تمرينك ونهضرو!"

    if 'شكرا' in msg_lower or 'thank you' in msg_lower or 'thanks' in msg_lower:
        return "العفو 🙏 مرحبا بيك فـ أي وقت\nبغيتي نحلو شي تمرين دابا؟"

    if 'بخير' in msg_lower or 'كيف حالك' in msg_lower or 'how are you' in msg_lower:
        return "أنا لاباس الحمد لله بخير 😊 وانت؟ واجد للقراية؟"

    if 'معادلة' in msg_lower or 'تمرين' in msg_lower or 'equation' in msg_lower:
        return "صيفط ليا المعادلة: 3x + 7 = 22\nولا صور التمرين من التحت 📸"

    if '=' in message and 'x' in message:
        return solve_equation(message)

    if lang == 'ar':
        return "ما فهمتكش مزيان 😅 جرب تكتب معادلة ولا صور التمرين\nولا سولني: شكون نتا؟"
    else:
        return "I didn't get that 😅 Try writing an equation or upload an image\nOr ask: who are you?"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("اكتب سؤالك / Write your question...")
if user_input:
    corrected_input = correct_spelling(user_input)

    st.session_state.messages.append({"role": "user", "content": corrected_input})
    with st.chat_message("user"):
        st.markdown(corrected_input)
        if corrected_input!= user_input:
            st.caption(f"✓ صححت: {user_input} → {corrected_input}")

    response = get_bot_response(corrected_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

st.divider()
st.subheader("📸 Upload exercise / صاور التمرين")
uploaded_file = st.file_uploader("Choose image / طلع الصورة", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Exercise / التمرين ديالك", use_column_width=True)

    with st.spinner("Reading... / كنقرا فـ التمرين..."):
        text = pytesseract.image_to_string(image, lang='ara+eng+fra')

    st.write("**📝 Text read / اللي قريت:**")
    st.code(text)

    if text.strip():
        corrected_text = correct_spelling(text)
        st.write("**💡 After correction / بعد التصحيح:**")
        st.code(corrected_text)
        st.info("كوبي المعادلة وحطها فـ الشات الفوق") 
