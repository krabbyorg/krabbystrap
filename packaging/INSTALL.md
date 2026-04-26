# Packaging

## AUR (Arch Linux)

Submit `PKGBUILD` to https://aur.archlinux.org/account/

```bash
yay -S krabbystrap
```

## Debian / Ubuntu

Downloads built .deb from GitHub releases:

```bash
sudo apt install ./krabbystrap_*.deb
```

## Build locally

### Debian .deb

```bash
fpm -s dir -t deb \
  -n krabbystrap \
  -v 1.0.0 \
  --depends "python3 (>= 3.11)" \
  --depends "python3-venv" \
  --depends "flatpak" \
  --prefix /usr/lib/krabbystrap \
  src templates assets requirements.txt

# Then add launcher + desktop manually or use packaging/build-deb.sh
```

### Manual install

```bash
git clone https://github.com/krabbyorg/krabbystrap
cd krabbystrap
./install.sh
```
