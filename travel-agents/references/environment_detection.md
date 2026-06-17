# Environment Detection

`detect_environment.py` reports a best-effort capability snapshot.

Important distinction:

- Host coding agents may expose native tools outside local Python's visibility, such as image generation, weather/search, reminders, or browser automation.
- Host coding agents may also expose automation tools outside local Python's visibility. Python cannot prove or create those automations; the agent must inspect its current tool list and call the real host automation tool when available.

Detection outputs:

- `native_image_tool_hint`: whether the surrounding agent likely has direct image generation. The value can also be supplied by environment variable `TRAVEL_AGENTS_NATIVE_IMAGE_TOOL=1`. This is only a local hint; Python cannot inspect the active host agent's tool list.
- `host_native_strategy`: what to do when the host may have native image tools. Python cannot prove this capability; the host agent should attempt the first real required image generation and treat that tool call as the probe.
- `provider.available_api_providers`: API providers available by environment variables.
- `provider.selected_api_provider`: highest-priority available local API provider, when one exists.
- `desktop_session`: whether DISPLAY/Wayland/macOS Aqua/Windows session hints exist.
- `automation`: available scheduler hints plus a reminder that host-platform automation must be checked by the coding agent.

Local API provider priority:

1. `gpt-image-2` with `OPENAI_API_KEY`.
2. Nano Banana 2 / Gemini image model with `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
3. Seedream latest configured model with `SEEDREAM_API_KEY` or `TRAVEL_AGENTS_IMAGE_COMMAND`.

When a native host image tool can satisfy the task, use it before requesting local API-provider setup, even if `native_image_tool_hint` is false. Prove the capability with the first real image the workflow already needs: the character reference, a requested postcard, or the current day's scene. Do not create a throwaway test image when an actual required image can serve as the probe. For exact-size image generation, check whether that tool exposes a size parameter. After host-native generation, use `scripts/import_generated_image.py` only when the tool reports a saved local image path. If the tool only displays an image without a local path, stop after reporting the generated image; do not poll or reason indefinitely waiting for an importable file.

If the current host has no native image-generation tool and `provider.selected_api_provider` is null, block setup immediately. Ask the user to provide a host image tool, an API key/provider, or `TRAVEL_AGENTS_IMAGE_COMMAND`. Do not initialize the trip, plan the route, or create prompt-only daily artifacts first.

When automation is available for a durable trip, create it by default. Ask only when the platform or operating system requires approval to install or enable the automation.

Host-platform automation is the required path when daily postcards depend on host-native image generation. In Codex, create it with the `automation_update` tool and verify the returned automation id/status before reporting success. OS schedulers are only valid when the local scripts can complete image generation without the host agent through a configured API provider or `TRAVEL_AGENTS_IMAGE_COMMAND`.
