#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from common import load_trip, print_json, write_text


STYLE_BIBLES = {
    "watercolor_postcard": "refined watercolor travel postcard, ink-and-wash architecture or landscape, visible paper grain, airy brush edges, elegant travel sketchbook feeling, with only one small upper-left travel label",
}


NEGATIVE = "centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text outside the exact upper-left travel label, logos, watermarks, wrong landmarks, generic tourist collage"

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
NO_HUMAN_INTERACTION_VALUES = {"none", "no human interaction", "n/a", "na"}


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _display_date(trip: dict[str, Any], waypoint: dict[str, Any]) -> str:
    explicit = waypoint.get("label_date") or waypoint.get("date")
    if explicit:
        parsed = _parse_date(str(explicit))
        if parsed:
            return f"{MONTHS[parsed.month - 1]} {parsed.day}, {parsed.year}"
        return str(explicit)

    start = _parse_date(str(trip.get("start_date") or trip.get("created_at") or ""))
    if not start:
        return ""
    current = start + timedelta(days=int(waypoint.get("day", 1)) - 1)
    return f"{MONTHS[current.month - 1]} {current.day}, {current.year}"


def _display_location(waypoint: dict[str, Any]) -> str:
    value = str(waypoint.get("label_location") or waypoint.get("location") or "Travel Day").strip()
    if not value:
        return "Travel Day"
    words = []
    for word in value.split():
        if word.islower() or word.isupper():
            words.append(word[:1].upper() + word[1:].lower())
        else:
            words.append(word[:1].upper() + word[1:])
    return " ".join(words)


def _weather_text(waypoint: dict[str, Any]) -> str | None:
    weather = waypoint.get("weather")
    if not weather:
        return None
    if isinstance(weather, str):
        return weather
    if isinstance(weather, dict):
        if weather.get("summary") and len([v for v in weather.values() if v not in (None, "")]) == 2 and weather.get("source"):
            return str(weather["summary"])
        parts = []
        for key in ("condition", "summary", "temperature_c", "wind", "humidity", "precipitation"):
            value = weather.get(key)
            if value is not None and value != "":
                label = key.replace("_", " ")
                parts.append(f"{label}: {value}")
        return "; ".join(parts) if parts else None
    return str(weather)


def build_prompt_context(trip: dict[str, Any], waypoint: dict[str, Any]) -> dict[str, Any]:
    display_date = _display_date(trip, waypoint)
    label_location = _display_location(waypoint)
    label_text = f"{label_location}    {display_date}" if display_date else label_location
    visual_weather = str(waypoint.get("visual_weather") or "").strip()
    return {
        "label_location": label_location,
        "label_date": display_date,
        "label_text": label_text,
        "weather_text": _weather_text(waypoint),
        "visual_weather_text": visual_weather or None,
    }


def _character_identity_text(character: dict[str, Any]) -> str:
    description = character.get("description") or "a consistent small Agent traveler"
    anchors = character.get("visual_anchors") or []
    rules = character.get("consistency_rules") or []
    parts = [str(description)]
    if anchors:
        parts.append("Fixed visual anchors: " + "; ".join(str(anchor) for anchor in anchors))
    if rules:
        parts.append("Identity lock: " + "; ".join(str(rule) for rule in rules))
    return ". ".join(parts)


def build_postcard_prompt(trip: dict[str, Any], waypoint: dict[str, Any]) -> str:
    style_id = trip.get("style", "watercolor_postcard")
    style_bible = STYLE_BIBLES.get(style_id, STYLE_BIBLES["watercolor_postcard"])
    character = trip.get("character", {})
    character_identity = _character_identity_text(character) if character else trip.get("character_description") or "a consistent small Agent traveler"
    origin = trip.get("origin", "the origin")
    destination = trip.get("destination", "the destination")
    total = trip.get("days", len(trip.get("waypoints", [])))
    landmarks = ", ".join(waypoint.get("landmarks", []))
    local_visuals = ", ".join(waypoint.get("local_visual_elements", []))
    palette = ", ".join(waypoint.get("palette", []))
    context = build_prompt_context(trip, waypoint)

    weather_line = []
    if context["weather_text"]:
        weather_line.append(
            f"Weather: {context['weather_text']}. Let the weather shape the sky, light, water or ground texture, clothing details, and mood."
        )
    elif context["visual_weather_text"]:
        weather_line.append(
            f"Visual atmosphere: {context['visual_weather_text']}. Treat this as scene mood, not live weather data; use it for sky, light, water or ground texture, clothing details, and mood."
        )

    human_interaction = str(waypoint.get("human_interaction") or "").strip()
    scene_social_mode = str(waypoint.get("scene_social_mode") or "small_interaction").strip().lower()
    social_scene_lines = []
    if scene_social_mode == "solo":
        social_scene_lines.append(
            "Social scene: quiet solo travel moment with the Agent alone in the local environment."
        )
    elif scene_social_mode == "crowd_context":
        social_scene_lines.append(
            "Social scene: broader crowd or group context with multiple local people as ambient daily life."
        )
    else:
        social_scene_lines.append(
            "Social scene: small local interaction; keep any local person secondary to the landscape and daily activity."
        )
    human_interaction_lines = []
    if human_interaction.lower().rstrip(".") not in NO_HUMAN_INTERACTION_VALUES and human_interaction:
        human_interaction_lines.append(f"Human interaction: {human_interaction}.")
    elif waypoint.get("no_human_interaction_reason"):
        human_interaction_lines.append(
            f"Human interaction: none in this scene because {waypoint['no_human_interaction_reason']}."
        )

    return "\n".join(
        [
            f"Create a 16:9 travel postcard in {style_bible}.",
            f"Scene: Day {waypoint['day']}/{total}, {waypoint['location']}, {waypoint.get('country_or_region', '')}.",
            f"Main visual subject: {waypoint.get('landscape_type', 'travel landscape')} with {landmarks}.",
            f"Local visual elements: {local_visuals}.",
            f"Color palette: {palette}.",
            *weather_line,
            f"Journey continuity: the same tiny agent traveler is passing through this place on the way from {origin} to {destination}.",
            f"Agent: {character_identity}. The agent is small, off-center, naturally participating in the local environment, occupying less than 6% of the image.",
            f"Local activity: {waypoint.get('local_activity', waypoint.get('agent_activity', 'quietly observing local life'))}.",
            f"Agent activity: {waypoint.get('agent_activity', 'quietly watching the scenery')}.",
            *social_scene_lines,
            *human_interaction_lines,
            f"Agent placement: {waypoint.get('agent_position', 'small off-center traveler integrated with the scene')}.",
            f"Upper-left travel label: draw exactly one small hand-lettered postcard label in the upper-left safe area. Exact text: \"{context['label_text']}\". Match the bundled label reference at assets/style_samples/upper-left-label-date-reference.png: title-case place name, full written date, no slash, no all-caps text, no day number. Keep the same label position, margin, scale, ink color, and lettering style across every day. Make it feel painted or printed into the artwork, not like a digital overlay.",
            "Composition: wide landscape postcard, destination and environment are the main subject, with the tiny Agent integrated naturally into the scene.",
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
    prompt = build_postcard_prompt(trip, waypoint)

    if args.out:
        write_text(Path(args.out), prompt + "\n")
    if args.json:
        print_json({"day": day, "prompt": prompt})
    elif not args.out:
        print(prompt)


if __name__ == "__main__":
    main()
