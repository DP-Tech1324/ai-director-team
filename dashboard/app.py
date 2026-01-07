# dashboard/app.py
import sys
import os
import time
import asyncio
import re
import html
import glob
import json
import streamlit as st
from datetime import datetime

# Ensure root path is included for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.orchestrator import run_agents
from agents.coder import coder  # used only if you ever want local-only fast mode (not used in Phase 2 path)
from state import init_session, log_message
from config import CONFIG

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(page_title="AI Director (MGX Clone)", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
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
.bubble.System .bubble-inner { background: #64748b; color: #0b1220; }

.avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.35em; margin-right: 0.65em; border: 2px solid #232e3a; }
.avatar.User { background: #2e8b57; }
.avatar.Planner { background: #2563eb; }
.avatar.Coder { background: #7c3aed; }
.avatar.Researcher { background: #ea580c; }
.avatar.Designer { background: #be123c; }
.avatar.Scribe { background: #059669; }
.avatar.QA { background: #f59e42; }
.avatar.Director { background: #0284c7; }
.avatar.System { background: #475569; }

.timestamp { font-size: 0.82em; color: #c7c7c7; margin-top: 0.4em; display: inline-block; opacity: 0.9; }
.panel { background: #20252b; border: 1px solid #2a313a; border-radius: 18px; padding: 1rem; box-shadow: 0 2px 12px #0002; }
.small { font-size: 0.95em; color: #cfcfcf; }
hr { border: none; border-top: 1px solid #2a313a; margin: 1rem 0; }
.badge { display:inline-block; padding: 0.25rem 0.6rem; border-radius: 999px; border: 1px solid #2a313a; background:#1a1f25; color:#d4d4d4; font-size:0.85em; }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
</style>
""",
    unsafe_allow_html=True,
)

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
    "System": "⚙️",
}


def parse_code_blocks(text: str):
    """
    Returns list of dicts:
    [{"lang": "python", "code": "...", "raw": "```python ...```"}, ...]
    plus remaining plain text.
    """
    blocks = []
    pattern = r"```(\w+)?\s*([\s\S]*?)```"
    for m in re.finditer(pattern, text or ""):
        lang = (m.group(1) or "").strip() or "text"
        code = (m.group(2) or "").strip()
        blocks.append({"lang": lang, "code": code, "raw": m.group(0)})
    plain = re.sub(pattern, "", text or "").strip()
    return blocks, plain


def get_last_output(prefer=("Scribe", "Coder", "Planner", "Designer", "Researcher", "QA", "Director", "System")):
    for name, msg_obj in reversed(st.session_state.get("messages", [])):
        if name in prefer:
            text = msg_obj["text"] if isinstance(msg_obj, dict) else str(msg_obj)
            return name, str(text)
    return None, ""


def list_scribe_files(limit=10, project_slug=None, run_id=None):
    """
    Supports BOTH legacy: memory/scribe_log_*.md
    AND new: projects/{project}/runs/{run_id}/scribe.md (or any scribe*.md)
    """
    files = []
    # Legacy
    files.extend(sorted(glob.glob(os.path.join("memory", "scribe_log_*.md")), reverse=True))
    # Project-based
    if project_slug:
        base = os.path.join("projects", project_slug, "runs")
        if run_id:
            files.extend(sorted(glob.glob(os.path.join(base, run_id, "scribe*.md")), reverse=True))
        else:
            files.extend(sorted(glob.glob(os.path.join(base, "*", "scribe*.md")), reverse=True))
    # De-dupe while preserving order
    seen = set()
    out = []
    for f in files:
        if f not in seen and os.path.isfile(f):
            seen.add(f)
            out.append(f)
    return out[:limit]


def render_message(name, text, timestamp, is_user):
    align = "flex-end" if is_user else "flex-start"
    bubble_class = "user" if is_user else "agent"
    avatar = emoji_map.get(name, "🤖")
    avatar_class = name if name in emoji_map else "Agent"

    blocks, plain = parse_code_blocks(text)

    st.markdown(
        f"""
    <div class='bubble {bubble_class} {html.escape(name)}' style='justify-content: {align};'>
      {'<div class="avatar ' + html.escape(avatar_class) + '">' + html.escape(avatar) + '</div>' if not is_user else ''}
      <div class='bubble-inner'>
        <div style='font-weight:800; margin-bottom: 0.35em;'>{html.escape(name)}</div>
    """,
        unsafe_allow_html=True,
    )

    if plain:
        st.markdown(
            f"<div style='white-space: pre-wrap;'>{html.escape(plain)}</div>",
            unsafe_allow_html=True,
        )

    for b in blocks:
        st.code(b["code"], language=b["lang"])

    st.markdown(
        f"<span class='timestamp'>{html.escape(timestamp or '')}</span></div>",
        unsafe_allow_html=True,
    )

    if is_user:
        st.markdown(
            f"<div class='avatar User'>{html.escape(emoji_map.get('User','🧑'))}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def infer_project_from_goal(goal: str) -> str:
    g = (goal or "").lower()
    if "realtor" in g or "real estate" in g or "lead" in g:
        return "realtor-leads"
    if "streamlit" in g:
        return "streamlit-apps"
    if "landing" in g or "website" in g:
        return "web-projects"
    return "default"


def safe_read_text(fp: str) -> str:
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def run_agents_sync(goal: str, project: str, mode: str, model: str):
    """
    Safe runner for async orchestrator from Streamlit.
    Prefer asyncio.run, but protect against environments that already have a loop.
    """
    try:
        loop = asyncio.get_running_loop()
        # If already inside an event loop, schedule task and wait
        task = loop.create_task(run_agents(goal=goal, project=project, mode=mode, model=model))
        return loop.run_until_complete(task)  # type: ignore[attr-defined]
    except RuntimeError:
        return asyncio.run(run_agents(goal=goal, project=project, mode=mode, model=model))
    except Exception:
        # Final fallback
        return asyncio.run(run_agents(goal=goal, project=project, mode=mode, model=model))


# ----------------------------
# Session defaults
# ----------------------------
if "project" not in st.session_state:
    st.session_state["project"] = "default"
if "last_run_context" not in st.session_state:
    st.session_state["last_run_context"] = None  # dict
if "last_run_dirs" not in st.session_state:
    st.session_state["last_run_dirs"] = None  # dict
if "_copy_last" not in st.session_state:
    st.session_state["_copy_last"] = ""

# ----------------------------
# Layout: Left / Center / Right
# ----------------------------
left, center, right = st.columns([1.1, 2.2, 1.2], gap="large")

with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Settings")

    # Project (Phase 2)
    st.session_state["project"] = st.text_input(
        "📁 Project",
        value=st.session_state["project"],
        help="Project slug (folder name). Saves to projects/{project}/runs/{run_id}/",
    )

    model_choice = st.selectbox("🧠 Choose Model", ["phi3:latest", "gemma3:latest", "tinyllama:latest"])
    CONFIG["llm_config"]["model"] = model_choice

    mode = st.radio("🚀 Execution Mode", ["Team Mode", "Fast Mode (Coder Only)"], horizontal=False)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Run status badge
    ctx = st.session_state.get("last_run_context") or {}
    if ctx:
        st.markdown(
            f"<div class='small'>Last run: <span class='badge mono'>{html.escape(ctx.get('run_id',''))}</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='small'>Project: <span class='badge mono'>{html.escape(ctx.get('project',''))}</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='small'>Status: <span class='badge mono'>{html.escape(ctx.get('status',''))}</span></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='small'>No runs yet.</div>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["last_run_context"] = None
            st.session_state["last_run_dirs"] = None
            st.session_state["_copy_last"] = ""
            st.rerun()
    with colB:
        who, out = get_last_output()
        if st.button("📋 Copy Last", use_container_width=True):
            st.session_state["_copy_last"] = out

    if st.session_state.get("_copy_last"):
        st.text_area("Copied text", value=st.session_state["_copy_last"], height=120)

    st.markdown("<div class='small'>Built by DP-Tech1324</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with center:
    st.markdown(
        """
    <div class='chat-header'>
      <h2 style='margin:0; font-weight:900;'>🤖 AI Director Team — MGX Clone</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Chat input
    user_input = st.chat_input("📤 Enter a task or goal...")

    if user_input and user_input.strip():
        goal = user_input.strip()

        # If project left blank, infer from goal
        if not st.session_state["project"].strip():
            st.session_state["project"] = infer_project_from_goal(goal)

        now = datetime.now().strftime("%H:%M:%S")
        log_message("User", {"text": goal, "timestamp": now})

        with st.spinner("🧠 Thinking..."):
            start = time.time()

            try:
                # Phase 2: ALWAYS run orchestrator (even fast mode) so everything gets saved
                ctx, dirs, logs = run_agents_sync(
                    goal=goal,
                    project=st.session_state["project"],
                    mode=mode,  # orchestrator decides "fast" vs "team"
                    model=CONFIG["llm_config"]["model"],
                )

                st.session_state["last_run_context"] = ctx
                try:
                    st.session_state["last_run_dirs"] = {k: str(v) for k, v in dirs.items()}
                except Exception:
                    st.session_state["last_run_dirs"] = None

                # Stable ordering in UI
                order = ["Director", "Planner", "Researcher", "Coder", "Designer", "Scribe", "QA", "System"]
                for name in order:
                    if name in logs:
                        now = datetime.now().strftime("%H:%M:%S")
                        content = logs[name].get("content", "")
                        log_message(name, {"text": str(content), "timestamp": now})

            except Exception as e:
                now = datetime.now().strftime("%H:%M:%S")
                log_message("System", {"text": f"❌ Error during agent execution: {e}", "timestamp": now})

            duration = time.time() - start
            st.success(f"✅ Done in {duration:.2f}s")

    # Conversation
    st.markdown("### 📜 Conversation")
    st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
    for name, msg_obj in st.session_state.get("messages", []):
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

    # Phase 2: show where run was saved + list files
    ctx = st.session_state.get("last_run_context") or {}
    dirs = st.session_state.get("last_run_dirs") or {}
    if ctx and dirs:
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown("### 📦 Saved Run")
        st.markdown(f"- **Run ID:** `{ctx.get('run_id','')}`")
        st.markdown(f"- **Project:** `{ctx.get('project','')}`")
        st.markdown(f"- **Runs folder:** `{dirs.get('runs','')}`")

        run_folder = dirs.get("runs", "")
        try:
            files = sorted(glob.glob(os.path.join(run_folder, "*")))
            if files:
                st.markdown("**Files:**")
                for fp in files[:18]:
                    st.caption(os.path.basename(fp))
            else:
                st.caption("No files found in run folder yet.")
        except Exception:
            st.caption("Could not list run files.")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("### 📝 Recent Scribe Logs")

    project_slug = (ctx.get("project") or st.session_state.get("project") or "").strip()
    run_id = (ctx.get("run_id") or "").strip()
    files = list_scribe_files(limit=8, project_slug=project_slug, run_id=run_id)

    if not files:
        st.caption("No scribe logs yet.")
    else:
        for fp in files:
            label = os.path.basename(fp)
            content = safe_read_text(fp)
            st.download_button(
                label=f"⬇️ {label}",
                data=content,
                file_name=label,
                mime="text/markdown",
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
