import sys
import os
import time
import asyncio
import re
import html
import glob
import streamlit as st
from datetime import datetime

# Ensure root path is included for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.orchestrator import run_agents
from agents.coder import coder
from state import init_session, log_message
from config import CONFIG

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="AI Director (MGX Clone)", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
body, .stApp { background: #181c20 !important; color: #f1f1f1 !important; font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif; }
.chat-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75em; }
.chat-window { max-height: 72vh; min-height: 520px; overflow-y: auto; padding: 1.2rem; background: #23272e; border-radius: 22px; box-shadow: 0 2px 16px #0004; border: 1px solid #2a313a; }
.bubble { display: flex; align-items: flex-end; margin-bottom: 1.1em; }
.bubble.agent { justify-content: flex-start; }
.bubble.user { justify-content: flex-end; }
.bubble-inner { padding: 1.05em 1.35em; border-radius: 22px; box-shadow: 0 2px 8px #0002; font-size: 1.05em; max-width: 48vw; word-break: break-word; border: 1.5px solid #232e3a; }
.bubble.agent .bubble-inner { background: #232e3a; color: #f1f1f1; }
.bubble.user .bubble-inner { background: #2e8b57; color: #fff; }
.bubble.Planner .bubble-inner { background: #3b82f6; color: #fff; }
.bubble.Coder .bubble-inner { background: #a21caf; color: #fff; }
.bubble.Researcher .bubble-inner { background: #f59e42; color: #fff; }
.bubble.Designer .bubble-inner { background: #f43f5e; color: #fff; }
.bubble.Scribe .bubble-inner { background: #10b981; color: #fff; }
.bubble.QA .bubble-inner { background: #fbbf24; color: #23272e; }
.bubble.Director .bubble-inner { background: #0ea5e9; color: #001018; }
.avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.35em; margin-right: 0.65em; border: 2px solid #232e3a; }
.avatar.User { background: #2e8b57; }
.avatar.Planner { background: #2563eb; }
.avatar.Coder { background: #7c3aed; }
.avatar.Researcher { background: #ea580c; }
.avatar.Designer { background: #be123c; }
.avatar.Scribe { background: #059669; }
.avatar.QA { background: #f59e42; }
.avatar.Director { background: #0284c7; }
.timestamp { font-size: 0.82em; color: #c7c7c7; margin-top: 0.4em; display: inline-block; opacity: 0.9; }
.panel { background: #20252b; border: 1px solid #2a313a; border-radius: 18px; padding: 1rem; box-shadow: 0 2px 12px #0002; }
.small { font-size: 0.95em; color: #cfcfcf; }
hr { border: none; border-top: 1px solid #2a313a; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

init_session()

# ----------------------------
# Helpers
# ----------------------------
emoji_map = {
    "User": "🧑",
    "Planner": "🗺️",
    "Coder": "💻",
    "Researcher": "🔬",
    "Designer": "🎨",
    "Scribe": "📝",
    "QA": "✅",
    "Director": "🎯",
    "System": "⚙️"
}

def parse_code_blocks(text: str):
    """
    Returns list of dicts:
    [{"lang": "python", "code": "...", "raw": "```python ...```"}, ...]
    plus remaining plain text.
    """
    blocks = []
    pattern = r"```(\w+)?\s*([\s\S]*?)```"
    for m in re.finditer(pattern, text):
        lang = (m.group(1) or "").strip() or "text"
        code = (m.group(2) or "").strip()
        blocks.append({"lang": lang, "code": code, "raw": m.group(0)})
    plain = re.sub(pattern, "", text).strip()
    return blocks, plain

def get_last_output(prefer=("Coder", "Planner", "Designer", "Researcher", "Scribe", "QA", "Director")):
    for name, msg_obj in reversed(st.session_state["messages"]):
        if name in prefer:
            text = msg_obj["text"] if isinstance(msg_obj, dict) else str(msg_obj)
            return name, str(text)
    return None, ""

def list_scribe_files(limit=10):
    # memory/scribe_log_*.md (root folder)
    files = sorted(glob.glob(os.path.join("memory", "scribe_log_*.md")), reverse=True)
    return files[:limit]

def render_message(name, text, timestamp, is_user):
    align = "flex-end" if is_user else "flex-start"
    bubble_class = "user" if is_user else "agent"
    avatar = emoji_map.get(name, "🤖")
    avatar_class = name if name in emoji_map else "Agent"

    blocks, plain = parse_code_blocks(text)

    # Bubble header (avatar + title)
    st.markdown(f"""
    <div class='bubble {bubble_class} {name}' style='justify-content: {align};'>
      {'<div class="avatar ' + avatar_class + '">' + avatar + '</div>' if not is_user else ''}
      <div class='bubble-inner'>
        <div style='font-weight:700; margin-bottom: 0.35em;'>{html.escape(name)}</div>
    """, unsafe_allow_html=True)

    # Plain text
    if plain:
        st.markdown(
            f"<div style='white-space: pre-wrap;'>{html.escape(plain)}</div>",
            unsafe_allow_html=True
        )

    # Code blocks rendered properly
    for b in blocks:
        st.code(b["code"], language=b["lang"])

    # Timestamp footer
    st.markdown(f"<span class='timestamp'>{html.escape(timestamp)}</span></div>", unsafe_allow_html=True)

    # User avatar on right (optional)
    if is_user:
        st.markdown(f"<div class='avatar User'>{emoji_map.get('User','🧑')}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Layout: Left / Center / Right
# ----------------------------
left, center, right = st.columns([1.1, 2.2, 1.2], gap="large")

with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Settings")

    model_choice = st.selectbox("🧠 Choose Model", ["phi3:latest", "gemma3:latest", "tinyllama:latest"])
    CONFIG["llm_config"]["model"] = model_choice

    mode = st.radio("🚀 Execution Mode", ["Team Mode", "Fast Mode (Coder Only)"], horizontal=False)

    st.markdown("<hr/>", unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()
    with colB:
        who, out = get_last_output()
        if st.button("📋 Copy Last", use_container_width=True):
            st.session_state["_copy_last"] = out

    st.markdown("<div class='small'>Built by DP-Tech1324</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with center:
    st.markdown("""
    <div class='chat-header'>
      <h2 style='margin:0; font-weight:800;'>🤖 AI Director Team — MGX Clone</h2>
    </div>
    """, unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("📤 Enter a task or goal...")

    if user_input and user_input.strip():
        now = datetime.now().strftime("%H:%M:%S")
        log_message("User", {"text": user_input.strip(), "timestamp": now})

        with st.spinner("🧠 Thinking..."):
            start = time.time()

            if mode == "Fast Mode (Coder Only)":
                response = coder.generate_reply([{"role": "user", "content": user_input.strip()}])
                now = datetime.now().strftime("%H:%M:%S")
                log_message("Coder", {"text": str(response), "timestamp": now})
            else:
                try:
                    responses = asyncio.run(run_agents(user_input.strip()))
                    # keep stable ordering in UI
                    order = ["Director", "Planner", "Researcher", "Coder", "Designer", "Scribe", "QA", "System"]
                    for name in order:
                        if name in responses:
                            now = datetime.now().strftime("%H:%M:%S")
                            log_message(name, {"text": str(responses[name]), "timestamp": now})
                except Exception as e:
                    now = datetime.now().strftime("%H:%M:%S")
                    log_message("System", {"text": f"❌ Error during agent execution: {e}", "timestamp": now})

            duration = time.time() - start
            st.success(f"✅ Done in {duration:.2f}s")

    # Conversation
    st.markdown("### 📜 Conversation")
    st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
    for name, msg_obj in st.session_state["messages"]:
        text = msg_obj["text"] if isinstance(msg_obj, dict) else str(msg_obj)
        timestamp = msg_obj.get("timestamp", "") if isinstance(msg_obj, dict) else ""
        is_user = name == "User"
        render_message(name, str(text), timestamp, is_user)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### 🏁 Final Output")

    last_name, last_text = get_last_output()
    if last_name:
        st.markdown(f"**From:** `{last_name}`")
        blocks, plain = parse_code_blocks(last_text)
        if plain:
            st.markdown(plain)
        for b in blocks:
            st.code(b["code"], language=b["lang"])
    else:
        st.info("Run a task to see the latest output here.")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("### 📝 Recent Scribe Logs")

    files = list_scribe_files(limit=6)
    if not files:
        st.caption("No scribe logs yet.")
    else:
        for fp in files:
            label = os.path.basename(fp)
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
                st.download_button(
                    label=f"⬇️ {label}",
                    data=content,
                    file_name=label,
                    mime="text/markdown",
                    use_container_width=True
                )
            except Exception:
                st.caption(f"Could not read {label}")

    st.markdown("</div>", unsafe_allow_html=True)
