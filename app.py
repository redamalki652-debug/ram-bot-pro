import streamlit as st
import random
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
import io
import datetime

st.set_page_config(page_title="RAM Bot Ultra", page_icon="🤖", layout="centered")

# ===== بطاقة الترحيب =====
st.markdown("""
<div dir="rtl" style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    border-radius: 25px;
    color: white;
    text-align: right;
    margin-bottom: 25px;
">
    <h1 style="margin: 0;">🤖 RAM Bot Ultra</h1>
    <h3>الإصدار v6.0 - يجاوب على أي حاجة</h3>
    <p><b>👨‍💻 المطور: رضا مالكي</b></p>
    <p>🎤 صوت + 📸 صور + 💬 محادثة + 📚 دراسة + 📖 دين + 🌍 معلومات عامة</p>
</div>
""", unsafe_allow_html=True)

# ===== قاعدة المعرفة الشاملة =====
KNOWLEDGE_BASE = {
    # محادثة عامة
    'سلام': "وعليكم السلام المعلم 👋 مرحبا بيك. كيف نقدر نعاونك اليوم؟",
    'شكون انت': "أنا RAM Bot Ultra 🤖 مساعد ذكي. كنفهم الدارجة، العربية، الفرنسية والإنجليزية. سولني على أي حاجة!",
    'شكرا': "العفو المعلم ❤️ راني هنا ديما. شنو باقي باغي تعرف؟",
    'بخير': "الحمد لله بخير دامك بخير المعلم 💪 وانت كيف داير؟",
    
    # معلومات عامة
    'عاصمة المغرب': "عاصمة المغرب هي **الرباط** 🇲🇦 وأكبر مدينة هي الدار البيضاء",
    'شحال الساعة': f"دابا الساعة {datetime.datetime.now().strftime('%H:%M')} فالمغرب ⏰",
    'شحال اليوم': f"اليوم {datetime.datetime.now().strftime('%Y/%m/%d')}",
    
    # علوم وتكنولوجيا
    'شنو هو الذكاء الاصطناعي': "الذكاء الاصطناعي AI هو أن نخليو الحاسوب يفكر ويتعلم بحال الإنسان 🤖\nمثال: أنا RAM Bot، كنفهمك ونجاوبك",
    'علاش السماء زرقاء': "حيت ضوء الشمس فيه جميع الألوان، واللون الأزرق كيتشتت كثر فالجو 🌤️",
    'شحال بعد القمر': "القمر بعيد على الأرض 384,400 كيلومتر تقريبا 🌙",
    
    # نصائح وحكم
    'عطيني حكمة': random.choice([
        "الصبر مفتاح الفرج المعلم 🔑",
        "من جد وجد ومن زرع حصد 🌱",
        "العلم نور والجهل ظلام 💡",
        "القناعة كنز لا يفنى"
    ]),
    'عطيني نكتة': random.choice([
        "واحد غبي مشا للطبيب قالو: دكتور كل ما نشرب القهوة كنحس بألم فعيني 😂 قالو: جرب تحيد المعلقة من الكاس",
        "واحد كسول قالو باباه: نوض قرا قالو: علاش؟ قالو: باش تولي دكتور قالو: والدكتور اش كيدير؟ قالو: كيعطي الدوا. قالو: صافي حتى أنا نبيع الدوا بلا قراية 😂"
    ]),
    
    # مشاكل شخصية
    'عندي مشكل في الوزن': "ساهلة المعلم 💪\n1. نقص الحلويات والمقليات\n2. مشي 30 دقيقة كل نهار\n3. شرب 2 لتر ماء\n4. نعس مزيان. الجسم كيحرق وهو ناعس",
    
    'كنخاف من المستقبل': "كلنا كنخافو المعلم 😊\n1. ركز على اليوم ديالك دابا\n2. دير خطة صغيرة كل أسبوع\n3. توكل على الله. الرزق بيدو\n4. تذكر: الماضي فات والمستقبل بيد الله",
    
    # دين
    'دعاء الرزق': "اللهم ارزقني رزقا واسعا حلالا طيبا 🤲\nوقول: اللهم إني أسألك من فضلك ورحمتك فإنه لا يملكها إلا أنت",
    'سورة الملك': "تبارك الذي بيده الملك وهو على كل شيء قدير... قراها قبل النوم تحميك من عذاب القبر",
}

