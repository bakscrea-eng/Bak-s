# Thiès Services 2.2 — pub avec voix off wolof (30 s, 9:16)

Pub qui montre la vraie application, avec les écrans de la maquette 2.2, dans un téléphone. Les écrans défilent, les boutons importants s'entourent d'orange et sont « tapés ». Les titres sont en wolof, sous-titrés en français.

## Texte de la voix off (wolof)

| # | Wolof (dit) | Sens en français | Écran |
|---|---|---|---|
| 1 | Thiès, lan ngay seet ? | Thiès, tu cherches quoi ? | Logo |
| 2 | Ak Thiès Services, benn recherche rekk : plombier, pharmacie, taxi… lépp a ngi fi. | Avec Thiès Services, une seule recherche : plombier, pharmacie, taxi… tout est là. | Accueil : barre de recherche, raccourcis |
| 3 | Bindal ko ci WhatsApp, walla nga woo ko, ci saa si. | Écris-lui sur WhatsApp ou appelle-le, tout de suite. | Résultats, puis fiche : WhatsApp / Appeler |
| 4 | Amuloo jot ? Bindal li nga soxla, ñu wut la ab pro buy la woo. | Pas le temps ? Écris ton besoin, on te trouve un pro qui te rappelle. | « Demander un devis », puis formulaire |
| 5 | Pharmacie de garde, lopitaal, ak lépp lu xew ci Thiès. | Pharmacie de garde, hôpital, et tout ce qui se passe à Thiès. | Santé et agenda |
| 6 | Yaa am liggéey ? Dugal sa service, kiliyaan yi gis la. | Tu as une activité ? Inscris ton service, les clients te voient. | Offres pros : Pack complet |
| 7 | Thiès Services. Thiès am na lépp ! | Thiès Services. Thiès a tout ! | Logo, slogan, www.thiesservices.com |

**À faire relire par un locuteur wolof avant diffusion**, pour l'orthographe des titres comme pour la prononciation de la voix.

## Voix
Prise générée avec ElevenLabs (modèle eleven_v4, voix « Bakumba », accent sénégalais). ElevenLabs ne propose pas officiellement le wolof : c'est un essai, à écouter. Une voix humaine enregistrée sur ce texte donnera un meilleur résultat, et la chaîne l'accepte telle quelle.

## Fabrication
```
./wolof/fabriquer.sh chemin/vers/voix_off.mp3
```
- `son_wolof.py` repère les 6 pauses de la voix, écrit `timing.json` (le moment où chaque écran arrive) et mixe la musique afro-beat, les bruitages et la voix.
- `index.html` contient l'animation : les écrans de la maquette (`ecrans/`) et le logo redessiné en vectoriel.
- Sans argument, le script produit un aperçu sans voix.
