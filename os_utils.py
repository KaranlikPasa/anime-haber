import os
import sys
import subprocess
import webbrowser

def open_path_or_url(target: str):
    """Cross-platform opener for files, directories, URLs, and magnet links."""
    if not target:
        return
    if sys.platform == "win32":
        try:
            os.startfile(target)
            return
        except Exception:
            pass
    elif sys.platform == "darwin":
        try:
            subprocess.Popen(["open", target])
            return
        except Exception:
            pass
    else:
        try:
            subprocess.Popen(["xdg-open", target])
            return
        except Exception:
            pass
            
    # Webbrowser fallback for urls/magnets
    if target.startswith(("http://", "https://", "magnet:")):
        webbrowser.open(target)
