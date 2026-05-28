# Route Planning

Routes are narrative wallpaper routes, not travel advice.

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
- `agent_activity`
- `agent_position`
- `prompt_focus`
- `is_natural_or_semi_natural`

Persist both:

- `trip.json`
- `route.geojson`

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
3. Avoid three consecutive city-only days.
4. For 15-24 day routes, include at least 7 natural or semi-natural days.
5. For 25-30 day routes, include at least 10 natural or semi-natural days.
6. Store coordinates for later website visualization.
7. If the user wants faster arrival, remove similar intermediate nodes and keep major geographic transitions.
