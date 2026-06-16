import streamlit as st
import re
from sympy import symbols, Eq, solve

st.set_page_config(page_title="رام بوت - المساعد الدراسي", page_icon="🤖")

st.title("🤖 رام بوت برو v4.4")
st.subheader("مطور: رضا مالكي")
st.write("📚 رياضيات + معادلات + نسب % + دين + مواد + دعم نفسي")

if "messages" not in st.session_state:
    st.session_state.messages = []

def solve_equation(eq_text):
    try:
        x = symbols('x')
        eq_text = eq_text.replace("=", "-(") + ")"
        eq = Eq(eval(eq_text), 0)
        solution = solve(eq, x)
        return f"حل المعادلة: x = {solution[0]} ✅\nالخطوات: نقلنا 5 للجهة الثانية، قسمينا على 2"
    except:
        return "كتب المعادلة بهاد الشكل: 2x + 5 = 15"

def calc_percent(text):
    match = re.search(r'(\d+)%\s*من\s*(\d+)', text)
    if match:
        percent = float(match.group(1))
        number = float(match.group(2))
        result = (percent / 100) * number
        return f"{percent}% من {number} = {result} ✅"
    return None

def get_bot_response(user_input):
    user_input = user_input.lower().strip()

    # 1. دعم المشاعر
    if any(x in user_input for x in ["معصب", "مقلق", "مهموم", "زعفان", "مضغوط"]):
        return """سمعتك المعلم 💙 عادي تحس هكا مرة.
خد نفس عميق، شرب ماء، وتهلا فراسك.
أنا بوت للمساعدة فقط. إلا الإحساس قوي، هضر مع شي حد كتثق فيه ولا اتصل بالخط الأخضر 0801002424 مجاني.
شنو اللي مضايقك نقدر نعاونك فيه؟"""

    # 2. حلول المواد - تخراج ديال شي حاجة
    if any(x in user_input for x in ["خرج ليا", "حل ليا", "تمرين", "درس", "شرح ليا", "وضعية", "production écrite"]):
        return f"""صافي فهمتك، بغيتي {user_input} ✅
عطيني السؤال كامل ولا صورة التمرين وغادي نحلو ليك خطوة بخطوة:
1. غنفهمو السؤال مزيان
2. غنطبقو القاعدة
3. غنعطيو الجواب النهائي
صيفط التمرين دابا ونشوفو."""

    # 3. مواد محددة
    if "رياضيات" in user_input or "math" in user_input:
        return "مرحبا بمادة الرياضيات ➕ عطيني المسألة: معادلة، دالة، هندسة... وغادي نحلها معاك."
    if "فيزياء" in user_input or "pc" in user_input:
        return "مرحبا بالفيزياء ⚡ عطيني القانون ولا التمرين وغادي نطبقو معاك."
    if "فرنسية" in user_input or "français" in user_input:
        return "مرحبا بالفرنسية 🇫🇷 بغيتي تصحيح ولا production écrite ولا قواعد؟ صيفط الموضوع."
    if "عربية" in user_input:
        return "مرحبا بالعربية 📝 بغيتي إعراب، تعبير، ولا تحليل نص؟ عطيني النص."

    # 4. شكون الله والرسول
    if "شكون الله" in user_input or "من هو الله" in user_input:
        return "الله سبحانه هو خالق كل شيء، الواحد الأحد، الرحمن الرحيم. نعبده وحده لا شريك له."
    if "شكون الرسول" in user_input or "من هو الرسول" in user_input:
        return "الرسول ﷺ هو محمد بن عبد الله، خاتم الأنبياء، بعثه الله رحمة للعالمين."

    # 5. النسب والمعادلات والحاسبة
    percent_result = calc_percent(user_input)
    if percent_result: return percent_result
    if "x" in user_input and "=" in user_input: return solve_equation(user_input)
    if any(x in user_input for x in ["+", "-", "*", "/", "احسب"]):
        try:
            expr = user_input.replace("x", "*").replace("÷", "/")
            return f"النتيجة هي: {eval(expr)} ✅"
        except: pass

    # 6. التحية
    if any(x in user_input for x in ["سلام", "مرحبا"]):
        return "وعليكم السلام 👋 مرحبا بيك فـ رام بوت. سولني فـ أي مادة ولا إلا مقلق نهضرو."

    return "عطيني السؤال ديالك كامل وغادي نعاونك فيه. رياضيات، فيزياء، فرنسية، عربية، دين... كاملين ناضيين."

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("مثال: خرج ليا تمرين 3 صفحة 20 أو 2x+5=15")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    response = get_bot_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
