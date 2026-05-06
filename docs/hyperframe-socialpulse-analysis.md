# SocialPulse × HyperFrame — Analyse & Plan d'Intégration

## Ce qu'est HyperFrame (résumé de la vidéo)

**HyperFrame** est un framework open-source qui transforme le montage vidéo en **prompting HTML/CSS**.

### Stack technique
- **HTML/CSS** = source de vérité (pas du pixel editing)
- **GSAP** (GreenSock) = moteur d'animation
- **Capture engine** = HTML → MP4
- **Skill .md** = instructions pour les agents IA (Claude Code, Codex, Cursor)
- **Studio** = éditeur vidéo avec timeline, code view, live preview

### Workflow (de la vidéo)
```
1. Filmer un one-shot (talking head)
2. Donner la vidéo à Claude Code + skill HyperFrame
3. L'agent:
   - Analyse la vidéo (transcription automatique)
   - Choisit les animations dans le catalogue
   - Génère le HTML/CSS/GSAP
   - Sous-titres, overlays, captures d'écran, barre de progression
4. Preview dans le Studio
5. Itérations via prompting (shift+click pour timestamp)
6. Render HTML → MP4
7. Publication directe
```

### Résultats du créateur
- YouTube: 50K vues
- Instagram: 28K vues
- TikTok: 41K vues
- Temps: ~30 min de prompting vs 2-3h de montage traditionnel

---

## Pourquoi c'est pertinent pour SocialPulse

### Le problème actuel
SocialPulse génère des **lead cards statiques** (infographies Kie.ai, emails texte, posts LinkedIn). Pour du lead gen B2B dans les professions régulées, on a besoin de contenu qui **capture l'attention** — surtout sur Instagram/LinkedIn.

### Ce qu'HyperFrame apporte
| Format | Avant (SocialPulse) | Après (+ HyperFrame) |
|--------|---------------------|----------------------|
| Lead card | Image statique | Vidéo animée 10s avec GSAP |
| Email d'approche | Texte + image | GIF/vidéo inline du risque |
| Post LinkedIn | Carousel d'images | Vidéo verticale animée |
| Rapport conformité | PDF statique | Walkthrough vidéo animé |
| Démo produit | Screenshots | Vidéo interactive HTML |

### Les 5 animations clés pour SocialPulse

1. **Caption animée** — Sous-titres style Karaoke mot par mot
   - Use case: Vidéos "3 risques IA pour les avocats" pour Instagram
   - Hook visuel au début

2. **Overlay compteur** — "1/3", "2/3", "3/3" flottant
   - Use case: Vidéo listicle des risques conformité par verticale

3. **Screenshot scroll** — Page web qui défile en arrière-plan
   - Use case: Montrer le site du prospect + l'alerte risque en overlay

4. **Keyword cards** — Mots-clés flottants (MCP, RGPD, AI Act...)
   - Use case: Vidéux éducatifs sur la conformité IA

5. **Progress bar** — Barre d'avancement en haut de la vidéo
   - Use case: Structure visuelle pour vidéos longues

---

## Architecture d'intégration

### Option A: MCP Tool (recommandé)

Ajouter un tool `hyperframe_compose` au MCP Cortex qui permet à n'importe quel agent de générer des compositions HTML animées.

```
┌──────────────┐    ┌────────────────────┐    ┌─────────────┐
│ Agent IA     │───▶│ MCP Tool           │───▶│ Render MP4  │
│ (pi/Claude)  │    │ hyperframe_compose  │    │ (local/cloud)│
│              │    │                    │    │             │
│ Prompt:      │    │ - Template HTML    │    │ HTML → MP4  │
│ "Vidéo lead  │    │ - GSAP animations  │    │ via Puppeteer│
│  card pour   │    │ - Style SocialPulse│    │ ou serveless │
│  avocat"     │    │ - Données lead     │    │             │
└──────────────┘    └────────────────────┘    └─────────────┘
```

### Option B: Skill pi (léger)

Créer un skill pi qui contient les templates HTML+GSAP et les règles de composition. L'agent génère le HTML, HyperFrame render.

### Option C: Hybride (recommandé pour production)

