import streamlit as st
from groq import Groq
import base64

st.set_page_config(
    page_title="RAM Bot v1.0 Ultra",
    page_icon="🤖",
    layout="centered"
)

GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {
    background: white; padding: 2rem; border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; text-align: center;
}
.card h1 {color: #667eea; margin: 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v1.0 Ultra</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر بالدارجة + كيقرا الصور + كيحل التمارين</p>
</div>
""", unsafe_allow_html=True)

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.last_image_id = None

for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            if "image" in msg and msg["image"]:
                st.image(msg["image"], width=300)
            st.markdown(msg["content"])

uploaded_file = st.file_uploader("📸 صيفط صورة ولا سول عادي", type=["png", "jpg", "jpeg"])

def process_image(image, user_prompt):
    image_b64 = encode_image(image)
    image_url = f"data:image/jpeg;base64,{image_b64}"

    with st.chat_message("user"):
        st.image(image, width=300)
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("كنقرا الصورة..."):
            try:
                system_prompt = {
                    "role": "system",
                    "content": """نتا RAM Bot v1.0 Ultra. المطور ديالك رضا مالكي.
1. كتهضر بالدارجة المغربية
2. إلا عطاوك صورة: وصفها مزيان وجاوب على أي سؤال عليها. إلا فيها تمارين حلها خطوة بخطوة"""
                }

                user_content = [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]

                messages = [system_prompt] + st.session_state.messages + [{"role": "user", "content": user_content}]

                # الموديل المضمون اللي عند كلشي
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.2-11b-vision-preview",
                    temperature=0.7
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "user", "content": user_prompt, "image": image})
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.last_image_id = image.file_id

            except Exception as e:
                st.error(f"خطأ: {e}")
                st.info("إلا بقا الخطأ، تأكد من GROQ_KEY ديالك واش مفعل فيه Vision")

# خدمة أوتوماتيك ملي تلوح تصويرة
if uploaded_file is not None:
    current_id = uploaded_file.file_id if hasattr(uploaded_file, 'file_id') else uploaded_file.name
    if st.session_state.last_image_id!= current_id:
        process_image(uploaded_file, "شنو فهاد الصورة؟ وصفها ليا بالتفصيل بالدارجة")

# الكتابة العادية
if prompt := st.chat_input("كتب سؤالك هنا...", key="chat_1"):

    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, width=300)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("كنجاوب..."):
            try:
                system_prompt = {
                    "role": "system",
                    "content": """نتا RAM Bot v1.0 Ultra. المطور ديالك رضا مالكي.
1. كتهضر بالدارجة المغربية
2. إلا عطاوك صورة: قراها مزيان وجاوب على أي سؤال عليها. إلا فيها تمارين حلها خطوة بخطوة
3. إلا سؤال نصي: جاوب بمعلومات دقيقة"""
                }

                if uploaded_file is not None:
                    image_b64 = encode_image(uploaded_file)
                    image_url = f"data:image/jpeg;base64,{image_b64}"
                    user_content = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                    model_to_use = "llama-3.2-11b-vision-preview" # هنا تاني
                    st.session_state.messages.append({"role": "user", "content": prompt, "image": uploaded_file})
                else:
                    user_content = prompt
                    model_to_use = "llama-3.3-70b-versatile"
                    st.session_state.messages.append({"role": "user", "content": prompt})

                messages = [system_prompt] + st.session_state.messages[:-1] + [{"role": "user", "content": user_content}]

                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=model_to_use,
                    temperature=0.7
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"خطأ: {e}")

if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.session_state.last_image_id = None
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
