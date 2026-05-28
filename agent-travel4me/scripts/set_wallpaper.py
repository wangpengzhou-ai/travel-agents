#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import os
import platform
import subprocess
from pathlib import Path


def set_macos(path: Path) -> None:
    script = f'''
    tell application "System Events"
      set picture of every desktop to POSIX file "{path}"
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "osascript failed")


def set_windows(path: Path) -> None:
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    ok = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, str(path), SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
    if not ok:
        raise RuntimeError("SystemParametersInfoW failed")


def set_gnome(path: Path) -> None:
    uri = path.resolve().as_uri()
    commands = [
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri],
        ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", uri],
    ]
    for cmd in commands:
        result = subprocess.run(cmd, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"{cmd[0]} failed")


def set_wallpaper(path: Path) -> None:
    system = platform.system()
    if system == "Darwin":
        set_macos(path)
    elif system == "Windows":
        set_windows(path)
    elif system == "Linux":
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
        if "GNOME" in desktop.upper() or os.environ.get("GNOME_DESKTOP_SESSION_ID"):
            set_gnome(path)
        else:
            raise RuntimeError("Linux desktop adapter unavailable; only GNOME gsettings is implemented")
    else:
        raise RuntimeError(f"unsupported platform {system}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    args = parser.parse_args()
    set_wallpaper(Path(args.image).expanduser().resolve())
    print(args.image)


if __name__ == "__main__":
    main()
