import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="RAM Bot v1.0 Ultra", page_icon="🤖", layout="centered")

GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
.card p {color: #555; margin: 0.5rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v1.0 Ultra</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر بالدارجة + كيقرا الصور + كيحل التمارين خطوة بخطوة</p>
</div>
""", unsafe_allow_html=True)

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            if "image" in msg and msg["image"]:
                st.image(msg["image"], width=300)
            st.markdown(msg["content"])

uploaded_file = st.file_uploader("📸 صيفط صورة ولا سول عادي", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

def get_text_messages():
    """كنرجعو غير messages ديال النص بلا الصور"""
    text_msgs = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            text_msgs.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            text_msgs.append({"role": "assistant", "content": msg["content"]})
    return text_msgs

def process_with_image(image, prompt):
    image_b64 = encode_image(image)
    image_url = f"data:image/jpeg;base64,{image_b64}"

    with st.chat_message("user"):
        st.image(image, width=300)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("كنقرا الصورة..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v1.0 Ultra. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية. إلا عطاوك صورة: وصفها مزيان وجاوب على أي سؤال عليها. إلا فيها تمارين رياضيات/فيزياء حلها خطوة بخطوة وبطريقة بسيطة."}

            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]

            messages = [system_prompt] + st.session_state.messages + [{"role": "user", "content": user_content}]

            chat_completion = client.chat.completions.create(
                messages=messages,
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.7,
                max_tokens=2048
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "user", "content": prompt, "image": image})
            st.session_state.messages.append({"role": "assistant", "content": response})

def process_text_only(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("كنجاوب..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v1.0 Ultra. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية. جاوب بمعلومات دقيقة ومفيدة."}

            # الحل: كنستعملو get_text_messages() باش نحيدو الصور من الـ history
            text_messages = get_text_messages()
            messages = [system_prompt] + text_messages + [{"role": "user", "content": prompt}]

            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1024
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response})

prompt_with_image = st.chat_input("كتب سؤالك على الصورة هنا...")
prompt_text_only = st.chat_input("كتب سؤالك هنا...", key="text_only")

if uploaded_file is not None and prompt_with_image:
    process_with_image(uploaded_file, prompt_with_image)
    st.session_state.uploader_key += 1
    st.rerun()

elif prompt_text_only:
    process_text_only(prompt_text_only)

if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
