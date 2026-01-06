import os
import subprocess
import tempfile

def run_python_code(code: str) -> str:
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        result = subprocess.run(
            ["python", temp_path],
            capture_output=True,
            text=True,
            timeout=15
        )
        try:
            os.remove(temp_path)
        except OSError:
            pass

        return result.stdout.strip() or result.stderr.strip() or "✅ Ran successfully (no output)."
    except Exception as e:
        return f"❌ Error running code: {e}"

def save_file(filename: str, content: str) -> str:
    try:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ File saved: {filename}"
    except Exception as e:
        return f"❌ Error saving file: {e}"
