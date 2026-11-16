#!/usr/bin/env bash
# Pub wolof : minutage + son, rendu image par image, MP4 final.
#   ./wolof/fabriquer.sh [voix_off.mp3]     (sans argument : aperçu sans voix)
set -euo pipefail
cd "$(dirname "$0")/.."
python3 wolof/son_wolof.py "$@"
python3 -m http.server 8123 >/dev/null 2>&1 & SERVEUR=$!
trap 'kill $SERVEUR' EXIT
sleep 1
mkdir -p segments
PIDS=()
for i in 0 1 2; do PAGE=wolof/index.html node tools/rendu.mjs video $((i*300)) $(((i+1)*300)) segments/w$i.mp4 & PIDS+=($!); done
for p in "${PIDS[@]}"; do wait "$p"; done
printf "file 'w0.mp4'\nfile 'w1.mp4'\nfile 'w2.mp4'\n" > segments/liste_w.txt
SORTIE=wolof/thies-services-wolof-30s-9x16.mp4
[ $# -eq 0 ] && SORTIE=wolof/thies-services-wolof-30s-9x16-apercu-sans-voix.mp4
ffmpeg -y -loglevel error -f concat -safe 0 -i segments/liste_w.txt -i wolof/audio/mix_wolof.wav \
  -map 0:v -map 1:a -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$SORTIE"
echo "OK : $SORTIE"
