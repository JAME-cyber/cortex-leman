#!/usr/bin/env python3
"""
Cortex Leman v5 — Test Pipeline Complet (sans NATS)

Pipeline: Intention → Routeur → Agent Data → Agent Raisonnement → Médiateur → Arbitrage
"""
import asyncio
import json
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(name)s — %(message)s")
logger = logging.getLogger("pipeline-test")


async def run_pipeline():
    from core.orchestrator.intention import intention_store
    from core.orchestrator.router import router
    from core.integrations.llm.provider import LLMService

    llm = LLMService()

    # ── Scénario métier réel ──────────────────────────────────────
    scenario = {
        "client_id": "cabinet-dupont-001",
        "vertical": "comptable",
        "query": "Notre cabinet utilise ChatGPT pour analyser les bilans fiscaux de nos clients. "
                 "Nous devons déterminer si cette pratique est conforme au RGPD, à l'AI Act et au "
                 "secret professionnel. Impact estimé : 450 clients, montant fiscal moyen 25 000€.",
        "context": {
            "nb_clients": 450,
            "montant_moyen": 25000,
            "outil": "ChatGPT (OpenAI)",
            "usage": "analyse bilans fiscaux",
        },
    }

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     CORTEX LEMAN v5 — PIPELINE COMPLET (DeepSeek V4)       ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print()
    print(f"  Client:    {scenario['client_id']}")
    print(f"  Verticale: {scenario['vertical']}")
    print(f"  Requête:   {scenario['query'][:80]}...")
    print(f"  Modèle:    {llm._provider._model}")
    print()

    # ── ÉTAPE 1: Créer l'intention ────────────────────────────────
    print("━" * 62)
    print("  ÉTAPE 1/6 — Création de l'intention")
    print("━" * 62)

    intention = intention_store.create(
        client_id=scenario["client_id"],
        vertical=scenario["vertical"],
        query=scenario["query"],
        context=scenario["context"],
    )
    print(f"  ✅ Intention créée: {intention.intention_id[:12]}...")
    print(f"     Version: {intention.version} | Statut: {intention.status}")
    print()

    # ── ÉTAPE 2: Routage dynamique ────────────────────────────────
    print("━" * 62)
    print("  ÉTAPE 2/6 — Routage dynamique (CaptainAgent)")
    print("━" * 62)

    routing = router.route(intention)
    team = router.assemble_team(intention)

    print(f"  Routage individuel:")
    for agent, active in routing.items():
        icon = "✅" if active else "⬜"
        print(f"    {icon} {agent}")
    print()
    print(f"  Équipe assemblée (CaptainAgent):")
    print(f"    Team ID:  {team.team_id}")
    print(f"    Membres:  {', '.join(team.agents)}")
    print(f"    Lead:     {team.lead}")
    print(f"    Raison:   {team.reason}")
    print()

    # ── ÉTAPE 3: Agent Data — Collecte & analyse ─────────────────
    print("━" * 62)
    print("  ÉTAPE 3/6 — Agent Data (collecte + LLM)")
    print("━" * 62)
    t0 = time.time()

    data_result = await llm.generate_for_agent(
        agent_name="data",
        task=(
            f"Pour le cabinet {scenario['client_id']}, collecte et analyse les données suivantes:\n"
            f"- Nombre de clients impactés: {scenario['context']['nb_clients']}\n"
            f"- Montant fiscal moyen: {scenario['context']['montant_moyen']}€\n"
            f"- Outil IA utilisé: {scenario['context']['outil']}\n"
            f"- Usage: {scenario['context']['usage']}\n\n"
            f"Identifie:\n"
            f"1. Les types de données personnelles traitées\n"
            f"2. Les flux de données vers des tiers\n"
            f"3. Le niveau de risque par catégorie de données\n"
            f"4. Le montant total d'exposition financière"
        ),
        context=scenario["context"],
        vertical=scenario["vertical"],
        client_id=scenario["client_id"],
        intention_id=intention.intention_id,
        use_rag=False,
    )
    t_data = time.time() - t0

    print(f"  ⏱  Temps: {t_data:.1f}s | Tokens: {data_result.get('tokens', 0)}")
    print(f"  📊 Résultat:")
    for line in data_result.get("text", "").split("\n")[:30]:
        print(f"    {line}")
    if data_result.get("error"):
        print(f"  ❌ Erreur: {data_result['error']}")
    print()

    # ── ÉTAPE 4: Agent Raisonnement — Analyse conformité ─────────
    print("━" * 62)
    print("  ÉTAPE 4/6 — Agent Raisonnement (analyse LLM)")
    print("━" * 62)
    t0 = time.time()

    reasoning_result = await llm.generate_for_agent(
        agent_name="reasoning",
        task=(
            f"Analyse de conformité complète pour le cabinet {scenario['client_id']}.\n\n"
            f"CONTEXTE:\n"
            f"- {scenario['context']['nb_clients']} clients impactés\n"
            f"- Montant moyen: {scenario['context']['montant_moyen']}€\n"
            f"- Outil: {scenario['context']['outil']}\n"
            f"- Usage: {scenario['context']['usage']}\n\n"
            f"DONNÉES COLLECTÉES (Agent Data):\n"
            f"{data_result.get('text', 'N/A')}\n\n"
            f"Produis une analyse structurée avec:\n"
            f"1. Score de risque global (0-100)\n"
            f"2. Conformité RGPD (Art. 5, 6, 13, 22, 35)\n"
            f"3. Conformité AI Act (Art. 50, risque limité/haut)\n"
            f"4. Secret professionnel (Art. 226-13 CP FR, Art. 321 CP CH)\n"
            f"5. Recommandations priorisées\n"
            f"6. Plan d'action à 30/60/90 jours\n\n"
            f"Format JSON structuré attendu."
        ),
        context={
            **scenario["context"],
            "data_agent_result": data_result.get("text", ""),
        },
        vertical=scenario["vertical"],
        client_id=scenario["client_id"],
        intention_id=intention.intention_id,
        use_rag=False,
    )
    t_reason = time.time() - t0

    print(f"  ⏱  Temps: {t_reason:.1f}s | Tokens: {reasoning_result.get('tokens', 0)}")
    print(f"  🧠 Résultat:")
    for line in reasoning_result.get("text", "").split("\n")[:40]:
        print(f"    {line}")
    if reasoning_result.get("error"):
        print(f"  ❌ Erreur: {reasoning_result['error']}")
    print()

    # ── ÉTAPE 5: Médiateur — Vérification & règles ───────────────
    print("━" * 62)
    print("  ÉTAPE 5/6 — Médiateur (règles + gel)")
    print("━" * 62)

    from core.mediator.rules_engine import rules_engine
    rules_engine.load_rules()
    rules_result = rules_engine.evaluate(scenario["vertical"], scenario["context"])

    print(f"  Règles évaluées: {len(rules_result)}")
    triggered = [r for r in rules_result if r.triggered]
    print(f"  Règles déclenchées: {len(triggered)}")
    for r in rules_result:
        icon = "⚠️ " if r.triggered else "✅"
        print(f"    {icon} [{r.severity:7s}] {r.rule_id}: {r.message[:60]}")

    # Simuler la logique de gel du Médiateur
    amount = scenario["context"]["montant_moyen"]
    sensitive = scenario["vertical"] in {"comptable", "avocat", "banque", "sante"}
    should_freeze = sensitive and amount >= 10000

    print()
    if should_freeze:
        print(f"  🔶 GEL AUTOMATIQUE — Verticale sensible ({scenario['vertical']}) "
              f"avec montant ≥ 10 000€ ({amount}€)")
        intention_store.freeze(intention.intention_id)
        print(f"  ❄️  Intention {intention.intention_id[:12]}... GELÉE")
        print(f"     → Arbitrage humain requis")
    else:
        print(f"  ✅ Aucun gel automatique nécessaire")

    conflict_detected = len(triggered) > 0 or should_freeze
    print()

    # ── ÉTAPE 6: Arbitrage humain (simulation) ────────────────────
    print("━" * 62)
    print("  ÉTAPE 6/6 — Arbitrage humain")
    print("━" * 62)

    if conflict_detected:
        print("  📋 Dossier contradictoire préparé pour l'arbitre:")
        print(f"     Position Agent Data:      Analyse {scenario['context']['nb_clients']} clients, "
              f"exposition {scenario['context']['nb_clients'] * scenario['context']['montant_moyen']:,}€")
        print(f"     Position Agent Raisonnement: Score de risque, recommandations conformité")
        print(f"     Position Médiateur:        {'Conflit détecté' if triggered else 'Gel préventif'}")
        print()

        # Simulation d'une décision d'arbitrage
        print("  ⚖️  Décision simulée de l'arbitre (expert-comptable):")
        print('     → APPROUVE AVEC CONDITIONS')
        print('     → Plan de mise en conformité obligatoire sous 60 jours')
        print('     → DPO désigné, consentements clients à recueillir')

        intention_store.unfreeze(intention.intention_id)
        intention_store.complete(intention.intention_id)
    else:
        print("  ✅ Aucun arbitrage nécessaire — flux complet")
        intention_store.complete(intention.intention_id)
    print()

    # ── BILAN FINAL ───────────────────────────────────────────────
    final = intention_store.get(intention.intention_id)
    total_time = t_data + t_reason
    total_tokens = data_result.get("tokens", 0) + reasoning_result.get("tokens", 0)

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    BILAN DU PIPELINE                        ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print(f"  Intention:     {intention.intention_id[:12]}...")
    print(f"  Statut final:  {final.status} (v{final.version})")
    print(f"  Agents activés: {', '.join(team.agents)}")
    print(f"  Lead:          {team.lead}")
    print(f"  Conflit:       {'OUI ⚠️' if conflict_detected else 'NON ✅'}")
    print(f"  Arbitrage:     {'OUI ⚖️' if conflict_detected else 'NON'}")
    print(f"  ────────────────────────────────────────────")
    print(f"  Modèle LLM:    {llm._provider._model}")
    print(f"  Temps total:   {total_time:.1f}s")
    print(f"  Tokens total:  {total_tokens}")
    print(f"  Agent Data:    {t_data:.1f}s ({data_result.get('tokens', 0)} tokens)")
    print(f"  Agent Raisonnement: {t_reason:.1f}s ({reasoning_result.get('tokens', 0)} tokens)")
    print("╚══════════════════════════════════════════════════════════════╝")

    return {
        "intention_id": intention.intention_id,
        "status": final.status,
        "team": team.to_dict(),
        "conflict": conflict_detected,
        "tokens": total_tokens,
        "time": total_time,
        "model": llm._provider._model,
    }


if __name__ == "__main__":
    result = asyncio.run(run_pipeline())
    print(f"\n🏁 Pipeline terminé — {result['status']}")
