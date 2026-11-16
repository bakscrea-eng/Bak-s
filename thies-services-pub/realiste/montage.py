"""Assemble la version réaliste à partir des clips générés par IA.

    python3 realiste/montage.py            (depuis thies-services-pub/)

Entrées : realiste/clips/p01.mp4 … p09.mp4 (voir PROMPTS.md), audio/mix.wav,
          realiste/logo.png (facultatif : le vrai logo, fond transparent).
Sortie  : thies-services-30s-9x16-realiste.mp4

Chaque clip est recadré en 1080×1920, ralenti s'il est trop court puis coupé à
sa durée. Les textes sont incrustés aux mêmes temps que la voix off.
"""
import os, subprocess, json

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
CLIPS = os.environ.get('CLIPS', os.path.join(ICI, 'clips'))
F800 = os.path.join(ICI, 'fonts', 'Poppins_800ExtraBold.ttf')
F600 = os.path.join(ICI, 'fonts', 'Poppins_600SemiBold.ttf')
LOGO = os.path.join(ICI, 'logo.png')
SORTIE = os.environ.get('SORTIE', os.path.join(RACINE, 'thies-services-30s-9x16-realiste.mp4'))
W, H, FPS = 1080, 1920, 30

# (fichier, durée) dans l'ordre ; le groupe « split » forme l'écran partagé 14–17 s
PLANS = [('p01', 2), ('p02', 3), ('p03', 3), ('p04', 3), ('p05', 3),
         ('split', 3), ('p07', 5), ('p08a', .75), ('p08b', .75), ('p08c', .75), ('p08d', .75), ('p09', 5)]
SPLIT = ['p06a', 'p06b', 'p06c', 'p06d']

# (texte, début, fin, y, taille, encadré) ; « | » = retour à la ligne
TEXTES = [
    ('Thiès, tu cherches|quoi ?', .95, 2.0, 1200, 96, True),
    ('20:00', 2.2, 4.95, 300, 54, True),
    ('Pharmacie|de garde ?', 2.35, 4.95, 1300, 92, True),
    ('Un plombier,|vite !', 5.3, 7.95, 1300, 92, True),
    ('SPLASH !', 5.55, 6.9, 880, 140, False),
    ('SAMEDI SOIR', 8.2, 10.95, 300, 54, True),
    ('Il se passe quoi|ce soir ?', 8.3, 10.95, 1300, 84, True),
    ('Et mes clients ?', 11.3, 13.95, 1300, 92, True),
    ('Thiès Services', 16.4, 17.0, 920, 84, True),
    ('Pharmacies', 18.0, 21.9, 1240, 64, True),
    ('Artisans', 18.8, 21.9, 1340, 64, True),
    ('Événements', 19.6, 21.9, 1440, 64, True),
    ('Mettre mon service|en avant', 20.4, 21.9, 1540, 56, True),
    ('Médicament trouvé', 22.05, 22.75, 1330, 80, True),
    ('Plombier en route', 22.8, 23.5, 1330, 80, True),
    ('Concert ce soir', 23.55, 24.25, 1330, 80, True),
    ('Clients au|rendez-vous', 24.3, 24.98, 1330, 76, True),
    ('Thiès Services', 27.3, 30.0, 1180, 120, False),
    ('Tout Thiès,|sur une seule ligne.', 27.5, 30.0, 1360, 70, False),
    ('www.thiesservices.com', 27.0, 30.0, 1560, 54, True),
]


def duree(f):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', f], capture_output=True, text=True, check=True)
    return float(json.loads(out.stdout)['format']['duration'])


def ajuste(idx, nom, d, w=W, h=H):
    """filtre : recadrage plein cadre, ralenti si trop court, coupe à la durée d."""
    f = os.path.join(CLIPS, nom + '.mp4')
    k = max(1.0, d / duree(f) * 1.02)
    return (f'[{idx}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,'
            f'setpts={k:.4f}*(PTS-STARTPTS),fps={FPS},trim=duration={d},setpts=PTS-STARTPTS')


def echappe(t):
    return t.replace('\\', '\\\\').replace(':', '\\:').replace("'", "’").replace('%', '\\%')


