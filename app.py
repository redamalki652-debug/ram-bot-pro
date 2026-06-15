import streamlit as st
import math, random
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(
    page_title="رام بوت برو - شات بوت عربي للدراسة وحل التمارين",
    page_icon="🤖",
    layout="wide"
) 

# CSS باش يجي الشكل زوين
st.markdown("""
<style>
    .main {background-color: #f0f2f6;}
    .stButton>button {background-color: #4CAF50; color: white; border-radius: 10px;}
    .chat-message {padding: 10px; border-radius: 10px; margin: 5px 0;}
    .user-msg {background-color: #DCF8C6; text-align: right;}
    .bot-msg {background-color: #FFFFFF; text-align: left; border: 1px solid #ddd;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 رام بوت برو v3.0")
st.subheader("مطور: رضا مالكي من سيدي حجاج")
st.write("9 لغات + دين + ساعة + حاسبة + حلول + سيرة الرسول ﷺ")

def جواب_البوت(سؤال_أصلي):
    سؤال = سؤال_أصلي.lower().strip()
    
    if any(k in سؤال for k in ["hy", "helo", "هلو"]): سؤال = "hello"
    elif any(k in سؤال for k in ["سلا", "سلم"]): سؤال = "سلام"
    elif any(k in سؤال for k in ["شحال سعا"]): سؤال = "شحال الساعة"
    elif any(k in سؤال for k in ["لابس"]): سؤال = "لابس"

    # الساعة
    if any(k in سؤال for k in ["شحال الساعة", "كم الساعة", "what time"]):
        دابا = datetime.now()
        الوقت = دابا.strftime("%H:%M:%S")
        التاريخ = دابا.strftime("%Y-%m-%d")
        return f"دابا {الوقت} المعلم رضا ⏰ والتاريخ {التاريخ} 📅"

    # الحاسبة
    try:
        عملية = سؤال_أصلي.replace('x','*').replace('×','*').replace('÷','/').replace('على','/')
        عملية = عملية.replace('في','*').replace('زائد','+').replace('ناقص','-').replace('جدر','sqrt').replace('اس','**')
        عملية = عملية.replace('شحال','').strip()
        عملية_نقية = ''.join([c for c in عملية if c in '0123456789+-*/.%() sqrt**'])
        if any(x in عملية_نقية for x in ['+','-','*','/','%','sqrt','**']) and len(عملية_نقية.strip())>2:
            النتيجة = eval(عملية_نقية)
            if النتيجة == int(النتيجة): النتيجة = int(النتيجة)
            return f"الحل = {النتيجة} ✅"
    except: pass

    # الدين
    if سؤال == "دين":
        return "مرحبا المعلم رضا 📿 سولني: شكون الله؟ شكون الرسول؟ قصة نوح؟ قصة محمد؟"
    
    elif any(k in سؤال for k in ["شكون الرسول", "الرسول", "محمد"]):
        return "سيدنا محمد ﷺ هو خاتم الأنبياء 💚 ولد فمكة عام الفيل، وبدا الوحي وهو عندو 40 عام. كان خلقو القرآن"
    
    elif any(k in سؤال for k in ["قصة محمد", "السيرة"]):
        return "📖 سيدنا محمد ﷺ: ولد يتيم، رباه جدو. خدم فالتجارة وكان الصادق الأمين. فغار حراء جاه الوحي 'اقرأ'. نشر الإسلام 23 عام ﷺ"
    
    elif any(k in سؤال for k in ["قصة نوح", "نوح"]):
        return "📖 سيدنا نوح: صنع السفينة وصبر 950 عام يدعو قومو. جا الطوفان ونجا هو والمؤمنين ⛵"

    # اللغات + لابس/لاباس
    elif any(k in سؤال for k in ["سلام", "السلام عليكم"]):
        return "وعليكم السلام المعلم رضا! واش لاباس؟ 😊"
    
    elif any(k in سؤال for k in ["لاباس", "لابس", "مزيان", "بخير"]):
        return "الحمد لله المعلم رضا، دامك نتا لابس/لاباس وصافي ❤️"
    
    elif any(k in سؤال for k in ["hello", "hi"]):
        return "Hello المعلم رضا! How are you? I'm fine 😄"
    
    elif any(k in سؤال for k in ["bonjour"]):
        return "Bonjour المعلم رضا! Ça va bien؟"
    
    elif any(k in سؤال for k in ["أزول"]):
        return "أزول المعلم رضا! مانزاكين؟ لاباس الحمد لله ⵣ"

    # الحلول
    elif any(k in سؤال for k in ["معصب", "غضبان"]):
        return "هدن راسك المعلم رضا 🧊: 1. شرب ما بارد 2. عد من 1 ل 10 3. قول أعوذ بالله"
    
    elif any(k in سؤال for k in ["مخلوع", "خلعة"]):
        return "ما تخافش المعلم رضا 🤲: 1. دير نفس عميق 2. قرا حسبي الله 3. الخلعة كدوز"
    
    elif any(k in سؤال for k in ["عيان", "تعبان"]):
        return "الحل المعلم رضا 😌: 1. توضا 2. غسل وجهك 3. خرج تشم الهواء"

    elif any(k in سؤال for k in ["شكون نتا"]):
        return "سميتي رام بوت برو v3.0 🤖 مطور تاعي رضا مالكي. كنفهم 9 لغات والدين والحلول 💻"
    
    else:
        return "فهمتك المعلم رضا 😄 جرب: شحال الساعة؟ hello؟ لابس؟ شكون الرسول؟"

# حفظ المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة القديمة
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-message user-msg">نتا: {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message bot-msg">البوت: {msg["content"]}</div>', unsafe_allow_html=True)

# صندوق الكتابة
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("كتب هنا المعلم رضا...", placeholder="مثال: سلام، شحال الساعة؟")
    submit_button = st.form_submit_button("سيفط 🚀")

if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    جواب = جواب_البوت(user_input)
    st.session_state.messages.append({"role": "assistant", "content": جواب})
    st.rerun()

st.markdown("---")
st.caption("جرب: سلام | لابس | شحال الساعة | 15x15 | شكون الرسول | أنا معصب")
