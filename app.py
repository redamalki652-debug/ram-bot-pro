import streamlit as st
from groq import Groq
import base64
import requests
import urllib.parse

st.set_page_config(page_title="RAM Bot v2.2 AI", page_icon="🤖", layout="centered")

GROQ_KEY = st.secrets["GROQ_KEY"]
client = Groq(api_key=GROQ_KEY)

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
.card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem; text-align: center;}
.card h1 {color: #667eea; margin: 0; font-size: 2.5rem;}
.card p {color: #333; font-size: 1.1rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h1>🤖 RAM Bot v2.2 AI</h1>
    <p><b>المطور:</b> رضا مالكي</p>
    <p>كيهضر بالدارجة + كيقرا الصور + كيولد تصاور مجاني 🎨</p>
</div>
""", unsafe_allow_html=True)

def encode_image(image):
    return base64.b64encode(image.getvalue()).decode('utf-8')

def generate_image(prompt):
    """توليد صورة مجاني - Pollinations.ai"""
    with st.spinner("كنرسم ليك الصورة... صبر 20 ثانية 🎨"):
        try:
            # 1. ننقاو الكلام ديال الدارجة
            clean_prompt = prompt.replace("ولد ليا", "").replace("صاوب ليا", "").replace("رسم ليا", "").replace("صورة ديال", "").strip()

            # 2. نحسنو الـ prompt بالإنجليزية باش النتيجة تكون بروفيسيونيل
            enhanced_prompt = f"professional high quality photo of {clean_prompt}, commercial photography, 4k, highly detailed, studio lighting"

            # 3. نـ encode الـ URL باش ما يوقعش مشكل مع العرب
            encoded_prompt = urllib.parse.quote(enhanced_prompt)

            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&enhance=true"

            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                return response.content # bytes ديال الصورة
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

for msg in st.session_state.messages:
    if msg["role"]!= "system":
        with st.chat_message(msg["role"]):
            if "image" in msg and msg["image"] and msg["image"]!= "ai_generated":
                st.image(msg["image"], width=300)
            elif msg.get("image") == "ai_generated":
                st.image(msg["content_bytes"]) # كنعرضو الصورة
            else:
                st.markdown(msg["content"])

uploaded_file = st.file_uploader("📸 صيفط صورة ولا سول عادي", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.uploader_key}")

def get_text_messages():
    text_msgs = []
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            text_msgs.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant" and "content_bytes" not in msg: # ما نصيفطوش الصور لـ Groq
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
            system_prompt = {"role": "system", "content": "نتا RAM Bot v2.2. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية. إلا عطاوك صورة وصفها وجاوب. إلا فيها تمارين حلها خطوة بخطوة. كون خفيف الدم."}
            user_content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": image_url}}]
            messages = [system_prompt] + get_text_messages() + [{"role": "user", "content": user_content}]
            chat_completion = client.chat.completions.create(messages=messages, model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.7, max_tokens=2048)
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "user", "content": prompt, "image": image})
            st.session_state.messages.append({"role": "assistant", "content": response})

def process_text_only(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("كنجاوب..."):
            system_prompt = {"role": "system", "content": "نتا RAM Bot v2.2. المطور ديالك رضا مالكي. كتهضر بالدارجة المغربية. كون مفيد و خفيف الدم."}
            text_messages = get_text_messages()
            messages = [system_prompt] + text_messages + [{"role": "user", "content": prompt}]
            chat_completion = client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=1024)
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": response})

prompt_with_image = st.chat_input("كتب سؤالك على الصورة هنا...")
prompt_text_only = st.chat_input("كتب سؤالك هنا... ولا قول 'ولد ليا صورة ديال...'", key="text_only")

if uploaded_file is not None and prompt_with_image:
    process_with_image(uploaded_file, prompt_with_image)
    st.session_state.uploader_key += 1
    st.rerun()

elif prompt_text_only:
    # إلا طلب توليد صورة بالدارجة
    if any(word in prompt_text_only for word in ["ولد ليا", "صاوب ليا", "رسم ليا", "صورة ديال"]):
        with st.chat_message("user"):
            st.markdown(prompt_text_only)
        with st.chat_message("assistant"):
            image_bytes = generate_image(prompt_text_only)
            if isinstance(image_bytes, bytes): # إلا رجعت الصورة
                st.image(image_bytes, caption="صورة مولدة بالذكاء الاصطناعي")
                st.download_button("📥 تحميل الصورة", image_bytes, "ram_bot_image.png", "image/png")

                st.session_state.messages.append({"role": "user", "content": prompt_text_only})
                # خزنا الصورة كـ bytes باش نقدر نعرضها من بعد
                st.session_state.messages.append({"role": "assistant", "content": f"ها هي الصورة ديال: {prompt_text_only}", "content_bytes": image_bytes, "image": "ai_generated"})
            else: # إلا كان Error
                st.error(f"ما قدرتش نولد الصورة دابا. الخطأ: {image_bytes}")
    else:
        process_text_only(prompt_text_only)

if st.button("🗑️ مسح المحادثة"):
    st.session_state.messages = []
    st.session_state.uploader_key = 0
    st.rerun()

st.markdown("<div style='text-align: center; color: white; margin-top: 2rem;'>صنع بـ ❤️ بواسطة رضا مالكي</div>", unsafe_allow_html=True)
