import streamlit as st
import google.generativeai as genai
from PIL import Image

# ... باقي الكود ديالك ...

uploaded_file = st.file_uploader("رفع صورة", type=["jpg", "jpeg", "png"], key="uploader")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="الصورة المرفوعة", use_column_width=True)
    
    if st.button("حلل الصورة"):
        with st.spinner("كنحلل الصورة..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "وصف ليا هاد الصورة بالتفصيل بالعربية"
            response = model.generate_content([prompt, image])
            st.write(response.text)
            
            # أهم سطر: نفرغو الصورة باش ما تبقاش فالذاكرة
            st.session_state.uploader = None
            st.rerun()

# باقي الكود ديال السؤال العادي
user_input = st.text_input("سول سؤال عادي بلا صورة:")
if user_input:
    # هنا غيجاوب عادي بلا ما يربطو بالصورة القديمة
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(user_input)
    st.write(response.text)
