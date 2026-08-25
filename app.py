import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse

st.set_page_config(page_title="RAM Bot v3.9", page_icon="🤖")

# جيب المفتاح
GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

st.title("🤖 RAM Bot v3.9 ⚡ AI")
st.caption("المطور: رضا مالكي")

def generate_image(prompt):
    clean_prompt = prompt.replace("ولد ليا", "").strip()
    encoded_prompt = urllib.parse.quote(clean_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
    response = requests.get(url, timeout=30)
    return response.content if response.status_code == 200 else None

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "image" in msg:
            st.image(msg["image"])

prompt = st.chat_input("سولني ولا قول 'ولد ليا...'")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        if "ولد ليا" in prompt:
            with st.spinner("كنرسم..."):
                img = generate_image(prompt)
                if img:
                    st.image(img)
                    st.session_state.messages.append({"role": "assistant", "content": "تفضل الصورة", "image": img})
                else:
                    st.write("ما قدرتش نولد الصورة")
        else:
            messages = [{"role": "system", "content": "نتا RAM Bot v3.9. المطور ديالك رضا مالكي"}] + st.session_state.messages
            chat = client.chat.completions.create(messages=messages, model="llama-3.1-8b-instant")
            response = chat.choices[0].message.content
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
