#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import load_trip, read_json, save_trip, utc_now, write_json, write_text
from prompt_postcard import build_prompt_context, build_postcard_prompt


def _copy_image(source: Path, target: Path, overwrite: bool) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        raise FileExistsError(f"{target} already exists; pass --overwrite to replace it")
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)


def import_image(
    trip_dir: Path,
    source_image: Path,
    day: int | None,
    size: str,
    provider: str,
    overwrite: bool,
    advance: bool,
) -> dict:
    trip = load_trip(trip_dir)
    current_day = day or trip.get("current_day", 1)
    if current_day > trip["days"]:
        raise ValueError(f"day {current_day} is beyond trip length {trip['days']}")

    waypoint = trip["waypoints"][current_day - 1]
    day_dir = trip_dir / f"day_{current_day:03d}"
    day_dir.mkdir(parents=True, exist_ok=True)

    prompt_path = day_dir / "prompt.txt"
    if not prompt_path.exists():
        write_text(prompt_path, build_postcard_prompt(trip, waypoint) + "\n")

    original = day_dir / "original.png"
    _copy_image(source_image.expanduser(), original, overwrite)

    prompt_context = build_prompt_context(trip, waypoint)
    metadata_path = day_dir / "metadata.json"
    metadata = read_json(metadata_path) if metadata_path.exists() else {}
    metadata.update(
        {
            "day": current_day,
            "location": waypoint["location"],
            "label_text": prompt_context["label_text"],
            "label_date": prompt_context["label_date"],
            "weather": waypoint.get("weather") or metadata.get("weather"),
            "provider": provider,
            "source_image": str(source_image),
            "imported_at": utc_now(),
            "prompt_path": str(prompt_path),
            "original_path": str(original),
            "size": size,
            "dry_run": False,
            "status": "imported_generated_image",
        }
    )
    write_json(metadata_path, metadata)

    if advance:
        latest_trip = load_trip(trip_dir)
        latest_trip["current_day"] = min(current_day + 1, latest_trip["days"] + 1)
        save_trip(trip_dir, latest_trip)

    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a host-agent generated image into trip state.")
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--day", type=int)
    parser.add_argument("--size", default="2560x1440")
    parser.add_argument("--provider", default="host_native")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-advance", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = import_image(
        Path(args.trip_dir).expanduser(),
        Path(args.image).expanduser(),
        args.day,
        args.size,
        args.provider,
        args.overwrite,
        not args.no_advance,
    )
    if args.json:
        import json
        import sys

        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(result["original_path"])


if __name__ == "__main__":
    main()
