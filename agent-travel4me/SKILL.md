---
name: agent-travel4me
description: "Plan and run an Agent travels for me journey, and directly generate strict postcard-style travel images when the user asks for postcards/images for specified places. Supports origin/destination setup, recurring Agent traveler identity, route scenes, prompts, optional images, wallpaper resizing, wallpaper setting, and route data export."
---

# agent-travel4me

Use this skill when the user wants an AI Agent to "travel for me" and maintain a multi-day journey along a route.

This is a portable coding-agent skill for UI and CLI hosts. Work through local files and scripts.

## Capability Adapters

Different coding agents expose different capabilities: native image generation, weather/search, reminders/automation, browser tools, or local command execution. Select the available adapter at run time and keep trip state portable across hosts.

Supported adapter categories:

- Native image tool adapter: call the host agent's image-generation tool directly from the current turn when it is available, then update local state if the tool returns a local image path.
- API provider adapter: local scripts generate through configured API keys or command hooks.
- Automation adapter: create the daily run automation by default after a durable trip is initialized. Use host agent reminder/automation first when available; use OS schedulers only when local scripts can complete the run without the host agent.
- Weather adapter: host weather/search tool first when available; otherwise use a user-provided weather summary or a configured weather command.

## Overview

`agent-travel4me` turns a user's travel wish into a local, multi-day Agent journey. The agent acts as a small recurring traveler moving from an origin to a destination. For each day, the workflow chooses a waypoint, builds a scene prompt with recognizable local details, can optionally generate an image, and advances the trip state.

The route is a visually coherent, geographically plausible narrative arc for daily postcard-style scenes. The main deliverable is durable journey state, route data, daily scene prompts, and optional visual artifacts. Desktop wallpaper is one supported presentation option.

## Direct Postcard Image Requests

Use this fast path when the user explicitly asks to generate one or more postcards/images from given places, an existing route, or a supplied character reference, and does not ask to start or advance a durable trip.

This fast path is complete by itself. Do not read `references/prompt_contract.md`, `references/route_planning.md`, `references/environment_detection.md`, or any scripts before the first image-generation call.

For this fast path:

1. Do not run environment detection, initialize a trip, validate a route, create a character reference, or ask for character confirmation first.
2. Resolve small ambiguities quickly. If the user gives a count that conflicts with the listed locations, prefer the explicit location list and mention the mismatch.
3. Build one compact prompt per requested image using the fixed watercolor postcard contract: 16:9, one small off-center recurring traveler, environment-first composition, varied solo/small-interaction/crowd-context activity, and exactly one upper-left `Place    Month D, YYYY` label.
4. If the user supplies a character image, keep that character as the identity lock and only add small recurring accessories when allowed.
5. Call the host image-generation tool directly after the first prompt is ready. In Codex, use `image_gen` / `imagegen`; do not first reason through the full trip-state workflow, inspect files, or run shell commands.
6. For multiple locations, generate images sequentially, one tool call per location, so the user sees progress quickly.
7. After generation, report the generated images. Import into local trip state only if the user asked for durable trip files or the host tool reports a local image path and the existing trip directory is already known.

Compact prompt pattern for each direct postcard:

