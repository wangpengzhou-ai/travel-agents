# Postcard Style

Use `watercolor_postcard` for every journey.

Style contract:

- Refined watercolor travel postcard.
- Ink-and-wash architecture or landscape.
- Visible paper grain and airy brush edges.
- Elegant travel sketchbook feeling.
- One readable text element only: the model-drawn upper-left place/date label.

Sample:

- `assets/style_samples/watercolor-postcard-rome.png`
- Runtime label reference: `assets/style_samples/upper-left-label-date-reference.png`

The repository-root `style-samples/` folder is legacy exploration material, not the runtime style source.

## Label Treatment

The upper-left place/date label is part of the generated image. Keep the same placement, margin, ink color, scale, and lettering style across daily images. Forbid readable text outside that exact label.

Match `assets/style_samples/upper-left-label-date-reference.png`:

- Format: `Rome    May 28, 2026`.
- Use title-case place names, not all caps.
- Use full written dates with month name, day, comma, and year.
- Do not use slash separators, uppercase month abbreviations, or `DAY XX`.

Use the label-only reference for runtime image references. Do not pass the full postcard sample merely to control label lettering, because the full scene can bleed its style, subject, and composition into later generations.
