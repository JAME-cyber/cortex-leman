# Campaign Audit Pattern + Trust/Safety Video Template

## Pattern: LLM-Driven Campaign Audit

### Quand utiliser
- Après avoir produit 5+ vidéos pour une campagne marketing
- Avant de finaliser/livrer une campagne complète
- Pour identifier les angles manquants (trust, sécurité, preuve sociale)

### Workflow
1. **Compiler le contexte projet** (scripts, VO texts, menu, contact, palette, livrables)
2. **Envoyer à un LLM externe** (Claude Sonnet 4 via OpenRouter) avec un prompt structurant
3. **Recevoir un audit** en 6 points: cohérence, message, points forts, risques, recommandations, manquants
4. **Agir sur les recommandations prioritaires**

### Prompt template (OpenRouter API)
```bash
curl -s "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d @audit_prompt.json
```

Structure du prompt:
```json
{
  "model": "anthropic/claude-sonnet-4",
  "messages": [
    {"role": "system", "content": "Tu es un consultant en marketing vidéo..."},
    {"role": "user", "content": "PROJET: [nom]\nCONTEXTE: [business details]\nLIVRABLES: [list]\nSCRIPTS VO: [texts]\nTASK: Analyse ce projet... pour chaque point sois direct:\n1. COHÉRENCE NARRATIVE\n2. MESSAGE MARKETING\n3. POINTS FORTS\n4. POINTS FAIBLES/RISQUES\n5. RECOMMANDATIONS (top 5)\n6. MANQUANTS critiques"}
  ],
  "max_tokens": 4000,
  "temperature": 0.7
}
```

### Résultat type (Culture en Saveur, Jul 2026)
Audit a identifié 3 problèmes critiques:
1. **Aucun adulte/animateur visible** → red flag parental
2. **Programme flou** → parents ne comprennent pas ce que font les enfants
3. **Manque trust signals** → pas d'assurance, pas de certifications, pas de témoignages

→ Action: Création vidéo "Programme V0" avec animateurs visibles (Seedance) + cards confiance

---

## Template: Trust/Safety Programme Video

### Structure (54s, 9 segments)
```
Intro(3s) → Steam(3s) → Animator(5s Seedance) → Schedule(6s card)
→ Flags(8s card) → Location/Security(8s card) → Proud Kids(5s Seedance)
→ Final Event(7s card) → Pricing/CTA(8s card)
```

### Cards indispensables pour trust

1. **Schedule card** — Day-by-day planning (Lundi→Vendredi, chaque jour = pays + plat)
2. **Location/Security card** — Lieu précis + horaires + protocole sécurité:
   - "Animatrice certifiée présente"
   - "Cuisine professionnelle sécurisée"
   - "Protocole allergies alimentaires"
3. **Pricing card** — Prix + ce qui est inclus + places limitées + contact

### VO angles (répondent aux peurs parentales)
- "Encadré par une animatrice certifiée" → sécurité
- "Maison de Quartier le Plateau, Petit-Lancy" → lieu réel, pas vague
- "Places limitées à 12 enfants" → qualité d'encadrement perçue
- "Le vendredi, vos enfants vous invitent à déguster" → preuve de résultat + moment fierté

### Seedance prompts: animateurs visibles
```
Clip 1 (Animator): "A friendly female cooking instructor in her 30s, wearing
a clean apron and a name badge, stands behind a counter guiding three children
as they learn to prepare African dishes..."

Clip 2 (Proud kids): "Three children in small aprons stand proudly behind a
counter laden with colorful African dishes they have just prepared. A friendly
female cooking instructor stands behind them, smiling proudly..."
```

**Key**: Toujours mentionner l'adulte EN PREMIER dans le prompt — Seedance le traite comme le sujet principal.

### Script de référence
`/home/tars/culture-en-saveur/scripts/build_programme_v0.py`
- 9 segments, 2 clips Seedance (animateur + enfants fiers), 5 PIL cards
- VO 6 segments (~40s total), sous-titres ASS police 38
- Musique afroswing_v2.mp3 à 0.12

### Checklist trust signals dans une vidéo programme
- [ ] Adulte/animateur visible (clip ou photo)
- [ ] Lieu précis nommé (pas juste "Genève")
- [ ] Horaires clairs
- [ ] Mention certifications/qualifications
- [ ] Prix + ce qui est inclus
- [ ] Places limitées (urgence + qualité)
- [ ] Contact multi-canal (téléphone + email + social)
- [ ] Moment de fierté/résultat pour parents
