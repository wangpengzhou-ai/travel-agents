#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import load_trip, write_json, write_text
from image_providers import ImageProviderError, generate_image


def build_character_prompt(character: str, style: str) -> str:
    return "\n".join(
        [
            "Create a character reference image for agent-travel4me.",
            f"Character: {character}.",
            "The character should be a small travel companion with clear recurring visual anchors.",
            "Show full body, three-quarter view, simple neutral travel backdrop, no text, no logos, no watermark.",
            "Keep the design suitable for reuse as a tiny recurring traveler in scenic wallpaper images.",
            f"Rendering style hint: {style}.",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trip-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--size", default="1024x1024")
    args = parser.parse_args()
    trip_dir = Path(args.trip_dir)
    trip = load_trip(trip_dir)
    character = trip["character"]["description"]
    prompt = build_character_prompt(character, trip.get("style", "watercolor_postcard"))
    write_text(trip_dir / "character_reference_prompt.txt", prompt + "\n")
    metadata = {"prompt_path": str(trip_dir / "character_reference_prompt.txt"), "dry_run": args.dry_run}
    if not args.dry_run:
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
