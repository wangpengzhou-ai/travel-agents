# Environment Detection

`detect_environment.py` reports a best-effort capability snapshot.

Important distinction:

- Host coding agents may expose native tools outside local Python's visibility, such as image generation, weather/search, reminders, or browser automation.
- CLI coding agent in the user's local logged-in desktop session can often detect screen size and set wallpaper.
- CLI coding agent over SSH, CI, sandbox, or headless runner usually has limited wallpaper and screen-detection access.
- GUI agent access still depends on system permissions.

Detection outputs:

- `native_image_tool_hint`: whether the surrounding agent likely has direct image generation. The value can also be supplied by environment variable `TRAVEL4ME_NATIVE_IMAGE_TOOL=1`. This is only a local hint; Python cannot inspect the active host agent's tool list.
- `provider.available_api_providers`: API providers available by environment variables.
- `provider.selected_api_provider`: highest-priority available local API provider, when one exists.
- `desktop_session`: whether DISPLAY/Wayland/macOS Aqua/Windows session hints exist.
- `screen`: result of best-effort screen detection.
- `wallpaper`: adapter availability.
- `automation`: available scheduler hints.

Local API provider priority:

1. `gpt-image-2` with `OPENAI_API_KEY`.
2. Nano Banana 2 / Gemini image model with `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
3. Seedream latest configured model with `SEEDREAM_API_KEY` or `TRAVEL4ME_IMAGE_COMMAND`.

When a native host image tool can satisfy the task, use it before requesting local API-provider setup, even if `native_image_tool_hint` is false. For exact-size image generation, check whether that tool exposes a size parameter; if not, generate at a close aspect ratio and resize locally. After host-native generation, use `scripts/import_generated_image.py` only when the tool reports a saved local image path. If the tool only displays an image without a local path, stop after reporting the generated image; do not poll or reason indefinitely waiting for an importable file.
