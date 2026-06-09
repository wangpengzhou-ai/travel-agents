# Prompt Contract

Prompt generation serves three goals:

1. Make the place recognizable.
2. Keep the same Agent identity.
3. Keep the Agent small, varied, and naturally participating in the environment.
4. Keep the upper-left place/date label consistent across days.

## Wallpaper Prompt Fields

Include these fields in order:

1. `style_bible`
2. `location_context`
3. `landmarks`
4. `landscape_type`
5. `local_visual_elements`
6. `weather_context`, when available
7. `agent_identity`
8. `local_activity`
9. `agent_activity`
10. `human_interaction`
11. `agent_composition_rule`
12. `upper_left_travel_label`
13. `wallpaper_layout`
14. `negative_constraints`

## Upper-left Travel Label

If `trip.label.enabled` is true, the image generation model should draw the place/date label inside the artwork. Local post-processing overlays are outside this workflow.

Rules:

- Put exactly one label in the upper-left safe area.
- Use exact text from `label_text`, with no paraphrase.
- Keep the same margin, scale, ink color, and lettering style across days.
- Make the label feel painted or printed into the postcard artwork.
- Keep all other areas free of readable text.
- Match `assets/style_samples/watercolor-postcard-rome.png`: title-case place name, then a full written date, such as `Rome    May 28, 2026`.
- Do not use all-caps place names, slash separators, uppercase month abbreviations, or `DAY XX` labels.
- Prefer short label locations when the route location name is too long.

## Weather Context

For live daily generation, use the day's local weather when it is already available or user-provided. Weather should affect sky, light, water or ground texture, clothing details, and mood while staying integrated into the scene.

Weather is optional prompt context:

- Route planning may omit weather.
- Final postcards, wallpapers, host-native image generation, and importable daily scene images may omit weather.
- Do not silently substitute generic seasonal climate for current/local weather. If weather is unavailable, simply omit the weather line.

## Character Identity Lock

Daily prompts must include the durable character description, fixed visual anchors, and consistency rules from `trip.character` or `character.json`. The model should vary only the Agent's tiny activity and placement, not the Agent's design.

Rules:

- Keep the same silhouette, body proportions, signature colors, accessories, material feel, and character type across days.
- Avoid age shifts, costume swaps, redesigns, and species/type changes.
- If `character_reference.png` exists and the provider or host agent supports image references, use it for every daily image.
- If the host agent lacks image-reference support, make the text identity lock explicit in the prompt.

## Local Activity and Human Interaction

Vary the Agent's placement instead of defaulting to the lower-left or lower-right corner. Choose one context-aware interaction from the day's local visual elements.

Each waypoint should plan a locally distinctive activity before prompt generation. Prefer activities that reveal local life, work, food, transport, craft, hospitality, worship, market routines, festivals, or route-specific travel rituals. The activity must already be written into route state and should name the place, region, landmark, festival, food, craft, transport line, or market context instead of saying only "local activity."

Human interaction is the default. At least 80% of days must show the Agent interacting with local people through the day's activity. Use specific local roles, such as a vendor, guide, ferry worker, resident, craftsperson, host, caretaker, or fellow traveler, and tie the interaction to the day's actual place, region, or landmark.

Up to 20% of days may skip human interaction if the place is genuinely sparse or remote and adding people would feel forced. Those waypoints must set `human_interaction` to `none` and include `no_human_interaction_reason`.

Examples of interaction sources:

- roof eave
- bridge
- station
- riverbank
- tea stall
- market
- boat
- mountain path
- bench
- balcony
- steps
- hot air balloon
- ferry
- awning
- map
- laptop
- camera
- local food
- local vendor
- guide
- ferry worker
- resident
- craftsperson

Rules:

- Use at most one small activity per image.
- Keep activities varied across eating, transport, resting, observing, and route-checking scenes.
- Allow quiet scenery-watching only as part of the 20% no-human-interaction exception, or as a background mood while the Agent still has a small human interaction.
- The Agent occupies less than 6% of image area.
- The Agent is off-center.
- The destination landscape and landmarks are the main subject.

Use this exact negative constraint block in generated prompts:

```text
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text outside the exact upper-left travel label, logos, watermarks, wrong landmarks, generic tourist collage.
```

## Skeleton

```text
Create a 16:9 travel wallpaper in {style_name}.
Scene: Day {day}/{total}, {location}, {country_or_region}.
Main visual subject: {landscape_type} with {landmarks}.
Local visual elements: {local_visual_elements}.
Weather, when available: {weather_context}. Let the weather shape the sky, light, water or ground texture, clothing details, and mood.
Journey continuity: the same tiny agent traveler is passing through this place on the way from {origin} to {destination}.
Agent: {character_identity}. The agent is small, off-center, naturally participating in the local environment, occupying less than 6% of the image.
Local activity: {local_activity}.
Agent activity: {context-aware interaction}.
Human interaction: {human_interaction}.
Upper-left travel label: draw exactly one small hand-lettered postcard label in the upper-left safe area. Exact text: "{label_text}". Use the sample style: title-case place name and full written date, no all-caps text, no slash separator, no day number. Keep the same label position, margin, scale, ink color, and lettering style across every day. Make it feel painted or printed into the artwork.
Composition: wide landscape wallpaper, destination and environment are the main subject, clear negative space for desktop icons.
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text outside the exact upper-left travel label, logos, watermarks, wrong landmarks, generic tourist collage.
```
