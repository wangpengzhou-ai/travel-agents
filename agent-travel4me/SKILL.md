---
name: agent-travel4me
description: "Plan and run an Agent travels for me journey for a user: infer or ask origin and destination, create a consistent small Agent traveler, plan a route with landmarks/nature/local visual elements, generate daily route scenes, prompts, and optional images, optionally resize an image for wallpaper use, optionally set the desktop wallpaper, and export route data for visualization."
---

# agent-travel4me

Use this skill when the user wants an AI Agent to "travel for me" and maintain a multi-day journey along a route.

This is a portable coding-agent skill for UI and CLI hosts. Work through local files and scripts.

## Capability Adapters

Different coding agents expose different capabilities: native image generation, weather/search, reminders/automation, browser tools, or local command execution. Select the available adapter at run time and keep trip state portable across hosts.

Supported adapter categories:

- Native image tool adapter: host agent generates the image from the prompt, then the local state is updated.
- API provider adapter: local scripts generate through configured API keys or command hooks.
- Automation adapter: host agent reminder/automation first when available; OS schedulers only when local scripts can complete the run without the host agent.
- Weather adapter: host weather/search tool first when available; otherwise use a user-provided weather summary or a configured weather command.

## Overview

`agent-travel4me` turns a user's travel wish into a local, multi-day Agent journey. The agent acts as a small recurring traveler moving from an origin to a destination. For each day, the workflow chooses a waypoint, builds a scene prompt with recognizable local details, can optionally generate an image, and advances the trip state.

The skill is for "Agent travels for me" narrative production. Travel booking and real itinerary advice are outside scope. The route should be visually coherent and geographically plausible. The main deliverable is durable journey state, route data, daily scene prompts, and optional visual artifacts. Desktop wallpaper is one supported presentation option.

## First-Run Start

When this skill is opened or invoked without an existing trip request, start setup immediately. The first response should ask concise setup questions.

First response should:

- Ask for the destination.
- Confirm or ask for the origin.
- Recommend three concrete Agent traveler candidates and ask the user to pick one or revise it.

Example first-run opener:

```text
我来替你开始一段旅程。你想让我从哪里出发，最后去哪里？
我先给你 3 个小旅行者形象，你可以直接选一个，也可以改：
1. 戴红围巾的小橘猫，背着卷起来的小地图
2. 穿蓝色雨衣的小白狗，带一个防水小背包
3. 圆滚滚的小邮差机器人，胸前挂着一只旧指南针
```

## Agent Candidate Guidance

The three first-run candidates are not fixed. Generate them from the route, user context, and the postcard mood, but make every option visually concrete enough for an image model to reproduce.

Each candidate should include:

- A concrete subject, such as a small cat, small dog, tiny robot, small bird, or other mascot-like traveler.
- One stable appearance anchor, such as color, scarf, raincoat, hat, or bag.
- One travel prop, such as a folded map, tiny backpack, postcard pouch, compass, sketchbook, or ticket sleeve.
- One small behavior that fits travel, such as checking a map, waiting by a boat, watching weather, collecting tickets, or sketching landmarks.

Avoid abstract role-only candidates such as "quiet mapkeeper", "little observer", or "small travel companion" unless they also have a concrete body and visible anchors.

## Inputs To Collect

- Destination: ask first.
- Origin: infer only if local Memory or context makes it likely, then confirm.
- Agent identity: recommend three concrete candidates first; let the user choose, combine, or rewrite one.
- Visual style: use the fixed watercolor postcard style.
- Day count: estimate automatically from distance, cap at 30 days, and let the user shorten it.
- Place/date label: default to a model-drawn upper-left label unless the user opts out.
- Label format: match `assets/style_samples/watercolor-postcard-rome.png`, for example `Rome    May 28, 2026`; do not use all caps, slash separators, uppercase month abbreviations, or `DAY XX`.

## Expected Outputs

A complete run should create or update a trip directory under `~/.agent-travel4me/trips/<trip_id>/` with:

