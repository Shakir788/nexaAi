# app.py — Nexa (Study Buddy for Karyle)
import os
import re
import base64
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as components
from langdetect import detect

# ---------- Page config ----------
st.set_page_config(page_title="Nexa — Your Study Buddy", page_icon="📚", layout="centered")

# ---------- Custom Styles ----------
custom_style = """
    <style>
    body {
        background: linear-gradient(to right, #6dd5ed, #2193b0);
        color: #2c2c2c;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin: 6px 0;
    }
    .stChatMessage[data-testid="stChatMessage-user"] {
        background: #bbdefb;
        color: #2c2c2c;
    }
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background: #c8e6c9;
        color: #2c2c2c;
    }
    .header {
        background: linear-gradient(to right, #6dd5ed, #2193b0);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        color: #fff;
    }
    .logo {
        font-size: 2.0em;
        color: #fff;
        font-weight: 700;
        font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    footer:after {
        content:'📚 Built by Mohammad — Nexa (Study Buddy)';
        visibility: visible;
        display: block;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #fff;
    }
    .chat-container {
        height: 60vh;
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: #2193b0 #6dd5ed;
        padding-right: 6px;
    }
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background-color: #2193b0;
        border-radius: 4px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: #6dd5ed;
    }
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# ---------- Helpers ----------
def remove_emojis(text: str) -> str:
    emoji_pattern = re.compile(
        "[" 
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r"", text)

def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", " ")

def process_image(file):
    bytes_data = file.getvalue()
    mime = "image/png" if file.name.lower().endswith(".png") else "image/jpeg"
    return base64.b64encode(bytes_data).decode("utf-8"), mime

# ---------- Load API Key ----------
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    st.error("⚠️ OPENROUTER_API_KEY missing in secrets or .env. Add OPENROUTER_API_KEY.")
    st.stop()

# ---------- Initialize OpenRouter client ----------
# Updated: compatible with OpenAI SDK usage, no proxies argument
from openai import OpenAI
import os

# Remove any proxy environment variables
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)

try:
    client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")
except TypeError as e:
    st.error(f"OpenRouter client initialization failed: {e}")
    st.stop()




# ---------- Header ----------
st.markdown('<div class="header"><div class="logo">Nexa — Your Study Buddy</div></div>', unsafe_allow_html=True)

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": (
                "You are Nexa, a supportive AI study buddy for Karyle from the Philippines. "
                "You help with studies, homework, notes, and motivation. "
                "If asked about your creator, say: 'Mohammad from India — a creative developer and designer'. "
                "Auto-detect Tagalog/English and reply naturally in the same. "
                "Keep your tone friendly, motivating, and helpful."
            ),
        }
    ]

if "profile" not in st.session_state:
    st.session_state["profile"] = {
        "name": "Karyle",
        "age": 20,
        "location": "Dasmariñas, Philippines",
        "languages": ["English", "Tagalog"]
    }

# ---------- Chat History ----------
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state["messages"]:
        if msg["role"] == "system":
            continue
        if msg["role"] == "user":
            with st.chat_message("user", avatar="assets/user.png"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="assets/logo.png"):
                st.markdown(msg["content"])
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Image Upload ----------
uploaded_image = st.file_uploader("Upload an image (homework / screenshot)", type=["jpg", "jpeg", "png"], key="chat_image")
if uploaded_image is not None:
    b64_image, mime = process_image(uploaded_image)
    vision_messages = [
        {"role": "user", "content": f"IMAGE_DATA:data:{mime};base64,{b64_image}\nPlease extract and summarize or solve if it's a question."}
    ]
    st.session_state["messages"].append({"role": "user", "content": f"Uploaded image: {uploaded_image.name}"})
    with st.chat_message("user", avatar="assets/user.png"):
        st.image(uploaded_image, caption=uploaded_image.name, use_container_width=True)
        st.markdown("Analyzing image...")
    with st.chat_message("assistant", avatar="assets/logo.png"):
        placeholder = st.empty()
        try:
            resp = client.chat.completions.create(
                model=os.getenv("VISION_MODEL", "qwen/qwen2.5-vl-32b-instruct:free"),
                messages=vision_messages,
                max_tokens=500
            )
            assistant_text = resp.choices[0].message.content
            placeholder.markdown(assistant_text)
        except Exception as e:
            assistant_text = f"Error analyzing image: {e}"
            placeholder.markdown(assistant_text)
    st.session_state["messages"].append({"role": "assistant", "content": assistant_text})

# ---------- User Input & Streaming ----------
user_input = st.chat_input("Type your question...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="assets/user.png"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="assets/logo.png"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=os.getenv("CHAT_MODEL", "openai/gpt-4o-mini"),
                messages=st.session_state["messages"],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        full_response += delta
                        placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response or "_(no response)_")
        except Exception as e:
            full_response = f"Error: {str(e)}"
            placeholder.markdown(full_response)
    st.session_state["messages"].append({"role": "assistant", "content": full_response})

# ---------- TTS ----------
if st.button("🔊 Read last response"):
    if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "assistant":
        last_reply = st.session_state["messages"][-1]["content"]
        safe_reply = remove_emojis(last_reply)
        try:
            lang = detect(last_reply)
            lang_code = "fil-PH" if lang in ["tl", "fil"] else "en-US"
        except Exception:
            lang_code = "en-US"
        components.html(
            f"""
            <script>
            if ('speechSynthesis' in window) {{
                const utterance = new SpeechSynthesisUtterance("{js_escape(safe_reply)}");
                utterance.lang = "{lang_code}";
                utterance.pitch = 1.05;
                utterance.rate = 0.95;
                speechSynthesis.speak(utterance);
            }} else {{
                alert('Speech synthesis not supported.');
            }}
            </script>
            """,
            height=0,
        )

# ---------- Sidebar Tools ----------
st.sidebar.header("Student Tools")
if "tools_visible" not in st.session_state:
    st.session_state["tools_visible"] = False
if st.sidebar.button("Show/Hide Tools"):
    st.session_state["tools_visible"] = not st.session_state["tools_visible"]

if st.session_state["tools_visible"]:
    # Study Timer
    if "timer_running" not in st.session_state:
        st.session_state["timer_running"] = False
        st.session_state["timer_start"] = 0.0
        st.session_state["timer_elapsed"] = 0.0

    if st.sidebar.button("Start Study Timer"):
        if not st.session_state["timer_running"]:
            st.session_state["timer_start"] = time.time()
            st.session_state["timer_running"] = True
            st.sidebar.success("Timer started! 📖")
    if st.sidebar.button("Stop Study Timer"):
        if st.session_state["timer_running"]:
            st.session_state["timer_elapsed"] += time.time() - st.session_state["timer_start"]
            st.session_state["timer_running"] = False
            minutes, seconds = divmod(int(st.session_state["timer_elapsed"]), 60)
            st.sidebar.success(f"Study time: {minutes}m {seconds}s ⏰")

    # Notes
    if "notes" not in st.session_state:
        st.session_state["notes"] = ""
    note_input = st.sidebar.text_area("Add a quick note", st.session_state["notes"], key="note_input")
    if st.sidebar.button("Save Note"):
        st.session_state["notes"] = note_input
        st.sidebar.success("Note saved! 📝")
    if st.session_state["notes"]:
        st.sidebar.write(st.session_state["notes"])

    # Motivation
    if st.sidebar.button("Get Motivation"):
        quotes = [
            "Keep going, Karyle! You're doing amazing! 🌟",
            "Every small step is progress 📚",
            "Believe in yourself—you got this 💪"
        ]
        idx = st.session_state.get("motivation_index", 0)
        st.sidebar.info(quotes[idx])
        st.session_state["motivation_index"] = (idx + 1) % len(quotes)
