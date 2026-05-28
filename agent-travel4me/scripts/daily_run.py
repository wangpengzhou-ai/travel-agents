#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import load_trip, save_trip, write_json
from generate_wallpaper import generate_for_day
from set_wallpaper import set_wallpaper


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--day", type=int)
    parser.add_argument("--size", default="2560x1440")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--set-wallpaper", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    trip_dir = Path(args.trip_dir).expanduser()
    trip = load_trip(trip_dir)
    day = args.day or trip.get("current_day", 1)
    if day > trip["days"]:
        result = {"status": "complete", "message": "trip already completed", "day": day, "days": trip["days"]}
    else:
        result = generate_for_day(trip_dir, day, args.size, args.dry_run)
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


if __name__ == "__main__":
    main()