- `trip.json`: durable trip state, current day, style, character identity, and waypoints.
- `character.json`: durable Agent identity lock, visual anchors, and consistency rules.
- `route.json`: planned route data.
- `route.geojson`: map-friendly route output for visualization.
- `start_date` and `label` config in `trip.json`, used for the model-drawn upper-left place/date label.
- `character_reference_prompt.txt`: prompt for the recurring Agent traveler.
- `character_reference.png`, when image generation is available and succeeds.
- `day_###/prompt.txt`: scene/image prompt for that day's waypoint.
- `day_###/metadata.json`: generation status, label text, weather, paths, provider metadata, and errors if any.
- `day_###/original.png`, when image generation is available and succeeds.
- `day_###/wallpaper.png`: desktop-sized optional presentation output after resize/crop, when image generation is available and succeeds.

If image generation is unavailable, the skill should still produce route data and prompts, then clearly state which local provider, API key, or native image tool is missing.

## Operating Rules

1. Start with environment detection:
   ```bash
   python scripts/detect_environment.py
   ```
2. Minimize questions. Ask destination first. Infer origin from Memory only as a guess and confirm it.
3. Recommend Agent identity candidates in a personal voice:
   - "我先给你几个我可以成为的小旅行者形象，你选一个或改掉它。"
   - Generate three concrete, visually reproducible candidates using the Agent Candidate Guidance.
4. Generate or prompt for a character reference before daily scene images. Ask the user to confirm it.
5. Estimate journey length automatically, capped at 30 days. Confirm the estimate:
   - "我算了一下，从 {origin} 到 {destination}，我大概需要 {days} 天能抵达。你想让我更快一点吗？如果想，告诉我你希望几天内到，我会换更快的交通工具。"
6. Keep the Agent as a small recurring traveler while the environment remains the main subject. Route planning must write a locally distinctive activity into each waypoint, and the Agent should usually interact with local people through that activity.
7. Keep the Agent off-center and vary placement across the frame, with no repeated lower-left/lower-right standing poses.
8. Allow at most 20% of days to skip human interaction, chosen as sparse/remote exceptions only when a human presence would feel forced. Record the exception reason on the waypoint.
9. Treat weather as optional enhancement context. If the day's local weather is already available or user-provided, write it into `waypoint.weather`; missing weather should not block prompt generation, local image generation, or host-native image generation.
10. Use local environment variables for API credentials; avoid asking users to paste keys into chat.
11. Set wallpaper only after the user explicitly allows it.
12. Keep user-facing travel narration separate from production logs. The traveler's voice excludes prompt, metadata, verification, composition, file paths, and image-generation mechanics.

## Provider Priority

Choose the first available generation path:

1. Native agent image generation tool, if the current agent exposes one.
2. `gpt-image-2` through `OPENAI_API_KEY`.
3. Nano Banana 2 / Gemini image model through `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
4. Seedream latest available model through `SEEDREAM_API_KEY` or a configured command hook.

If none are available, still create route data and prompts. Tell the user which key or capability is missing.

## Core Workflow

## Visual Style

Use `watercolor_postcard` for every journey. Read `references/style_presets.md` only for the postcard style contract. The bundled sample is:

- `watercolor_postcard`: `assets/style_samples/watercolor-postcard-rome.png`

### 1. Detect

```bash
python scripts/detect_environment.py --json
```

Use the result to decide whether image generation, screen detection, automation, and wallpaper setting are available.

### 2. Initialize Trip

After the user confirms origin, destination, character, and day count:

```bash
python scripts/init_trip.py \
  --origin "<origin city or region>" \
  --destination "<destination city or region>" \
  --character "<confirmed Agent appearance>" \
  --character-anchor "<fixed color/accessory/shape detail>"
