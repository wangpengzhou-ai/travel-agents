#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from common import DEFAULT_STATE_DIR, slugify, utc_now, write_json
from export_route_geojson import to_geojson
from plan_route import plan_route


def build_character_state(description: str, anchors: list[str] | None = None) -> dict:
    visual_anchors = anchors or [description]
    return {
        "description": description,
        "visual_anchors": visual_anchors,
        "consistency_rules": [
            "same silhouette and body proportions every day",
            "same signature colors and accessories every day",
            "same material feel and facial/body design every day",
            "do not redesign, age-shift, costume-swap, or change species/type",
        ],
        "scale_rule": "small off-center traveler, naturally participating in the local environment, never the main subject",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--character", required=True)
    parser.add_argument("--character-anchor", action="append", default=[])
    parser.add_argument("--style", default="watercolor_postcard", choices=["watercolor_postcard"])
    parser.add_argument("--origin-lat", type=float)
    parser.add_argument("--origin-lon", type=float)
    parser.add_argument("--destination-lat", type=float)
    parser.add_argument("--destination-lon", type=float)
    parser.add_argument("--target-days", type=int)
    parser.add_argument("--start-date", default=date.today().isoformat())
    parser.add_argument("--state-dir", default=str(DEFAULT_STATE_DIR))
    parser.add_argument("--trip-id")
    args = parser.parse_args()

    origin_coords = None
    destination_coords = None
    if args.origin_lat is not None and args.origin_lon is not None:
        origin_coords = {"lat": args.origin_lat, "lon": args.origin_lon}
    if args.destination_lat is not None and args.destination_lon is not None:
        destination_coords = {"lat": args.destination_lat, "lon": args.destination_lon}

    route = plan_route(args.origin, args.destination, origin_coords, destination_coords, args.target_days)
    trip_id = args.trip_id or f"{slugify(args.origin)}-to-{slugify(args.destination)}-{route['days']}d"
    trip_dir = Path(args.state_dir).expanduser() / "trips" / trip_id
    trip_dir.mkdir(parents=True, exist_ok=True)
    character = build_character_state(args.character, args.character_anchor)

    trip = {
        "trip_id": trip_id,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "start_date": args.start_date,
        "origin": args.origin,
        "destination": args.destination,
        "days": route["days"],
        "direct_distance_km": route.get("direct_distance_km"),
        "route_distance_km": route.get("route_distance_km"),
        "day_count_source": route.get("day_count_source"),
        "requested_target_days": route.get("requested_target_days"),
        "style": args.style,
        "character": character,
        "label": {
            "enabled": True,
            "source": "model_drawn",
            "position": "upper_left",
            "format": "{Title Case label_location}    {Month D, YYYY}",
        },
        "current_day": 1,
        "waypoints": route["waypoints"],
    }

    write_json(trip_dir / "trip.json", trip)
    write_json(trip_dir / "character.json", character)
    write_json(trip_dir / "route.json", route)
    write_json(trip_dir / "route.geojson", to_geojson(route))
    print(trip_dir)


if __name__ == "__main__":
    main()
