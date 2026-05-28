#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class ImageProviderError(RuntimeError):
    pass


def selected_provider() -> str | None:
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("SEEDREAM_API_KEY") or os.environ.get("TRAVEL4ME_IMAGE_COMMAND"):
        return "seedream"
    return None


def generate_image(prompt: str, out_path: Path, size: str = "2560x1440", provider: str | None = None, reference_image: Path | None = None) -> dict[str, Any]:
    provider = provider or selected_provider()
    if provider == "openai":
        return generate_openai(prompt, out_path, size)
    if provider == "gemini":
        return generate_gemini(prompt, out_path, size)
    if provider == "seedream":
        return generate_seedream(prompt, out_path, size, reference_image)
    raise ImageProviderError(
        "No image provider is configured. Set OPENAI_API_KEY, GOOGLE_API_KEY/GEMINI_API_KEY, "
        "SEEDREAM_API_KEY, or TRAVEL4ME_IMAGE_COMMAND; or use the surrounding agent's native image tool."
    )


def _write_b64_png(out_path: Path, data: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(data))


def _http_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 180) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ImageProviderError(f"HTTP {exc.code} from {url}: {detail}") from exc


def generate_openai(prompt: str, out_path: Path, size: str) -> dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ImageProviderError("OPENAI_API_KEY is not set")
    model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": os.environ.get("OPENAI_IMAGE_QUALITY", "high"),
        "output_format": "png",
    }
    response = _http_json(
        "https://api.openai.com/v1/images/generations",
        payload,
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    data = response.get("data", [])
    if not data:
        raise ImageProviderError(f"OpenAI response had no image data: {response}")
    first = data[0]
    if first.get("b64_json"):
        _write_b64_png(out_path, first["b64_json"])
    elif first.get("url"):
        with urllib.request.urlopen(first["url"], timeout=180) as img:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(img.read())
    else:
        raise ImageProviderError(f"OpenAI response had no b64_json or url: {first}")
    return {"provider": "openai", "model": model, "response": {"has_revised_prompt": "revised_prompt" in first}}


def generate_gemini(prompt: str, out_path: Path, size: str) -> dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ImageProviderError("GEMINI_API_KEY or GOOGLE_API_KEY is not set")
    model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")
    payload = {
        "contents": [{"parts": [{"text": f"{prompt}\n\nOutput an image at {size} aspect/quality when supported."}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    response = _http_json(url, payload, {"Content-Type": "application/json"})
    try:
        parts = response["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError) as exc:
        raise ImageProviderError(f"Gemini response had no candidates/content parts: {response}") from exc
    for part in parts:
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            _write_b64_png(out_path, inline["data"])
            return {"provider": "gemini", "model": model}
    raise ImageProviderError(f"Gemini response had no inline image data: {response}")


def generate_seedream(prompt: str, out_path: Path, size: str, reference_image: Path | None = None) -> dict[str, Any]:
    command = os.environ.get("TRAVEL4ME_IMAGE_COMMAND")
    if not command:
        raise ImageProviderError(
            "Seedream direct API wiring is deployment-specific. Set TRAVEL4ME_IMAGE_COMMAND to a command "
            "that reads JSON from stdin and writes the image to the provided output path."
        )
    payload = {
        "provider": "seedream",
        "model": os.environ.get("SEEDREAM_MODEL", "latest"),
        "prompt": prompt,
        "size": size,
        "output_path": str(out_path),
        "reference_image": str(reference_image) if reference_image else None,
    }
    result = subprocess.run(command, input=json.dumps(payload), text=True, shell=True, capture_output=True, timeout=300, check=False)
    if result.returncode != 0:
        raise ImageProviderError(f"TRAVEL4ME_IMAGE_COMMAND failed: {result.stderr or result.stdout}")
    if not out_path.exists():
        raise ImageProviderError(f"TRAVEL4ME_IMAGE_COMMAND did not create {out_path}")
    return {"provider": "seedream", "model": payload["model"], "command_stdout": result.stdout.strip()}
