# Analyse Genspark AI → Cortex Leman v5
# Comparaison stratégique et différenciation

## Source
Bing search results, Wikipedia, OpenAI case study, Liora.io, Clubic, Bitrue
Dernière mise à jour : Avril 2026

---

## 1. QU'EST GESNSPARK AI ?

### Résumé
Genspark AI est un **"Super Agent" IA tout-en-un** — un espace de travail IA qui :
- Transforme un prompt en **action** (pas juste du texte)
- Mène de la **recherche approfondie** (remplacement Google)
- Crée du contenu : **slides, documents, images, vidéos, code, design**
- Passe des **appels téléphoniques** réels
- Fonctionne comme un **browser** dédié (Genspark Browser)
- Utilise **GPT-4.1** (OpenAI) comme moteur
- A fait un **Super Bowl commercial** avec Matthew Broderick

### Concept clé : "Sparkpages"
Genspark génère des **Sparkpages** — des pages web dynamiques créées par l'IA
en temps réel à partir d'une requête. Au lieu d'une liste de liens (Google),
l'utilisateur obtient une **page complète** avec :
- Synthèse sourcée
- Tableaux comparatifs
- Recommandations
- Liens intégrés

### Produits
1. **Genspark AI Workspace** — app mobile + web (iOS, Android, web)
2. **Genspark Browser** — navigateur dédié avec IA intégrée
3. **Super Agent** — agents personnalisables sans code (GPT-4.1)
4. **Sparkpages** — pages de recherche augmentée

### Positionnement
- **Grand public + PME** (B2C/B2B mixte)
- **Horizontal** (tout usage confondu)
- **US-first**, expansion mondiale
- **Gratuit** avec premium
- **Tech stack** : GPT-4.1, browser, mobile

---

## 2. COMPARAISON DIRECTE

| Dimension | Genspark AI | Cortex Leman v5 |
|---|---|---|
| **Type** | Super Agent IA grand public | Infrastructure de confiance IA réglementée |
| **Target** | Grand public + PME horizontales | Professions réglementées FR-CH (6 verticals) |
| **Modèle** | Freemium B2C | B2B SaaS (49-299€/mois) |
| **LLM** | GPT-4.1 (OpenAI) | OpenRouter multi-modèles + Ollama local |
| **Architecture** | Monolithe cloud | Graphe de confiance (6 agents spécialisés) |
| **Recherche** | Sparkpages (remplace Google) | RAG ChromaDB (knowledge vault réglementaire) |
| **Exécution** | Appels téléphoniques, création contenu | Exécution transactionnelle + Saga compensation |
| **Audit** | Aucun | Journal WORM hash-chainé SHA-256 |
| **Conformité** | Aucune mention | RGPD, AI Act, CP 321, LB 47, LPM |
| **Médiateur** | Aucun | JsonLogic 22 règles, 0% LLM |
| **Arbitrage** | Aucun | Humain obligatoire sur gel |
| **Guardrails** | Aucun visible | PII detection, topic control, output safety |
| **Secret pro** | ❌ Aucun | ✅ Avocat, banquier, médecin |
| **Mode local** | ❌ Cloud only | ✅ K3s + Ollama (Haute Protection) |
| **Data residency** | ❌ US | ✅ CH/EU au choix |
| **Journal** | ❌ Aucun | ✅ WORM + HMAC + hash-chain |
| **RBAC** | ❌ Basic | ✅ 4 rôles, 8 ressources, permissions matrix |
| **Chiffrement** | ❌ Non documenté | ✅ Fernet at-rest, JWT, bcrypt |
| **Monitoring** | ❌ Non documenté | ✅ Prometheus 11 métriques + Grafana |
| **CI/CD** | ❌ Non documenté | ✅ GitHub Actions 5 jobs |
| **Tests** | ❌ Non documenté | ✅ 159 tests automatisés |
| **Open source** | ❌ Propriétaire | ✅ Architecture documentée |
| **Browser** | ✅ Navigateur dédié | ❌ Web app standard |
| **Mobile** | ✅ iOS + Android natifs | ❌ Web responsive (prévu Sprint 5) |
| **Appels téléphoniques** | ✅ Via agent | ❌ Non prévu |
| **Sparkpages** | ✅ Pages dynamiques | ❌ Chat + dashboard |
| **Création contenu** | ✅ Slides, images, vidéos | ❌ Analyse + conformité |
| **Super Bowl ad** | ✅ Matthew Broderick 🏈 | ❌ 0€ marketing |