def get_smart_response(user_msg):
    msg = user_msg.lower().strip()
    
    # 1. قلب فـ قاعدة المعرفة
    for key, answer in KNOWLEDGE_BASE.items():
        if key in msg:
            return answer
    
    # 2. إلا كان سؤال "علاش" 
    if 'علاش' in msg:
        return f"سؤال زوين المعلم 🤔 علاش {msg.replace('علاش', '')}؟\nبصراحة ما عنديش جواب 100%، ولكن نقدر نقول ليك الرأي ديالي: كل حاجة فالدنيا عندها سبب وحكمة. باغي نشرح ليك كثر؟"
    
    # 3. إلا كان سؤال "كيفاش"
    if 'كيفاش' in msg or 'كيف' in msg:
        return f"باش ندير {msg} المعلم؟\nعلى حسب الحالة، ولكن القاعدة العامة: بدا بخطوة صغيرة، تعلم، غلط، عاود حتى تضبطها. شنو بالضبط باغي تدير؟"
    
    # 4. إلا كان سؤال "شنو"
    if 'شنو' in msg or 'ما هو' in msg:
        return f"{msg}... سؤال مهم 👌\nخليني نقول ليك من وجهة نظري: أي حاجة فالدنيا عندها تعريف وهدف. وضح ليا كثر عاد نعطيك جواب دقيق المعلم"
    
    # 5. رد ذكي على أي كلام
    smart_replies = [
        f"هضرتك فيها المعنى المعلم 🤔 واش باغي نعمقو فهاد الموضوع؟",
        f"فهمت عليك. من وجهة نظري: {msg} موضوع كبير، وكل واحد عندو رأي. وانت شنو رأيك؟",
        f"سؤال زوين والله 👌 خليني نفكر معاك... شنو بان ليك نتا؟",
        f"RAM Bot كيسمعك المعلم 👂 قول ليا كثر على {msg} باش نعطيك جواب ناضي",
        f"هادشي اللي قلتي مهم بزاف. فكرتي فيه من قبل ولا غير دابا خطر على بالك؟"
    ]
    
    return random.choice(smart_replies)

# ===== دالة الصوت =====
def audio_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="ar-MA")
        return text, None
    except Exception as e:
        if "ffprobe" in str(e):
            return None, "⚠️ خاص ffmpeg فـ packages.txt ودير Reboot"
        return None, "ما فهمتش الصوت، عاود 🎤"

# ===== الواجهة =====
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "السلام عليكم المعلم 👋 أنا RAM Bot Ultra. سولني على أي حاجة تخطر على بالك!"}]

# الصوت
audio_input = st.audio_input("🎤 هضر معايا")
if audio_input:
    audio_bytes = audio_input.getvalue()
    with st.spinner("كيسمع ليك..."):
        text, error = audio_to_text(audio_bytes)
    if error:
        st.error(error)
    else:
        st.session_state.messages.append({"role": "user", "content": f"🎤 {text}"})
        response = get_smart_response(text)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# الصور OCR
uploaded_file = st.file_uploader("📸 صيفط صورة", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_column_width=True)
    text = pytesseract.image_to_string(image, lang='ara+eng+fra')
    st.success(f"قريت: {text}")
    st.session_state.messages.append({"role": "assistant", "content": f"من الصورة قريت:\n```\n{text}\n```\nشنو ندير بيه؟"})

# عرض المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# الكتابة
if prompt := st.chat_input("سولني على أي حاجة..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = get_smart_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
