#!/usr/bin/env python3
"""
Contre-analyse externe via OpenRouter (GPT-5.5).
Demande à un LLM tiers de stress-tester l'analyse initiale nanocorp.so vs Cortex Leman v5.
"""
import json
import os
import sys
import urllib.request

API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL = "openai/gpt-5.5"

CONTEXTE_CORTEX = """
PROJET: Cortex Leman v5 « Graphe de Confiance »
MISSION: Réduire le risque de non-conformité IA pour les PME franco-suisses (professions régulées).
6 verticales métier: comptable, avocat, santé, banque, startup, rh.
Deux modes de déploiement: Standard (cloud/OpenRouter) et Haute Protection (Edge/Ollama, zero appel externe).
Architecture: Orchestrateur conversationnel + 5 agents (Data, Raisonnement, Action, Superviseur) pair-à-pair asynchrones via NATS JetStream + 1 MÉDIATEUR déterministe (JsonLogic, JAMAIS de LLM) qui peut GELER une intention.
Principes clés: Humain arbitre, pas valideur. Déterministe par défaut, LLM par exception. Journal WORM hash-chainé. Conformité RGPD + AI Act + secret professionnel FR-CH (art. 321 CP avocat, art. 47 LB banque, nLPD Suisse).
Tech: Python 3.12, FastAPI, Pydantic, NATS JetStream, Redis, Ollama, K3s, Docker.
Statut roadmap: Sprint 0-3 ✅, Phase 1A (Trust Box API) ✅, Phase 1B/1C (dashboards) 📋, Phases 2-4 📋.
"""

FAITS_NANOCORP = """
NANOCORP.so (YC W24):
- Plateforme créant des « entreprises autonomes gérées par IA ». Un prompt → un agent-CEO construit le produit, déploie un site Vercel, configure Stripe avec pricing tiers, lance cold email + prospection Apollo, et (plan Founder $120/mois) des pubs Meta.
- Architecture: 1 agent CEO qui délègue à des worker agents spécialisés dans des sandbox Linux isolés (Python/Node/Git). 1 tâche par compagnie à la fois. PostgreSQL dédié par compagnie, browser automation, code execution.
- Cloud-only, FERMÉ: pas de self-host, pas de choix de modèle, pas d'export de code/DB, Stripe proxifié via le compte NanoCorp, pas de data residency, pas de mention régulation/secret professionnel.
- Monétisation: credits-based (~1 crédit/tâche), plans jusqu'à $120/mois.
- Traction affichée: $264 revenus réels / 29 transactions sur 7 compagnies (compteur marketing). Presse: Maddyness, Alexis Bouchez.
- Discours: « no human intervention », « maximiser le revenu, éviter la faillite », « making money while you sleep ».
- Limites connues: pas d'auto mode (chaque étape approuvée manuellement selon la revue Alexis Bouchez), duplication de tâches récurrente, pas de réseaux sociaux, pas d'apps mobiles, pas de self-host.
"""

ANALYSE_INITIALE = """
ANALYSE INITIALE (par l'assistant Cortex Leman) — RÉSUMÉ:
1. Opposition philosophique: NanoCorp (« no human ») vs Cortex Leman (« humain arbitre »). Pas concurrents, contre-exemples.
2. NanoCorp ne peut juridiquement pas servir avocat/banque/santé (données chez tiers, pas de data residency, pas de secret pro).
3. À prendre de NanoCorp (UX): interface conversationnelle « parle à ton CEO », dashboard multi-entités temps réel, transparence visuelle des tâches, pricing credits-based pour mode Standard, déploiement Stripe-early, pattern worker-sandbox.
4. Vulnérabilités Cortex Leman: perception de lenteur, traction/validité marché inférieure, récit plus complexe à pitcher, érosion du référentiel mental (NanoCorp normalise l'autonomie totale), risque qu'un DRH veuille l'autonomie NanoCorp.
5. Kill factors: pivot régulé de NanoCorp, commoditisation du discours conformité, rejet du modèle humain-arbitre par fatigue.
6. Verdict: OUI MAIS — NanoCorp = contre-exemple stratégique + source UX limitée. Ne pas copier la philosophie, copier l'UX. Moat = Médiateur déterministe + journal WORM + Haute Protection Edge.
7. Recommandations: forger un contre-récit public, accélérer Phase 1B/1C, Orchestrateur conversationnel prioritaire, quantifier le moat, pricing hybride.
"""

PROMPT = f"""Tu es un analyste stratégique EXPÉRIMENTÉ et SCEPTIQUE, spécialisé en go-to-market legaltech/regtech et en IA agents. Ta mission: CONTRE-ANALYSER de façon agressive et honnête l'analyse ci-dessous. Tu es l'avocat du diable, PAS un valideur.

Ne so pas polissez rien. Identifie:
- Les hypothèses fausses ou non démontrées de l'analyse initiale
- Les angles morts (ce qu'elle a manqué)
- Les contradictions internes
- Les biais (ex: biais de confirmation en faveur du projet Cortex Leman)
- Les risques que l'analyste a sous-estimés ou sur-estimés
- Où l'analyse initiale a POSSIBLEMENT TORT

Sois concret, cite des éléments précis. Si tu penses que NanoCorp est en réalité une MENACE plus grande que ce que dit l'analyse, dis-le. Si tu penses que le « moat » de Cortex Leman est plus faible que prétendu, dis-le. Si tu penses que la stratégie recommandée est mauvaise, dis-le.

Structure ta réponse ainsi:
## 1. OÙ L'ANALYSE INITIALE A RAISON
## 2. OÙ L'ANALYSE INITIALE A TORT (le cœur de ta contre-analyse)
## 3. CE QUE L'ANALYSE A MANQUÉ (angles morts)
## 4. RÉÉVALUATION DE LA MENACE NANOCORP (1-10, justifié)
## 5. RÉÉVALUATION DU MOAT CORTEX LEMAN (1-10, justifié)
## 6. TON VERDICT HONNÊTE (différent ou identique, mais justifié)

---
CONTEXTE PROJET CORTEX LEMAN v5:
{CONTEXTE_CORTEX}

FAITS NANOCORP.so:
{FAITS_NANOCORP}

ANALYSE À CONTRE-ANALYSER:
{ANALYSE_INITIALE}
"""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "Tu es un analyste stratégique rigoureux, franc, indépendant. Tu n'as aucun intérêt à flatter le projet Cortex Leman. Réponds en français."},
        {"role": "user", "content": PROMPT},
    ],
    "temperature": 0.7,
}

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://cortex-leman.local",
        "X-Title": "Cortex Leman v5 - Contre-analyse",
    },
)

try:
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    msg = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    print(msg)
    print("\n\n--- META ---")
    print(f"Modèle: {data.get('model', MODEL)}")
    print(f"Tokens in/out: {usage.get('prompt_tokens')} / {usage.get('completion_tokens')}")
except urllib.error.HTTPError as e:
    print(f"ERREUR HTTP {e.code}:", e.read().decode(), file=sys.stderr)
    sys.exit(1)
