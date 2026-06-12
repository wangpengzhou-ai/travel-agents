#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import load_trip, save_trip
from generate_wallpaper import generate_for_day
from set_wallpaper import set_wallpaper


def apply_daily_context(trip: dict, day: int, weather: str | None, label_date: str | None, label_location: str | None) -> bool:
    waypoint = trip["waypoints"][day - 1]
    changed = False
    if weather:
        waypoint["weather"] = {"summary": weather, "source": "daily_run --weather"}
        changed = True
    if label_date:
        waypoint["label_date"] = label_date
        changed = True
    if label_location:
        waypoint["label_location"] = label_location
        changed = True
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--day", type=int)
    parser.add_argument("--size", default="2560x1440")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--set-wallpaper", action="store_true")
    parser.add_argument("--weather", help="Daily weather summary to weave into the image prompt.")
    parser.add_argument("--label-date", help="Exact date text or ISO date for the model-drawn upper-left label.")
    parser.add_argument("--label-location", help="Exact location text for the model-drawn upper-left label.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    trip_dir = Path(args.trip_dir).expanduser()
    trip = load_trip(trip_dir)
    day = args.day or trip.get("current_day", 1)
    exit_code = 0
    if day > trip["days"]:
        result = {"status": "complete", "message": "trip already completed", "day": day, "days": trip["days"]}
    else:
        if apply_daily_context(trip, day, args.weather, args.label_date, args.label_location):
            save_trip(trip_dir, trip)
            trip = load_trip(trip_dir)
        result = generate_for_day(trip_dir, day, args.size, args.dry_run)
        blocked = str(result.get("status", "")).startswith("blocked_")
        if blocked:
            exit_code = 2
        else:
            wallpaper_path = result.get("wallpaper_path")
            if args.set_wallpaper and wallpaper_path and not args.dry_run:
                try:
                    set_wallpaper(Path(wallpaper_path))
                    result["wallpaper_set"] = True
                except Exception as exc:
                    result["wallpaper_set"] = False
                    result["wallpaper_error"] = str(exc)

            if not args.dry_run and "error" not in result:
                trip["current_day"] = min(day + 1, trip["days"] + 1)
                save_trip(trip_dir, trip)

    if args.json:
        import json, sys
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(result)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
