"""Bande-son de la pub (30 s, 48 kHz stéréo) : afro-beat 100 BPM, bruitages, voix off.

Tout est synthétisé ici avec numpy (aucun échantillon externe) ; les répliques
viennent de tools/voix_off.py. Sortie : audio/mix.wav
"""
import json
import numpy as np
import soundfile as sf

from synthe import *

DUREE = 30.0
N = int(SR * DUREE)
BEAT = 60 / 100
T0 = 2.0                      # la musique démarre après l'intro (sifflet + rail)

music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); vo = np.zeros(N)

# ---------------------------------------------------------------- musique
# Vamp à deux accords (Ré mineur 7 / Sol 7), classique en afro-beat.
CHORDS = [(50, [62, 65, 69, 72]), (55, [59, 62, 65, 67])]
bars = int((DUREE - T0) / (4 * BEAT)) + 1
for b in range(bars):
    t_bar = T0 + b * 4 * BEAT
    root, ch = CHORDS[b % 2]
    final = t_bar >= 27.3
    if t_bar > 27.4: break
    for s16 in range(16):
        t = t_bar + s16 * BEAT / 4
        if t >= 27.35: break
        if s16 in (0, 6, 8, 11): add(music, kick(), t, .9 if s16 in (0, 8) else .6)
        if s16 in (4, 12): add(music, clap(), t, 1, .1)
        add(music, shaker(s16 % 4 == 2), t, 1, .4)
        if s16 in (0, 3, 6, 10, 12): add(music, bell(1567 if s16 in (0, 10) else 1318), t, 1, -.35)
    # basse syncopée
    for pos, off, d in ((0, 0, .45), (3, 0, .2), (6, 7, .3), (8, 0, .4), (11, 12, .2), (14, 10, .3)):
        t = t_bar + pos * BEAT / 4
        if t < 27.35: add(music, bass(note(root - 12 + off), d), t)
    # guitare : arpèges en doubles-croches à partir de 5 s
    if t_bar >= 4.4:
        for s16 in range(16):
            t = t_bar + s16 * BEAT / 4
            if t >= 27.35: break
            if s16 % 2 == 0 or s16 in (3, 11):
                add(music, pluck(note(ch[(s16 * 3) % 4] + 12), .35), t, .7, .3 if s16 % 4 else -.2)
    add(music, pad([note(n) for n in ch], 4 * BEAT), t_bar, 1)

# accord final sur l'apparition du logo
fin = sum(pluck(note(n), 2.6) for n in (62, 69, 74, 77, 81))
add(music, fin, 27.35, .8); add(music, pad([note(n) for n in (62, 65, 69, 74)], 2.6), 27.35, 1.6)
add(music, kick(), 27.35, 1.2)


# intro : sifflet, puis le rail déchire l'écran
add(sfx, whistle(1.35), .03, 1.3)
add(sfx, whoosh(.95, 300, 6000, .45), .38)
for k in range(28):
    add(sfx, click() * .5, .45 + k * .03, rng.uniform(.2, .6), rng.uniform(-.6, .6))
# transitions entre les plans
for c in (2, 5, 8, 11, 14, 17, 22, 25):
    add(sfx, whoosh(.32, 800, 7000, .2), c - .16, 1, .2)
add(sfx, crickets(3.0), 2.0)                       # nuit, Awa
add(sfx, splash(), 5.53, 1.1); add(sfx, spray(2.4), 5.6)   # Modou
for i, tc in enumerate((14.6, 15.2, 15.8, 16.4)):  # clic ×4 + écrans qui s'allument
    add(sfx, click(), tc, 1.3, (-.4, .4, -.4, .4)[i]); add(sfx, pop(note(72 + (0, 4, 7, 12)[i])), tc + .01, 1, (-.4, .4, -.4, .4)[i])
# train qui roule sur la carte (clac-clac calés sur le tempo)
add(sfx, rumble(5.0), 17.0, .9)
t = 17.0
while t < 21.9:
    add(sfx, clack(), t, .9, -.2); add(sfx, clack(), t + .13, .7, .2); t += BEAT
add(sfx, crowd(.75), 23.5, 1.2)                     # concert
# arrivée en gare : ralentissement, freins, sifflet, impact du logo
add(sfx, rumble(2.4), 25.0, .9); add(sfx, whistle(.6, .7), 25.05, .8)
t, gap = 25.0, .3
while t < 26.7:
    add(sfx, clack(), t, .9); add(sfx, clack(), t + .12, .7); t += gap; gap *= 1.25
add(sfx, squeal(.8), 26.0, 1)
add(sfx, whoosh(.6, 400, 5000, .3), 26.75)
add(sfx, impact(), 27.33, 1.1)

# ---------------------------------------------------------------- voix off
durees = json.load(open('audio/durees_vo.json'))
PLACEMENT = {'vo01': .55, 'vo02': 2.45, 'vo03': 5.9, 'vo04': 8.45, 'vo05': 11.55, 'vo06': 14.1,
             'vo07': 17.35, 'vo08': 22.15, 'vo09': 27.0}
for nom, at in PLACEMENT.items():
    x, sr = sf.read(f'audio/{nom}.wav')
    x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)   # 24 -> 48 kHz
    x = x / (np.max(np.abs(x)) + 1e-9) * .9
    add(vo, x, at)
vo = reverb(vo, .5, .08, seed=9)

# ducking : la musique baisse sous la voix
lvl = np.convolve(np.abs(vo), np.ones(2400) / 2400, mode='same')
duck = 1 - .5 * np.clip(lvl / .05, 0, 1)
duck = np.convolve(duck, np.ones(4800) / 4800, mode='same')

music = np.stack([reverb(music[:, 0], 1.0, .12, 1), reverb(music[:, 1], 1.0, .12, 2)], 1)
mix = music * .55 * duck[:, None] + sfx * .9 + vo[:, None] * 1.0
# fondu de fin
fade = np.ones(N); fade[-int(.6 * SR):] = np.linspace(1, 0, int(.6 * SR)) ** 2
mix *= fade[:, None]
# limiteur doux
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix *= .95 / np.max(np.abs(mix))
sf.write('audio/mix.wav', mix.astype(np.float32), SR, subtype='PCM_16')
print('audio/mix.wav', mix.shape[0] / SR, 's')