def main():
    manquants = [n for n, _ in PLANS if n != 'split' and not os.path.exists(os.path.join(CLIPS, n + '.mp4'))]
    manquants += [n for n in SPLIT if not os.path.exists(os.path.join(CLIPS, n + '.mp4'))]
    if manquants:
        raise SystemExit('Clips manquants dans realiste/clips/ : ' + ', '.join(m + '.mp4' for m in manquants))
    entrees, filtres, segs = [], [], []
    for nom, d in PLANS:
        if nom == 'split':
            noms = []
            for s in SPLIT:
                i = len(entrees) // 2; entrees += ['-i', os.path.join(CLIPS, s + '.mp4')]
                filtres.append(ajuste(i, s, d, W // 2 - 8, H // 2 - 8) + f',pad={W // 2}:{H // 2}:4:4:color=0xF28C28[{s}]')
                noms.append(f'[{s}]')
            filtres.append(''.join(noms) + f'xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v{len(segs)}]')
        else:
            i = len(entrees) // 2; entrees += ['-i', os.path.join(CLIPS, nom + '.mp4')]
            filtres.append(ajuste(i, nom, d) + f'[v{len(segs)}]')
        segs.append(f'[v{len(segs)}]')
    filtres.append(''.join(segs) + f'concat=n={len(segs)}:v=1:a=0,format=yuv420p[base]')
    # voile blanc cassé sous le texte final, puis textes
    chaine = '[base]drawbox=x=0:y=1080:w=iw:h=640:color=0xF4EFE6@0.92:t=fill:enable=\'gte(t,27)\''
    for txt, a, b, y, taille, cadre in TEXTES:
        fin_ = txt in ('Thiès Services', 'Tout Thiès,|sur une seule ligne.') and a > 27
        couleur = '0x2B2D31' if fin_ else '0xF4EFE6'
        if txt == 'Thiès Services' and a > 27: couleur = '0x127C7F'
        if txt == 'SPLASH !': couleur = 'white'
        boite = ':box=1:boxcolor=0x2B2D31@0.86:boxborderw=26' if cadre else ''
        if txt in ('20:00', 'SAMEDI SOIR'): boite = ':box=1:boxcolor=0xF28C28:boxborderw=14'; couleur = '0x2B2D31'
        if txt == 'www.thiesservices.com': boite = ':box=1:boxcolor=0x127C7F:boxborderw=22'
        if txt == 'Thiès Services' and a < 27: boite = ':box=1:boxcolor=0x127C7F:boxborderw=26'
        bord = ':borderw=8:bordercolor=0x0B4F55' if txt == 'SPLASH !' else ''
        police = F600 if txt == 'www.thiesservices.com' else F800
        x = '120' if txt in ('20:00', 'SAMEDI SOIR') else '(w-text_w)/2'
        for n, ligne in enumerate(txt.split('|')):
            # garde la ligne dans l'écran (Poppins 800 : ~0,62 × taille par caractère)
            tl = min(taille, int(960 / (.62 * len(ligne))))
            chaine += (f",drawtext=fontfile='{police}':text='{echappe(ligne)}':fontsize={tl}:fontcolor={couleur}"
                       f":x={x}:y={y + int(n * taille * 1.3)}{boite}{bord}:enable='between(t,{a},{b})'")
    if os.path.exists(LOGO):
        entrees += ['-i', LOGO]; il = len(entrees) // 2 - 1
        filtres.append(chaine + '[txt]')
        filtres.append(f'[{il}:v]scale=600:-1[logo];[txt][logo]overlay=(W-w)/2:430:enable=\'gte(t,27.3)\'[out]')
    else:
        filtres.append(chaine + '[out]')
    ia = len(entrees) // 2; entrees += ['-i', os.path.join(RACINE, 'audio', 'mix.wav')]
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', *entrees, '-filter_complex', ';'.join(filtres), '-map', '[out]', '-map', f'{ia}:a',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-r', str(FPS), '-c:a', 'aac', '-b:a', '192k', '-t', '30', '-movflags', '+faststart', SORTIE]
    subprocess.run(cmd, check=True)
    print('OK :', SORTIE)


if __name__ == '__main__':
    main()
