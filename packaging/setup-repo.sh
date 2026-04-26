#!/bin/bash
set -e

REPO_URL="https://github.com/krabbyorg/krabbystrap"
KEY_URL="https://raw.githubusercontent.com/krabbyorg/krabbystrap/main/packaging/keyring/krabbystrap.gpg"

echo "Setting up Krabbystrap repository..."

if [ "$(uname)" = "Linux" ]; then
    if command -v pacman &>/dev/null; then
        echo "→ Detected Arch Linux"

        sudo mkdir -p /etc/pacman.d/keyrings
        echo "→ Downloading GPG key..."
        sudo curl -fsSL "$KEY_URL" -o /etc/pacman.d/keyrings/krabbystrap.gpg

        echo "→ Adding key to pacman..."
        sudo pacman-key --add /etc/pacman.d/keyrings/krabbystrap.gpg
        sudo pacman-key --lsign-key krabbystrap

        echo "→ Adding repository to pacman.conf..."
        echo "" | sudo tee -a /etc/pacman.conf > /dev/null
        cat | sudo tee -a /etc/pacman.conf > /dev/null <<EOF
[krabbystrap]
Server = $REPO_URL/releases/download/repo/arch
SigLevel = Required
EOF

        echo ""
        echo "✓ Repository added! Now run:"
        echo "  sudo pacman -Sy krabbystrap"

    elif command -v apt &>/dev/null; then
        echo "→ Detected Debian/Ubuntu"

        sudo mkdir -p /etc/apt/keyrings
        echo "→ Downloading GPG key..."
        sudo curl -fsSL "$KEY_URL" | sudo gpg --dearmor --yes -o /etc/apt/keyrings/krabbystrap-repo-key.gpg

        echo "→ Adding repository to sources.list.d..."
        cat | sudo tee /etc/apt/sources.list.d/krabbystrap.sources > /dev/null <<EOF
Types: deb
URIs: $REPO_URL/releases/download/repo/debian
Suites: stable
Components: main
Signed-By: /etc/apt/keyrings/krabbystrap-repo-key.gpg
EOF

        sudo apt update

        echo ""
        echo "✓ Repository added! Now run:"
        echo "  sudo apt install krabbystrap"

    else
        echo "✗ Unsupported distro. Install manually:"
        echo "  git clone $REPO_URL && cd krabbystrap && ./install.sh"
        exit 1
    fi
else
    echo "✗ This script only works on Linux"
    exit 1
fi