- Skill pi pour les templates et le style SocialPulse
- MCP tool pour la génération programmatique
- CLI HyperFrame pour le rendu

---

## Templates SocialPulse pour HyperFrame

### Template 1: Lead Card Animée
```html
<!-- Risque: {risk_type} | Verticale: {vertical} | Entreprise: {company} -->
<div data-composition-id="lead-card-{id}" data-start="0" data-duration="10">
  <div class="scene" id="scene1">
    <!-- Hook: compteur -->
    <div class="counter">⚠️ ALERTE CONFORMITÉ</div>

    <!-- Logo entreprise (animation GSAP) -->
    <div class="company-card">
      <h2>{company}</h2>
      <span>{vertical}</span>
    </div>

    <!-- Risque principal (slide-in) -->
    <div class="risk-card">
      <h1>{risk_type}</h1>
      <p>{risk_description}</p>
    </div>

    <!-- CTA (fade-in) -->
    <div class="cta">
      Audit gratuit → cortex-leman.com
    </div>
  </div>
</div>
```

### Template 2: Vidéo Listicle Conformité
```
Scène 1 (3s): Hook "3 risques IA pour {vertical}"
Scène 2 (3s): Risque #1 + screenshot outil
Scène 3 (3s): Risque #2 + overlay compteur
Scène 4 (3s): Risque #3 + keyword cards
Scène 5 (2s): CTA + logo Cortex Leman
Total: 14 secondes, format 9:16
```

### Template 3: Rapport Animé
```
Scène 1: Logo client + date
Scène 2: Score conformité (gauge animée)
Scène 3: Risques détectés (bar chart GSAP)
Scène 4: Recommandations (cards empilées)
Scène 5: CTA contact
```

---

## Comparaison: HyperFrame vs Kie.ai vs Higgsfield

| Critère | HyperFrame | Kie.ai | Higgsfield |
|---------|-----------|--------|------------|
| **Approche** | HTML/CSS → MP4 | API cloud vidéo | API cloud vidéo |
| **Contrôle** | Total (code) | Limité (prompt) | Limité (prompt) |
| **Coût** | Gratuit (local) | $0.005/crédit | Credits propriétaires |
| **Render** | CPU local | Cloud | Cloud |
| **Personnalisation** | Complète | Template API | Template API |
| **Agent-compatible** | ✅ Skill .md | ✅ MCP tool | ✅ MCP natif |
| **Cas d'usage** | Montage précis | Génération brute | Génération brute |
| **Brand consistency** | ✅ DESIGN.md | ❌ | ❌ |
| **Lead cards** | ✅ Templates custom | ❌ Générique | ❌ Générique |

### Verdict
- **HyperFrame** pour les vidéos SocialPulse (lead cards, listicles, rapports) — contrôle total, branding custom, gratuit
- **Kie.ai** pour la génération rapide d'images (infographies, thumbnails) — quand on a pas besoin d'animation
- **Higgsfield** pas nécessaire (Kie.ai couvre le même usage)

---

## Plan d'implémentation

### Phase 1: Templates HTML+GSAP (1 jour)
- [ ] Créer 3 templates SocialPulse (lead card, listicle, rapport)
- [ ] DESIGN.md avec palette Cortex Leman
- [ ] Tester les compositions dans le Studio HyperFrame

### Phase 2: MCP Tool (1 jour)
- [ ] Ajouter `hyperframe_compose` au MCP Cortex
- [ ] Handler qui merge données lead + template → HTML
- [ ] Endpoint de rendu HTML → MP4 (Puppeteer local ou API)

### Phase 3: Pipeline automatisé (1 jour)
- [ ] Workflow n8n: Trust Box → lead data → HyperFrame → vidéo → email
- [ ] Intégration SocialPulse: FACTURE étape génère vidéo au lieu d'image
- [ ] Preview dans le frontend SocialPulse

### Phase 4: Distribution (1 jour)
- [ ] Publication Instagram/LinkedIn via API
- [ ] A/B testing: image statique vs vidéo animée
- [ ] Metrics: taux d'ouverture email, engagement LinkedIn
