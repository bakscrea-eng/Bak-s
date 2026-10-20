"""Bande-son de la pub (30 s, 48 kHz stéréo) : afro-beat 100 BPM, bruitages, voix off.

Tout est synthétisé ici avec numpy (aucun échantillon externe) ; les répliques
viennent de tools/voix_off.py. Sortie : audio/mix.wav
"""
import json, wave
import numpy as np
import soundfile as sf

SR = 48000
DUREE = 30.0
N = int(SR * DUREE)
BEAT = 60 / 100
T0 = 2.0                      # la musique démarre après l'intro (sifflet + rail)
rng = np.random.default_rng(7)

music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); vo = np.zeros(N)


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def add(bus, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    if bus.ndim == 1:
        bus[i:i + len(sig)] += sig
    else:
        bus[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2)
        bus[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2)


def env(n, a, d):
    """attaque linéaire, décroissance exponentielle (secondes)."""
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)




def lp_fft(x, fc, hp=0):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    if hp: X *= 1 / np.sqrt(1 + (hp / np.maximum(f, 1)) ** 4)
    return np.fft.irfft(X, len(x))


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def reverb(x, dur=1.2, mix=.2, seed=3):
    r = np.random.default_rng(seed); n = int(dur * SR)
    ir = r.standard_normal(n) * np.exp(-np.arange(n) / SR * 5 / dur)
    ir = lp_fft(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n; F = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[: len(x)]
    return x * (1 - mix) + y * mix * 1.5


def note(n):  # numéro MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)


# ---------------------------------------------------------------- instruments
def kick():
    t = t_(.4); f = 48 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .002, .16) * 1.0


def clap():
    n = noise(.25); e = env(len(n), .001, .06)
    for d in (.0, .011, .022): e += np.roll(env(len(n), .001, .012), int(d * SR)) * .6
    return lp_fft(n, 6000, 900) * e * .35


def shaker(acc):
    n = noise(.08); return lp_fft(n, 12000, 5000) * env(len(n), .006, .025) * (.16 if acc else .08)


def bell(f):
    t = t_(.3)
    return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.76 * t)) * env(len(t), .001, .06) * .16


def pluck(f, dur=.5, bright=.5):
    """corde pincée Karplus-Strong (guitare highlife)."""
    n = int(dur * SR); p = int(SR / f); buf = rng.uniform(-1, 1, p); out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]; j = (i + 1) % p
        buf[i % p] = .996 * ((1 - bright) * buf[i % p] + bright * buf[j])
    return out * env(n, .002, dur * .5) * .35


def bass(f, dur):
    t = t_(dur)
    s = np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * 2 * f * t) + .12 * np.sin(2 * np.pi * 3 * f * t)
    e = np.minimum(t / .008, 1) * np.exp(-t / (dur * .9)); e[-200:] *= np.linspace(1, 0, 200)
    return s * e * .42


def pad(freqs, dur):
    t = t_(dur); s = sum(np.sin(2 * np.pi * f * t + i) + .3 * np.sin(2 * np.pi * f * 2.003 * t) for i, f in enumerate(freqs))
    e = np.minimum(t / .4, 1) * np.minimum((dur - t) / .4, 1)
    return lp_fft(s, 1800) * e * .05


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

# ---------------------------------------------------------------- bruitages
def whistle(dur, gain=1.0):
    """sifflet de locomotive : accord de trois tuyaux + souffle."""
    t = t_(dur); vib = 1 + .004 * np.sin(2 * np.pi * 5.5 * t)
    s = sum(np.sin(2 * np.pi * f * vib * t) * a for f, a in ((466, 1), (587, .8), (698, .7), (932, .25)))
    s += lp_fft(noise(dur), 3000, 600) * .25
    e = np.minimum(t / .06, 1) * np.minimum((dur - t) / .25, 1)
    return reverb(s * e * .12 * gain, 1.8, .35)


def whoosh(dur, f0, f1, gain=.3):
    # bruit filtré par un passe-bas dont la coupure glisse de f0 à f1
    n = noise(dur); t = t_(dur); out = np.empty_like(n); s = 0.0
    a = np.exp(-2 * np.pi * f0 * (f1 / f0) ** (t / dur) / SR)
    for i in range(len(n)):
        s = (1 - a[i]) * n[i] + a[i] * s; out[i] = s
    out = out - np.convolve(out, np.ones(64) / 64, mode='same')
    return out * np.sin(np.pi * t / dur) ** 2 * gain * 3


def click():
    t = t_(.05); return (np.sin(2 * np.pi * 3200 * t) * env(len(t), .0005, .004) + noise(.05) * env(len(t), .0003, .002) * .5) * .5


def pop(f):
    t = t_(.25); fr = f * (1 + .5 * np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(len(t), .002, .07) * .28


def splash():
    n = noise(1.2); s = lp_fft(n, 3500, 200) * env(len(n), .005, .25) * .7
    for k in range(40):
        f = rng.uniform(900, 3000); tt = t_(.06); d = np.sin(2 * np.pi * np.cumsum(f * (1 + 2 * tt / .06)) / SR) * env(len(tt), .001, .015)
        s[int(rng.uniform(.02, .9) * SR):][:len(tt)] += d * .25
    return reverb(s, .9, .25)


def spray(dur):
    n = noise(dur); t = t_(dur); return lp_fft(n, 5000, 900) * np.minimum(t / .1, 1) * np.minimum((dur - t) / .3, 1) * .06


def clack():
    t = t_(.12); return (lp_fft(noise(.12), 1800, 120) * env(len(t), .001, .02) + np.sin(2 * np.pi * 90 * t) * env(len(t), .001, .03)) * .35


def rumble(dur):
    n = noise(dur); t = t_(dur); return lp_fft(n, 180) * np.minimum(t / .5, 1) * np.minimum((dur - t) / .5, 1) * .5


def crickets(dur):
    t = t_(dur); s = np.zeros_like(t)
    for f, r_ in ((4200, 7.1), (4600, 5.3)):
        s += np.sin(2 * np.pi * f * t) * (np.sin(2 * np.pi * 40 * t) > .3) * (np.sin(2 * np.pi * r_ * t / 7) > 0)
    return s * .012


def crowd(dur):
    n = noise(dur); t = t_(dur); return lp_fft(n, 2500, 300) * np.minimum(t / .2, 1) * np.minimum((dur - t) / .2, 1) * .25


def squeal(dur):
    t = t_(dur); f = 2900 + 120 * np.sin(2 * np.pi * 7 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(t / .1, 1) * np.minimum((dur - t) / .2, 1) * .03


def impact():
    t = t_(2.5); f = 40 + 60 * np.exp(-t * 12)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .002, .5)
    s += lp_fft(noise(2.5), 4000, 200) * env(len(t), .002, .3) * .3
    shim = sum(np.sin(2 * np.pi * f_ * t) for f_ in (1760, 2217, 2637)) * env(len(t), .05, .7) * .05
    return reverb(s * .6 + shim, 2.2, .3)


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
