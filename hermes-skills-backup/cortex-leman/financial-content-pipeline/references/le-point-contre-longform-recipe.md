# LE CONTRE-POINT — Recipe podcast long-form bear case

Format validé 2026-07-19 (épisode pilote OVHcloud, 507s = 8.5 min, 12.1 MB, 1920×1080).

## Positionnement éditorial

> *"Pour chaque thèse d'investissement présentée sur L'EFFET COMPOSÉ, un épisode LE CONTRE-POINT décortique ce qui peut mal tourner. Pas pour dézinguer — pour investir les yeux ouverts."*

**Différenciateur concurrentiel** : Grand Angle Nova (concurrent principal) ne produit que du bull case. Le bear case = transparence méthodologique = **avantage commercial + conformité AMF L541-1 supérieure** (présentation équilibrée).

## Spécifications techniques

| Paramètre | Valeur | Raison |
|---|---|---|
| Format | 1920×1080 (16:9 horizontal) | YouTube long-form, pas Shorts |
| Durée cible | 8-12 min | Niche commute/walk ; viser 10-15 min pour l'algo YT |
| Voix | `fr-FR-HenriNeural`, rate **+0%** (pas +10%) | Plus posé que les Shorts, soutenabilité sur 8+ min |
| BGM | Stellardrone **-28 dB** (pas -24) | Plus discret que les Shorts, ne fatigue pas sur la durée |
| Visuel | Slide statique unique PNG | Pas de broll — le contenu est dans la parole |
| Sous-titres | ASS burn-in, taille **52**, position basse (MarginV=80) | Lisibilité cinéma long-form |
| Intro/outro signature | **NON** (contrairement aux Shorts) | Format podcast — disclaimer AMF renforcé intégré au script |

## Structure narrative (7 sections, ~1500 mots)

```
01_cold_open    [0:00]  Hook + disclaimer AMF renforcé (45s)
02_rappel       [0:45]  Rappel thèse bull en 3 piliers (90s)
03_angle1       [2:15]  Angle d'attaque 1 (120-150s)
04_angle2       [4:30]  Angle d'attaque 2 (120-150s)
05_angle3       [7:00]  Angle d'attaque 3 (90-120s)
06_changement   [9:00]  Critères falsifiables publics (60-90s) ← MOAT rare
07_verdict      [10:30] Verdict nuancé + outro MiFID II (75s)
```

### Section 06 = le moat éditorial

Les **critères falsifiables publics** sont ce qui différencie LE CONTRE-POINT du opinion-post-hoc qui domine la finance FR sur YouTube. Format :

> *"Trois critères falsifiables.
> Premier : si [condition observable et datée], je retirerais l'angle [N].
> Deuxième : si [condition], je retirerais l'angle [N].
> Troisième : si [condition], je reconsidérerais la thèse bull dans son ensemble.
> Ces trois critères sont publics. Ils sont datés."*

Ça permet à l'auditeur de vérifier dans 6/12/24 mois si le contre-point tient. Crédibilité rare.

## Conformité AMF / MiFID II — RENFORCÉE vs Shorts

Le bear case est plus exposé réglementairement que le bull case (implicite : "vendez"). Double disclaimer obligatoire :

### Disclaimer intro (lu par la voix, ~15s)

> *"Avertissement : ce contenu est fourni à titre informatif et éducatif uniquement. Il ne constitue pas un conseil en investissement, une recommandation d'achat ou de vente, ni une sollicitation. Les instruments financiers mentionnés sont volatils et présentent un risque de perte en capital. Consultez un conseiller financier agréé avant toute décision. L'auteur déclare ses positions éventuelles en fin d'épisode."*

### Disclosure outro (lu par la voix, ~10s)

> *"Disclosure de l'auteur : l'auteur peut détenir, avoir détenu, ou envisager de détenir des positions sur les instruments mentionnés. Les positions sont susceptibles d'évolution sans préavis. Ce contenu ne constitue pas un conseil en investissement au sens de la directive MiFID II. Consultez un professionnel agréé avant toute décision."*

### Slide statique — disclaimer visible

