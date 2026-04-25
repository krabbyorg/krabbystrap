# Krabbystrap

A [Bloxstrap](https://github.com/bloxstraplabs/bloxstrap) / [Fishstrap](https://github.com/fishstrap/fishstrap)-inspired launcher for **Roblox on Linux** via [Sober](https://sober.vinegarhq.org/).

![license](https://img.shields.io/badge/license-GPL--3.0-yellow) ![platform](https://img.shields.io/badge/platform-Linux-lightgrey)

---

## Features

- Home launcher — choose **Launch** or **Settings** on startup
- Fluent-design settings UI (dark theme, Fishstrap-style)
- Edit **Fast Flags** directly from the UI
- Toggle Discord Rich Presence, GameMode, HiDPI, OpenGL, and more
- Reads & writes Sober's `config.json` natively

## Requirements

- **Sober** installed as a Flatpak (`org.vinegarhq.Sober`)
- Python 3.11+
- `python3-venv`

## Install

```bash
git clone https://github.com/you/krabbystrap
cd krabbystrap
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
chmod +x krabbystrap.sh
```

### Optional: add to app launcher

```bash
cp krabbystrap.desktop.example ~/.local/share/applications/krabbystrap.desktop
# edit the Exec path inside the file to match your clone location
update-desktop-database ~/.local/share/applications/
```

## Usage

```bash
./krabbystrap.sh            # home screen (launch or settings)
./krabbystrap.sh --settings # open settings directly
```

## Config location

Sober's config is stored at:

```
~/.var/app/org.vinegarhq.Sober/config/sober/config.json
```

Krabbystrap reads and writes this file directly.

## Project structure

```
krabbystrap.sh      entry point
launch.py           Qt home dialog + settings window shell
server.py           Flask backend (config API)
templates/
  index.html        settings UI (HTML/CSS/JS)
assets/
  krabby.svg        app icon (source)
  krabby.png        app icon (rasterised)
requirements.txt
```

## License

GPL-3.0 — see [LICENSE](LICENSE).
