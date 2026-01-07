# core/sandbox.py
from __future__ import annotations

import ast
import io
import traceback
from multiprocessing import Process, Queue
from contextlib import redirect_stdout, redirect_stderr
from typing import Tuple, Optional, List


BLOCKED_IMPORTS = {
    "subprocess", "socket", "requests", "urllib", "httpx", "ftplib",
    "paramiko", "shutil", "pathlib", "os", "sys"
}
# NOTE: We block os/sys by default in Phase 2. If you want to allow os for simple file ops,
# we can allow only os.path + open in run folder later, but keep it strict for now.

BLOCKED_CALLS = {
    ("os", "system"),
    ("os", "popen"),
    ("subprocess", "run"),
    ("subprocess", "Popen"),
    ("subprocess", "call"),
    ("subprocess", "check_output"),
}


class UnsafeCodeError(Exception):
    pass


def _scan(code: str) -> None:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise UnsafeCodeError(f"SyntaxError: {e}")

    for node in ast.walk(tree):
        # block imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = []
            if isinstance(node, ast.Import):
                mods = [n.name.split(".")[0] for n in node.names]
            else:
                if node.module:
                    mods = [node.module.split(".")[0]]
            for m in mods:
                if m in BLOCKED_IMPORTS:
                    raise UnsafeCodeError(f"Blocked import: {m}")

        # block suspicious calls like os.system, subprocess.run
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # e.g. os.system(...)
            if isinstance(node.func.value, ast.Name):
                base = node.func.value.id
                attr = node.func.attr
                if (base, attr) in BLOCKED_CALLS:
                    raise UnsafeCodeError(f"Blocked call: {base}.{attr}()")


def _child_exec(code: str, q: Queue) -> None:
    out = io.StringIO()
    err = io.StringIO()

    try:
        _scan(code)

        safe_globals = {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "dict": dict,
                "list": list,
                "set": set,
                "tuple": tuple,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "enumerate": enumerate,
                "zip": zip,
            }
        }

        with redirect_stdout(out), redirect_stderr(err):
            exec(code, safe_globals, {})
        q.put(("ok", out.getvalue(), err.getvalue()))
    except Exception as e:
        q.put(("err", out.getvalue(), err.getvalue() + "\n" + traceback.format_exc()))


def run_python_sandbox(code: str, timeout_sec: int = 5) -> Tuple[str, str, str]:
    """
    Returns: (status, stdout, stderr)
      status: "ok" | "err" | "timeout" | "unsafe"
    """
    q: Queue = Queue()
    p = Process(target=_child_exec, args=(code, q))
    p.start()
    p.join(timeout=timeout_sec)

    if p.is_alive():
        p.terminate()
        p.join()
        return ("timeout", "", f"Execution timed out after {timeout_sec}s")

    if not q.empty():
        status, stdout, stderr = q.get()
        return (status, stdout, stderr)

    return ("err", "", "Unknown execution error (no output returned)")