```text
Create one 16:9 watercolor travel postcard for {place}. Use {character_source} as the same recurring tiny Agent traveler: {character_identity}. Preserve the identity and stable visual anchors; add only {allowed_accessories}. The Agent must be small, off-center, naturally participating in a local activity; vary scenes across solo moments, gentle local interactions, and broader crowd/public-life context. The environment is the main subject, with recognizable local landmarks, landscape, textures, colors, weather or atmospheric mood, and daily life. Add exactly one small hand-lettered upper-left label: "{place_label}    {date_label}". No other readable text, logos, watermarks, centered Agent, close-up mascot portrait, generic tourist collage, or wrong landmarks.
```

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
1. 戴红围巾的小橘猫，背着轻便小背包
2. 穿蓝色雨衣的小白狗，带一个防水小背包
3. 圆滚滚的小邮差机器人，胸前挂着一只旧指南针
```

## Agent Candidate Guidance

The three first-run candidates are not fixed. Generate them from the route, user context, and the postcard mood, but make every option visually concrete enough for an image model to reproduce.

Each candidate should include:

- A concrete subject, such as a small cat, small dog, tiny robot, small bird, or other mascot-like traveler.
- One stable appearance anchor, such as color, scarf, raincoat, hat, or bag.
- One travel prop, such as a tiny backpack, postcard pouch, compass, sketchbook, ticket sleeve, or folded map.
- One small behavior that fits travel, such as waiting by a boat, watching weather, collecting tickets, sketching landmarks, or tasting a local snack.
- Do not make a map the default fixed prop unless the user explicitly asks for it. Map-checking should be occasional, not the Agent's repeated daily action.

Avoid abstract role-only candidates such as "quiet mapkeeper", "little observer", or "small travel companion" unless they also have a concrete body and visible anchors.

## Inputs To Collect

- Destination: ask first.
- Origin: infer only if local Memory or context makes it likely, then confirm.
- Agent identity: recommend three concrete candidates first; let the user choose, combine, or rewrite one.
- Visual style: use the fixed watercolor postcard style.
- Day count: estimate automatically from distance, cap at 30 days, and let the user shorten it.
- Place/date label: default to a model-drawn upper-left label unless the user opts out.
- Label format: match `assets/style_samples/upper-left-label-date-reference.png`, for example `Rome    May 28, 2026`; do not use all caps, slash separators, uppercase month abbreviations, or `DAY XX`.

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

If daily automation is available, the skill should create it without asking whether the user wants automation. Report what was created. Ask only when the host or operating system requires an approval step to install or enable the automation.

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
   - "我算了一下，从 {origin} 到 {destination}，我大概需要 {days} 天能抵达。你想让我把旅程压缩一点吗？如果想，告诉我你希望几天内抵达，我会减少中间停留、让叙事节奏更紧凑。"
6. Keep the Agent as a small recurring traveler while the environment remains the main subject. Route planning must write a locally distinctive activity into each waypoint and vary `scene_social_mode` across solo, small interaction, and crowd context.
7. Keep the Agent off-center and vary placement across the frame, with no repeated lower-left/lower-right standing poses.
8. Allow quiet solo scenes when they improve visual variety, not only for remote exceptions. Keep no-human-interaction days to about 35% or less and record the reason on the waypoint.
9. Treat live weather as optional enhancement context. If the day's local weather is already available or user-provided, write it into `waypoint.weather`; missing weather should not block prompt generation, local image generation, or host-native image generation. If live weather is unavailable, use `visual_weather` only as scene mood, not current weather data.
10. Use local environment variables for API credentials; avoid asking users to paste keys into chat.
11. Create daily automation after trip initialization when an automation adapter is available. Do not ask the user whether to set automation; report the created schedule or the missing adapter. This is separate from wallpaper changes.
12. Set wallpaper only after the user explicitly allows it.
13. Keep future route stops as internal state. User-facing narration should reveal only the current day, already visited places, total day count, and broad journey direction. Show future waypoint names, landmarks, or the full route only if the user explicitly asks to see or export the full route.
14. Keep user-facing travel narration separate from production logs. The traveler's voice excludes prompt, metadata, verification, composition, file paths, and image-generation mechanics.

## Image Generation Priority

Use the current host's native image-generation tool first when it exists. Otherwise use the local provider reported by `scripts/detect_environment.py --json`.

When a host advertises or exposes native image generation, prove it by attempting the first real required image generation: the character reference during durable-trip setup, or the first requested postcard/daily scene when no character reference is needed. Do not rely only on static capability text. If that actual image-generation call succeeds, continue on the host-native path. If the tool call itself fails or is unavailable, fall back to the local provider path.

If no image path is available, still create route data and prompts, then state which local provider, API key, or host capability is missing. `native_image_tool_hint=false` is only a local detection hint; it is not a reason to skip an actually available host-native image tool.

## Core Workflow

## Visual Style

Use `watercolor_postcard` for every journey. Read `references/style_presets.md` only for the postcard style contract. The bundled sample is:

- `watercolor_postcard`: `assets/style_samples/watercolor-postcard-rome.png`
- Upper-left label reference: `assets/style_samples/upper-left-label-date-reference.png`

Do not use the repository-root `style-samples/` folder for runtime style guidance; it contains legacy exploration samples. For runtime image references, prefer the label-only reference above instead of passing the full postcard sample, so the reference controls only the upper-left date label and does not steer the whole scene style.

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
- `scene_social_mode`: `solo`, `small_interaction`, or `crowd_context`.
- `visual_weather`: optional non-live atmospheric cue when actual local weather is unavailable.

Weather is nice-to-have prompt context. If it is missing, generate the daily prompt without a `Weather:` line and continue the workflow. `visual_weather` may still be used as a scene mood, but must not be presented as current weather.

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

### 4. Create Daily Automation

After the trip exists and before or immediately after the first daily scene, create the daily automation when an adapter is available. Prefer host agent automation/reminders when the host provides them. Use `scripts/install_schedule.py` for OS schedulers only when local scripts can run the daily image workflow without the host agent.

Do not ask whether to create automation. Ask only if a tool, platform, or operating system approval dialog is required. If no automation adapter exists, report that daily generation will require manual runs until one is configured.

For supported local OS schedulers:

```bash
python scripts/install_schedule.py \
  --trip-dir <trip_dir> \
  --install
