#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
from pathlib import Path


def launchd_plist(name: str, trip_dir: Path, hour: int, minute: int, skill_dir: Path) -> str:
    daily_run = skill_dir / "scripts" / "daily_run.py"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{name}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{os.environ.get("PYTHON", "python3")}</string>
    <string>{daily_run}</string>
    <string>--trip-dir</string>
    <string>{trip_dir}</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>{hour}</integer>
    <key>Minute</key><integer>{minute}</integer>
  </dict>
  <key>StandardOutPath</key><string>{trip_dir}/daily_run.out.log</string>
  <key>StandardErrorPath</key><string>{trip_dir}/daily_run.err.log</string>
</dict>
</plist>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a scheduler setup artifact. Does not install automatically.")
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--hour", type=int, default=9)
    parser.add_argument("--minute", type=int, default=0)
    parser.add_argument("--out")
    args = parser.parse_args()

    system = platform.system()
    skill_dir = Path(__file__).resolve().parent.parent
    trip_dir = Path(args.trip_dir).expanduser().resolve()
    if system == "Darwin":
        label = "com.agent-travel4me.daily"
        content = launchd_plist(label, trip_dir, args.hour, args.minute, skill_dir)
        if args.out:
            Path(args.out).write_text(content, encoding="utf-8")
            print(args.out)
        else:
            print(content)
    elif system == "Linux":
        daily_run = skill_dir / "scripts" / "daily_run.py"
        print(f"{args.minute} {args.hour} * * * {os.environ.get('PYTHON', 'python3')} {daily_run} --trip-dir {trip_dir}")
    elif system == "Windows":
        daily_run = skill_dir / "scripts" / "daily_run.py"
        print(f'schtasks /Create /SC DAILY /TN agent-travel4me /TR "python {daily_run} --trip-dir {trip_dir}" /ST {args.hour:02d}:{args.minute:02d}')
    else:
        raise SystemExit(f"unsupported platform {system}")


if __name__ == "__main__":
    main()
