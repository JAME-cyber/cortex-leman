# Editorial Guardrails — African Heroes

## 1. Intégrité historique (OBLIGATOIRE)
- **Distinction des registres :** chaque script doit marquer clairement ce qui est (a) historique, (b) légendaire, (c) mythologique
- **Pas d'invention :** les dialogues et scènes reconstituées doivent être signalées comme reconstitutions
- **Sources à l'écran :** slide "Sources" obligatoire en fin de vidéo

## 2. Respect culturel
- Prononciation correcte des noms (vérifier avec locuteurs natifs si possible)
- Utiliser les noms dans la langue d'origine (ex: "Nzinga" pas "Jinga", "En-kai" pas "Enkai")
- Contextualiser les pratiques culturelles sans jugement contemporain

## 3. Contre les biais
- **Pas de romantisation coloniale :** citer la violence coloniale quand pertinente (Nzinga vs Portugais, etc.)
- **Pas d'afro-pessimisme :** montrer la complexité politique, diplomatique, militaire des royaumes africains
- **Pas d'afrocentrisme non plus :** ne pas attribuer sans preuve des origines africaines à tout (ex: fausses claims sur les Olmèques, etc.)
- **Honnêteté sur les sources :** dire "la tradition orale raconte..." et non "il est prouvé que..."

## 4. Format narratif
- **Hook (0-15s) :** scène marquante ou question intrigante
- **Contexte (15s-1min) :** géographie, époque, enjeux
- **Récit (1-5min) :** l'histoire elle-même, structurée en actes
- **Héritage (dernière min) :** impact jusqu'à aujourd'hui
- **Sources (final) :** slide obligatoire

## 5. Contenu interdit
- Régime de vérité politique (pas de débats contemporains non historiques)
- Contenu discriminant ou essentialisant
- Apologie de violence ou de pratiques condamnées aujourd'hui présentées sans contexte

## 6. Moteur de règles (pattern guardrail)
Comme pour LEC + AMF, le LLM génère le script mais un moteur de règles vérifie :
- [x] Distinction mythe/histoire présente
- [x] Au moins 2 sources citées par fait clé
- [x] Noms orthographiés correctement (liste blanche)
- [x] Aucune affirmation non sourcée présentée comme fait
- [x] Slide sources présente à la fin
