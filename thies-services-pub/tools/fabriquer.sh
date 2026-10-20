#!/usr/bin/env bash
# Chaîne complète : voix off -> bande-son -> rendu 3D image par image -> MP4 final.
# Prérequis : node, ffmpeg, python3 (numpy, soundfile, kokoro-onnx), Chromium Playwright.
#   ./tools/fabriquer.sh <dossier_modeles_kokoro>
set -euo pipefail
cd "$(dirname "$0")/.."
MODELES="${1:?dossier contenant kokoro.onnx et voices.bin}"
npm install --no-audit --no-fund
python3 tools/voix_off.py "$MODELES"
python3 tools/son.py
python3 -m http.server 8123 >/dev/null 2>&1 & SERVEUR=$!
trap 'kill $SERVEUR' EXIT
sleep 1
mkdir -p segments
PIDS=()
for i in 0 1 2; do node tools/rendu.mjs video $((i*300)) $(((i+1)*300)) segments/seg$i.mp4 & PIDS+=($!); done
for p in "${PIDS[@]}"; do wait "$p"; done
printf "file 'seg0.mp4'\nfile 'seg1.mp4'\nfile 'seg2.mp4'\n" > segments/liste.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i segments/liste.txt -i audio/mix.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart thies-services-30s-9x16.mp4
echo "OK : thies-services-30s-9x16.mp4"
