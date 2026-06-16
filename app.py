import streamlit as st
import re
from sympy import symbols, Eq, solve
from PIL import Image
import pytesseract
from spellchecker import SpellChecker

st.set_page_config(page_title="رام بوت - المساعد الدراسي", page_icon="🤖", layout="centered")

st.title("🤖 رام بوت برو v5.2")
st.header("مطور: رضا مالكي")
st.write("📚 حاسبة + معادلات + دين + دعم + قراءة الصور + كلام خفيف")

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

def calculate(expr):
    try:
        expr = expr.replace('÷', '/').replace('×', '*').replace(',', '.')
        expr = re.sub(r'[a-zA-Z\u0600-\u06FF\s]', '', expr)
        if expr:
            result = eval(expr)
            return f"✅ النتيجة: {expr} = {result}"
    except:
        return None
    return None

def solve_equation(eq_text):
    try:
        x = symbols('x')
        eq_text = eq_text.replace("=", "-(") + ")"
        eq = Eq(eval(eq_text), 0) # ← صلحت القوس هنا
        solution = solve(eq, x)
        return f"✅ حل المعادلة: x = {solution[0]}"
    except:
        return "❌ ما قدرتش نحلها. كتبها: 2x + 5 = 15"

def get_islamic_response(msg_lower):
    islamic_data = {
        'بسم الله': "بسم الله الرحمن الرحيم 🤲\nكنبداو بيها كلشي باش ربي يبارك لنا",
        'الحمد لله': "الحمد لله رب العالمين 🙏\nالحمد لله على كل حال",
        'أذكار الصباح': "أذكار الصباح:\n1. آية الكرسي\n2. قل هو الله أحد 3 مرات\n3. أصبحنا وأصبح الملك لله",
        'أذكار النوم': "قبل النوم قول:\nباسمك ربي وضعت جنبي وبك أرفعه\nآية الكرسي\nتصبح على خير 🌙",
        'دعاء النجاح': "دعاء النجاح فـ الدراسة:\nاللهم لا سهل إلا ما جعلته سهلا\nوأنت تجعل الحزن إذا شئت سهلا\nاللهم وفقني",
        'الفاتحة': "سورة الفاتحة:\nبسم الله الرحمن الرحيم\nالحمد لله رب العالمين...",
        'صلاة': "حي على الصلاة 🕌\nالصلاة عماد الدين. الله يتقبل منا ومنكم",
        'استغفر': "أستغفر الله العظيم وأتوب إليه\nكثرة الاستغفار كتجيب الرزق والراحة"
    }
    for key, value in islamic_data.items():
        if key in msg_lower:
            return value
    return None

def get_support_response(msg_lower):
    support_data = {
        'متوتر': "عادي تتوتر قبل الامتحان كلنا كنوترو 😊\nتنفس معايا: شهيق 4 ثواني، حبس 4، زفير 4\nانت قدها والله",
        'خايف': "الخوف طبيعي المعلم 👊\nقسم التمرين لقطع صغار وبدا بأسهل واحد\nكل سؤال كتحلو كتزيد ثقة فراسك",
        'يائس': "لا تيأس أبدا 💪\nكل العباقرة فشلو قبل ما ينجحو. طيح ونوض، جرب مرة أخرى",
        'تعبان': "عطي راسك راحة دقيقة 👀\nاشرب الماء، غسل وجهك، نوض تحرك\nالراحة جزء من النجاح",
        'ما فهمتش': "عادي ما تفهمش من أول مرة\nشرح ليا فين بالضبط وقف ونشوفوها خطوة خطوة",
        'ضايع': "ما ضاع والو المعلم ❤️\nرجع للنقطة اللي فهمتي فيها وعاود من تما"
    }
    for key, value in support_data.items():
        if key in msg_lower:
            return value + "\n\n**ملاحظة**: إلا الإحساس بقا قوي بزاف، هضر مع أخصائي نفسي. فالمغرب: 0801002424"
    return None

def get_casual_response(msg_lower):
    casual_data = {
        'سلام عليكم': "وعليكم السلام ورحمة الله وبركاته 👋\nمرحبا بيك المعلم رضا مالكي",
        'سلام': "وعليكم السلام 👋\nكيف داير؟ شنو نقدر نعاونك؟",
        'مرحبا': "أهلا وسهلا بيك 🌟\nنورت البوت ديالك",
        'أهلا': "أهلا بيك ❤️\nواجد للدراسة ولا للدردشة؟",
        'صباح الخير': "صباح النور والسرور ☀️\nنهارك مبروك إن شاء الله",
        'مساء الخير': "مساء الخيرات 🌙\nكيف داز نهارك؟",
        'شكرا': "العفو المعلم 🙏\nواجبنا هادا. مرحبا بيك فـ أي وقت",
        'شكرا بزاف': "لا شكر على واجب ❤️\nالله ينجحك ويفرحك",
        'بارك الله فيك': "وفيك بارك الله 🤲\nالله يحفظك",
        'تصبح على خير': "وانت من أهلو 🌙\nفي أمان الله، أحلام سعيدة",
        'تصبحو على خير': "وانتم من أهلو\nنعس مزيان باش تفوق غدا",
        'مع السلامة': "الله يسلمك 👋\nتلاقينا فـ الخير إن شاء الله",
        'هاي': "هاي عليك المعلم 😎\nشخبار القراية؟",
        'كي داير': "لاباس الحمد لله وانت؟\nأنا واجد لأي سؤال",
        'لباس': "الحمد لله ملي لباس ❤️\nنبداو نقراو ولا نراجعو؟"
    }
    for key, value in casual_data.items():
        if key in msg_lower:
            return value
    return None

def get_bot_response(message):
    msg_lower = message.lower().strip()
    lang = detect_lang(message)

    # 1. كلام خفيف
    casual = get_casual_response(msg_lower)
    if casual:
        return casual

    # 2. ديني
    islamic = get_islamic_response(msg_lower)
    if islamic:
        return islamic

    # 3. دعم نفسي
    support = get_support_response(msg_lower)
    if support:
        return support

    # 4. شكون نتا
    if 'شكون نتا' in msg_lower or 'من انت' in msg_lower or 'who are you' in msg_lower:
        return "أنا رام بوت 🤖 مساعدك فـ الدراسة والدين\nمطور من طرف المعلم رضا مالكي 👊\nكنحسب، كنحل معادلات، كنقرا الصور، وكنضحك معاك"

    # 5. حسابات
    calc_result = calculate(message)
    if calc_result:
        return calc_result

    # 6. معادلات
    if '=' in message and 'x' in message:
        return solve_equation(message)

    if 'معادلة' in msg_lower or 'تمرين' in msg_lower:
        return "صيفط ليا المعادلة: 3x + 7 = 22\nولا عملية: 200÷50\nولا صور التمرين 📸"

    if lang == 'ar':
        return "ما فهمتكش مزيان 😅 جرب: سلام ولا 200÷50 ولا دعاء النجاح"
    else:
        return "I didn't get that 😅 Try: Salam or 200/50"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("سولني أي حاجة...")
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
st.subheader("📸 صاور التمرين")
uploaded_file = st.file_uploader("طلع الصورة", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="التمرين ديالك", use_column_width=True)

    with st.spinner("كنقرا فـ التمرين..."):
        text = pytesseract.image_to_string(image, lang='ara+eng+fra')

    st.write("**📝 اللي قريت:**")
    st.code(text) 
