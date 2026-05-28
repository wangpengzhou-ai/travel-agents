# Environment Detection

`detect_environment.py` reports a best-effort capability snapshot.

Important distinction:

- CLI coding agent in the user's local logged-in desktop session can often detect screen size and set wallpaper.
- CLI coding agent over SSH, CI, sandbox, or headless runner usually cannot reliably set wallpaper or detect screens.
- GUI agent is not automatically sufficient; system permissions still matter.

Detection outputs:

- `native_image_tool_hint`: whether the surrounding agent likely has direct image generation. Scripts cannot inspect all agent tool inventories, so this can also be supplied by environment variable `TRAVEL4ME_NATIVE_IMAGE_TOOL=1`.
- `image_provider`: highest-priority API provider available by environment variables.
- `desktop_session`: whether DISPLAY/Wayland/macOS Aqua/Windows session hints exist.
- `screen`: result of best-effort screen detection.
- `wallpaper`: adapter availability.
- `automation`: available scheduler hints.

Image provider priority:

1. `gpt-image-2` with `OPENAI_API_KEY`.
2. Nano Banana 2 / Gemini image model with `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
3. Seedream latest configured model with `SEEDREAM_API_KEY` or `TRAVEL4ME_IMAGE_COMMAND`.

Do not ask for API keys if a native image tool is available and can satisfy the task. For exact-size image generation, check whether that tool exposes a size parameter; if not, generate at a close aspect ratio and resize locally.
