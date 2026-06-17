# Route Planning

Routes are narrative postcard routes for visual storytelling.

## Day Cap

Maximum journey length is 30 days. If a distance estimate exceeds 30 days, cap it at 30.

Routes longer than 8000 km, polar routes, and cross-continent routes should normally estimate 25-30 days unless the user explicitly asks for a faster compressed journey. Do not treat a no-coordinate fallback as a trustworthy final estimate for a very long route.

Set `day_count_source` on the route:

- `distance_estimate`: default estimate from real coordinates or distance.
- `fallback_no_coordinates`: temporary fallback only; enrich before live generation.
- `user_target`: user explicitly requested a faster or custom day count.

After estimating, confirm with the user:

```text
我算了一下，从 {origin} 到 {destination}，我大概需要 {days} 天能抵达。你想让我把旅程压缩一点吗？如果想，告诉我你希望几天内抵达，我会减少中间停留、让叙事节奏更紧凑。
```

## Waypoint Fields

Every waypoint must include:

- `day`
- `location`
- `country_or_region`
- `coordinates.lat`
- `coordinates.lon`
- `role`
- `landmarks`
- `landscape_type`
- `local_visual_elements`
- `palette`
- `local_activity` with a concrete place, region, landmark, festival, food, craft, route ritual, or transport detail
- `agent_activity`
- `scene_social_mode`: `solo`, `small_interaction`, or `crowd_context`
- `human_interaction` with a concrete local role and the place, region, or landmark it belongs to, or `none` for solo scenes
- `no_human_interaction_reason` when human interaction is skipped
- `visual_weather` when live/user-provided weather is unavailable and the scene needs a non-real-time atmospheric cue
- `agent_position`
- `prompt_focus`
- `is_natural_or_semi_natural`

Persist both:

- `trip.json`
- `route.geojson`

## Validation Gate

Before live image generation, run:

```bash
python scripts/validate_route.py --trip-dir <trip_dir>
```

Block live image generation when validation reports unresolved placeholders, generic local activity, generic human interaction, missing coordinates, missing landmarks, missing local activity, missing human interaction without a valid exception reason, more than 35% no-human-interaction days, too few natural/semi-natural days, or three consecutive city-only days. Dry-run prompt generation is still allowed for route debugging.

Validation may also report quality warnings, such as repeated exact `agent_activity` text, too many map/route-card Agent activities, overly narrow social variety, missing solo/crowd scene variety, or local activities that do not explicitly mention the waypoint place, region, or landmark. These warnings do not block live generation by default. Pass `--strict-quality` when those warnings should fail validation.

Before generating any final daily image prompt or asking a host-native image tool to generate, you may run the daily context gate for required label context:

```bash
python scripts/validate_route.py --trip-dir <trip_dir> --require-day-context <day>
```

Weather is optional nice-to-have context. If it is unavailable, continue without a live-weather line. Use `visual_weather` only as a narrative atmospheric cue; do not present it as current/local weather data.

When a host agent enriches the route, write the enriched route as JSON and apply it with:

```bash
python scripts/apply_route_enrichment.py --trip-dir <trip_dir> --route <enriched_route.json>
```

The enriched route must pass `validate_route.py` before it replaces `trip.json`, `route.json`, and `route.geojson`.

## Selection Strategy

Score candidate nodes:

```text
score = recognizability * 0.30
      + visual_diversity * 0.25
      + route_progress * 0.20
      + local_specificity * 0.15
      + postcard_quality * 0.10
```

Rules:

1. Preserve origin and destination.
2. Prefer recognizable landmarks and distinctive landscapes.
3. Plan one locally distinctive activity for each waypoint before prompt generation. Write it directly into `local_activity`; do not leave it for prompt generation to invent later.
4. Vary social density across `solo`, `small_interaction`, and `crowd_context` scenes. For routes of 4+ days, include at least one quiet solo Agent moment and at least one market, queue, festival, transit, or public-life crowd scene.
5. Balance direct small interactions with broader public-life scenes. Keep small interactions to about 60% of days or less, and write crowd or public-life context directly into `human_interaction` when `scene_social_mode` is `crowd_context`.
6. If a day has no direct human interaction, mark `human_interaction` as `none` and write `no_human_interaction_reason`; these solo scenes should stay at or below 35% of the route.
7. Avoid three consecutive city-only days.
8. For 15-24 day routes, include at least 7 natural or semi-natural days.
9. For 25-30 day routes, include at least 10 natural or semi-natural days.
10. Store coordinates for later website visualization.
11. If the user wants a shorter journey, remove similar intermediate nodes and keep the major geographic transitions.

## User-Facing Reveal Rule

The complete route is internal state for generation and automation. By default, reveal only the current day, already visited places, total day count, and broad journey direction. Do not show future waypoint names, landmarks, or a full route table unless the user explicitly asks to see or export the full route.

For a durable trip, generate the current due day by default. Do not proactively offer to continue or generate all remaining days. If the user explicitly asks for a manual catch-up, preview, or bulk generation, it is allowed after route validation.

Bad examples:

- `local_activity`: `joining a local activity`
- `human_interaction`: `talking to a local vendor`

Good examples:

- `local_activity`: `tasting hand-pulled noodles at Lanzhou Zhengning Road Night Market`
- `human_interaction`: `asking a Lanzhou noodle stall owner near Zhengning Road how far the Yellow River crossing is`
