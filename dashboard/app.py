import streamlit as st
import time
from orchestrator import run_agents
from state import init_session, log_message
from config import CONFIG

st.set_page_config(page_title="AI Director Dashboard", layout="wide")
st.title("🤖 AI Agent Company Dashboard")

# Initialize memory state
init_session()

# 🔄 Model selector
st.markdown("### 🧠 Choose a Model")
model_choice = st.selectbox(
    "Select a local model to use:",
    ["phi3:latest", "gemma3:latest", "tinyllama:latest"],
    index=0
)
CONFIG["llm_config"]["model"] = model_choice

# Input box for user command
with st.container():
    st.markdown("### 🧭 Enter a Goal for the AI Team")
    user_input = st.text_input("📤 What do you want the team to do?", key="user_input")

    if st.button("▶️ Run Task") and user_input.strip():
        log_message("User", user_input.strip())
        with st.spinner("🧠 Thinking..."):
            start_time = time.time()
            responses = run_agents(user_input.strip())
            duration = time.time() - start_time
            st.success(f"✅ Task completed in {duration:.2f} seconds")
            for name, reply in responses.items():
                log_message(name, reply)

            st.experimental_rerun()  # 🔁 Force UI to refresh and show new messages


st.divider()

# Display chat history
st.markdown("## 📜 Conversation Log")
for name, msg in st.session_state["messages"]:
    st.markdown(f"**{name}:** {msg}")