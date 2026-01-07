# agents/scribe.py
from __future__ import annotations

import os
import re
from datetime import datetime

from agents.base import BaseAgent


def _wrap_md(md: str) -> str:
    return (md or "").strip() + "\n"


def _extract_section(text: str, header: str) -> str:
    """
    Extracts content under a markdown header like '## Planner' until next '## ' or end.
    """
    if not text:
        return ""
    pattern = rf"##\s+{re.escape(header)}\s*\n([\s\S]*?)(?=\n##\s+|\Z)"
    m = re.search(pattern, text, flags=re.IGNORECASE)
    return (m.group(1).strip() if m else "")


def _extract_goal(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"GOAL:\s*\n([\s\S]*?)(?=\n\n|\Z)", text, flags=re.IGNORECASE)
    return (m.group(1).strip() if m else "")


class ScribeAgent(BaseAgent):
    
    """
    Scribe = finalizer (NO extra LLM call here).
    It receives a combined input like:

    GOAL:
    ...
    OUTPUTS:
    ## Planner
    ...
    ## Researcher
    ...
    """


    def generate_reply(self, messages):
        raw = messages[-1]["content"] if messages else ""
        os.makedirs("memory", exist_ok=True)

        goal = _extract_goal(raw) or raw.strip()[:200]

        planner = _extract_section(raw, "Planner")
        researcher = _extract_section(raw, "Researcher")
        coder = _extract_section(raw, "Coder")
        designer = _extract_section(raw, "Designer")
        qa = _extract_section(raw, "QA")

        md = f"""# ✅ Final Summary

## Goal
{goal}

## What the team produced

### 🗺️ Plan (Planner)
{planner if planner else "- (No planner output found)"}

### 🔬 Tips (Researcher)
{researcher if researcher else "- (No researcher output found)"}

### 💻 Implementation / Template (Coder)
{coder if coder else "- (No coder output found)"}

### 🎨 UI / UX (Designer)
{designer if designer else "- (No designer output found)"}

"""

        # If QA content exists, add it (optional)
        if qa:
            md += f"""### ✅ QA Review
{qa}

"""

        # Always end with useful next steps (not generic run commands)
        md += """## Next steps
- If code was generated: save it as a file and run it.
- If the answer is informational: convert it into a checklist and apply it to your project.
- If something is missing: ask for the missing inputs (requirements, fields, constraints) and re-run.

"""

        md = _wrap_md(md)

        # Save log
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fp = os.path.join("memory", f"scribe_log_{ts}.md")
        try:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(md)
        except Exception:
            pass

        return md + f"\n---\n📝 ✅ File saved: {fp}"


# keep this line (and silence Pylance if it complains)
scribe = ScribeAgent(
    name="Scribe",
    system_message="You are Scribe. You create a final combined summary that is actually useful."
)
