#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import shutil
from typing import Any

from common import print_json
from detect_screen import detect_screen


def provider_status() -> dict[str, Any]:
    native = os.environ.get("TRAVEL4ME_NATIVE_IMAGE_TOOL") in {"1", "true", "yes"}
    providers = []
    if os.environ.get("OPENAI_API_KEY"):
        providers.append({"name": "openai", "model": os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2"), "priority": 1})
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        providers.append({"name": "gemini", "model": os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview"), "priority": 2})
    if os.environ.get("SEEDREAM_API_KEY") or os.environ.get("TRAVEL4ME_IMAGE_COMMAND"):
        providers.append({"name": "seedream", "model": os.environ.get("SEEDREAM_MODEL", "latest"), "priority": 3})
    providers.sort(key=lambda x: x["priority"])
    return {"native_image_tool_hint": native, "available_api_providers": providers, "selected_api_provider": providers[0] if providers else None}


def desktop_session() -> dict[str, Any]:
    system = platform.system()
    hints = {}
    if system == "Darwin":
        hints["aqua_session"] = bool(os.environ.get("TERM_PROGRAM") or os.environ.get("__CF_USER_TEXT_ENCODING"))
    elif system == "Windows":
        hints["sessionname"] = os.environ.get("SESSIONNAME")
    else:
        hints["display"] = os.environ.get("DISPLAY")
        hints["wayland_display"] = os.environ.get("WAYLAND_DISPLAY")
        hints["xdg_current_desktop"] = os.environ.get("XDG_CURRENT_DESKTOP")
    return {"platform": system, "hints": hints, "likely_interactive": any(bool(v) for v in hints.values())}


def wallpaper_status() -> dict[str, Any]:
    system = platform.system()
    if system == "Darwin":
        return {"platform": "macos", "adapter": "osascript", "available": shutil.which("osascript") is not None}
    if system == "Windows":
        return {"platform": "windows", "adapter": "ctypes:SystemParametersInfoW", "available": True}
    if system == "Linux":
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
        return {"platform": "linux", "adapter": "gsettings" if "GNOME" in desktop.upper() else "unknown", "available": shutil.which("gsettings") is not None}
    return {"platform": system, "adapter": None, "available": False}


def automation_status() -> dict[str, Any]:
    system = platform.system()
    candidates = []
    if os.environ.get("TRAVEL4ME_AGENT_AUTOMATION") in {"1", "true", "yes"}:
        candidates.append("agent_platform_automation")
    if system == "Darwin" and shutil.which("launchctl"):
        candidates.append("launchd")
    if system == "Windows" and shutil.which("schtasks"):
        candidates.append("windows_task_scheduler")
    if system == "Linux":
        if shutil.which("systemctl"):
            candidates.append("systemd_timer")
        if shutil.which("crontab"):
            candidates.append("cron")
    return {"available": bool(candidates), "candidates": candidates}


def detect_environment() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "shell": bool(shutil.which("sh") or shutil.which("bash") or shutil.which("zsh") or shutil.which("powershell")),
        "provider": provider_status(),
        "desktop_session": desktop_session(),
        "screen": detect_screen(),
        "wallpaper": wallpaper_status(),
        "automation": automation_status(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = detect_environment()
    if args.json:
        print_json(result)
    else:
        print_json(result)


if __name__ == "__main__":
    main()
