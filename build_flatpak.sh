#!/bin/sh
#flatpak-builder --force-clean --user --install-deps-from=flathub --repo=repo --mirror-screenshots-url=URL builddir io.github.jasonritchie06.mp3shuffler.yaml
flatpak run org.flatpak.Builder --force-clean --sandbox --user --install --install-deps-from=flathub --ccache --mirror-screenshots-url=https://dl.flathub.org/media/ --repo=repo builddir io.github.jasonritchie06.mp3shuffler.yaml
