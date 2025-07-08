import streamlit as st

def init_session():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "task_log" not in st.session_state:
        st.session_state["task_log"] = []

    if "agent_outputs" not in st.session_state:
        st.session_state["agent_outputs"] = {}

def log_message(sender, content):
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    st.session_state["messages"].append((sender, content))


def log_task(agent, task):
    if "task_log" not in st.session_state:
        st.session_state["task_log"] = []
    st.session_state["task_log"].append({"agent": agent, "task": task})

def store_output(agent, output):
    if agent not in st.session_state["agent_outputs"]:
        st.session_state["agent_outputs"][agent] = []
    st.session_state["agent_outputs"][agent].append(output)