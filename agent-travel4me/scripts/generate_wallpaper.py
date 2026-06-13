#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import load_trip, read_json, style_sample_path, utc_now, write_json, write_text
from image_providers import ImageProviderError, generate_image
from prompt_wallpaper import build_prompt_context, build_wallpaper_prompt
from resize_wallpaper import resize_wallpaper
from validate_route import validate_daily_context, validate_route


def generate_for_day(trip_dir: Path, day: int, size: str = "2560x1440", dry_run: bool = False) -> dict:
    trip = load_trip(trip_dir)
    waypoint = trip["waypoints"][day - 1]
    day_dir = trip_dir / f"day_{day:03d}"
    day_dir.mkdir(parents=True, exist_ok=True)
    prompt_context = build_prompt_context(trip, waypoint)
    style_sample = style_sample_path()

    metadata = {
        "day": day,
        "location": waypoint["location"],
        "label_text": prompt_context["label_text"],
        "label_date": prompt_context["label_date"],
        "weather": waypoint.get("weather"),
        "style_sample_path": str(style_sample),
        "created_at": utc_now(),
        "prompt_path": str(day_dir / "prompt.txt"),
        "size": size,
        "dry_run": dry_run,
    }
    daily_issues = validate_daily_context(trip, day)
    if daily_issues:
        metadata["status"] = "blocked_daily_context_invalid"
        metadata["issues"] = daily_issues
        write_json(day_dir / "metadata.json", metadata)
        return metadata

    if not dry_run:
        validation_issues = validate_route(trip)
        if validation_issues:
            metadata["status"] = "blocked_route_or_daily_context_invalid"
            metadata["issues"] = validation_issues
            write_json(day_dir / "metadata.json", metadata)
            return metadata

    prompt = build_wallpaper_prompt(trip, waypoint)
    write_text(day_dir / "prompt.txt", prompt + "\n")
    if dry_run:
        write_json(day_dir / "metadata.json", metadata)
        return metadata

    original = day_dir / "original.png"
    wallpaper = day_dir / "wallpaper.png"
    character_reference = trip_dir / "character_reference.png"
    reference_images = [style_sample]
    if character_reference.exists():
        reference_images.append(character_reference)
    metadata["reference_image_paths"] = [str(path) for path in reference_images]
    try:
        provider_meta = generate_image(prompt, original, size=size, reference_images=reference_images)
        resize_wallpaper(original, wallpaper, *[int(x) for x in size.split("x", 1)])
        metadata.update(provider_meta)
        metadata["original_path"] = str(original)
        metadata["wallpaper_path"] = str(wallpaper)
    except ImageProviderError as exc:
        metadata["error"] = str(exc)
        metadata["status"] = "prompt_only_provider_missing_or_failed"
    write_json(day_dir / "metadata.json", metadata)
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--day", type=int)
    parser.add_argument("--size", default="2560x1440")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    trip = load_trip(Path(args.trip_dir))
    day = args.day or trip.get("current_day", 1)
    result = generate_for_day(Path(args.trip_dir), day, args.size, args.dry_run)
    if args.json:
        import json, sys
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(result.get("wallpaper_path") or result.get("prompt_path"))


if __name__ == "__main__":
    main()
