# Krabbystrap

A [Bloxstrap](https://github.com/bloxstraplabs/bloxstrap) / [Fishstrap](https://github.com/fishstrap/fishstrap)-inspired launcher for **Roblox on Linux** via [Sober](https://sober.vinegarhq.org/).

![license](https://img.shields.io/badge/license-GPL--3.0-yellow) ![platform](https://img.shields.io/badge/platform-Linux-lightgrey)

---

## Features

- Home launcher — choose **Launch** or **Settings** on startup
- Launch progress splash with real Sober process detection
- Fluent-design settings UI (dark theme, yellow accent)
- Edit **Fast Flags** directly from the UI
- Toggle Discord Rich Presence, GameMode, HiDPI, OpenGL, and more
- **Browse Mods** — install, apply, and remove mods & themes from the Lution Marketplace
- Fast Flag presets from the marketplace, applied with one click
- Thumbnail image cache (no repeated downloads)
- Reads & writes Sober's `config.json` natively

## Requirements

- [Sober](https://sober.vinegarhq.org/) installed as a Flatpak (`org.vinegarhq.Sober`)
- Python 3.11+
- `python3-venv`
- `flatpak`

## Install

```bash
git clone https://github.com/krabbyorg/krabbystrap
cd krabbystrap
./install.sh
```

`install.sh` will:
- Check Python and Flatpak are present
- Create a `.venv` and install dependencies
- Add a `krabbystrap.desktop` entry to your app launcher

## Usage

```bash
./krabbystrap.sh            # home screen (launch or open settings)
./krabbystrap.sh --settings # open settings directly
```

## Data locations

| Path | Purpose |
|------|---------|
| `~/.var/app/org.vinegarhq.Sober/config/sober/config.json` | Sober config (read/write) |
| `~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay/` | Active mod/theme overlay |
| `~/Documents/Krabbystrap/Marketplace/` | Downloaded mods & themes |
| `~/Documents/Krabbystrap/installed.json` | Installed items index |
| `~/Documents/Krabbystrap/img_cache/` | Cached marketplace thumbnails |

## Project structure

```
krabbystrap.sh        entry point
install.sh            installer (venv + desktop entry)
src/
  launch.py           Qt home dialog, launch splash, settings window
  server.py           Flask backend (API + marketplace)
templates/
  index.html          settings UI (HTML/CSS/JS)
assets/
  krabby.svg          app icon (source)
  krabby.png          app icon (rasterised)
requirements.txt
```

## License

GPL-3.0 — see [LICENSE](LICENSE).
