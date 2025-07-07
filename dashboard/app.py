import streamlit as st
from orchestrator import run_agents
from state import init_session

st.set_page_config(page_title="AI Director Dashboard", layout="wide")
st.title("🤖 AI Agent Company Dashboard")

# Initialize memory state
init_session()

# Input box for user command
user_input = st.text_input("📤 What do you want the team to do?", key="user_input")

if st.button("▶️ Run Task") and user_input:
    st.session_state["messages"].append(("User", user_input))
    with st.spinner("🧠 Thinking..."):
        responses = run_agents(user_input)
        for name, reply in responses.items():
            st.session_state["messages"].append((name, reply))

# Display chat history
st.markdown("## 📜 Conversation Log")
for name, msg in st.session_state["messages"]:
    st.markdown(f"**{name}:** {msg}")
