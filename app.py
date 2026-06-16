import streamlit as st
from groq import Groq

# حط المفتاح ديالك هنا
GROQ_KEY = gsk_rWaFSIOPGVbr9it5v1D5WGdyb3FYEfhPZGwZGEwB9pWHDedQJazuimport streamlit as st
from groq import Groq

# حط المفتاح ديالك هنا
GROQ_KEY = "gsk_حط_المفتاح_الجديد_ديالك_هنا"

st.set_page_config(page_title="RAM Bot", page_icon="🤖", layout="wide")

st.title("🤖 RAM Bot - ChatGPT ديالك")
st.caption("صنع بواسطة المعلم + Meta AI")

# تهيئة الكلاينت ديال Groq
client = Groq(api_key=GROQ_KEY)

# الذاكرة ديال المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة القديمة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# مربع الكتابة
if prompt := st.chat_input("سولني شنو بغيتي..."):
    # زيد السؤال ديال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # الجواب ديال البوت
    with st.chat_message("assistant"):
        with st.spinner("كنفكر..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="llama-4-scout", # سريع ومزيان للعربية
                    temperature=0.7,
                    max_tokens=2048
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"وقع خطأ: {e}")

# زر مسح المحادثة
if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.rerun()

st.set_page_config(page_title="RAM Bot", page_icon="🤖", layout="wide")

st.title("🤖 RAM Bot - ChatGPT ديالك")
st.caption("صنع بواسطة المعلم + Meta AI")

# تهيئة الكلاينت ديال Groq
client = Groq(api_key=GROQ_KEY)

# الذاكرة ديال المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة القديمة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# مربع الكتابة
if prompt := st.chat_input("سولني شنو بغيتي..."):
    # زيد السؤال ديال المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # الجواب ديال البوت
    with st.chat_message("assistant"):
        with st.spinner("كنفكر..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="llama-4-scout", # سريع ومزيان للعربية
                    temperature=0.7,
                    max_tokens=2048
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"وقع خطأ: {e}")

# زر مسح المحادثة
if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.rerun()
