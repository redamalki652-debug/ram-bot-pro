import streamlit as st
from groq import Groq

# قرا المفتاح من Secrets ماشي من الكود
GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="RAM Bot", page_icon="🤖")
st.title("🤖 RAM Bot - ديال رضا مالكي")
st.caption("صنع بواسطة المعلم + Meta AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# هنا زدنا key باش ما يوقعش الخطأ
if prompt := st.chat_input("سولني شنو بغيتي...", key="chat_1"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("كنفكر..."):
            system_prompt = {
                "role": "system",
                "content": "نتا RAM Bot. المطور ديالك هو رضا مالكي. كتهضر بالدارجة. إلا تسولك شكون مطورك قول 'المطور ديالي هو رضا مالكي بكل فخر'."
            }
            messages = [system_prompt] + st.session_state.messages
            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama-4-scout"
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if st.button("🗑️ مسح المحادثة", key="clear_1"):
    st.session_state.messages = []
    st.rerun()