---

## 3. ANALYSE DES DIFFÉRENCES FONDAMENTALES

### A. Paradigme complètement différent

```
Genspark = "Je fais tout pour vous" (exécution déléguée)
Cortex Leman = "Je fais tout pour vous, mais avec preuve et contrôle"
```

Genspark est un **productivité tool**.
Cortex Leman est une **infrastructure de conformité**.

Ce n'est PAS le même marché. C'est comme comparer :
- **Google Docs** vs **SAP** → pas le même usage
- **ChatGPT** vs **Thomson Reuters** → pas le même client

### B. Genspark NE PEUT PAS servir les professions réglementées

Pourquoi un avocat français ne peut PAS utiliser Genspark :

1. **Art. 321 CP** → Le secret professionnel implique qu'aucune donnée client ne quitte le cabinet.
   Genspark envoie TOUT à GPT-4.1 (US). ❌ Illégal.

2. **RGPD** → Les données doivent rester en EU/CH. Genspark = US. ❌ Non conforme.

3. **AI Act** → Pas de gestion des risques IA. ❌ Non conforme.

4. **Audit trail** → Aucun journal. En cas de contrôle, l'avocat ne peut rien prouver. ❌

5. **Responsabilité** → Si Genspark fait une erreur, qui est responsable ? Pas de traçabilité. ❌

### C. Ce que Genspark fait bien (à inspirer)

| Feature Genspark | Ce qu'on peut en tirer |
|---|---|
| **Sparkpages** → pages dynamiques | Rapports de conformité auto-générés |
| **Appels téléphoniques** → agent vocal | Alertes proactives par SMS/email |
| **Browser dédié** → expérience intégrée | Dashboard Cortex Leman en mode kiosk |
| **Super Agent** → personnalisable | Nos agents spécialisés par vertical |
| **Mobile natif** → iOS/Android | Sprint 5 : PWA + Electron/Tauri |
| **Onboarding 60s** → friction zéro | Wizard 5 minutes guidé par vertical |
| **Création slides** → output riche | Rapports PDF auto-générés |

---

## 4. CARTOGRAPHIE DES MARCHÉS

```
                    ┌─────────────────────────────────────────────┐
                    │           GRAND PUBLIC / B2C                 │
                    │                                              │
                    │   ChatGPT   Gemini   Claude   Genspark       │
                    │   Perplexity  Co-pilot  You.com              │
                    │                                              │
                    │   → Usage personnel, productivité            │
                    │   → Zero conformité                          │
                    │   → Zero audit trail                         │
                    └─────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────┐
                    │           PME HORIZONTALES / B2B             │
                    │                                              │
                    │   Accio Work  Genspark Pro  Notion AI        │
                    │   Zapier AI   n8n AI                         │
                    │                                              │
                    │   → E-commerce, marketing, ops               │
                    │   → Zero conformité réglementaire            │
                    │   → Zero secret professionnel                │
                    └─────────────────────────────────────────────┘

          ╔═════════════════════════════════════════════════════════╗
          ║   PROFESSIONS RÉGLEMENTÉES FR-CH / B2B VERTICAL       ║
          ║                                                        ║
          ║   ★ CORTEX LEMAN V5 ★                                 ║
          ║                                                        ║
          ║   → Avocats, comptables, banquiers, médecins          ║
          ║   → Startups réglementées, RH                         ║
          ║   → Conformité native (RGPD, AI Act, CP 321, LB 47)  ║
          ║   → Audit trail WORM, arbitrage humain                ║
          ║   → Mode local/offline                                ║
          ║                                                        ║
          ║   → Marché : ~300K cabinets FR + ~50K CH              ║
          ║   → AUCUN concurrent direct identifié                 ║
          ╚═══════════════════════════════════════════════════════╝
```

