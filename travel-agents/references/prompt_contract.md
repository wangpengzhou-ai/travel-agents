# Prompt Contract

Prompt generation serves three goals:

1. Make the place recognizable.
2. Keep the same Agent identity.
3. Keep the Agent small, varied, and naturally participating in the environment.
4. Keep the upper-left place/date label consistent across days.

## Postcard Prompt Fields

Include these fields in order:

1. `style_bible`
2. `location_context`
3. `landmarks`
4. `landscape_type`
5. `local_visual_elements`
6. `weather_context`, when available, or `visual_weather` as non-live atmospheric mood
7. `agent_identity`
8. `local_activity`
9. `agent_activity`
10. `scene_social_mode`
11. `human_interaction`
12. `agent_composition_rule`
13. `upper_left_travel_label`
14. `postcard_layout`
15. `negative_constraints`

## Upper-left Travel Label

If `trip.label.enabled` is true, the image generation model should draw the place/date label inside the artwork. Local post-processing overlays are outside this workflow.

Rules:

- Put exactly one label in the upper-left safe area.
- Use exact text from `label_text`, with no paraphrase.
- Keep the same margin, scale, ink color, and lettering style across days.
- Make the label feel painted or printed into the postcard artwork.
- Do not place the label on any box, banner, placard, sticker, ribbon, background panel, underline, divider, or decorative title strip.
- Keep the label signature-sized, tucked into the extreme upper-left margin, roughly 2% of image height and no more than 15% of image width.
- Keep the label visually subtle and tiny, not a headline.
- Keep all other areas free of readable text.
- Match `assets/style_samples/upper-left-label-date-reference.png`: title-case place name, then a full written date, such as `Rome    May 28, 2026`.
- Do not use all-caps place names, slash separators, uppercase month abbreviations, or `DAY XX` labels.
- Prefer short label locations when the route location name is too long.
- Use the label-only reference for runtime image references; do not pass the full postcard sample only to control label lettering.
- Mentioning the label reference path in the prompt is not enough. When the image tool supports image/reference inputs, attach `assets/style_samples/upper-left-label-date-reference.png` as an actual input image; otherwise report that the run was prompt-only.

## Weather Context

For live daily generation, use the day's local weather when it is already available or user-provided. Weather should affect sky, light, water or ground texture, clothing details, and mood while staying integrated into the scene.

Weather is optional prompt context:

- Route planning may omit weather.
- Final postcards, host-native image generation, and importable daily scene images may omit weather.
- Do not silently substitute generic seasonal climate for current/local weather. If weather is unavailable, simply omit the weather line.
- When live/user-provided weather is unavailable, route planning may set `visual_weather` as a narrative atmosphere cue, such as mist, wind, drizzle, blue hour, or post-rain reflections. Label it as scene mood, not live weather data.

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

Vary the scene's social density. Use `scene_social_mode` to choose among:

- `solo`: the Agent is alone or only has distant/background people; use this for quiet rest, observation, play, weather-watching, sketching, or route pauses.
- `small_interaction`: the Agent has a specific, secondary interaction with a local role such as a vendor, guide, ferry worker, resident, craftsperson, host, caretaker, or fellow traveler.
- `crowd_context`: the Agent is part of broader public life, such as a market, queue, ferry, festival, commuters, visitors, or a group activity.

For routes of 4+ days, include at least one solo scene and at least one crowd-context scene. Keep direct small interactions to about 60% of days or less. Solo scenes should set `human_interaction` to `none` and include `no_human_interaction_reason`.

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
- Keep activities varied across eating, transport, resting, observing, playing, sheltering from weather, sketching, and route-checking scenes.
- Do not repeat the exact same `agent_activity` text across multiple days.
- Use maps or route cards sparingly, at most about 25% of days. Do not make map-checking the repeated visible action unless the user explicitly made the map the Agent's signature item.
- Quiet scenery-watching, resting, or playing can be a deliberate solo scene; keep it visually specific to the waypoint instead of generic staring.
- The Agent occupies less than 6% of image area.
- The Agent is off-center.
- The destination landscape and landmarks are the main subject.

Use this exact negative constraint block in generated prompts:

```text
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, large title text, oversized label text, boxed label, label background panel, banner, placard, ribbon, sticker, caption box, underline or divider around the label, readable text outside the exact upper-left travel label, logos, watermarks, wrong landmarks, generic tourist collage.
```

## Skeleton

```text
Create a 16:9 travel postcard in {style_name}.
Scene: Day {day}/{total}, {location}, {country_or_region}.
Main visual subject: {landscape_type} with {landmarks}.
Local visual elements: {local_visual_elements}.
Weather, when available: {weather_context}. Let the weather shape the sky, light, water or ground texture, clothing details, and mood.
Visual atmosphere, when live weather is unavailable: {visual_weather}. Treat this as scene mood, not live weather data.
Journey continuity: the same tiny agent traveler is passing through this place on the way from {origin} to {destination}.
Agent: {character_identity}. The agent is small, off-center, naturally participating in the local environment, occupying less than 6% of the image.
Local activity: {local_activity}.
Agent activity: {context-aware interaction}.
Social scene: {solo | small local interaction | broader crowd or group context}.
Human interaction: {human_interaction}.
Upper-left travel label: draw exactly one tiny hand-lettered postcard label in the upper-left corner. Exact text: "{label_text}". Use the label reference style: title-case place name and full written date, no all-caps text, no slash separator, no day number. Keep the same label position, margin, scale, ink color, and lettering style across every day. Make it feel painted or printed directly into the artwork, not like a digital overlay. Do not place the label on any box, banner, placard, sticker, ribbon, background panel, underline, divider, or decorative title strip. Keep it signature-sized: very small, quiet, tucked into the extreme upper-left margin, roughly 2% of image height and no more than 15% of image width. It must not read as a headline or title.
Composition: wide landscape postcard, destination and environment are the main subject, with the tiny Agent integrated naturally into the scene.
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, large title text, oversized label text, boxed label, label background panel, banner, placard, ribbon, sticker, caption box, underline or divider around the label, readable text outside the exact upper-left travel label, logos, watermarks, wrong landmarks, generic tourist collage.
```
