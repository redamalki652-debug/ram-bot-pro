import streamlit as st
import random
from PIL import Image
import pytesseract
import speech_recognition as sr
from pydub import AudioSegment
import io

st.set_page_config(page_title="المعلم رضا مالكي", page_icon="🤖", layout="centered")

# ===== قاموس الأخطاء الإملائية =====
SPELLING_DICT = {
    'لوزن': 'الوزن',
    'لكتابه': 'الكتابة', 
    'معنديش': 'ما عنديش',
    'كنتسا': 'كننسا',
    'فراسي': 'في راسي',
}

def check_spelling(text):
    words = text.split()
    mistakes = []
    corrected_words = []
    
    for word in words:
        clean_word = word.strip('.,!?،؟')
        if clean_word in SPELLING_DICT:
            mistakes.append(f"**{clean_word}** ← الصحيح: **{SPELLING_DICT[clean_word]}**")
            corrected_words.append(SPELLING_DICT[clean_word])
        else:
            corrected_words.append(word)
    
    corrected_text = " ".join(corrected_words)
    
    if mistakes:
        correction_msg = "⚠️ لقيت شي أخطاء إملائية:\n" + "\n".join(mistakes[:3])
        correction_msg += f"\n\n**النص المصح:** {corrected_text}"
        return correction_msg, corrected_text
    return None, text

# ===== تحويل الصوت لنص =====
def audio_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    
    try:
        # تحويل webm ل wav
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        
        # التعرف على الدارجة المغربية + العربية
        text = recognizer.recognize_google(audio_data, language="ar-MA")
        return text, None
        
    except sr.UnknownValueError:
        return None, "ما فهمتش الصوت مزيان 🎤 عاود سجل"
    except sr.RequestError:
        return None, "مشكل فـ النت، عاود جرب"
    except Exception as e:
        return None, f"خطأ: {str(e)}"

# ===== الدوال ديال الرد - نفس اللي عطيتك قبل =====
def get_casual_response(msg_lower):
    casual = {
        'سلام': "وعليكم السلام المعلم رضا مالكي 👋 كيف داير؟",
        'لاباس': "لاباس الحمد لله وانت؟ شنو نعاونك اليوم؟",
        'بخير': "دامت ليك البخير المعلم 💪 شنو الطلب؟",
        'شكون انت': "أنا البوت ديالك المعلم، خدام 24/24",
        'شكرا': "العفو المعلم، هذا واجب 👊"
    }
    for key, value in casual.items():
        if key in msg_lower:
            return value
    return None

def get_problem_solution(msg_lower):
    problems = {
        'مشكل في الكتابة': "مشكل الكتابة عندو حل المعلم ✍️\n1. **الخط**: درب 10 دقايق كل نهار\n2. **السرعة**: الأهم الوضوح\n3. **التطبيق**: اكتب اللي كتسمعو",
        'كنتسا بزاف': "النسيان عندو حلول المعلم 👇\n1. **المراجعة**: عاود اللي قريتي\n2. **التلخيص**: كتب الأفكار المهمة",
        'كنخاف من الامتحان': "رهبة الامتحان طبيعية 😊\n1. **التنفس**: 3 مرات عميق\n2. **بدا بالساهل**\nقول: اللهم لا سهل إلا ما جعلته سهلا"
    }
    
    for key, value in problems.items():
        if key in msg_lower:
            return value
    return None

def get_bot_response(user_input):
    spelling_msg, corrected_input = check_spelling(user_input)
    msg_lower = corrected_input.lower().strip()
    
    casual = get_casual_response(msg_lower)
    if casual:
        return f"{spelling_msg}\n\n---\n{casual}" if spelling_msg else casual
    
    problem = get_problem_solution(msg_lower)
    if problem:
        return f"{spelling_msg}\n\n---\n{problem}" if spelling_msg else problem
    
    response = "فهمتك المعلم 🤔 وضح ليا كثر"
    return f"{spelling_msg}\n\n---\n{response}" if spelling_msg else response

# ===== الواجهة =====
st.title("🤖 المعلم رضا مالكي")
st.caption("هضر ولا كتب - البوت فاهمك بجوج 🎤⌨️")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ===== الفوكال 🎤 =====
st.markdown("### 🎤 ولا هضر مباشرة:")
audio_input = st.audio_input("ضغط وسجل صوتك")

if audio_input is not None:
    audio_bytes = audio_input.getvalue()
    
    with st.spinner("كنسمع ليك..."):
        text, error = audio_to_text(audio_bytes)
    
    if error:
        st.error(error)
    else:
        st.success(f"فهمتك: **{text}**")
        st.session_state.messages.append({"role": "user", "content": f"🎤 {text}"})
        
        response = get_bot_response(text)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ===== رفع الصور OCR =====
uploaded_file = st.file_uploader("ولا ارفع صورة تمرين", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="تمرين ديالك")
    
    with st.spinner("كنقرا فـ التمرين..."):
        text = pytesseract.image_to_string(image, lang='ara+eng')
    
    spelling_msg, corrected_text = check_spelling(text)
    st.write("**📝 اللي قريت:**")
    st.code(text)
    
    if spelling_msg:
        st.warning(spelling_msg)
    
    st.session_state.messages.append({"role": "assistant", "content": f"قريت:\n```\n{corrected_text}\n```"})

# ===== الشات العادي =====
if prompt := st.chat_input("ولا كتب هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    response = get_bot_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
