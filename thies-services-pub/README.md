# Thiès Services — « Une seule ligne pour tout Thiès »

Pub vidéo 3D, 30 s, format 9:16 (1080×1920, 30 i/s) pour TikTok, Reels et Statut WhatsApp, avec voix off en français.

**Fichiers finaux :** `thies-services-30s-9x16.mp4` (haute qualité) et `thies-services-30s-9x16-whatsapp.mp4` (moins de 16 Mo, pour le Statut WhatsApp)

## Concept
Thiès est la ville du rail. Une voie ferrée orange traverse la ville et relie quatre Thiésois qui ont chacun un problème. Chaque arrêt devient une gare, et chaque gare un service. À la fin, le train se change en logo : le « T », dont la barre verticale est une voie ferrée.

## Déroulé et voix off

| Temps | Image (3D) | Texte à l'écran | Voix off (FR) | Son |
|---|---|---|---|---|
| 0–2 s | Écran noir, un rail orange en fusion déchire l'écran de bas en haut, étincelles | Thiès, tu cherches quoi ? | « Thiès… tu cherches quoi ? » | Sifflet de train, déchirure |
| 2–5 s | 20 h, rue de nuit : Awa porte son enfant fiévreux devant la pharmacie fermée (rideau « FERMÉ », croix qui grésille) | 20:00 · Pharmacie de garde ? | « La pharmacie de garde… elle est où ? » | Grillons, début de l'afro-beat |
| 5–8 s | Cuisine : le tuyau éclate, l'eau monte, Modou panique | Un plombier, vite ! · SPLASH ! | « Un plombier, vite ! » | Splash, jet d'eau |
| 8–11 s | Chambre au crépuscule : Fatou s'ennuie (calendrier « SAMEDI ») | SAMEDI SOIR · Il se passe quoi ce soir ? | « Il se passe quoi, ce soir ? » | |
| 11–14 s | Atelier de couture vide, rayon de soleil : Ibou attend | Et mes clients ? | « Et mes clients, alors ? » | |
| 14–17 s | Écran partagé en 4 : chacun ouvre Thiès Services, les écrans s'allument sur le temps | Thiès Services | « Ouvre Thiès Services. » | Clic ×4 sur le tempo |
| 17–22 s | Zoom arrière sur la carte 3D de Thiès : le rail se dessine, le train le suit, les gares apparaissent | Pharmacies · Artisans · Événements · Mettre mon service en avant | « Une seule ligne relie tout Thiès : pharmacies, artisans, événements… et ton service. » | Train qui roule (clac-clac) |
| 22–25 s | Montage rapide : Awa reçoit son médicament, le plombier arrive, Fatou danse au concert, Ibou a une file de clients | Médicament trouvé · Plombier en route · Concert ce soir · Clients au rendez-vous | « Tout ce qu'il y a à Thiès, c'est ici. » | Foule au concert |
| 25–30 s | Le train entre en gare, les wagons s'envolent et forment la barre du « T » : le logo | Thiès Services · Tout Thiès, sur une seule ligne. · www.thiesservices.com (tenus 3 s) | « Thiès Services. Tout Thiès, sur une seule ligne. » | Freins, sifflet, impact, accord final |

Palette : bleu-vert `#127C7F`, orange `#F28C28`, blanc cassé `#F4EFE6`, gris anthracite `#2B2D31`. Typo : Poppins 800/600. Grain léger sur toute la vidéo.

## Fabrication
- `index.html` : la scène 3D (three.js) : personnages, décors, caméras, textes animés, grain. Chaque image est calculée à partir du temps, donc le rendu est identique d'une fois à l'autre. Ouvert dans un navigateur (via un petit serveur local), il lit l'animation en temps réel avec le son.
- `tools/voix_off.py` : voix off française synthétisée hors ligne (Kokoro TTS, voix `ff_siwis`). « Thiès » est écrit « Tièss » pour le moteur afin d'obtenir la prononciation /tjɛs/.
- `tools/son.py` : musique afro-beat à 100 BPM (grosse caisse, clap, shaker, cloche, basse, guitare highlife pincée), bruitages et mixage avec ducking sous la voix. Tout est synthétisé, sans échantillon externe : pas de question de droits.
- `tools/rendu.mjs` : rendu image par image dans Chromium headless.
- `tools/fabriquer.sh <modèles_kokoro>` : toute la chaîne d'un coup.

## À savoir / prochaines étapes
- **Logo** : aucun fichier de logo n'a été fourni. Le « T-rail » final est une proposition qui suit le brief. Il faudra le remplacer par le vrai logo (SVG/PNG) s'il existe.
- **Voix off** : c'est une voix de synthèse, faite pour valider le rythme. Pour la diffusion, mieux vaut enregistrer une voix humaine chaleureuse sur le même texte et les mêmes temps (voir le tableau ci-dessus), puis remplacer `audio/vo0X.wav` et relancer `tools/son.py`. La version wolof du brief (« Fan la pharmacie bi ubbee ? », « Lépp lu am ci Thiès, fii la. ») se place aux mêmes endroits.
- **Style** : le brief initial prévoyait du flat 2D. Cette version est en 3D, comme demandé, mais garde la palette, la kinetic typography et le grain.
