#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import load_trip, print_json, write_text


STYLE_BIBLES = {
    "watercolor_postcard": "refined watercolor travel postcard, ink-and-wash architecture or landscape, visible paper grain, airy brush edges, elegant travel sketchbook feeling without any written text",
    "cinematic_landscape": "cinematic travel landscape, realistic natural textures, high dynamic range, premium travel film still",
    "high_quality_3d_animation": "original high-quality 3D animated movie look, rounded appealing forms, stylized environments, soft global illumination; do not imitate a named studio, franchise, or existing character",
    "anime_travel": "high-quality Japanese anime travel-film background art, clean expressive linework, luminous color, soft atmospheric perspective, detailed hand-painted landmarks",
}


NEGATIVE = "centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text, logos, watermarks, wrong landmarks, generic tourist collage"


def build_wallpaper_prompt(trip: dict[str, Any], waypoint: dict[str, Any]) -> str:
    style_id = trip.get("style", "watercolor_postcard")
    style_bible = STYLE_BIBLES.get(style_id, STYLE_BIBLES["watercolor_postcard"])
    character = trip.get("character", {})
    character_identity = character.get("description") or trip.get("character_description") or "a consistent small Agent traveler"
    origin = trip.get("origin", "the origin")
    destination = trip.get("destination", "the destination")
    total = trip.get("days", len(trip.get("waypoints", [])))
    landmarks = ", ".join(waypoint.get("landmarks", []))
    local_visuals = ", ".join(waypoint.get("local_visual_elements", []))
    palette = ", ".join(waypoint.get("palette", []))

    return "\n".join(
        [
            f"Create a 16:9 travel wallpaper in {style_bible}.",
            f"Scene: Day {waypoint['day']}/{total}, {waypoint['location']}, {waypoint.get('country_or_region', '')}.",
            f"Main visual subject: {waypoint.get('landscape_type', 'travel landscape')} with {landmarks}.",
            f"Local visual elements: {local_visuals}.",
            f"Color palette: {palette}.",
            f"Journey continuity: the same tiny agent traveler is passing through this place on the way from {origin} to {destination}.",
            f"Agent: {character_identity}. The agent is small, off-center, naturally participating in the local environment, occupying less than 6% of the image.",
            f"Agent activity: {waypoint.get('agent_activity', 'quietly watching the scenery')}.",
            f"Agent placement: {waypoint.get('agent_position', 'small off-center traveler integrated with the scene')}.",
            "Composition: wide landscape wallpaper, destination and environment are the main subject, clear negative space for desktop icons.",
            f"Prompt focus: {waypoint.get('prompt_focus', waypoint.get('location', 'travel scene'))}.",
            f"Avoid: {NEGATIVE}.",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--day", type=int)
    parser.add_argument("--out")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    trip_dir = Path(args.trip_dir)
    trip = load_trip(trip_dir)
    day = args.day or trip.get("current_day", 1)
    waypoint = trip["waypoints"][day - 1]
    prompt = build_wallpaper_prompt(trip, waypoint)

    if args.out:
        write_text(Path(args.out), prompt + "\n")
    if args.json:
        print_json({"day": day, "prompt": prompt})
    elif not args.out:
        print(prompt)


if __name__ == "__main__":
    main()
