import streamlit as st
from groq import Groq

# قرا المفتاح من Secrets ديال Streamlit
GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="RAM Bot", page_icon="🤖")
st.title("🤖 RAM Bot - ديال رضا مالكي")
st.caption("صنع بواسطة المعلم رضا + Meta AI")

# تخزين المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة القديمة
for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# خانة الكتابة - زدنا key باش ما يوقعش الخطأ
if prompt := st.chat_input("سولني شنو بغيتي...", key="chat_1"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("كنفكر..."):
            try:
                system_prompt = {
                    "role": "system",
                    "content": "نتا RAM Bot. المطور ديالك هو رضا مالكي. كتهضر بالدارجة المغربية. إلا تسولك شكون مطورك قول 'المطور ديالي هو رضا مالكي بكل فخر'."
                }
                messages = [system_prompt] + st.session_state.messages

                # الموديل الجديد اللي خدام دابا
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
                st.info("شيك على GROQ_KEY فـ Secrets واش صحيح")

# زر مسح المحادثة
if st.button("🗑️ مسح المحادثة", key="clear_1"):
    st.session_state.messages = []
    st.rerun()