**Conclusion : Genspark et Cortex Leman ne sont PAS concurrents.**
Ils opèrent sur des marchés différents, avec des clients différents,
des exigences différentes, et des architectures différentes.

---

## 5. POSITIONNEMENT MARKETING

### Contre-Genspark (dans notre landing/communication)

```
"Genspark est parfait pour rechercher un restaurant ou créer des slides.
Mais pour votre cabinet d'avocat ? Il envoie vos données client
à GPT-4.1 aux États-Unis. Article 321 du Code Pénal : 1 an de prison
et 15 000€ d'amende.

Cortex Leman : votre IA reste chez vous. Mode Haute Protection,
Ollama local, zéro appel cloud. Conformité native."
```

### Notre différentiateur unique

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   "Le Super Agent est cool. Le Super Agent certifié est mieux."║
║                                                               ║
║   Genspark : "Je fais votre recherche"                        ║
║   Cortex Leman : "Je fais votre conformité, avec preuves"     ║
║                                                               ║
║   Genspark : Zero audit trail                                 ║
║   Cortex Leman : WORM + SHA-256 + HMAC + hash-chain           ║
║                                                               ║
║   Genspark : Cloud US                                         ║
║   Cortex Leman : Local CH/EU ou Cloud EU                      ║
║                                                               ║
║   Genspark : Trust the AI                                     ║
║   Cortex Leman : Verify the AI (arbitrage humain)             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 6. CE QU'ON INSPIRE DE GENSPARK

### Court terme (à ajouter au backlog)
1. **"Sparkpages" → "Compliance Reports"** : Génération auto de rapports
   de conformité en PDF (audit annuel, déclaration AI Act, rapport RGPD)
2. **Onboarding rapide** : Genspark = 60s. Nous = wizard 5 min par vertical
3. **Mobile** : Genspark a iOS + Android. Nous devons prioriser PWA Sprint 5
4. **Rich output** : Slides → Rapports de conformité visuels

### Moyen terme
5. **Browser extension** : Genspark Browser → Extension Chrome qui detecte
   les problèmes de conformité sur les pages visitées
6. **Voice** : Genspark fait des appels → Nous : alertes vocales pour gel
7. **Super Agent personnalisable** : Nos agents par vertical sont déjà
   spécialisés, mais le "no-code customisation" serait un plus

### Ne PAS copier
- ❌ Cloud-only (incompatible avec secret professionnel)
- ❌ GPT-4.1 unique (risque de dépendance, data residency)
- ❌ Pas de journal (incompatible avec audit)
- ❌ Pas de médiateur (incompatible avec certification)
- ❌ Grand public (pas notre marché)

---

## 7. CONCLUSION

### Genspark en une phrase
> "Genspark est un super-agent IA pour le grand public et les PME horizontales.
> Il excelle en productivité mais ignore totalement la conformité réglementaire."

### Cortex Leman en une phrase
> "Cortex Leman est une infrastructure de confiance IA pour les professions
> réglementées franco-suisses, avec audit trail natif, arbitrage humain
> et mode local offline."

### Pourquoi on gagne dans NOTRE marché
1. **Barrière réglementaire** : Genspark ne PEUT PAS servir les avocats (CP 321),
   banquiers (LB 47), médecins (LPM) — leur architecture le rend impossible.
2. **Barrière de confiance** : Aucun journal d'audit = aucune certification possible.
3. **Barrière de localisation** : Data residency US = non conforme RGPD/CH.
4. **Zero concurrent** : Sur le créneau "IA agentique + conformité réglementée FR-CH",
   il n'existe AUCUN produit sur le marché.

### Risque Genspark
- Si Genspark ajoute la conformité EU → nous devons avoir 12 mois d'avance.
- Si Genspark propose un mode "enterprise EU" → nous devons avoir notre
  certification en cours.
- **Mitigation** : Aller vite. Premier sur le marché = avantage durable.
