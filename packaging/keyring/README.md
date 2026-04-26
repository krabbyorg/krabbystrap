# Krabbystrap GPG Keyring

This directory contains the GPG public key used to sign Krabbystrap packages.

## Generate Key (One-time setup)

```bash
# Generate key
gpg --generate-key
# Name: Krabbystrap
# Email: noreply@github.com
# Comment: Krabbystrap Repository

# Get key ID
gpg --list-keys --keyid-format=long | grep Krabbystrap
# Copy the key ID (after 'rsa4096/')

# Export public key
gpg --export --armor <KEY_ID> > krabbystrap.gpg

# Export secret key (KEEP SAFE, add to GitHub Secrets)
gpg --export-secret-key --armor <KEY_ID> > krabbystrap-secret.gpg
```

## Sign Packages

```bash
# For .deb
dpkg-sig -k <KEY_ID> -s builder krabbystrap_*.deb

# For .tar.gz (Arch)
gpg --detach-sign --armor krabbystrap-*.tar.gz
```

## Verify

Users can verify package integrity:

```bash
# Debian
dpkg-sig --verify krabbystrap_*.deb

# Arch
pacman-key --verify krabbystrap-*.tar.gz.asc
```
