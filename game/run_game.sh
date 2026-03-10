#!/usr/bin/env bash
set -e

# 1. DB im Hintergrund starten
docker compose up -d db

# 2. Spiel interaktiv starten
docker compose run --rm roulette

# 3. Danach alles wieder runterfahren
docker compose down