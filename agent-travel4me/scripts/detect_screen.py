#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
from typing import Any

from common import print_json


def run_capture(cmd: list[str], timeout: int = 5) -> str:
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False)
        return (result.stdout or "") + (result.stderr or "")
    except Exception:
        return ""


def detect_macos() -> dict[str, Any]:
    output = run_capture(["system_profiler", "SPDisplaysDataType"])
    matches = re.findall(r"Resolution:\s+(\d+)\s+x\s+(\d+)", output)
    if matches:
        width, height = matches[0]
        return {"ok": True, "method": "system_profiler", "width": int(width), "height": int(height), "scale": None}
    return {"ok": False, "method": "system_profiler", "reason": "no display resolution found"}


def detect_windows() -> dict[str, Any]:
    ps = "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Size"
    output = run_capture(["powershell", "-NoProfile", "-Command", ps])
    nums = re.findall(r"(?:Width|Height)\s*:\s*(\d+)", output)
    if len(nums) >= 2:
        return {"ok": True, "method": "System.Windows.Forms", "width": int(nums[0]), "height": int(nums[1]), "scale": None}
    return {"ok": False, "method": "System.Windows.Forms", "reason": "no screen size found"}


def detect_linux() -> dict[str, Any]:
    output = run_capture(["xrandr", "--current"])
    match = re.search(r"current\s+(\d+)\s+x\s+(\d+)", output)
    if match:
        return {"ok": True, "method": "xrandr", "width": int(match.group(1)), "height": int(match.group(2)), "scale": None}
    if os.environ.get("WAYLAND_DISPLAY"):
        return {"ok": False, "method": "wayland", "reason": "Wayland session detected; compositor-specific screen query needed"}
    return {"ok": False, "method": "xrandr", "reason": "no screen size found"}


def detect_screen() -> dict[str, Any]:
    system = platform.system()
    if system == "Darwin":
        return detect_macos()
    if system == "Windows":
        return detect_windows()
    if system == "Linux":
        return detect_linux()
    return {"ok": False, "method": "unknown", "reason": f"unsupported platform {system}"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = detect_screen()
    if args.json:
        print_json(result)
    else:
        print(result)


if __name__ == "__main__":
    main()
