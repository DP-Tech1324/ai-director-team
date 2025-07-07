# 🧠 AI Director Team

A local-first, MGX-style multi-agent AI company — powered by [AutoGen](https://github.com/microsoft/autogen), Streamlit, and Ollama.

## 🚀 Features
- 🤖 Multi-agent setup: Director, Planner, Coder, Researcher, Scribe, Designer, QA
- 🧠 Task delegation and collaboration
- 🖥️ Streamlit dashboard to manage agents
- 🌐 Local-only AI via Ollama — no cloud API needed

## 📁 Structure

ai-director-team/
├── agents/ # All agent roles
├── dashboard/ # Streamlit UI
├── memory/ # Chat logs and saved outputs
├── main.py # CLI interface
└── requirements.txt # Base dependencies


## 📦 Setup Instructions

```bash
# Install base
cd ai-director-team
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# For dashboard
cd dashboard
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
🛠 Tech Stack
AutoGen

Streamlit

Ollama