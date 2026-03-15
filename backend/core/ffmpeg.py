import os
import shutil


def find_ffmpeg() -> str:
    """Locate the ffmpeg executable, checking PATH then common install locations."""
    # 1. Check PATH first
    ff = shutil.which("ffmpeg")
    if ff:
        return ff

    # 2. WinGet install location
    winget_base = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    if os.path.isdir(winget_base):
        for pkg in os.listdir(winget_base):
            if "Gyan.FFmpeg" in pkg or "ffmpeg" in pkg.lower():
                for root, _dirs, files in os.walk(os.path.join(winget_base, pkg)):
                    if "ffmpeg.exe" in files:
                        return os.path.join(root, "ffmpeg.exe")

    # 3. Legacy manual install paths (kept for backwards compat)
    legacy_paths = [
        r"C:\ffmpeg-2026-03-12-git-9dc44b43b2-full_build\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    for path in legacy_paths:
        if os.path.isfile(path):
            return path

    raise FileNotFoundError(
        "ffmpeg not found. Install via: winget install --id Gyan.FFmpeg"
    )
