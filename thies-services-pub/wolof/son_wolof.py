"""Bande-son de la pub wolof (30 s) et minutage des écrans sur la voix off.

    python3 wolof/son_wolof.py [voix_off.mp3|wav]      (depuis thies-services-pub/)

Avec une voix off : repère les 6 pauses entre les 7 répliques, écrit
wolof/timing.json (lu par wolof/index.html) et mixe la voix. Sans voix off :
minutage par défaut, musique et bruitages seuls (aperçu).
Sortie : wolof/audio/mix_wolof.wav
"""
import json, os, subprocess, sys, tempfile
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from synthe import *  # noqa: E402,F401

ICI = os.path.dirname(os.path.abspath(__file__))
DUREE = 30.0
N = int(SR * DUREE)
BEAT = 60 / 100
DEBUT_VO = .45
T = [0.5, 2.5, 8.5, 12.5, 17.3, 21.5, 25.7]          # minutage par défaut (= index.html)


def lire_vo(chemin):
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, 'vo.wav')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', chemin, '-ac', '1', '-ar', str(SR), wav], check=True)
        x, _ = sf.read(wav)
    return x / (np.max(np.abs(x)) + 1e-9) * .9


def debuts_repliques(x, n=7):
    """début de chaque réplique : on coupe aux n-1 silences les plus longs."""
    hop = int(.01 * SR)
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    parle = e > max(.02, .08 * np.percentile(e, 95))
    idx = np.flatnonzero(parle); d0, d1 = idx[0], idx[-1]
    trous, i = [], d0
    while i < d1:
        if not parle[i]:
            j = i
            while j < d1 and not parle[j]: j += 1
            trous.append((j - i, j)); i = j
        else: i += 1
    coupes = sorted(j for _, j in sorted(trous, reverse=True)[:n - 1])
    return [round(d0 * .01, 2)] + [round(c * .01, 2) for c in coupes]


vo = np.zeros(N)
src = sys.argv[1] if len(sys.argv) > 1 else None
if src:
    x = lire_vo(src)
    if len(x) / SR > DUREE - DEBUT_VO - 2.2:          # garde 2 s de logo à la fin
        k = (len(x) / SR) / (DUREE - DEBUT_VO - 2.2)
        x = np.interp(np.arange(0, len(x), k), np.arange(len(x)), x)
    T = [round(DEBUT_VO + d, 2) for d in debuts_repliques(x)]
    add(vo, x, DEBUT_VO)
    json.dump({'debuts': T, 'source': os.path.basename(src)}, open(os.path.join(ICI, 'timing.json'), 'w'), indent=1)
    print('répliques à', T)

music = np.zeros((N, 2)); sfx = np.zeros((N, 2))
FIN = T[6] - .3                                       # le logo final arrive ici
CHORDS = [(50, [62, 65, 69, 72]), (55, [59, 62, 65, 67])]
t_bar, b = 0.0, 0
while t_bar < FIN:
    root, ch = CHORDS[b % 2]
    for s16 in range(16):
        t = t_bar + s16 * BEAT / 4
        if t >= FIN: break
        if t_bar >= 1.2:                              # la rythmique entre après le logo d'intro
            if s16 in (0, 6, 8, 11): add(music, kick(), t, .9 if s16 in (0, 8) else .6)
            if s16 in (4, 12): add(music, clap(), t, 1, .1)
            add(music, shaker(s16 % 4 == 2), t, 1, .4)
            if s16 in (0, 3, 6, 10, 12): add(music, bell(1567 if s16 in (0, 10) else 1318), t, 1, -.35)
        if (s16 % 2 == 0 or s16 in (3, 11)) and t_bar >= 2.4:
            add(music, pluck(note(ch[(s16 * 3) % 4] + 12), .35), t, .7, .3 if s16 % 4 else -.2)
    for pos, off, d in ((0, 0, .45), (3, 0, .2), (6, 7, .3), (8, 0, .4), (11, 12, .2), (14, 10, .3)):
        t = t_bar + pos * BEAT / 4
        if t < FIN and t_bar >= 1.2: add(music, bass(note(root - 12 + off), d), t)
    add(music, pad([note(n) for n in ch], 4 * BEAT), t_bar, 1)
    t_bar += 4 * BEAT; b += 1
fin = sum(pluck(note(n), 2.6) for n in (62, 69, 74, 77, 81))
add(music, fin, FIN + .5, .8); add(music, pad([note(n) for n in (62, 65, 69, 74)], 30 - FIN), FIN + .5, 1.6)

# bruitages calés sur index.html : pop du logo, téléphone, écrans qui glissent, taps
add(sfx, pop(note(79)), .1, 1.2)
add(sfx, whoosh(.6, 300, 5000, .3), T[1] - .9)
for at in (T[1] - .45, T[2] - .4, T[2] + 1.9, T[3] + 1.75, T[4] - .4, T[5] - .4):
    add(sfx, whoosh(.3, 900, 7000, .18), at, 1, .25)
for at in (T[1] + 1.05, T[2] + .75, T[2] + 2.85, T[3] + .75, T[3] + 3.95, T[4] + 2.05, T[5] + .95):
    add(sfx, click(), at, 1.3); add(sfx, pop(note(84)), at + .01, .6)
add(sfx, whoosh(.6, 5000, 400, .3), FIN - .1)
add(sfx, impact(), FIN + .5, .9)

vo = reverb(vo, .4, .06, seed=9)
lvl = np.convolve(np.abs(vo), np.ones(2400) / 2400, mode='same')
duck = np.convolve(1 - .55 * np.clip(lvl / .05, 0, 1), np.ones(4800) / 4800, mode='same')
music = np.stack([reverb(music[:, 0], 1.0, .12, 1), reverb(music[:, 1], 1.0, .12, 2)], 1)
mix = music * .5 * duck[:, None] + sfx * .9 + vo[:, None]
fade = np.ones(N); fade[-int(.6 * SR):] = np.linspace(1, 0, int(.6 * SR)) ** 2
mix *= fade[:, None]
mix = np.tanh(mix * 1.1) / np.tanh(1.1); mix *= .95 / np.max(np.abs(mix))
os.makedirs(os.path.join(ICI, 'audio'), exist_ok=True)
sf.write(os.path.join(ICI, 'audio', 'mix_wolof.wav'), mix.astype(np.float32), SR, subtype='PCM_16')
print('wolof/audio/mix_wolof.wav', 'avec voix off' if src else 'sans voix off (aperçu)')
