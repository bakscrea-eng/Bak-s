"""Assemble les PNG de contrôle en planches contact (8 images par planche)."""
import glob, sys
from PIL import Image
d = sys.argv[1]
fs = sorted(glob.glob(f'{d}/still_*.png'), key=lambda f: float(f.rsplit('_', 1)[1][:-4]))
for n in range(0, len(fs), 8):
    ims = [Image.open(f).resize((300, 533)) for f in fs[n:n + 8]]
    out = Image.new('RGB', (300 * len(ims), 533))
    for i, im in enumerate(ims): out.paste(im, (i * 300, 0))
    out.save(f'{d}/sheet_{n}.jpg', quality=85)
