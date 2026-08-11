# Visual Asset Discovery — Trouver des photos réelles d'une organisation

Méthodologie pour retrouver des photos authentiques d'une entité spécifique
(orphelinat, association, école, personne, lieu) quand les sources sont
éparpillées entre réseaux sociaux et sites web. Tâche récurrente lors de
projets vidéo client: le client dit "tiens, voilà une photo de X" et il
faut la retrouver en ligne.

## Workflow en 4 phases

### Phase 1: Discovery — empreinte digitale de la cible

Lancer **2-3 requêtes parallèles** (apify/rag-web-browser, maxResults=5):
```
1. "{nom exact}" {lieu} {pays}                    → pages officielles
2. "{nom exact}" {lieu} site:facebook.com          → pages FB
3. "{nom exact}" {lieu} {contexte additionnel}     → mentions tierces
```

Extraire du résultat: site officiel, pages FB (multiple IDs possibles),
handles IG/TikTok, localisation précise, associations liées.

### Phase 2: Scraping — récupérer le contenu de chaque source

#### 2a. Galeries JS sur sites officiels
`apify/rag-web-browser` extrait le texte mais **PAS** les images JS-rendered.

**Fix**: utiliser les outils browser:
```
browser_navigate(url_galerie)
browser_click(@eN)            # accepter cookies si banner bloque
browser_get_images()          # liste toutes les images: src, width, height
```

Filtrer: ignorer logos/gstatic, garder images du domaine avec width≥800.
Noms de fichiers associatifs souvent descriptifs (`enfantsdanslacour.jpg`).

#### 2b. Facebook — cross-page discovery (bypass login wall)
Les pages FB scrapées retournent uniquement le formulaire de login.

**Solution**: chercher les mentions de la cible sur d'AUTRES pages FB publiques.
Posts de visiteurs/bénévoles contiennent souvent des photos DES enfants/lieu.
```python
# Pattern de recherche
'"{nom cible}" {lieu} site:facebook.com'
```

Sources tierces typiques qui mentionnent un orphelinat/association:
- Autres orphelinats/associations de la région
- Pages info locales (Infoducameroun.com, etc.)
- Comptes de donateurs/bénévoles
- Groupes communautaires

#### 2c. Instagram
- Profils publics avec underscores multiples (`@association_joie_de_vivre_`):
  scraping via RAG browser **échoue** (0 résultats).
- **Alternative**: chercher les mentions du handle sur d'autres comptes publics
  (ex: `ogclub7` mentionne `@association_joie_de_vivre_` → photos de dons).

#### 2d. Téléchargement
```bash
# CDN Instagram/FB: URLs signées avec expiration (~24h). Télécharger IMMÉDIATEMENT.
curl -sL -o output.jpg "{URL_complète_avec_paramètres_oh_oe}"
file output.jpg   # vérifier: "JPEG image data" pas "HTML document"
```

### Phase 3: Verification — analyser chaque photo
```bash
python3 scripts/vision_check.py <image.jpg> "Décris cette photo. Y a-t-il
des enfants? Combien? Que font-ils? Quel est le décor?"
```

**Qwen VL rate limiting**: OpenRouter peut retourner 429. Espacer 3-5s ou retry.
**vision_analyze GLM-5.2**: échoue (error 1210). Toujours utiliser vision_check.py.

Trier par pertinence: ⭐⭐⭐ enfants+décor+résolution / ⭐⭐ enfants flous / ⭐ contexte seul.

### Phase 4: Storage
```
project/assets/{entity_name}/
├── site_champ.jpg                    # source: galerie officielle
├── site_enfantsdanslacour.jpg        # source: galerie officielle
├── fb_noel_2022_enfants.jpg          # source: FB page tierce
└── ogclub7_donation_toys.jpg         # source: IG compte affilié
```
Convention: `{source}_{contexte}_{date}.jpg`

## Pitfalls

1. **FB login wall** → pages FB retournent un formulaire. Contourner via
   mentions sur pages tierces publiques.
2. **Galerie JS** → RAG browser ne capture pas les images JS-rendered.
   Utiliser browser tools.
3. **URLs CDN signées expirent** → paramètres `oh=`/`oe=` expirent en ~24h.
   Télécharger immédiatement.
4. **IG handles protégés** → chercher mentions sur comptes publics affiliés.
5. **Qwen VL 429** → espacer les appels de 3-5s.

## Cas validé

Orphelinat Joie de Vivre (Banfelouk, Bafang, Cameroun) — 6 photos récupérées
depuis 3 sources (site officiel galerie JS, FB page tierce, IG compte affilié)
en ~30 min de recherche. Photos intégrées dans le projet Culture en Saveur.

**Résolution complète (juil. 2026)**: après découverte, la photo `fb_noel_2022_enfants.jpg`
(~15 enfants + visiteurs devant l'orphelinat, Noël 2022) a été intégrée dans la
vidéo V1-PRO via la technique Ken Burns décrite dans le SKILL.md principal
(section "Insertion de photo réelle dans un segment vidéo existant").

**Sources identifiées pour cet orphelinat**:
- Site officiel: `joiedevivrevillagedenfants.org/galerie` (5 photos: champ, bâtiment,
  enfants dans la cour, potage, cours verticale)
- Facebook: `@Joiedevivre237` (page principale, ~123 likes)
- Facebook tierce: `61555542150984` (page secondaire)
- Instagram: `@association_joie_de_vivre_` (profil protégé, scraping KO)
- TikTok: `@m_l_ajdv`
- Instagram affilié: `ogclub7` (compte du fondateur — contient des photos des enfants)

**Leçon**: pour les associations suisses opérant à l'étranger, le site officiel
hébergé en Suisse (`joiedevivrevillagedenfants.org`) contient souvent une galerie
JS avec les meilleures photos haute résolution. Toujours `browser_navigate` +
`browser_get_images` sur la page `/galerie` — c'est plus rapide et plus fiable
que le scraping FB/IG.
