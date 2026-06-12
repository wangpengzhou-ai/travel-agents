# Wallpaper Platforms

Wallpaper setting is best-effort and requires a local desktop session.

## macOS

Current implementation uses AppleScript through `osascript`.

AppleScript may require user approval in Privacy & Security for controlling other apps.

## Windows

Use Win32 `SystemParametersInfoW` with `SPI_SETDESKWALLPAPER`. Must run in the user's desktop session.

## GNOME

Use:

```bash
gsettings set org.gnome.desktop.background picture-uri file:///path/to/image.png
gsettings set org.gnome.desktop.background picture-uri-dark file:///path/to/image.png
```

Other Linux desktops need separate adapters.
