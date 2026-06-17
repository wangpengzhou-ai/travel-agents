#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import shutil
from typing import Any

from common import print_json


def _truthy_env(*names: str) -> bool:
    return any(os.environ.get(name) in {"1", "true", "yes"} for name in names)


def _env_value(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def provider_status() -> dict[str, Any]:
    native = _truthy_env("TRAVEL_AGENTS_NATIVE_IMAGE_TOOL", "TRAVEL4ME_NATIVE_IMAGE_TOOL")
    providers = []
    if os.environ.get("OPENAI_API_KEY"):
        providers.append({"name": "openai", "model": os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2"), "priority": 1})
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        providers.append({"name": "gemini", "model": os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview"), "priority": 2})
    if os.environ.get("SEEDREAM_API_KEY") or _env_value("TRAVEL_AGENTS_IMAGE_COMMAND", "TRAVEL4ME_IMAGE_COMMAND"):
        providers.append({"name": "seedream", "model": os.environ.get("SEEDREAM_MODEL", "latest"), "priority": 3})
    providers.sort(key=lambda x: x["priority"])
    return {
        "native_image_tool_hint": native,
        "host_native_strategy": {
            "python_can_verify": False,
            "probe": "attempt_first_required_image_with_host_tool",
            "fallback": "local_api_provider_or_block_setup",
        },
        "available_api_providers": providers,
        "selected_api_provider": providers[0] if providers else None,
    }


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


def automation_status(provider: dict[str, Any]) -> dict[str, Any]:
    system = platform.system()
    candidates = []
    local_scheduler_candidates = []
    host_agent_automation_hint = _truthy_env("TRAVEL_AGENTS_AGENT_AUTOMATION", "TRAVEL4ME_AGENT_AUTOMATION")
    if host_agent_automation_hint:
        candidates.append("agent_platform_automation")
    has_local_image_provider = bool(provider["available_api_providers"])
    if system == "Darwin" and shutil.which("launchctl"):
        local_scheduler_candidates.append("launchd")
    if system == "Windows" and shutil.which("schtasks"):
        local_scheduler_candidates.append("windows_task_scheduler")
    if system == "Linux":
        if shutil.which("systemctl"):
            local_scheduler_candidates.append("systemd_timer")
        if shutil.which("crontab"):
            local_scheduler_candidates.append("cron")
    if has_local_image_provider:
        candidates.extend(local_scheduler_candidates)
    if "agent_platform_automation" in candidates:
        default_action = "create_host_agent_daily_automation_after_trip_initialization"
    elif candidates:
        default_action = "install_local_daily_scheduler_after_trip_initialization"
    else:
        default_action = "check_host_agent_automation_tool_or_manual_daily_run_until_configured"
    return {
        "available": bool(candidates),
        "candidates": candidates,
        "host_agent_automation": {
            "python_can_verify": False,
            "hint": host_agent_automation_hint,
            "agent_action": "inspect_current_host_tools_and_call_real_automation_tool_when_available",
        },
        "local_scheduler_candidates": local_scheduler_candidates,
        "local_scheduler_requires": "local_image_provider_or_TRAVEL_AGENTS_IMAGE_COMMAND",
        "local_scheduler_available": bool(local_scheduler_candidates and has_local_image_provider),
        "host_agent_required_for_images": not has_local_image_provider,
        "default_action": default_action,
        "ask_user_first": False,
    }


def detect_environment() -> dict[str, Any]:
    provider = provider_status()
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "shell": bool(shutil.which("sh") or shutil.which("bash") or shutil.which("zsh") or shutil.which("powershell")),
        "provider": provider,
        "desktop_session": desktop_session(),
        "automation": automation_status(provider),
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
