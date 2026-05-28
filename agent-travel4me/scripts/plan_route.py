#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from common import estimate_days, haversine_km, print_json, write_json


LANDSCAPE_SEQUENCE = [
    {
        "landscape_type": "departure city",
        "role": "departure from the user's current place",
        "local_visual_elements": ["recognizable local skyline", "morning light", "departure object", "street texture"],
        "agent_activity": "checking the route before departure",
        "is_natural_or_semi_natural": False,
    },
    {
        "landscape_type": "river or waterfront",
        "role": "first soft transition into open water or river scenery",
        "local_visual_elements": ["water reflections", "riverbank plants", "small boat or bridge", "mist or open sky"],
        "agent_activity": "reading a map beside the water",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "hills or highland path",
        "role": "entering higher ground",
        "local_visual_elements": ["winding path", "regional plants", "distant ridges", "stone or soil texture"],
        "agent_activity": "sketching the terrain from a low resting spot",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "local town or old quarter",
        "role": "passing through a place with visible local architecture",
        "local_visual_elements": ["local facade materials", "market awning", "balcony or arcade", "street objects"],
        "agent_activity": "resting under shade with a small drink or map",
        "is_natural_or_semi_natural": False,
    },
    {
        "landscape_type": "mountain, cliff, or dramatic geology",
        "role": "major natural transition",
        "local_visual_elements": ["rock faces", "large sky", "trail markers", "wind-shaped plants"],
        "agent_activity": "standing small on a trail while the landscape dominates",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "plain, desert, grassland, or open country",
        "role": "wide-open crossing",
        "local_visual_elements": ["open horizon", "track or road", "sparse shelter", "weathered local material"],
        "agent_activity": "sorting the backpack in a patch of shade",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "harbor, ferry, or strait",
        "role": "water crossing",
        "local_visual_elements": ["ferry rail", "harbor lights", "seabirds or wind", "distant shore"],
        "agent_activity": "waiting by a ferry rail with a folded map",
        "is_natural_or_semi_natural": True,
    },
    {
        "landscape_type": "arrival city",
        "role": "arrival at the destination",
        "local_visual_elements": ["recognizable arrival landmark", "local pavement", "river or skyline", "arrival light"],
        "agent_activity": "holding a final travel postcard",
        "is_natural_or_semi_natural": False,
    },
]


def _run_external_route_planner(payload: dict[str, Any]) -> dict[str, Any] | None:
    command = os.environ.get("TRAVEL4ME_ROUTE_COMMAND")
    if not command:
        return None
    result = subprocess.run(command, input=json.dumps(payload), text=True, shell=True, capture_output=True, timeout=120, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"TRAVEL4ME_ROUTE_COMMAND failed: {result.stderr or result.stdout}")
    return json.loads(result.stdout)


def _interpolate(start: dict[str, float], end: dict[str, float], t: float) -> dict[str, float]:
    return {
        "lat": round(start["lat"] + (end["lat"] - start["lat"]) * t, 4),
        "lon": round(start["lon"] + (end["lon"] - start["lon"]) * t, 4),
    }


def _day_count(origin_coords: dict[str, float] | None, destination_coords: dict[str, float] | None, target_days: int | None) -> tuple[int, int | None]:
    distance = None
    if origin_coords and destination_coords:
        distance = round(haversine_km((origin_coords["lat"], origin_coords["lon"]), (destination_coords["lat"], destination_coords["lon"])))
    if target_days:
        return max(3, min(30, target_days)), distance
    if distance is not None:
        return estimate_days(distance), distance
    return 12, None


def _landscape_for(day_index: int, total_days: int) -> dict[str, Any]:
    if day_index == 0:
        return LANDSCAPE_SEQUENCE[0]
    if day_index == total_days - 1:
        return LANDSCAPE_SEQUENCE[-1]
    inner = LANDSCAPE_SEQUENCE[1:-1]
    return inner[(day_index - 1) % len(inner)]


