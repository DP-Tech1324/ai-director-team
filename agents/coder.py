import os
from agents.base import BaseAgent


def _wrap_code(lang: str, code: str) -> str:
    code = (code or "").rstrip()
    return f"```{lang}\n{code}\n```"


class CoderAgent(BaseAgent):
    def generate_reply(self, messages):
        task = messages[-1]["content"] if messages else ""
        task_l = task.lower()

        # Ensure memory folder exists
        os.makedirs("memory", exist_ok=True)

        # 1) Streamlit login page
        if "streamlit" in task_l and "login" in task_l:
            code = """import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

# Demo credentials (replace with real auth later)
VALID_USER = "admin"
VALID_PASS = "admin123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def logout():
    st.session_state.logged_in = False

st.title("🔐 Login")

if st.session_state.logged_in:
    st.success("✅ You are logged in!")
    st.write("Protected content goes here…")
    st.button("Logout", on_click=logout)
else:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if not username or not password:
                st.error("Please enter both username and password.")
            elif username == VALID_USER and password == VALID_PASS:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
    with col2:
        st.caption("Tip: Replace hardcoded creds with OAuth/Supabase/Auth0 later.")
"""
            return _wrap_code("python", code)

        # 2) Realtor lead capture PRD + Streamlit MVP
        if (
            ("realtor" in task_l or "real estate" in task_l)
            and ("lead" in task_l or "capture" in task_l or "form" in task_l or "prd" in task_l)
        ):
            md = """# Mini PRD — Realtor Lead Capture Form

## Goal
Capture buyer/seller leads and route them quickly with clean data.

## Must-have Fields
- Full name
- Email
- Phone
- Interest type: Buyer / Seller / Both
- Location (City/Neighborhood)
- Timeline (ASAP / 1–3 months / 3–6 months / 6+ months)
- Consent checkbox (CASL/marketing)

## Nice-to-have
- Preferred contact method + best time
- Budget range (buyers) / estimate range (sellers)
- Notes/free text
- Lead source (hidden: UTM/referrer/page)

## Validation
- Required: name/email/phone + interest type
- Block submit if consent unchecked (optional, depends on policy)

## Success
- Thank-you message
- Save lead to CSV (MVP)
- Notify agent later (email/SMS)

---

## Streamlit MVP Form (saves to CSV)
```python
import streamlit as st
import csv
import os
from datetime import datetime

os.makedirs("memory", exist_ok=True)
FILE = "memory/realtor_leads.csv"

st.title("🏡 Contact a Realtor")

with st.form("lead_form"):
    name = st.text_input("Full Name *")
    email = st.text_input("Email *")
    phone = st.text_input("Phone *")
    interest = st.selectbox("I am a *", ["Buyer", "Seller", "Both"])
    city = st.text_input("Preferred City/Area")
    timeline = st.selectbox("Timeline", ["ASAP", "1–3 months", "3–6 months", "6+ months"])
    notes = st.text_area("Notes")
    consent = st.checkbox("I agree to be contacted about real estate services.")
    submitted = st.form_submit_button("Submit")

if submitted:
    if not name or not email or not phone:
        st.error("Please fill Name, Email, and Phone.")
    elif not consent:
        st.error("Please confirm consent to be contacted.")
    else:
        with open(FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([datetime.now().isoformat(), name, email, phone, interest, city, timeline, notes])
        st.success("✅ Thanks! We’ll contact you shortly.")
"""
            return md
        # 3) Fallback generic starter snippet
        code = f"""# Starter snippet generator
    Task: {task}

def main():
    print("Task received:")
    print({task!r})
    print("\\nNext: implement your specific requirement here.")

if __name__ == "__main__":
    main()
"""
        return _wrap_code("python", code)

coder = CoderAgent(
    name="Coder",
    system_message="You are Coder. Always return working code/templates relevant to the task. Wrap code using triple-backticks.",
)