#!/bin/sh
flatpak-builder --force-clean --user --install-deps-from=flathub --repo=repo --install builddir io.github.jasonritchie06.mp3shuffler.yaml
