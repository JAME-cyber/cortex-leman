# Cortex Leman v5 — Graphe de Confiance

> Infrastructure de confiance pour professions régulées FR-CH
> Pipeline 5 étapes → Graphe d'agents dynamiques avec Médiateur transverse

## Architecture

```
[Interface Arbitrage] ◄──► [Orchestrateur Conversationnel]
                                    │
                            [Journal Append-Only]
                                    │
                    [Bus NATS JetStream (pair-à-pair)]
                     │              │              │
              [Agent Data]  [Agent Raisonnement]  [Agent Action]
                     │              │              │
                     └──────┬───────┘              │
                            ▼                      │
                   [Agent Médiateur] ──gel──► [Arbitrage Humain]
                            │
                   [Circuit Breakers / Saga / Locks]
```

## 4 Piliers

| Pilier | Module | Description |
|--------|--------|-------------|
| 1. Graphe dynamique | `core/bus/`, `core/journal/`, `core/orchestrator/` | Bus NATS + Journal WORM + Orchestrateur événementiel |
| 2. Médiateur | `core/mediator/`, `core/security/` | Moteur JsonLogic + Circuit breakers + Saga |
| 3. Arbitrage humain | `core/arbitration/` | Dashboard contradictoire + Signature + Horodatage |
| 4. Edge hybride | `edge/` | K3s appliance + Ollama local + Compliance Gateway |

## Démarrage rapide

```bash
# Développement (nécessite NATS + Redis)
docker compose up -d nats redis
pip install -r requirements.txt
python -m api.main

# Edge (K3s appliance)
bash edge/k3s-install.sh
bash edge/ollama-setup.sh
```

## Verticales supportées

Comptable · Avocat · Santé · Banque · Startup · RH

## Conformité

- AI Act (Limited / High)
- RGPD Art. 22 (anti-biais)
- Secret professionnel (Art. 321 CP, Art. 47 LB, LPM)
- Data Residency (CH / EU)
- ISO/IEC 42001 (prêt pour certification)
