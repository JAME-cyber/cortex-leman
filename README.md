# Cortex Leman — Assets & Research

Workshop Tars. Opérations, recherche, et assets de production.

> **🗂️ Coordination inter-laptops:** voir [`DIVISION-TRAVAIL-TARS-OPENCODE.md`](./DIVISION-TRAVAIL-TARS-OPENCODE.md)
> — qui fait quoi entre Tars (raisonnement/structure) et OpenCode (sites web).

## Structure

```
├── index.html                     # Landing page (Cloudflare Pages)
├── cortex-leman/
│   └── docs/                      # Playbooks, moats, specs commerciales
│       ├── marketing-playbook.md
│       ├── moat-compliance-pitch.md
│       ├── agent-readiness-offer.md
│       ├── audit-prisme-live-spec.md
│       ├── evidence-ledger.md
│       └── evidence-ledger-template.json
├── sankofa/                       # Chaîne YouTube @sankofa-histoire
│   ├── prompt_template_seedance.md
│   ├── STRATEGIE_MONETISATION.md
│   ├── scripts/
│   │   ├── comment_manager.py     # Auto-reply commentaires (cron 6h)
│   │   └── comments_cron.sh       # Watchdog wrapper
│   ├── config/
│   │   └── commenters_db.example.json
│   └── video/
│       ├── mansa_moussa/          # Prompts Seedance
│       ├── amanirenas/            # Prompts Gemini Omni
│       └── baobab_kids/           # Pilote Anansi (contes africains kids)
└── research/                      # Veille signaux (tweets, outils, patterns)
```

## Chaînes

| Chaîne | Statut | Stack |
|---|---|---|
| **Sankofa** (@sankofa-histoire) | 8 vidéos publiques | Higgsfield (Shorts verticaux 4K) |
| **Baobab Kids** (TBD) | Pilote Anansi en prépa | Flova (long-form) + Higgsfield (assets) |

## Stack Vidéo

- **Higgsfield Plus** (€39/mo) — Nano Banana 2 illimité + 4K video gen
- **Flova** ($0.03/s) — Long-form 5-10min, AI Short Drama
- **Edge TTS** — Voix off FR
- **ffmpeg** — Assembly, sous-titres brûlés

## Patterns Production

Patterns distillés du brief Higgsfield "Cully Hill Boys" ($1M R&D, 137 plans) :
Skill Hermes `ai-film-production-bible` — 15-block prompt skeleton, character sheets 3-panel, optics FOV degrés, ~150 locks nommés.

## Licence

MIT — sauf assets clients (AlConst).
