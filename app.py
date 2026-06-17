import streamlit as st
import time

# إعدادات الصفحة باش تبان فـ Google
st.set_page_config(
    page_title="رام بوت برو v3.0 - تطبيق تنظيف الرام",
    page_icon="🚀",
    layout="centered"
)

# العنوان
st.title("🚀 رام بوت برو v3.0")
st.markdown('<meta name="description" content="رام بوت برو v3.0 - أفضل تطبيق لتنظيف وتسريع الرام ديال تيليفونك اندرويد">', unsafe_allow_html=True)
st.markdown("بواسطة رضا مالكي ❤️")

# هادي أهم حاجة - الذاكرة ديال الشات
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# خانة الكتابة + زر الميكرو
prompt = st.chat_input("كتب سؤالك... ولا قول 'ولد ليا صورة ديال'")

if prompt:
    # زيد رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # الجواب ديال البوت - بدل هنا الكود ديالك
    with st.chat_message("assistant"):
        with st.spinner("كنفكر..."):
            time.sleep(1)  # محاكاة التفكير
            
        # هنا حط المنطق ديال البوت ديالك
        if "سلام" in prompt:
            response = "وعليكم السلام ورحمة الله وبركاته. كيفاش دابا؟"
        elif "ولد ليا صورة" in prompt:
            response = "أوكي، غادي نولد ليك صورة دابا... صيفط ليا شنو بغيتي فـ الصورة"
        else:
            response = f"فهمتك: {prompt} \n\nأنا رام بوت برو v3.0، كيف نقدر نعاونك؟"
        
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# زر مسح المحادثة - هادا هو الحل
st.divider()
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🗑️ مسح المحادثة", use_container_width=True, type="primary"):
        st.session_state.messages = []  # كيمسح كلشي
        st.success("تم مسح المحادثة بنجاح!")
        time.sleep(0.5)
        st.rerun()  # كيعاود يحمل الصفحة ناضية

# الفوتر
st.caption("© 2026 رام بوت برو v3.0 - جميع الحقوق محفوظة")
