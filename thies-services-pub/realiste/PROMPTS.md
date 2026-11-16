# Version réaliste : prompts plan par plan

Ces prompts servent à générer les plans en vidéo IA photoréaliste (Kling, Veo, Runway, Sora, Canva Video…). Ensuite, `montage.sh` assemble tout : voix off française, musique, bruitages et textes.

## Méthode (pour que les personnages restent les mêmes)
1. **Créer d'abord une image de référence par personnage** avec les prompts « Personnages » ci-dessous (Midjourney, Firefly, Ideogram, ChatGPT…). Garder la meilleure image de chacun.
2. **Générer chaque plan en mode « image → vidéo »**, en donnant l'image du personnage comme référence et en collant le prompt du plan.
3. **Réglages communs** : format **9:16**, 1080×1920 si possible, 24 ou 30 i/s, **sans texte ni sous-titres dans l'image** (les textes sont ajoutés au montage), **sans son** (la bande-son est fournie).
4. Nommer les fichiers exactement comme indiqué (`p01.mp4`, `p02.mp4`…) et les déposer dans `realiste/clips/`. Si un clip est plus long que prévu, le montage le coupe ; s'il est plus court, il le ralentit légèrement.

Les prompts sont en anglais : les générateurs les comprennent mieux. Les ajouts « negative » sont à mettre dans le champ prévu quand il existe.

**Style commun, à ajouter à la fin de chaque prompt :**
`photorealistic, shot on ARRI Alexa, 35mm lens, shallow depth of field, natural skin texture, subtle film grain, color grade with teal-green and warm orange accents, off-white and charcoal tones, vertical 9:16 framing, no text, no subtitles, no logos`

**Negative :** `cartoon, 3D render, plastic skin, extra fingers, deformed hands, text, watermark, subtitles`

---

## Personnages (images de référence)

**AWA** : `Portrait of a Senegalese woman in her early 30s, dark brown skin, warm expressive eyes, wearing a colorful wax-print headwrap in orange and teal and a long teal boubou dress with orange patterns, gentle but worried expression, full body, neutral background, photorealistic`

