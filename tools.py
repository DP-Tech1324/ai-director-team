import os
import subprocess
import tempfile

def run_python_code(code: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name
        result = subprocess.run(["python", temp_path], capture_output=True, text=True, timeout=10)
        os.remove(temp_path)
        return result.stdout or result.stderr
    except Exception as e:
        return f"❌ Error running code: {e}"

def save_file(filename: str, content: str) -> str:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ File saved: {filename}"
    except Exception as e:
        return f"❌ Error saving file: {e}"