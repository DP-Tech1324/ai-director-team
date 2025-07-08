import streamlit as st

def init_session():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

def log_message(name, msg):
    st.session_state["messages"].append((name, msg))
