import streamlit as st
from groq import Groq
import base64

st.set_page_config(
    page_title="RAM Bot Ultra v1.1 Vision",
    page_icon="🤖",
    layout="centered"
)

GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

# CSS محسن
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
</style>
""", unsafe_allow_html=True)

# البطاقة Ultra v1.1 Vision
st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v1.1 Ultra Vision</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر + كيقرا الصور بالذكاء الاصطناعي 📸</p>
</div>
""", unsafe_allow_html=True)

# دالة باش نحولو الصورة لـ base64
def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

# تخزين المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            if "image" in msg:
                st.image(msg["image"])
            st.markdown(msg["content"])

# رفع الصورة + خانة الكتابة
uploaded_file = st.file_uploader("📸 صيفط صورة لـ RAM Bot", type=["png", "jpg", "jpeg"])

if prompt := st.chat_input("سولني ولا وصف ليا الصورة...", key="chat_1"):

    # إلا كاينة صورة
    if uploaded_file is not None:
        image_b64 = encode_image(uploaded_file)
        image_url = f"data:image/jpeg;base64,{image_b64}"

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "image": uploaded_file
        })

        with st.chat_message("user"):
            st.image(uploaded_file, width=300)
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("كنقرا الصورة..."):
                try:
                    system_prompt = {
                        "role": "system",
                        "content": "نتا RAM Bot v1.1 Ultra Vision. المطور ديالك رضا مالكي. كتهضر بالدارجة. إلا عطاوك صورة وصفها مزيان وجاوب على أي سؤال عليها."
                    }

                    messages = [
                        system_prompt,
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ]

                    # موديل Vision ديال Groq
                    chat_completion = client.chat.completions.create(
                        messages=messages,
                        model="llama-3.2-90b-vision-preview"
                    )
                    response = chat_completion.choices[0].message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    st.error(f"خطأ فقراءة الصورة: {e}")
                    st.info("جرب موديل نصي إلا الصورة ما بغاتش")

    # إلا غير نص بلا صورة
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("كنفكر..."):
                system_prompt = {"role": "system", "content": "نتا RAM Bot v1.1 Ultra. المطور ديالك رضا مالكي. كتهضر بالدارجة."}
                messages = [system_prompt] + st.session_state.messages

                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile"
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# زر المسح
if st.button("🗑️ مسح المحادثة", use_container_width=True, key="clear_1"):
    st.session_state.messages = []
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
