# Prononciation TTS — Sigles FR & edge-tts

edge-tts écorche systématiquement les sigles/acronymes techniques français ("OVH" → "ovech", "ASML" → "asmel"). Deux stratégies validées selon le contexte, à choisir par test comparatif.

## Les deux stratégies (et quand utiliser laquelle)

| Stratégie | Pattern | Effet | Quand |
|---|---|---|---|
| **Phonétique d'un bloc** | `Ovéache Cloud` | Lu comme un mot, flow naturel | Sigles dans une phrase connectée (discours fluide) |
| **Points espacés** | `A. W. S.` | Lettres très distinctes, pauses marquées | Sigles isolés ou énumérés (scorecard, liste) |

### ⚠️ Piège : les points espacés cassent le flow

`O. V. H. Cloud` (points espacés) force bien la lecture lettre par lettre, **mais** edge-tts interprète chaque point comme une fin de phrase → pauses excessives entre les lettres. En français connecté (« on parle d'O. V. H. Cloud »), ça coupe le rythme de façon audible et gênante. Thierry a rejeté cette variante pour cette raison exacte (2026-07-18).

**Règle** : réserver les points espacés aux sigles cités isolément. Pour les sigles dans le fil du discours, préférer la phonétique d'un bloc.

## Test de prononciation comparatif (pattern reproductible)

Quand un sigle est mal prononcé, NE PAS deviner la substitution. Procédure :

1. Générer 8-12 variantes orthographiques du même sigle dans la même phrase porteuse
2. Produire un MP3 par variante avec la voix cible
3. Faire écouter les 3-4 meilleures au utilisateur, attendre son choix
4. **Alors seulement** patcher le pipeline

```python
# Template de test reproductible — couvrir les deux stratégies
VARIANTS = {
    "01_natural":      "on parle d'OVHcloud.",
    "02_space":        "on parle d'O V H Cloud.",
    "03_dash":         "on parle d'O-V-H-Cloud.",
    "04_periods_strict":"on parle d'O.V.H.cloud.",       # pauses longues → souvent rejeté
    "05_periods_space": "on parle d'O. V. H. Cloud.",    # pauses longues → souvent rejeté
    "06_phonetic_oveash":"on parle d'Ovéache Cloud.",    # ← gagnant OVH (flow naturel)
    "07_phonetic_oviatch":"on parle d'Oviatch Cloud.",
    "08_spelled":      "on parle d'O.V.H. (O-V-H) cloud.",
}
```

Envoyer 3 samples `.mp3` au utilisateur via `MEDIA:` et attendre verdict **avant** toute modification du pipeline. Ne jamais normaliser un script de production sans test préalable validé.

## Map phonétique validée (Thierry, 2026-07-18)

```python
PHONETIC_MAP = {
    # --- Phonétique d'un bloc (validé en session, voix HenriNeural) ---
    "OVHcloud": "Ovéache Cloud",   # ✅ flow naturel — rejet de "O. V. H. Cloud" (pauses trop longues)
    "OVH":      "Ovéache",          # ✅ même règle
    "Soitec":   "Soitèce",          # phonétique nom de marque — non re-testé en phrase
    # --- Points espacés (sigles isolés ou énumérés) ---
    "ASML":     "A. S. M. L.",     # ⚠️ non re-testé en phrase connectée
    "AWS":      "A. W. S.",
    "GCP":      "G. C. P.",
    "GPU":      "G. P. U.",
    "PEA":      "P. E. A.",
    # --- BRUTS : prononciation native edge-tts validée comme CORRECTE ---
    # Thierry a testé 4 variants (word / points / spelled / phonetic) et choisi le mot brut.
    # NE PAS normaliser ces termes — la version native est meilleure que toute substitution testée.
    # "ANSSI": (brut),  "FISA": (brut)
}
```

### ⚠️ Certains sigles sont mieux laissés BRUTS

L'assumption « edge-tts écorche tous les sigles → toujours normaliser » est **fausse**. ANSSI et FISA ont été testés comparativement (4 variants × 2 sigles, voix HenriNeural, 2026-07-18) et la prononciation native edge-tts est **meilleure** que :
- points espacés (`A. N. S. S. I.`) → pauses excessives
- sans points (`A N S S I`) → « anssi » indistinct
- phonétique (`Anssé` / `Fiza`) → déforme le terme

**Conclusion** : ne jamais présumer qu'un sigle sera mal prononcé. Tester systématiquement avant de normaliser. La map ne doit contenir QUE les sigles pour lesquels la native edge-tts est défectueuse ET une substitution a été validée en session.

**Ordre des clés important** : `OVHcloud` doit être traité **avant** `OVH` (sinon la forme courte intercepte la longue).

**Cohérence** : la map doit être identique dans `build_podcast.py` (podcast) et `gen_tts.py` (clips). Toute modification de l'un doit être reportée dans l'autre.

## Intégration pipeline

Fonction `phonetic_normalize()` branchée **après** nettoyage Markdown, **avant** envoi à `edge_tts.Communicate()` :

```python
def phonetic_normalize(text):
    for orig, phon in PHONETIC_MAP.items():
        text = text.replace(orig, phon)
    return text

# Dans la boucle de génération :
clean = re.sub(r'\*+([^*]+)\*+', r'\1', txt)   # strip emphasis
clean = phonetic_normalize(clean)               # ← ici
comm = edge_tts.Communicate(clean, voice, rate=RATE)
```

À appliquer dans **tous** les scripts TTS du pipeline (`build_podcast.py` pour le podcast, `gen_tts.py` pour les clips, `finalize_clipA.py` / `make_clipA.py` pour l'assemblage clips).

## Ajouter un nouveau sigle

1. Ne pas ajouter sans test comparatif (procédure ci-dessus)
2. Si le sigle apparaît dans la marque (ex: "OVHcloud"), ajouter la forme longue **et** courte
3. Pour les noms de marque phonétiquement ambigus (ex: "Soitec"), tester l'orthographe phonétique
4. Tester sur les 2 voix du pipeline (`HenriNeural` hôte + `DeniseNeural` analyste) — la substitution peut différer
5. **Tester en phrase connectée**, pas seulement en citation isolée — les pauses induites par les points ne se manifestent qu'en discours fluide
6. Reporter la modification dans les DEUX scripts (`build_podcast.py` + `gen_tts.py`) pour garder la map synchronisée