def _make_placeholder_landmarks(location: str, landscape_type: str) -> list[str]:
    return [
        f"primary recognizable landmark for {location}",
        f"secondary local feature fitting {landscape_type}",
    ]


def plan_route(
    origin: str,
    destination: str,
    origin_coords: dict[str, float] | None = None,
    destination_coords: dict[str, float] | None = None,
    target_days: int | None = None,
) -> dict[str, Any]:
    external_payload = {
        "origin": origin,
        "destination": destination,
        "origin_coords": origin_coords,
        "destination_coords": destination_coords,
        "target_days": target_days,
        "requirements": {
            "max_days": 30,
            "include_coordinates": True,
            "include_landmarks": True,
            "avoid_three_city_days": True,
            "include_natural_or_semi_natural_days": True,
        },
    }
    external = _run_external_route_planner(external_payload)
    if external:
        return external

    days, direct_distance = _day_count(origin_coords, destination_coords, target_days)
    start = origin_coords or {"lat": 0.0, "lon": 0.0}
    end = destination_coords or {"lat": 0.0, "lon": 0.0}
    has_real_coords = origin_coords is not None and destination_coords is not None

    waypoints = []
    for idx in range(days):
        t = idx / max(1, days - 1)
        template = _landscape_for(idx, days)
        if idx == 0:
            location = origin
        elif idx == days - 1:
            location = destination
        else:
            location = f"Route waypoint {idx + 1}"
        coords = _interpolate(start, end, t) if has_real_coords else {"lat": None, "lon": None}
        landscape_type = template["landscape_type"]
        waypoints.append(
            {
                "day": idx + 1,
                "location": location,
                "country_or_region": "to be resolved",
                "coordinates": coords,
                "role": template["role"],
                "landmarks": _make_placeholder_landmarks(location, landscape_type),
                "landscape_type": landscape_type,
                "local_visual_elements": template["local_visual_elements"],
                "palette": ["locally appropriate colors", "route-specific light", "style-consistent accents"],
                "agent_activity": template["agent_activity"],
                "agent_position": "small off-center traveler naturally participating in the local environment",
                "prompt_focus": f"{landscape_type} with recognizable local identity",
                "is_natural_or_semi_natural": template["is_natural_or_semi_natural"],
                "needs_enrichment": True,
            }
        )

    route_distance = None
    if has_real_coords:
        route_distance = round(
            sum(
                haversine_km(
                    (a["coordinates"]["lat"], a["coordinates"]["lon"]),
                    (b["coordinates"]["lat"], b["coordinates"]["lon"]),
                )
                for a, b in zip(waypoints, waypoints[1:])
            )
        )

    return {
        "origin": origin,
        "destination": destination,
        "days": days,
        "direct_distance_km": direct_distance,
        "route_distance_km": route_distance,
        "needs_enrichment": True,
        "enrichment_note": "No external route/geocoding command was configured. A coding agent should enrich route waypoints with real city/region names, landmarks, local visual elements, and coordinates before live generation.",
        "waypoints": waypoints,
    }


def _coords(prefix: str, args: argparse.Namespace) -> dict[str, float] | None:
    lat = getattr(args, f"{prefix}_lat")
    lon = getattr(args, f"{prefix}_lon")
    if lat is None or lon is None:
        return None
    return {"lat": lat, "lon": lon}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--origin-lat", type=float)
    parser.add_argument("--origin-lon", type=float)
    parser.add_argument("--destination-lat", type=float)
    parser.add_argument("--destination-lon", type=float)
    parser.add_argument("--target-days", type=int)
    parser.add_argument("--out")
    args = parser.parse_args()

    route = plan_route(
        args.origin,
        args.destination,
        _coords("origin", args),
        _coords("destination", args),
        args.target_days,
    )
    if args.out:
        write_json(Path(args.out), route)
    else:
        print_json(route)


if __name__ == "__main__":
    main()
