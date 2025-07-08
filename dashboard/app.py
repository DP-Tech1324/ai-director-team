import sys
import os
import time
import asyncio
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

# Ensure root path is included for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.orchestrator import run_agents
from agents.coder import coder
from state import init_session, log_message
from config import CONFIG


# Page setup
st.set_page_config(page_title="AI Director (MGX Clone)", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    body, .stApp { background: #181c20 !important; color: #f1f1f1 !important; font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif; }
    .chat-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5em; }
    .chat-window { max-height: 60vh; min-height: 320px; overflow-y: auto; padding: 1.2rem 1.2rem 2.5rem 1.2rem; background: #23272e; border-radius: 22px; box-shadow: 0 2px 16px #0004; }
    .bubble { display: flex; align-items: flex-end; margin-bottom: 1.2em; transition: box-shadow 0.2s; }
    .bubble:hover .bubble-inner { box-shadow: 0 4px 16px #0005; }
    .bubble.agent { justify-content: flex-start; }
    .bubble.user { justify-content: flex-end; }
    .bubble-inner { padding: 1.1em 1.5em; border-radius: 22px; box-shadow: 0 2px 8px #0002; font-size: 1.13em; position: relative; max-width: 70vw; word-break: break-word; border: 1.5px solid #232e3a; }
    .bubble.agent .bubble-inner { background: #232e3a; color: #f1f1f1; }
    .bubble.user .bubble-inner { background: #2e8b57; color: #fff; }
    .bubble.Planner .bubble-inner { background: #3b82f6; color: #fff; }
    .bubble.Coder .bubble-inner { background: #a21caf; color: #fff; }
    .bubble.Researcher .bubble-inner { background: #f59e42; color: #fff; }
    .bubble.Designer .bubble-inner { background: #f43f5e; color: #fff; }
    .bubble.Scribe .bubble-inner { background: #10b981; color: #fff; }
    .bubble.QA .bubble-inner { background: #fbbf24; color: #23272e; }
    .avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5em; margin-right: 0.7em; box-shadow: 0 1px 4px #0002; border: 2px solid #232e3a; }
    .avatar.Planner { background: #2563eb; }
    .avatar.Coder { background: #7c3aed; }
    .avatar.Researcher { background: #ea580c; }
    .avatar.Designer { background: #be123c; }
    .avatar.Scribe { background: #059669; }
    .avatar.QA { background: #f59e42; }
    .avatar.User { background: #2e8b57; }
    .timestamp { font-size: 0.85em; color: #bdbdbd; margin-left: 0.7em; margin-top: 0.2em; }
    .input-bar { position: fixed; bottom: 0; left: 0; width: 100vw; background: #181c20cc; z-index: 100; padding: 1.1em 0.5em 1.1em 0.5em; box-shadow: 0 -2px 12px #0005; display: flex; align-items: center; }
    .input-bar input { width: 70vw; max-width: 700px; border-radius: 18px; border: none; padding: 0.9em 1.2em; font-size: 1.1em; background: #232e3a; color: #fff; margin-right: 1em; }
    .input-bar button { border-radius: 18px; background: #2e8b57; color: #fff; border: none; padding: 0.9em 1.5em; font-size: 1.1em; box-shadow: 0 2px 8px #0002; transition: background 0.2s; }
    .input-bar button:hover { background: #38b169; }
    .stTextInput>div>div>input { background: #232e3a !important; color: #fff !important; border-radius: 18px !important; }
    .collapsible { background: #232e3a; color: #fff; cursor: pointer; padding: 1em; width: 100%; border: none; text-align: left; outline: none; font-size: 1.1em; border-radius: 12px; margin-bottom: 0.5em; }
    .active, .collapsible:hover { background: #2e8b57; }
    .content { padding: 0 1.2em; display: none; overflow: hidden; background: #232e3a; border-radius: 0 0 12px 12px; }
    </style>
    <script>
    window.addEventListener('DOMContentLoaded', function() {
      var chatWindow = document.querySelector('.chat-window');
      if (chatWindow) chatWindow.scrollTop = chatWindow.scrollHeight;
    });
    </script>
""", unsafe_allow_html=True)
init_session()


# Live Preview Panel with button
st.markdown("### 🖥️ Live Preview")
if st.button("Open Live Preview in New Tab"):
    js = "window.open('http://localhost:8600', '_blank')"
    st.markdown(f'<script>{js}</script>', unsafe_allow_html=True)
st.info("Click the button above to open the live preview in a new browser tab.")

# Sidebar: Model + Mode
st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.selectbox("🧠 Choose Model", ["phi3:latest", "gemma3:latest", "tinyllama:latest"])
CONFIG["llm_config"]["model"] = model_choice

mode = st.sidebar.radio("🚀 Execution Mode", ["Team Mode", "Fast Mode (Coder Only)"])
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state["messages"] = []

st.sidebar.markdown("---")
st.sidebar.markdown("Built by DP-Tech1324")


# --- Modern Chat Header ---
st.markdown("""
<div class='chat-header'>
  <h2 style='margin:0; font-weight:700;'>🤖 AI Director Team — MGX Clone</h2>
  <button onclick="window.location.reload()" style='background:#232e3a;color:#fff;border:none;border-radius:14px;padding:0.6em 1.2em;font-size:1em;box-shadow:0 1px 4px #0002;cursor:pointer;'>🆕 New Chat</button>
</div>
""", unsafe_allow_html=True)

# --- Persistent Input Bar at Bottom ---
import streamlit.components.v1 as components
components.html('''
<div class="input-bar">
  <form id="chat-form" autocomplete="off">
    <input id="chat-input" name="chat-input" type="text" placeholder="📤 Enter a task or goal..." autofocus style="outline:none;" />
    <button type="submit">▶️ Run Task</button>
  </form>
</div>
<script>
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  form.onsubmit = function(e) {
    e.preventDefault();
    window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setComponentValue', value: input.value}, '*');
    input.value = '';
  };
</script>
''', height=90)

# --- Handle Input from Custom Bar ---
if "_input_value" not in st.session_state:
    st.session_state["_input_value"] = ""

user_input = st.query_params.get("chat-input", [""])[0]
if user_input.strip():
    now = datetime.now().strftime("%H:%M:%S")
    log_message("User", {"text": user_input.strip(), "timestamp": now})
    with st.spinner("🧠 Thinking..."):
        start = time.time()
        if mode == "Fast Mode (Coder Only)":
            response = coder.generate_reply([{"role": "user", "content": user_input.strip()}])
            now = datetime.now().strftime("%H:%M:%S")
            log_message("Coder", {"text": response, "timestamp": now})
        else:
            try:
                responses = asyncio.run(run_agents(user_input.strip()))
                for name, reply in responses.items():
                    now = datetime.now().strftime("%H:%M:%S")
                    log_message(name, {"text": reply, "timestamp": now})
            except Exception as e:
                now = datetime.now().strftime("%H:%M:%S")
                log_message("System", {"text": f"❌ Error during agent execution: {e}", "timestamp": now})
        duration = time.time() - start
        st.success(f"✅ Task completed in {duration:.2f} seconds")

st.markdown("<div style='height: 2.5em'></div>", unsafe_allow_html=True)

# Final Output Panel
st.markdown("## 🏁 Final Output")

# Find the last code output from Coder, Planner, or Scribe
final = ""
for name, msg in reversed(st.session_state["messages"]):
    if name in ["Planner", "Scribe", "Coder"]:
        text = msg["text"] if isinstance(msg, dict) else str(msg)
        # Try to extract code from a dict or string
        if text.strip().startswith("{')") or text.strip().startswith("{"):
            import json
            try:
                data = json.loads(text.replace("'", '"'))
                code = data.get("text", "")
                if code:
                    final = code
                    break
            except Exception:
                final = text
                break
        else:
            final = text
            break

import re


def extract_html_anywhere(text):
    # Try to extract HTML from code block first
    match = re.search(r"```html\s*([\s\S]+?)```", text, re.IGNORECASE)
    if match:
        return match.group(1)
    # Try to find the first <html ... </html> block
    match = re.search(r'(<html[\s\S]*?</html>)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    # Try to find the first <!DOCTYPE html ... </html> block
    match = re.search(r'<!DOCTYPE html[\s\S]*?</html>', text, re.IGNORECASE)
    if match:
        return match.group(0)
    # Fallback: if <html is present, extract from there to end (even if not closed)
    if '<html' in text:
        idx = text.find('<html')
        # Try to find closing </html>
        end_idx = text.find('</html>', idx)
        if end_idx != -1:
            return text[idx:end_idx+7]
        else:
            return text[idx:]
    return None

html_code = extract_html_anywhere(final)
if final:
    if html_code:
        st.code(html_code, language="html")
        if st.button("Preview HTML Output"):
            import base64
            html_b64 = base64.b64encode(html_code.encode("utf-8")).decode("utf-8")
            js = f"window.open('data:text/html;base64,{html_b64}', '_blank')"
            st.markdown(f'<script>{js}</script>', unsafe_allow_html=True)
    elif final.strip().startswith("```"):
        st.markdown(final)
    else:
        st.code(final, language="python")
else:
    st.info("No final output yet. Run a task to see results.")


st.markdown('</div>', unsafe_allow_html=True)

# --- Modern ChatGPT/Claude-like Chat UI ---
st.markdown("## 📜 Conversation")

import time as _time
import streamlit as st
import re

emoji_map = {
    "User": "🧑",
    "Planner": "🗺️",
    "Coder": "💻",
    "Researcher": "🔬",
    "Designer": "🎨",
    "Scribe": "📝",
    "QA": "✅",
    "System": "⚙️"
}

def render_code_block(code, lang_hint=None):
    # Show code with copy and preview (if HTML/JS/CSS)
    st.code(code, language=lang_hint or "text")
    col1, col2 = st.columns([1,1])
    with col1:
        st.button("Copy", key=f"copy_{hash(code)}", on_click=st.session_state.setdefault("_copy_code", code))
    with col2:
        if lang_hint and lang_hint.lower() in ["html", "css", "javascript", "js"]:
            if st.button("Preview", key=f"preview_{hash(code)}"):
                import base64
                html_b64 = base64.b64encode(code.encode("utf-8")).decode("utf-8")
                js = f"window.open('data:text/html;base64,{html_b64}', '_blank')"
                st.markdown(f'<script>{js}</script>', unsafe_allow_html=True)

def extract_code_blocks(text):
    # Returns list of (lang, code) tuples
    code_blocks = re.findall(r"```(\w+)?\s*([\s\S]+?)```", text)
    return code_blocks

def render_message(name, text, timestamp, is_user):
    # Modern bubble: pill shape, avatar, spacing, alignment
    align = "flex-end" if is_user else "flex-start"
    bubble_class = "user" if is_user else "agent"
    avatar = emoji_map.get(name, "🤖")
    avatar_class = name if name in emoji_map else "Agent"
    st.markdown(f"""
    <div class='bubble {bubble_class} {name}' style='justify-content: {align};'>
      {'<div class="avatar ' + avatar_class + '">' + avatar + '</div>' if not is_user else ''}
      <div class='bubble-inner'>
        <div style='font-size: 1.1em;'>{text}</div>
        <span class='timestamp'>{timestamp}</span>
      </div>
      {'<div class="avatar User">' + avatar + '</div>' if is_user else ''}
    </div>
    """, unsafe_allow_html=True)


# --- Chat Window ---
st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
for idx, (name, msg_obj) in enumerate(st.session_state["messages"]):
    text = msg_obj["text"] if isinstance(msg_obj, dict) else str(msg_obj)
    timestamp = msg_obj.get("timestamp", "") if isinstance(msg_obj, dict) else ""
    is_user = name == "User"
    code_blocks = extract_code_blocks(text)
    if code_blocks:
        for lang, code in code_blocks:
            render_message(name, f"<b>[{lang}]</b>", timestamp, is_user)
            render_code_block(code, lang)
    else:
        render_message(name, text, timestamp, is_user)
st.markdown("</div>", unsafe_allow_html=True)

# --- MVP: Show All Code Blocks (Collapsible) ---
all_code_blocks = []
for name, msg_obj in st.session_state["messages"]:
    text = msg_obj["text"] if isinstance(msg_obj, dict) else str(msg_obj)
    code_blocks = extract_code_blocks(text)
    for lang, code in code_blocks:
        all_code_blocks.append((lang, code))
if all_code_blocks:
    st.markdown("---")
    st.markdown("<button class='collapsible'>🗂️ All Code Blocks in Conversation</button><div class='content' style='display:none;'>", unsafe_allow_html=True)
    for i, (lang, code) in enumerate(all_code_blocks):
        st.markdown(f"**Block {i+1} [{lang}]**")
        render_code_block(code, lang)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <script>
    var coll = document.getElementsByClassName("collapsible");
    for (var i = 0; i < coll.length; i++) {
      coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
          content.style.display = "none";
        } else {
          content.style.display = "block";
        }
      });
    }
    </script>
    """, unsafe_allow_html=True)