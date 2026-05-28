# Prompt Contract

Prompt generation serves three goals:

1. Make the place recognizable.
2. Keep the same Agent identity.
3. Keep the Agent small, varied, and naturally participating in the environment.

## Wallpaper Prompt Fields

Include these fields in order:

1. `style_bible`
2. `location_context`
3. `landmarks`
4. `landscape_type`
5. `local_visual_elements`
6. `agent_identity`
7. `agent_activity`
8. `agent_composition_rule`
9. `wallpaper_layout`
10. `negative_constraints`

## Agent Activity

The Agent must not always stand in the lower-left or lower-right corner. Choose one context-aware interaction from the day's local visual elements.

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

Rules:

- Use at most one small activity per image.
- Do not make every day an eating scene or transport scene.
- Allow about 30-40% of days to be quiet scenery-watching days.
- The Agent occupies less than 6% of image area.
- The Agent is off-center.
- The destination landscape and landmarks are the main subject.

Use this exact negative constraint block in generated prompts:

```text
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text, logos, watermarks, wrong landmarks, generic tourist collage.
```

## Skeleton

```text
Create a 16:9 travel wallpaper in {style_name}.
Scene: Day {day}/{total}, {location}, {country_or_region}.
Main visual subject: {landscape_type} with {landmarks}.
Local visual elements: {local_visual_elements}.
Journey continuity: the same tiny agent traveler is passing through this place on the way from {origin} to {destination}.
Agent: {character_identity}. The agent is small, off-center, naturally participating in the local environment, occupying less than 6% of the image.
Agent activity: {context-aware interaction}.
Composition: wide landscape wallpaper, destination and environment are the main subject, clear negative space for desktop icons.
Avoid: centered agent, close-up agent, mascot poster, repeated lower-corner standing pose, extra animals, readable text, logos, watermarks, wrong landmarks, generic tourist collage.
```
