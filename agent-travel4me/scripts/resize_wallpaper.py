#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def resize_with_pillow(src: Path, out: Path, width: int, height: int) -> bool:
    try:
        from PIL import Image
    except Exception:
        return False
    img = Image.open(src).convert("RGB")
    target_ratio = width / height
    src_ratio = img.width / img.height
    if src_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    elif src_ratio < target_ratio:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    return True


def resize_with_sips(src: Path, out: Path, width: int, height: int) -> bool:
    if not shutil.which("sips"):
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["sips", "-z", str(height), str(width), str(src), "--out", str(out)], capture_output=True, text=True, check=False)
    return result.returncode == 0 and out.exists()


def resize_wallpaper(src: Path, out: Path, width: int, height: int) -> None:
    if resize_with_pillow(src, out, width, height):
        return
    if resize_with_sips(src, out, width, height):
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out)
    raise RuntimeError("No image resize backend available; copied source without resizing. Install Pillow or run on macOS with sips.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--size", default="2560x1440")
    args = parser.parse_args()
    width, height = [int(x) for x in args.size.lower().split("x", 1)]
    resize_wallpaper(Path(args.input), Path(args.out), width, height)
    print(args.out)


if __name__ == "__main__":
    main()
