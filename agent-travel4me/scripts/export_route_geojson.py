#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import print_json, read_json, write_json


def to_geojson(route: dict[str, Any]) -> dict[str, Any]:
    features = []
    line = []
    for wp in route["waypoints"]:
        lon = wp["coordinates"]["lon"]
        lat = wp["coordinates"]["lat"]
        if lon is None or lat is None:
            continue
        line.append([lon, lat])
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "day": wp["day"],
                    "location": wp["location"],
                    "country_or_region": wp.get("country_or_region"),
                    "landscape_type": wp.get("landscape_type"),
                    "landmarks": wp.get("landmarks", []),
                    "is_natural_or_semi_natural": wp.get("is_natural_or_semi_natural", False),
                },
            }
        )
    if len(line) >= 2:
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": line},
                "properties": {
                    "origin": route["origin"],
                    "destination": route["destination"],
                    "days": route["days"],
                    "route_distance_km": route.get("route_distance_km"),
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    geojson = to_geojson(read_json(Path(args.route)))
    if args.out:
        write_json(Path(args.out), geojson)
    else:
        print_json(geojson)


if __name__ == "__main__":
    main()
