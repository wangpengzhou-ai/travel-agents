# Route Planning

Routes are narrative wallpaper routes for visual storytelling.

## Day Cap

Maximum journey length is 30 days. If a distance estimate exceeds 30 days, cap it at 30.

After estimating, confirm with the user:

```text
我算了一下，从 {origin} 到 {destination}，我大概需要 {days} 天能抵达。你想让我更快一点吗？如果想，告诉我你希望几天内到，我会换更快的交通工具。
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
- `human_interaction` with a concrete local role and the place, region, or landmark it belongs to
- `no_human_interaction_reason` when human interaction is skipped
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

Block live image generation when validation reports unresolved placeholders, generic local activity, generic human interaction, missing coordinates, missing landmarks, missing local activity, missing human interaction without a valid exception reason, more than 20% no-human-interaction days, too few natural/semi-natural days, or three consecutive city-only days. Dry-run prompt generation is still allowed for route debugging.

Before generating any final daily image prompt or asking a host-native image tool to generate, you may run the daily context gate for required label context:

```bash
python scripts/validate_route.py --trip-dir <trip_dir> --require-day-context <day>
```

Weather is optional nice-to-have context. If it is unavailable, continue without a weather line.

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
      + wallpaper_quality * 0.10
```

Rules:

1. Preserve origin and destination.
2. Prefer recognizable landmarks and distinctive landscapes.
3. Plan one locally distinctive activity for each waypoint before prompt generation. Write it directly into `local_activity`; do not leave it for prompt generation to invent later.
4. Include an interaction with local people on at least 80% of days. Write it directly into `human_interaction` with a concrete local role and the specific place, region, or landmark context.
5. If a sparse or remote day has no believable local human activity, mark `human_interaction` as `none` and write `no_human_interaction_reason`; these exceptions must stay at or below 20% of the route.
6. Avoid three consecutive city-only days.
7. For 15-24 day routes, include at least 7 natural or semi-natural days.
8. For 25-30 day routes, include at least 10 natural or semi-natural days.
9. Store coordinates for later website visualization.
10. If the user wants faster arrival, remove similar intermediate nodes and keep major geographic transitions.

Bad examples:

- `local_activity`: `joining a local activity`
- `human_interaction`: `talking to a local vendor`

Good examples:

- `local_activity`: `tasting hand-pulled noodles at Lanzhou Zhengning Road Night Market`
- `human_interaction`: `asking a Lanzhou noodle stall owner near Zhengning Road how far the Yellow River crossing is`