```

### 5. Generate Daily Scene Image

Before live image generation, validate route quality:

```bash
python scripts/validate_route.py --trip-dir <trip_dir>
```

Default validation blocks only route structure and generation-readiness errors. It may also print quality warnings, such as repeated Agent actions, too many map/route-card activities, overly narrow social variety, or missing solo/crowd variety; treat those as route improvement suggestions unless the user wants strict review. Use `--strict-quality` when quality warnings should fail validation too.

If validation fails because the route still contains placeholders, missing required route data, or other blocking errors, enrich the route with real places, coordinates, landmarks, local visual elements, and natural/semi-natural days, save it as JSON, then apply it:

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
2. Call the host image-generation tool directly with that exact prompt. In Codex, use the `image_gen` / `imagegen` tool when it is available; do not describe this as a request for the user or for another agent to perform later.
3. If the host tool reports a saved local image path, import that exact generated file:

```bash
python scripts/import_generated_image.py \
  --trip-dir <trip_dir> \
  --day <day> \
  --image <generated_image_path>
```

If the host tool only displays or attaches an image and does not expose a local file path, do not keep searching or waiting for one. Report that the image was generated/displayed and leave the trip with `day_###/prompt.txt` plus prompt-only metadata, or ask the user to provide the saved file path if local trip-state import is required.

For a durable trip, generate only the current due day by default. Do not proactively offer to continue or generate all remaining days at once. If the user explicitly asks for a manual catch-up, preview, or bulk generation, follow the request while preserving route validation and state updates.

To set wallpaper after generation, pass `--set-wallpaper` to the local API live run, or import the host-generated image and then call `scripts/set_wallpaper.py` manually.

Only use `--set-wallpaper` after user approval.

## Quality Contracts

Before route enrichment or live daily image generation, use `references/route_planning.md` for waypoint requirements and `references/prompt_contract.md` for prompt requirements.

Non-negotiables: use real places, coordinates, landmarks, locally specific activities, varied Agent actions, and varied social density across solo, small-interaction, and crowd-context scenes. Keep live weather optional; use `visual_weather` only as atmospheric mood when needed. Keep the Agent small and off-center. Draw exactly one upper-left place/date label.

The script gate is `python scripts/validate_route.py --trip-dir <trip_dir>`. Use `--strict-quality` only when route quality warnings should also block generation.

## References

- `references/environment_detection.md`
- `references/route_planning.md`
- `references/prompt_contract.md`
- `references/style_presets.md`
- `references/wallpaper_platforms.md`
