import streamlit as st
import random
from PIL import Image
import pytesseract

st.set_page_config(page_title="المعلم رضا مالكي", page_icon="🤖", layout="centered")

# ===== قاموس الكلمات الشائعة الغالطة =====
SPELLING_DICT = {
    'لوزن': 'الوزن',
    'لكتابه': 'الكتابة', 
    'بزاف': 'بزاف',
    'كنقرا': 'كنقرا',
    'معنديش': 'ما عنديش',
    'كنتسا': 'كننسا',
    'كنمل': 'كنمل',
    'كنتقلق': 'كنتقلق',
    'امتحان': 'امتحان',
    'صحابي': 'صحابي',
    'ثقة': 'ثقة',
    'فراسي': 'في راسي',
    'النعاس': 'النعاس',
    'التلفون': 'التلفون'
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

# ===== الدوال ديال الرد =====
def get_casual_response(msg_lower):
    casual = {
        'سلام': "وعليكم السلام المعلم رضا مالكي 👋 كيف داير؟",
        'لاباس': "لاباس الحمد لله وانت؟ شنو نعاونك اليوم؟",
        'بخير': "دامت ليك البخير المعلم 💪 شنو الطلب؟",
        'شكون انت': "أنا البوت ديالك المعلم، خدام 24/24 باش نعاونك فـ القراية والدين والمشاكل",
        'شكرا': "العفو المعلم، هذا واجب 👊"
    }
    for key, value in casual.items():
        if key in msg_lower:
            return value
    return None

def get_islamic_response(msg_lower):
    islamic = {
        'دعاء': "الله يسهل عليك المعلم 🤲\nاللهم لا سهل إلا ما جعلته سهلا، وأنت تجعل الحزن إذا شئت سهلا",
        'استغفر': "أستغفر الله العظيم وأتوب إليه 🌿\nكثرة الاستغفار كتفتح الأبواب المسدودة",
        'الله': "ونعم بالله المعلم ❤️ هو المعين",
        'الحمدلله': "الحمد لله على كل حال"
    }
    for key, value in islamic.items():
        if key in msg_lower:
            return value
    return None

def get_support_response(msg_lower):
    support = {
        'محبط': "كلنا كنفوتو بهاد الإحساس المعلم ❤️\n1. خد نفس عميق 3 مرات\n2. فكر فـ إنجاز صغير درتيه اليوم\n3. هضر مع شي حد كتاق فيه\nانت قوي وقادر تفوت هاد المرحلة",
        'مكتئب': "سامحني ما نقدرش نعطيك تشخيص، ولكن أنا معاك ❤️\nإلا الإحساس قاصح بزاف، هضر مع طبيب نفسي ولا شي حد قريب ليك. انت ماشي بوحدك\nفـ المغرب: 0801002424 الخط ديال الاستماع",
        'بغيت نبكي': "بكي المعلم إلا بغيتي، الدموع كتريح القلب 😊\nمن بعد البكا كيجي الفرج. شنو اللي مضايقك؟ هضر معايا"
    }
    for key, value in support.items():
        if key in msg_lower:
            return value
    return None

def get_problem_solution(msg_lower):
    problems = {
        'مشكل في الكتابة': "مشكل الكتابة عندو حل المعلم ✍️\n1. **الخط**: درب 10 دقايق كل نهار على نسخ سطر\n2. **السرعة**: الأهم الوضوح، السرعة كتجي مع الوقت\n3. **وضعية اليد**: شد القلم مزيان وما تضغطش بزاف\n4. **التطبيق**: اكتب اللي كتسمعو ولا كتقراه\nالصبر مفتاح النجاح، غادي تحسن",

        'مشكل في الوزن': "الوزن كيتعلق بالنظام والحركة 💪\n1. **الماكلة**: قلل الحلويات والمقليات، زيد الماء والخضرة\n2. **الحركة**: مشي 30 دقيقة فـ النهار\n3. **النعاس**: نعس مزيان 7-8 سوايع\n**ملاحظة**: أنا ماشي أخصائي تغذية. إلا بغيتي نظام مضبوط استاشر طبيب ولا أخصائي",

        'وزني زايد': "عادي المعلم كلنا كنفوتو بهاد المرحلة 😊\nبدا بخطوات صغار: كاس ماء قبل الماكلة + نقص المشروبات الغازية\nالمشي اليومي كيدير فرق كبير مع الوقت",

        'وزني ناقص': "باش تزيد وزن صحي 💪\n1. زيد عدد الوجبات: 4-5 وجبات صغار\n2. دخل مكسرات، تمر، حليب كامل الدسم\n3. تمارين خفيفة كتبني العضلات\nإلا النحافة مفرطة، طبيب التغذية هو اللي يعرف السبب",

        'ما كنركزش': "التشتت مشكل ديال الجميع 🧠\n1. **قسم الوقت**: قرا 25 دقيقة، راحة 5 دقايق\n2. **التلفون**: بعدو ولا ديرو صامت\n3. **المكان**: قرا فـ بلاصة هادئة\n4. **النعاس**: الدماغ ما كيركزش إلا ما نعستش مزيان",

        'كنتسا بزاف': "النسيان عندو حلول المعلم 👇\n1. **المراجعة**: عاود اللي قريتي بعد ساعة، بعد نهار\n2. **التلخيص**: كتب الأفكار المهمة بوراقتك\n3. **الشرح**: إلا قدرتي تشرح لشي واحد = فهمتي مزيان",

        'كنخاف من الامتحان': "رهبة الامتحان طبيعية 100% 😊\n1. **الاستعداد**: حِل تمارين قديمة\n2. **التنفس**: قبل ما تبدا، تنفس 3 مرات عميق\n3. **الترتيب**: بدا بالسؤال الساهل\nقول: اللهم لا سهل إلا ما جعلته سهلا",

        'كنتقلق بزاف': "القلق كيجي من التفكير بزاف 💭\n1. **كتب أفكارك**: خرجهم من راسك للورقة\n2. **الرياضة**: حتى المشي كيصفّي الذهن\n3. **الذكر**: ألا بذكر الله تطمئن القلوب\nإلا القلق مأثر على حياتك بزاف، الأخصائي النفسي كيعاون مزيان",

        'معنديش ثقة فراسي': "الثقة كتبنى بالمواقف الصغار المعلم 💪\n1. **الإنجازات**: كتب 3 حوايج درتيهم مزيان كل نهار\n2. **المقارنة**: ما تقارنش راسك مع الناس\n3. **التجربة**: جرب حوايج جداد، حتى إلا فشلتي راه تعلمتي\nانت قادر، غير خاصك الوقت",

        'كنمل من القراية': "الملل عادي إلا القراية طويلة 😴\n1. **نوع**: بدل المادة كل 45 دقيقة\n2. **الهدف**: قرا باش تفهم، ماشي باش تسالي\n3. **المكافأة**: ملي تسالي تمرين، عطي راسك 5 دقايق راحة",

        'كنتسهر بزاف': "السهر كيخرب التركيز المعلم 🌙\n1. **روتين النوم**: نعس و نوض فـ نفس الوقت\n2. **التلفون**: قطعه ساعة قبل النعاس\n3. **الجو**: البيت بارد ومظلم كيعاون على النعاس",

        'مشكل مع صحابي': "العلاقات كتخاصها الصبر ❤️\n1. **سمع**: خلي الطرف الآخر يهضر حتى يسالي\n2. **هضر بهدوء**: قول شنو حسيتي بلا ما تلوم\n3. **السماح**: ماشي ضعف، القوة هي اللي كتسامح"
    }
    
    for key, value in problems.items():
        if key in msg_lower:
            return value
    return None

def get_bot_response(user_input):
    # 0. تصحيح الأخطاء الإملائية الأول
    spelling_msg, corrected_input = check_spelling(user_input)
    
    msg_lower = corrected_input.lower().strip()
    
    # 1. الرد العادي
    casual = get_casual_response(msg_lower)
    if casual:
        if spelling_msg:
            return f"{spelling_msg}\n\n---\n{casual}"
        return casual
    
    # 2. الرد الديني
    islamic = get_islamic_response(msg_lower)
    if islamic:
        if spelling_msg:
            return f"{spelling_msg}\n\n---\n{islamic}"
        return islamic
    
    # 3. الدعم النفسي
    support = get_support_response(msg_lower)
    if support:
        if spelling_msg:
            return f"{spelling_msg}\n\n---\n{support}"
        return support
    
    # 4. حل المشاكل
    problem = get_problem_solution(msg_lower)
    if problem:
        if spelling_msg:
            return f"{spelling_msg}\n\n---\n{problem}"
        return problem
    
    # 5. الرد الافتراضي
    defaults = [
        "فهمتك المعلم 🤔 وضح ليا كثر باش نعاونك مزيان",
        "ما فهمتش مزيان، عاود بصيغة أخرى؟",
        "أنا معاك، شنو المشكل بالضبط؟"
    ]
    response = random.choice(defaults)
    if spelling_msg:
        return f"{spelling_msg}\n\n---\n{response}"
    return response

# ===== واجهة Streamlit =====
st.title("🤖 المعلم رضا مالكي")
st.caption("البوت الذكي ديالك - قراية، دين، مشاكل، وإملاء")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# رفع الصور OCR
uploaded_file = st.file_uploader("ارفع صورة تمرين", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="تمرين ديالك")
    
    with st.spinner("كنقرا فـ التمرين..."):
        text = pytesseract.image_to_string(image, lang='ara+eng')
    
    # صحح النص اللي خرج من الصورة
    spelling_msg, corrected_text = check_spelling(text)
    
    st.write("**📝 اللي قريت:**")
    st.code(text)
    
    if spelling_msg:
        st.warning(spelling_msg)
        st.session_state.messages.append({"role": "assistant", "content": f"قريت هادشي من الصورة وصححتو ليك:\n```\n{corrected_text}\n```"})
    else:
        st.session_state.messages.append({"role": "assistant", "content": f"قريت هادشي من الصورة:\n```\n{text}\n```"})

# الشات
if prompt := st.chat_input("سول المعلم رضا مالكي..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    response = get_bot_response(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response) 
