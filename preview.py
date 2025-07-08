import subprocess
import os

def launch_preview(app_path="preview_app.py", port=8600):
    try:
        subprocess.Popen(
            ["streamlit", "run", app_path, "--server.port", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return f"http://localhost:{port}"
    except Exception as e:
        return f"❌ Failed to launch preview: {e}"