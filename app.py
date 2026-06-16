import streamlit as st
from groq import Groq

# إعداد الصفحة
st.set_page_config(
    page_title="RAM Bot Ultra v1.0",
    page_icon="🤖",
    layout="centered"
)

# المفتاح من Secrets
GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

# CSS باش نحسنو البطاقة والواجهة
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.card {
    background: white;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    margin-bottom: 2rem;
    text-align: center;
}
.card h1 {
    color: #667eea;
    margin-bottom: 0.5rem;
}
.card p {
    color: #666;
    font-size: 1.1rem;
}
.stChatMessage {
    background: rgba(255,255,255,0.95);
    border-radius: 15px;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# البطاقة ديال التعريف Ultra v1.0
st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v1.0 Ultra</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>أذكى بوت دردشة بالدارجة المغربية<br>
    مدعوم بـ Groq Llama 3.3 Ultra</p>
</div>
""", unsafe_allow_html=True)

# تخزين المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# خانة الكتابة
if prompt := st.chat_input("كتب سؤالك هنا...", key="chat_1"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("RAM Bot كيتفكر..."):
            try:
                system_prompt = {
                    "role": "system",
                    "content": "نتا RAM Bot v1.0 Ultra. المطور ديالك هو رضا مالكي. كتهضر بالدارجة المغربية بطريقة ذكية وخفيفة. إلا تسولك شكون مطورك قول 'المطور ديالي هو رضا مالكي بكل فخر'."
                }
                messages = [system_prompt] + st.session_state.messages

                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.8
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"وقع خطأ: {e}")

# زر مسح المحادثة
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🗑️ مسح المحادثة", use_container_width=True, key="clear_1"):
        st.session_state.messages = []
        st.rerun()
