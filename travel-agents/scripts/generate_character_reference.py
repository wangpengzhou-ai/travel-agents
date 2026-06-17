#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import load_trip, write_json, write_text
from image_providers import ImageProviderError, generate_image, selected_provider


def build_character_prompt(character: dict | str, style: str) -> str:
    if isinstance(character, dict):
        description = character.get("description", "")
        anchors = character.get("visual_anchors") or []
        rules = character.get("consistency_rules") or []
    else:
        description = str(character)
        anchors = [description]
        rules = []
    lines = [
        "Create a character reference image for travel agents.",
        f"Character: {description}.",
    ]
    if anchors:
        lines.append("Fixed visual anchors: " + "; ".join(str(anchor) for anchor in anchors) + ".")
    if rules:
        lines.append("Identity lock: " + "; ".join(str(rule) for rule in rules) + ".")
    lines.extend(
        [
            "The character should be a small travel companion with clear recurring visual anchors.",
            "Show full body, three-quarter view, simple neutral travel backdrop, no text, no logos, no watermark.",
            "Keep the design suitable for reuse as a tiny recurring traveler in scenic postcard images.",
            f"Rendering style hint: {style}.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--size", default="1024x1024")
    args = parser.parse_args()
    trip_dir = Path(args.trip_dir)
    trip = load_trip(trip_dir)
    character = trip["character"]
    prompt = build_character_prompt(character, trip.get("style", "watercolor_postcard"))
    write_text(trip_dir / "character_reference_prompt.txt", prompt + "\n")
    metadata = {"prompt_path": str(trip_dir / "character_reference_prompt.txt"), "dry_run": args.dry_run}
    if not args.dry_run:
        if not selected_provider():
            metadata["status"] = "blocked_image_provider_unavailable"
            metadata["issues"] = [
                "No local image provider is configured. Use a host-native image tool with this prompt, or set OPENAI_API_KEY, GEMINI_API_KEY, SEEDREAM_API_KEY, or TRAVEL_AGENTS_IMAGE_COMMAND."
            ]
            write_json(trip_dir / "character_reference_metadata.json", metadata)
            print(metadata["prompt_path"])
            return
        try:
            provider_meta = generate_image(prompt, trip_dir / "character_reference.png", size=args.size)
            metadata.update(provider_meta)
            metadata["image_path"] = str(trip_dir / "character_reference.png")
        except ImageProviderError as exc:
            metadata["error"] = str(exc)
            metadata["status"] = "prompt_only_provider_missing_or_failed"
    write_json(trip_dir / "character_reference_metadata.json", metadata)
    print(metadata.get("image_path") or metadata["prompt_path"])


if __name__ == "__main__":
    main()