**ENFANT d'Awa** : `A 3-year-old Senegalese child, sleepy and feverish, flushed cheeks, wearing a light cream t-shirt, resting on his mother's shoulder, photorealistic`

**MODOU** : `Portrait of a Senegalese man in his late 30s, dark skin, short black hair, trimmed beard, wearing an orange t-shirt and dark navy trousers, expressive face, full body, neutral background, photorealistic`

**FATOU** : `Portrait of a Senegalese female university student, 20 years old, dark brown skin, natural hair in a high puff bun, small gold earrings, wearing an off-white top and teal jeans, full body, neutral background, photorealistic`

**IBOU** : `Portrait of a Senegalese tailor in his 50s, very dark skin, short grey beard, wearing a white kufi cap and an off-white embroidered kaftan with teal and orange details, a yellow measuring tape around his neck, full body, neutral background, photorealistic`

**PLOMBIER** : `Portrait of a Senegalese plumber in his 30s, wearing blue work overalls and an orange cap, carrying a red toolbox, friendly confident smile, full body, photorealistic`

---

## Plans

| Fichier | Durée | Temps final |
|---|---|---|
| p01.mp4 | 2 s | 0–2 s |
| p02.mp4 | 3 s | 2–5 s |
| p03.mp4 | 3 s | 5–8 s |
| p04.mp4 | 3 s | 8–11 s |
| p05.mp4 | 3 s | 11–14 s |
| p06a…p06d.mp4 | 3 s chacun | 14–17 s (écran partagé en 4) |
| p07.mp4 | 5 s | 17–22 s |
| p08a…p08d.mp4 | 0,75 s utiles chacun (générer 3 s) | 22–25 s |
| p09.mp4 | 5 s | 25–30 s |

**p01 — Le rail déchire le noir (0–2 s)**
`Pitch black frame. A glowing molten-orange railway track tears through the darkness from the bottom of the frame to the top, sparks flying off the rails, top-down view, camera slowly tilting up, cinematic, dramatic contrast, dust in the air`

**p02 — Awa, 20 h, pharmacie fermée (2–5 s)** *(réf. : AWA, ENFANT)*
`Night street in Thiès, Senegal, 8 pm. Awa holds her feverish child against her shoulder in front of a closed pharmacy with a lowered metal shutter, the green pharmacy cross sign above flickers and is mostly off. Warm sodium streetlight from the left, deep blue night. She looks at the shutter, then turns towards the camera, worried, gently rocking the child. Slow push-in, handheld feel`

**p03 — Modou, cuisine inondée (5–8 s)** *(réf. : MODOU)*
`Small tiled kitchen in a Senegalese home, daylight from a window. A pipe under the sink suddenly bursts, water sprays across the room and floods the floor. Modou jumps back, hands raised in panic, water splashing around his feet. Quick camera shake at the burst, then a slight push-in`

**p04 — Fatou s'ennuie (8–11 s)** *(réf. : FATOU)*
`Saturday evening in a modest bedroom, warm bedside lamp, orange dusk light through the window, colorful wax-print bedspread. Fatou sits on the edge of the bed, chin in her hand, bored, sighs and looks out of the window. Slow lateral dolly`

**p05 — Ibou attend (11–14 s)** *(réf. : IBOU)*
`Tailor workshop in Thiès: sewing machine on a wooden table, rolls of wax-print fabric on shelves, a mannequin with a half-made boubou, dust floating in a beam of sunlight from the open door. Ibou sits behind the table, tapping his fingers, glancing at the empty doorway, waiting for clients. Slow push-in`

**p06a / p06b / p06c / p06d — Les téléphones s'allument (14–17 s)** *(réf. : un personnage par clip)*
Même prompt pour les quatre, en changeant le personnage et le décor (a = Awa dans la rue de nuit, b = Modou dans la cuisine, c = Fatou dans la chambre, d = Ibou dans l'atelier) :
`Medium close-up of [PERSONNAGE] in [DÉCOR], taking out a smartphone and unlocking it; the screen lights up and illuminates the face with a soft cool teal glow; the expression changes from worry to relief and a small smile. Locked-off camera`

**p07 — La ligne qui relie tout Thiès (17–22 s)**
`Aerial drone shot rising above the city of Thiès, Senegal, golden hour: low-rise sand-colored buildings, neem trees, wide streets. A glowing orange railway line draws itself across the city, connecting four neighborhoods, a modern teal-and-off-white train travels along it. The camera pulls back from street level to a high wide view of the whole city. Smooth continuous motion`

**p08a…p08d — Montage des solutions (22–25 s)**
- p08a *(AWA)* : `A pharmacist in a white coat hands a small medicine box to Awa across the counter of a brightly lit pharmacy at night; Awa smiles with relief, her child calm on her shoulder`
- p08b *(MODOU, PLOMBIER)* : `The plumber walks into Modou's kitchen carrying a red toolbox; Modou greets him with a relieved handshake`
- p08c *(FATOU)* : `Fatou dancing joyfully in a crowd at an outdoor evening concert in Thiès, teal and orange stage lights, confetti`
- p08d *(IBOU)* : `Ibou's tailor workshop full of happy customers waiting in line; Ibou smiles while measuring a client's shoulders with his tape`

**p09 — Le train entre en gare (25–30 s)**
`A modern teal-and-off-white passenger train with orange stripes slowly pulls into a clean, sunlit station in Thiès and stops; camera rises to a top-down view of the track. Soft white light, minimalist off-white platform. Last 2 seconds: the image fades to a clean off-white background`
*(Le logo, le slogan et l'URL s'affichent par-dessus au montage. Si tu as le vrai logo de Thiès Services, place-le dans `realiste/logo.png` : le montage l'utilisera.)*
