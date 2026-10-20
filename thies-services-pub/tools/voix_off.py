"""Génère les répliques de la voix off (français, hors ligne, Kokoro TTS)."""
import json, sys, soundfile as sf
from kokoro_onnx import Kokoro

MODELS = sys.argv[1]  # dossier contenant kokoro.onnx et voices.bin
LIGNES = [
    ("vo01", "Thiès… tu cherches quoi ?", 1.0),
    ("vo02", "La pharmacie de garde… elle est où ?", 1.05),
    ("vo03", "Un plombier, vite !", 1.1),
    ("vo04", "Il se passe quoi, ce soir ?", 1.05),
    ("vo05", "Et mes clients, alors ?", 1.0),
    ("vo06", "Ouvre Thiès Services.", 1.0),
    ("vo07", "Une seule ligne relie tout Thiès : pharmacies, artisans, événements… et ton service.", 1.12),
    ("vo08", "Tout ce qu'il y a à Thiès, c'est ici.", 1.05),
    ("vo09", "Thiès Services. Tout Thiès, sur une seule ligne.", 0.95),
]
k = Kokoro(f"{MODELS}/kokoro.onnx", f"{MODELS}/voices.bin")
durees = {}
for nom, texte, vitesse in LIGNES:
    # « Thiès » se prononce /tjɛs/ ; sans cette graphie, le phonétiseur lit « thighs ».
    s, sr = k.create(texte.replace("Thiès", "Tièss"), voice="ff_siwis", speed=vitesse, lang="fr-fr")
    sf.write(f"audio/{nom}.wav", s, sr)
    durees[nom] = round(len(s) / sr, 2)
    print(nom, durees[nom], texte)
json.dump(durees, open("audio/durees_vo.json", "w"), indent=1)
