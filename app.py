import streamlit as st
from groq import Groq
import io
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av

st.set_page_config(page_title="RAM Bot v4.7", page_icon="🤖")

try: client = Groq(api_key=st.secrets["GROQ_KEY"])
except: st.error("🚨 GROQ_KEY"); st.stop()

st.markdown("""<style>.stApp{background:#0e1117}.card{background:#262730;padding:1rem;border-radius:15px;text-align:center;color:white}</style>""",unsafe_allow_html=True)
st.markdown('<div class="card"><h2>🤖 RAM Bot v4.7 - Live</h2></div>', unsafe_allow_html=True)

def tts_fast(text):
    return BytesIO(client.audio.speech.create(model="playai-tts", voice="Arman", input=text, response_format="wav").read())

def stt_groq(audio_bytes):
    audio_file = io.BytesIO(audio_bytes); audio_file.name = "audio.webm"
    res = client.audio.transcriptions.create(file=audio_file, model="whisper-large-v3-turbo", language="ar")
    return res.text

def call_groq(messages):
    return client.chat.completions.create(messages=messages, model="llama-3.3-70b-versatile", max_tokens=100).choices[0].message.content

class AudioProcessor(AudioProcessorBase):
    def __init__(self): self.audio_buffer = BytesIO(); self.last_send = 0
    def recv_audio(self, frame: av.AudioFrame):
        # كنرسلو كل 3 ثواني تلقائيا إلا كان فيه صوت
        import time
        if time.time() - self.last_send > 3:
            self.last_send = time.time()
            if self.audio_buffer.getbuffer().nbytes > 5000: # إلا هضرتي
                st.session_state.audio_q.put(self.audio_buffer.getvalue())
                self.audio_buffer = BytesIO()
        self.audio_buffer.write(frame.to_ndarray().tobytes())
        return frame

if "messages" not in st.session_state: st.session_state.messages = []
if "audio_q" not in st.session_state: st.session_state.audio_q = queue.Queue()
if "is_bot_speaking" not in st.session_state: st.session_state.is_bot_speaking = False

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "audio" in msg: st.audio(msg["audio"], autoplay=(msg["role"]=="assistant"))
        st.markdown(msg["content"])

# يبدا يخدم بوحدو
webrtc_ctx = webrtc_streamer(key="voice", mode=WebRtcMode.SENDONLY, audio_processor_factory=AudioProcessor, media_stream_constraints={"video": False, "audio": True}, auto_start=True)

# المعالجة فالخلفية
if not st.session_state.audio_q.empty() and not st.session_state.is_bot_speaking:
    audio_data = st.session_state.audio_q.get()
    with st.spinner("..."):
        st.session_state.is_bot_speaking = True
        user_text = stt_groq(audio_data)
        if user_text:
            st.session_state.messages.append({"role":"user","content":user_text})
            response = call_groq([{"role":"system","content":"جاوب بجملة وحدة قصيرة بالدارجة"}] + st.session_state.messages)
            audio_res = tts_fast(response)
            st.session_state.messages.append({"role":"assistant","content":response, "audio":audio_res})
        st.session_state.is_bot_speaking = False
        st.rerun()