```

This writes `trip.json`, `route.geojson`, prompts, and state under `~/.agent-travel4me/trips/<trip_id>/` by default.

If coordinates are known or supplied by a geocoder, pass them with `--origin-lat`, `--origin-lon`, `--destination-lat`, and `--destination-lon`. If not, the route is marked `needs_enrichment`; the coding agent must enrich waypoints with real places, landmarks, local visual elements, and coordinates before live image generation.

Each live day should also have:

- `label_location`: short place name for the upper-left label when the full route location is too long.
- `label_date`: exact date text or ISO date when overriding the default trip start date. The rendered label should use the full written date style, such as `May 28, 2026`.
- `weather`: optional day's local weather summary. Use the current agent's weather/search capability when available, or accept a user-provided weather summary.

Weather is nice-to-have prompt context. If it is missing, generate the daily prompt without a `Weather:` line and continue the workflow.

### 3. Generate Character Reference

Dry run:

```bash
python scripts/generate_character_reference.py --trip-dir <trip_dir> --dry-run
```

Live run, if API/tooling is available:

```bash
python scripts/generate_character_reference.py --trip-dir <trip_dir>
```

Ask user to confirm the resulting reference before generating daily scene images.

### 4. Generate Daily Scene Image

Before live image generation, validate route quality:

```bash
python scripts/validate_route.py --trip-dir <trip_dir>
```

If validation fails because the route still contains placeholders, enrich the route with real places, coordinates, landmarks, local visual elements, and natural/semi-natural days, save it as JSON, then apply it:

```bash
python scripts/apply_route_enrichment.py \
  --trip-dir <trip_dir> \
  --route <enriched_route.json>
```

Dry run to produce the prompt:

```bash
python scripts/daily_run.py \
  --trip-dir <trip_dir> \
  --weather "<daily local weather summary>" \
  --label-location "<short place label>" \
  --dry-run
```

Live run with a local API provider or configured image command:

```bash
python scripts/daily_run.py \
  --trip-dir <trip_dir> \
  --weather "<daily local weather summary>" \
  --label-location "<short place label>"
```

Live run with a host agent native image tool:

1. Run the dry-run command and read `day_###/prompt.txt`.
2. Ask the host agent to generate the image from that exact prompt.
3. Import the generated file:

```bash
python scripts/import_generated_image.py \
  --trip-dir <trip_dir> \
  --day <day> \
  --image <generated_image_path>
```

To set wallpaper after generation, pass `--set-wallpaper` to the local API live run, or import the host-generated image and then call `scripts/set_wallpaper.py` manually.

Only use `--set-wallpaper` after user approval.

## Route Quality

Each waypoint must include:

- location name
- country or region
- coordinates
- role in the journey
- landmarks
- landscape type
- local visual elements
- local activity with concrete place, region, landmark, festival, food, craft, route ritual, or transport detail
- human interaction with a concrete local role and place/region/landmark context, unless the day is one of the allowed sparse/remote exceptions
- palette
- optional weather
- upper-left label text
- agent activity
- prompt focus

For 15-24 day routes, at least 7 days should be natural or semi-natural. For 25-30 day routes, at least 10 days should be natural or semi-natural. Avoid three consecutive city-only days.

## Prompt Quality

Generated prompts must include:

- recognizable landmarks
- varied landscapes
- local visual elements
- current or user-provided weather reflected in sky, light, terrain/water, clothing details, and mood when available
- consistent Agent identity
- locally distinctive activity already planned on the waypoint
- human interaction with local people on at least 80% of days
- varied, context-aware Agent interaction
- exactly one model-drawn upper-left place/date label, with consistent placement, margin, scale, ink color, and lettering style across days; format it like `Rome    May 28, 2026`
- wide-image layout with negative space, so the image can work as wallpaper if the user wants that output
- negative constraints: no readable text outside the exact upper-left label, no logos, no watermark, no centered Agent, no close-up mascot shot

Read `references/prompt_contract.md` for the exact prompt contract.

## References

- `references/environment_detection.md`
- `references/route_planning.md`
- `references/prompt_contract.md`
- `references/style_presets.md`
- `references/wallpaper_platforms.md`
