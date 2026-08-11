# Conversion-First Content — Méthodologie

> Quand on a un pipeline de production vidéo performant, la tentation est de produire toujours plus de contenu. Mais la conversion dépend de facteurs hors vidéo : funnel, trust, angle. Cette référence documente comment identifier les angles morts d'un projet client AVANT de produire plus de contenu.

## Le piège de surproduction

**Symptôme** : on a produit 3+ vidéos sans feedback client, ou le client n'a pas encore répondu à un briefing/questionnaire.

**Diagnostic GPT-5.6 (juil. 2026, Culture en Saveur)** : *"En avance sur la production, en retard sur la conversion, la preuve de confiance, et le cadrage business. Le volume de vidéos ne compense aucun de ces défits."*

## Cross-source data mining — Identifier les angles morts

La méthode : croiser **5 sources** pour révéler les contradictions et les angles inexploités.

| Source | Ce qu'elle contient | Ce qu'on cherche |
|--------|---------------------|------------------|
| Brief client | Programme, tarifs, dates, USP listées | Les infos pratiques de base |
| Questionnaire de découverte | Réponses libres, motivées, contextuelles | L'angle de conversion caché (souvent dans une réponse accessoire) |
| Charte graphique | Palette officielle, tagline, slogan | La vraie identité de marque (pas un flyer ponctuel) |
| État de production | Vidéos/assets déjà créés | Surproduction vs manques |
| Contre-analyse GPT-5.6 | Verdict externe, risks, correctifs | Les angles morts que le prestataire ne voit pas |

### Pattern de dispatch contre-analyse

```bash
# Compiler le brief (toutes les sources ci-dessus)
# Puis dispatcher
timeout 180 hermes -z "$(cat /tmp/counter_prompt.txt)" \
  -m openai/gpt-5.6-luna --provider openrouter --cli
```

Le prompt doit structurer l'analyse sur 5 axes : adéquation production/besoin, funnel/conversion, trust/authenticité, périmètre/business, timing. Demander : TOP 3 risques mortels + TOP 3 actions 48h + verdict global.

Voir `references/counter_analysis_business_plan.md` dans le skill `critical-objective-analysis` pour le pattern complet.

## End card completeness audit

Avant de livrer une vidéo avec un end card / CTA frame, vérifier que TOUTES les infos critiques sont présentes.

### Checklist (12 items)

- [ ] Nom de l'événement/association
- [ ] Dates (du / au)
- [ ] Horaires complets
- [ ] Lieu + adresse postale complète (n° rue + code postal + ville)
- [ ] Tranche d'âge / public cible
- [ ] Tarifs (toutes les formules + réductions)
- [ ] Téléphone (format international si transfrontalier)
- [ ] Email
- [ ] Instagram + autres réseaux sociaux
- [ ] Lien d'inscription / Linktree
- [ ] Tagline/slogan de marque
- [ ] Logo

### Validation automatisée (GLM-5.2 vision KO → Qwen 2.5 VL)

GLM-5.2 retourne systématiquement l'erreur 1210 (`messages.content.type is invalid`). Contournement validé : Qwen 2.5 VL 72B via OpenRouter lit l'image et liste tout le texte visible.

```python
import base64, json, urllib.request, os

img_path = 'end_card.png'
with open(img_path, 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = json.dumps({
    'model': 'qwen/qwen2.5-vl-72b-instruct',
    'messages': [{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': 'List ALL text visible on this image, top to bottom, exactly as shown.'},
            {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{img_b64}'}}
        ]
    }],
    'temperature': 0.3,
    'max_tokens': 2000
}).encode()

req = urllib.request.Request(
    'https://openrouter.ai/api/v1/chat/completions',
    data=payload,
    headers={
        'Authorization': f'Bearer {os.environ["OPENROUTER_API_KEY"]}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://hermes-agent.nousresearch.com',
        'X-Title': 'End Card Audit'
    }
)
with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
print(result['choices'][0]['message']['content'])
```

Comparer le texte extrait avec la checklist. Si un item manque → rebuild l'end card.

## Conversion angle mining

L'argument de vente réel est rarement dans le brief client. Il est enfoui dans les réponses libres du questionnaire de découverte.

### Où chercher

1. **Questionnaires Q10+** — les premières questions (Q1-Q5) sont sur l'identité. Les questions tardives (Q10+) révèlent le contexte pratique.
2. **Phrases commençant par "Mais" / "Aussi" / "Je souhaite aussi"** — ce sont des ajouts accessoire qui contiennent l'argument de conversion.
3. **Réponses à "remarques complémentaires"** — la dernière question libre est souvent la plus révélatrice.

### Exemple validé (Culture en Saveurs Q14)

> *"Les ateliers ont lieu la semaine précédant la rentrée scolaire. Ils permettent aux parents de préparer cette période plus sereinement."*

Cet angle ("garde intelligente pendant la semaine de boulot des parents") est devenu le hook principal de la vidéo V2 et du message WhatsApp, remplaçant l'angle noble mais abstrait "découverte culturelle."

## Sequencing rule (projet événementiel à date fixe)

Pour un projet avec événement à date fixe (camp, festival, lancement) :

1. **Valider les fondamentaux** : parcours d'inscription, infos pratiques, consentements, trust signals
2. **Produire le contenu de conversion** : FAQ, flyer, message WhatsApp transférable, vidéo courte
3. **THEN étendre la production vidéo** si pertinent (long-form, séries, variations)

Ne jamais inverser cet ordre. Si on produit de la vidéo avant d'avoir un funnel, on a du contenu que personne ne peut actionner.

## Livrables conversion-first (priorité)

| Livrable | Priorité | Raison |
|----------|----------|--------|
| Parcours d'inscription testé | P0 | Sans ça = zéro conversion |
| Message WhatsApp transférable | P0 | Canal réel de diffusion parent-à-parent |
| End card avec TOUTES les infos | P0 | Dernier écran = dernière chance |
| Vidéo courte (hook + angle conversion) | P1 | Attire l'attention, ammo pour WhatsApp |
| FAQ parents | P1 | Réduit les questions répétitives |
| Vidéo longue (storytelling) | P2 | Notoriété, pas conversion directe |
| Variations / V2 / V3 | P3 | Seulement après validation client |
