"""Synthèse sonore partagée par les pubs : instruments afro-beat et bruitages (numpy seul)."""
import numpy as np

SR = 48000
rng = np.random.default_rng(7)

def t_(dur):
    return np.arange(int(dur * SR)) / SR




def add(bus, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); n = len(bus)
    if i >= n: return
    sig = sig[: n - i] * gain
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
