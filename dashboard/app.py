import sys
import os
import time
import asyncio
import streamlit as st
import streamlit.components.v1 as components

# Ensure root path is included for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.orchestrator import run_agents
from agents.coder import coder
from state import init_session, log_message
from config import CONFIG

# Page setup
st.set_page_config(page_title="AI Director (MGX Clone)", layout="wide")
init_session()

# Live Preview Panel
st.markdown("### 🖥️ Live Preview")
try:
    components.iframe("http://localhost:8600", height=600)
except Exception as e:
    st.warning(f"⚠️ Could not load preview: {e}")

# Sidebar: Model + Mode
st.sidebar.title("⚙️ Settings")
model_choice = st.sidebar.selectbox("🧠 Choose Model", ["phi3:latest", "gemma3:latest", "tinyllama:latest"])
CONFIG["llm_config"]["model"] = model_choice

mode = st.sidebar.radio("🚀 Execution Mode", ["Team Mode", "Fast Mode (Coder Only)"])
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state["messages"] = []

st.sidebar.markdown("---")
st.sidebar.markdown("Built by DP-Tech1324")

# Main Title
st.title("🤖 AI Director Team — MGX Clone")

# Input Area
st.markdown("### 🧭 What should the AI team do?")
user_input = st.text_input("📤 Enter a task or goal", key="user_input")

# Run Task
if st.button("▶️ Run Task") and user_input.strip():
    log_message("User", user_input.strip())
    with st.spinner("🧠 Thinking..."):
        start = time.time()
        if mode == "Fast Mode (Coder Only)":
            response = coder.generate_reply([{"role": "user", "content": user_input.strip()}])
            log_message("Coder", response)
        else:
            try:
                responses = asyncio.run(run_agents(user_input.strip()))
                for name, reply in responses.items():
                    log_message(name, reply)
            except Exception as e:
                log_message("System", f"❌ Error during agent execution: {e}")
        duration = time.time() - start
        st.success(f"✅ Task completed in {duration:.2f} seconds")

st.divider()

# Final Output Panel
st.markdown("## 🏁 Final Output")
final = ""
for name, msg in reversed(st.session_state["messages"]):
    if name in ["Planner", "Scribe", "Coder"]:
        final = msg
        break
if final:
    st.code(final, language="python")
else:
    st.info("No final output yet. Run a task to see results.")

# Conversation Log
st.markdown("## 📜 Agent Conversation Log")
for name, msg in st.session_state["messages"]:
    st.markdown(f"**{name}:** {msg}")