La slide PNG affiche en bas, en petit (`opacity 0.4`) : *"Ce contenu ne constitue pas un conseil en investissement · MiFID II"*. Permanence visuelle du disclaimer pendant tout l'épisode.

## Pipeline de production (5 étapes)

```python
# templates/le_contre_point_template.py — copier et éditer SECTIONS

SECTIONS = {
    "01_cold_open":   "...",  # hook + disclaimer
    "02_rappel":      "...",  # 3 piliers bull
    "03_angle1":      "...",  # 1er angle d'attaque
    "04_angle2":      "...",  # 2e angle
    "05_angle3":      "...",  # 3e angle
    "06_changement":  "...",  # critères falsifiables
    "07_verdict":     "...",  # verdict + outro MiFID
}

# 1. Capture slide statique 1920x1080 (Playwright)
# 2. TTS HenriNeural +0% par section, concat audio
# 3. Sous-titres SRT (phrases par ponctuation) → ASS taille 52
# 4. Render final : loop slide + BGM -28dB + subs burn-in
# 5. Vérif durée (8-12 min cible)
```

**Détail clé render** : `-loop 1 -framerate 30 -t {durée_audio}` sur la slide PNG. Le render final (~8 min de vidéo 1920×1080 + subs burn-in `preset medium crf 22`) prend **~15-20 min CPU**. Lancer en `background=true` avec `notify_on_complete=true`.

## Sous-titres long-form — découpage par phrase

Contrairement aux Shorts (découpage par 4 mots), le long-form découpe par **phrase** (ponctuation `. ! ?`). Plus naturel à lire sur 8+ min :

```python
phrases = re.split(r'(?<=[.!?])\s+', text)
# chaque phrase = une entrée SRT, durée proportionnelle au nombre de caractères
```

## Sources — extraction depuis les contre-analyses existantes

Deux documents sources cumulatifs (`CHANNEL/contre_analyse_*.md`) :

| Fichier | Modèle | Focus | Richesse |
|---|---|---|---|
| `contre_analyse_gpt56.md` | GPT-5.6 | Démontage thèse "compute = pétrole", P/B CoreWeave, angles morts data | 479 lignes, très dense |
| `contre_analyse_opus47.md` | Claude Opus 4.7 | Angles morts stratégiques (asset pas ta propriété, SEO-hostile, timing marché) | 69 lignes, percutant |

**Attention** : ces docs portent surtout sur CoreWeave et la chaîne globale. Pour un épisode sur une valeur spécifique (OVHcloud, ASML...), **adapter** les arguments génériques au cas particulier. Ne pas recopier — transformer.

## Honest gaps du format (à améliorer)

- **Voix HenriNeural sur 8+ min** : peut lasser par répétitivité tonale. Évaluer ElevenLabs FR (~$5/mois) pour la série si budget.
- **Slide statique = visuellement plat** pour YouTube. Pour ép. 2+ : ajouter b-roll léger (photos entreprise traitées style portfolio, transitions douces).
- **8.5 min = fourchette basse**. L'algo YT long-form préfère 10-15 min → script plus dense la prochaine fois (viser 1800-2000 mots).

## Industrialisation — template réutilisable

- `templates/le_contre_point_template.py` — générateur complet paramétrable (éditer `SECTIONS` + `TITLE` + `EPISODE_NUM`, lancer)
- Production ép. : copier le template dans `CHANNEL/le_contre_point/ep0N_acteur/`, éditer `SECTIONS`, lancer.

## Décisions de design validées (2026-07-19, ép.1 OVHcloud)

| Décision | Choix | Alternatives rejetées | Raison |
|---|---|---|---|
| Mono vs multi-voix | **Mono HenriNeural** | Débat multi-voix TTS | Uncanny valley FR TTS non validé, zéro gain pour risque sonore élevé |
| Nom de la série | **LE CONTRE-POINT** | "L'ENVERS", "SOUS LA CROISSANCE" | Descriptif, neutre, sérieux. "L'ENVERS" = trop manichéen. |
| Série vs one-off | **Série récurrente** | Documentaire one-off | Momentum algo YT + capitalisation matière + discipline production |
| Format visuel | **Slide statique 16:9** | Broll dynamique | Podcast = la parole est le contenu. Broll = distraction. |
