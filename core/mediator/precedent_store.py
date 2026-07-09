"""
Cortex Leman v5 — PrecedentStore (Jurisprudence IA)

Chaque arbitrage humain crée un précédent qui enrichit le Médiateur.
Les précédents peuvent être promus en règles JsonLogic candidates.

Inspiré de:
- La common law (stare decisis)
- Le Codex Harness d'OpenAI (le modèle apprend de son environnement)
- Notre doc PENSEE-DIVERGENTE.md (Concept 4: Jurisprudence IA)

Cycle de vie:
  1. Arbitrage humain → ARBITRATION_PRECEDENT journal entry
  2. PrecedentStore.capture() → stocke le précédent
  3. Médiateur.query_precedents() → matching avant évaluation règles
  4. Si 3+ précédents similaires → suggestion de promotion en règle
  5. Expert valide → règle JsonLogic candidate ajoutée

Force des précédents:
  - NONE: pas de valeur de précédent
  - WEAK: 1 précédent similaire (guidance)
  - MEDIUM: 2 précédents similaires (recommandation forte)
  - STRONG: 3+ précédents similaires → suggestion de promotion en règle
"""
import json
import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from core.config import settings
from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


# ── Models ────────────────────────────────────────────────────

class PrecedentStrength(str, Enum):
    NONE = "none"
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


class PrecedentStatus(str, Enum):
    ACTIVE = "active"
    PROMOTED = "promoted"   # Devenu une règle JsonLogic
    OVERRIDDEN = "overridden"  # Invalide par un arbitrage ultérieur
    ARCHIVED = "archived"


class Precedent(BaseModel):
    """Un précédent créé par un arbitrage humain."""
    precedent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conflict_id: str
    intention_id: str
    client_id: str
    vertical: str
    question: str  # La question/ambiguïté soumise
    conflict_reason: str
    agent_positions: dict  # {agent_name: position}
    arbiter_id: str  # Qui a décidé
    arbiter_name: str
    decision: str  # approve | reject | modify
    justification: str
    selected_position: str  # Agent choisi
    strength: PrecedentStrength = PrecedentStrength.WEAK
    status: PrecedentStatus = PrecedentStatus.ACTIVE
    # Matching: signature du contexte pour retrouver les précédents similaires
    context_signature: str = ""  # hash(vertical + question_type + action_type)
    rule_id_source: Optional[str] = None  # Règle qui a causé le gel (si applicable)
    regulatory_references: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    matched_count: int = 0  # Nombre de fois que ce précédent a été matché
    promoted_to_rule: Optional[str] = None  # ID de la règle créée si promotion


class PrecedentMatch(BaseModel):
    """Résultat d'une recherche de précédents."""
    precedent: Precedent
    relevance: float  # 0.0-1.0
    match_reason: str


class RuleCandidate(BaseModel):
    """Candidat à une nouvelle règle JsonLogic, généré automatiquement."""
    candidate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vertical: str
    source_precedent_ids: list[str]
    suggested_condition: dict  # JsonLogic condition
    suggested_action: str  # freeze | warn | arbitrate
    suggested_severity: str  # low | medium | high | critical
    suggested_message: str
    status: str = "pending"  # pending | approved | rejected
    reviewed_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Store ─────────────────────────────────────────────────────

class PrecedentStore:
    """
    Store de jurisprudence IA pour Cortex Leman.

    Stocke les précédents, les recherche par similarité,
    et suggère des promotions en règles quand 3+ précédents
    couvrent le même pattern.
    """

    def __init__(self, persist_path: Optional[str] = None):
        self._path = Path(persist_path or settings.arbitration_precedent_file)
        self._precedents: dict[str, Precedent] = {}
        self._candidates: dict[str, RuleCandidate] = {}
        self._load()

    # ── Persistance ──────────────────────────────────────

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            for pid, pdata in data.get("precedents", {}).items():
                self._precedents[pid] = Precedent(**pdata)
            for cid, cdata in data.get("candidates", {}).items():
                self._candidates[cid] = RuleCandidate(**cdata)
            logger.info(f"PrecedentStore: {len(self._precedents)} précédents, "
                        f"{len(self._candidates)} candidats chargés")
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"PrecedentStore: échec chargement: {e}")

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "precedents": {
                    pid: p.model_dump(mode="json")
                    for pid, p in self._precedents.items()
                },
                "candidates": {
                    cid: c.model_dump(mode="json")
                    for cid, c in self._candidates.items()
                },
            }
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(data, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            tmp.replace(self._path)  # atomic
        except Exception as e:
            logger.error(f"PrecedentStore: échec persistance: {e}")

    # ── Capture ──────────────────────────────────────────

    def capture(
        self,
        conflict_id: str,
        intention_id: str,
        client_id: str,
        vertical: str,
        question: str,
        conflict_reason: str,
        agent_positions: dict,
        arbiter_id: str,
        arbiter_name: str,
        decision: str,
        justification: str,
        selected_position: str,
        rule_id_source: Optional[str] = None,
        regulatory_references: Optional[list[str]] = None,
    ) -> Precedent:
        """
        Capturer un arbitrage comme précédent.

        Appelé après chaque arbitrage humain résolu.
        Journalise dans le WORM et persiste le précédent.
        """
        # Calculer la signature de contexte
        context_signature = self._compute_signature(
            vertical, question, conflict_reason, rule_id_source
        )

        # Déterminer la force initiale
        similar = self._find_similar(context_signature, vertical)
        if len(similar) >= 3:
            strength = PrecedentStrength.STRONG
        elif len(similar) >= 2:
            strength = PrecedentStrength.MEDIUM
        else:
            strength = PrecedentStrength.WEAK

        precedent = Precedent(
            conflict_id=conflict_id,
            intention_id=intention_id,
            client_id=client_id,
            vertical=vertical,
            question=question,
            conflict_reason=conflict_reason,
            agent_positions=agent_positions,
            arbiter_id=arbiter_id,
            arbiter_name=arbiter_name,
            decision=decision,
            justification=justification,
            selected_position=selected_position,
            strength=strength,
            context_signature=context_signature,
            rule_id_source=rule_id_source,
            regulatory_references=regulatory_references or [],
        )

        self._precedents[precedent.precedent_id] = precedent

        # Journaliser dans le WORM
        journal.append(
            event_type=JournalEventType.ARBITRATION_PRECEDENT,
            client_id=client_id,
            vertical=vertical,
            agent_source="precedent_store",
            intention_id=intention_id,
            payload={
                "precedent_id": precedent.precedent_id,
                "strength": strength.value,
                "decision": decision,
                "arbiter": arbiter_name,
                "justification": justification[:500],
                "similar_count": len(similar),
            },
        )

        # Vérifier si on peut suggérer une promotion en règle
        # Need 2+ existing similar + this one = 3+ total
        if len(similar) >= 2:
            strength = PrecedentStrength.STRONG
            precedent.strength = strength
            self._suggest_rule_promotion(precedent, similar)
        elif len(similar) >= 1:
            strength = PrecedentStrength.MEDIUM
            precedent.strength = strength

        self._save()
        logger.info(
            f"PrecedentStore: capturé {precedent.precedent_id[:8]}... "
            f"force={strength.value} verticale={vertical}"
        )
        return precedent

    # ── Query ────────────────────────────────────────────

    def query(
        self,
        vertical: str,
        question: str = "",
        conflict_reason: str = "",
        rule_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[PrecedentMatch]:
        """
        Rechercher les précédents applicables.

        Utilisé par le Médiateur AVANT l'évaluation des règles.
        Si un précédent fort existe, il peut éviter un gel inutile
        ou au contraire renforcer la décision de gel.
        """
        signature = self._compute_signature(
            vertical, question, conflict_reason, rule_id
        )

        matches = []
        for p in self._precedents.values():
            if p.vertical != vertical:
                continue
            if p.status != PrecedentStatus.ACTIVE:
                continue

            # Scoring de pertinence
            relevance = 0.0
            reasons = []

            # Match exact sur la signature
            if p.context_signature == signature:
                relevance += 0.6
                reasons.append("signature_exact")
            else:
                # Similarité partielle
                sig_parts_this = set(signature.split("|"))
                sig_parts_that = set(p.context_signature.split("|"))
                overlap = sig_parts_this & sig_parts_that
                if overlap:
                    partial = len(overlap) / max(len(sig_parts_this), 1)
                    relevance += partial * 0.3
                    reasons.append(f"signature_partial({partial:.1%})")

            # Match sur la règle source
            if rule_id and p.rule_id_source == rule_id:
                relevance += 0.3
                reasons.append("same_rule")

            # Bonus de force
            strength_bonus = {
                PrecedentStrength.WEAK: 0.0,
                PrecedentStrength.MEDIUM: 0.05,
                PrecedentStrength.STRONG: 0.1,
            }
            relevance += strength_bonus.get(p.strength, 0.0)

            # Bonus d'utilisation (plus il a été matché, plus il est pertinent)
            if p.matched_count > 0:
                relevance += min(0.1, p.matched_count * 0.02)

            if relevance > 0.1:
                matches.append(PrecedentMatch(
                    precedent=p,
                    relevance=min(relevance, 1.0),
                    match_reason=" + ".join(reasons),
                ))

        # Trier par pertinence décroissante
        matches.sort(key=lambda m: m.relevance, reverse=True)

        # Incrémenter le compteur de match
        for m in matches[:limit]:
            self._precedents[m.precedent.precedent_id].matched_count += 1

        self._save()
        return matches[:limit]

    def get_precedent(self, precedent_id: str) -> Optional[Precedent]:
        return self._precedents.get(precedent_id)

    def get_all_for_vertical(self, vertical: str) -> list[Precedent]:
        return [
            p for p in self._precedents.values()
            if p.vertical == vertical and p.status == PrecedentStatus.ACTIVE
        ]

    def get_pending_candidates(self) -> list[RuleCandidate]:
        return [
            c for c in self._candidates.values()
            if c.status == "pending"
        ]

    def approve_candidate(self, candidate_id: str, reviewer: str) -> Optional[RuleCandidate]:
        """Approuver un candidat — il sera ajouté aux règles JsonLogic."""
        candidate = self._candidates.get(candidate_id)
        if not candidate:
            return None
        candidate.status = "approved"
        candidate.reviewed_by = reviewer

        # Marquer les précédents source comme promus
        for pid in candidate.source_precedent_ids:
            p = self._precedents.get(pid)
            if p:
                p.status = PrecedentStatus.PROMOTED
                p.promoted_to_rule = candidate_id

        self._save()
        logger.info(f"PrecedentStore: candidat {candidate_id[:8]}... approuvé par {reviewer}")
        return candidate

    def reject_candidate(self, candidate_id: str, reviewer: str) -> Optional[RuleCandidate]:
        candidate = self._candidates.get(candidate_id)
        if not candidate:
            return None
        candidate.status = "rejected"
        candidate.reviewed_by = reviewer
        self._save()
        return candidate

    def override_precedent(self, precedent_id: str, reason: str = "") -> bool:
        """Invalider un précédent (nouvel arbitrage contradictoire)."""
        p = self._precedents.get(precedent_id)
        if not p:
            return False
        p.status = PrecedentStatus.OVERRIDDEN
        self._save()

        journal.append(
            event_type=JournalEventType.ARBITRATION_PRECEDENT,
            client_id=p.client_id,
            vertical=p.vertical,
            agent_source="precedent_store",
            intention_id=p.intention_id,
            payload={
                "event": "overridden",
                "precedent_id": precedent_id,
                "reason": reason,
            },
        )
        logger.info(f"PrecedentStore: précédent {precedent_id[:8]}... invalidé: {reason}")
        return True

    # ── Stats ────────────────────────────────────────────

    def get_stats(self) -> dict:
        active = [p for p in self._precedents.values() if p.status == PrecedentStatus.ACTIVE]
        by_vertical: dict[str, int] = {}
        by_strength: dict[str, int] = {}
        for p in active:
            by_vertical[p.vertical] = by_vertical.get(p.vertical, 0) + 1
            by_strength[p.strength.value] = by_strength.get(p.strength.value, 0) + 1

        return {
            "total_precedents": len(self._precedents),
            "active": len(active),
            "promoted": sum(1 for p in self._precedents.values() if p.status == PrecedentStatus.PROMOTED),
            "overridden": sum(1 for p in self._precedents.values() if p.status == PrecedentStatus.OVERRIDDEN),
            "pending_candidates": sum(1 for c in self._candidates.values() if c.status == "pending"),
            "approved_candidates": sum(1 for c in self._candidates.values() if c.status == "approved"),
            "by_vertical": by_vertical,
            "by_strength": by_strength,
            "most_matched": sorted(
                active, key=lambda p: p.matched_count, reverse=True
            )[:3] if active else [],
        }

    # ── Internals ────────────────────────────────────────

    def _compute_signature(
        self,
        vertical: str,
        question: str,
        conflict_reason: str,
        rule_id: Optional[str],
    ) -> str:
        """
        Calculer une signature de contexte pour le matching.

        Combine: verticale + type de question + règle source
        en un hash qui permet de retrouver les cas similaires.
        """
        # Normaliser la question en mots-clés
        q_normalized = question.lower().strip()[:200]
        r_normalized = conflict_reason.lower().strip()[:200]
        parts = [
            vertical,
            self._extract_question_type(q_normalized),
            rule_id or "no_rule",
            self._extract_action_type(r_normalized),
        ]
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode()).hexdigest()[:32] + "|" + "|".join(parts)

    def _extract_question_type(self, text: str) -> str:
        """Extraire le type de question depuis le texte."""
        question_types = {
            "deduction": ["déduire", "deduction", "frais", "charge"],
            "declaration": ["déclarer", "declaration", "tva", "fiscal"],
            "montant": ["montant", "amount", "seuil", "limite"],
            "delai": ["délai", "delai", "deadline", "échéance"],
            "secret": ["secret", "confidentiel", "professionnel"],
            "consentement": ["consentement", "consent", "rgpd", "données"],
            "audit": ["audit", "contrôle", "controle", "vérification"],
            "signature": ["signature", "signer", "horodatage"],
            "export": ["export", "transfert", "transfrontalier"],
        }
        for qtype, keywords in question_types.items():
            if any(kw in text for kw in keywords):
                return qtype
        return "autre"

    def _extract_action_type(self, text: str) -> str:
        """Extraire le type d'action depuis la raison du conflit."""
        action_types = {
            "gel_montant": ["montant", "seuil", "amount"],
            "gel_secret": ["secret", "confidentiel"],
            "gel_conformite": ["conformité", "conformite", "violation"],
            "gel_donnees": ["données", "donnees", "rgpd", "data"],
            "conflit_agents": ["divergence", "recommande"],
        }
        for atype, keywords in action_types.items():
            if any(kw in text for kw in keywords):
                return atype
        return "autre"

    def _find_similar(self, context_signature: str, vertical: str) -> list[Precedent]:
        """Trouver les précédents avec la même signature de contexte.
        
        Compare sur les parties lisibles de la signature (après le hash)
        pour tolérer les différences mineures de hash.
        """
        similar = []
        # Extraire la partie lisible de la signature (après le hash)
        sig_parts = context_signature.split("|", 1)[-1] if "|" in context_signature else ""
        for p in self._precedents.values():
            if p.vertical != vertical or p.status != PrecedentStatus.ACTIVE:
                continue
            p_parts = p.context_signature.split("|", 1)[-1] if "|" in p.context_signature else ""
            # Match exact sur la partie lisible
            if p_parts and p_parts == sig_parts:
                similar.append(p)
            # Fallback: match exact sur le hash complet
            elif p.context_signature == context_signature:
                similar.append(p)
        return similar

    def _suggest_rule_promotion(
        self, new_precedent: Precedent, similar: list[Precedent]
    ) -> None:
        """
        Suggérer la promotion en règle quand 3+ précédents couvrent
        le même pattern.

        Crée un RuleCandidate que l'expert peut approuver ou rejeter.
        """
        all_ids = [new_precedent.precedent_id] + [p.precedent_id for p in similar]

        # Déterminer l'action majoritaire parmi les précédents
        decisions = [new_precedent.decision] + [p.decision for p in similar]
        from collections import Counter
        decision_counts = Counter(decisions)
        majority_decision = decision_counts.most_common(1)[0][0]

        # Mappper la décision en action de règle
        decision_to_action = {
            "reject": "freeze",
            "approve": "pass",
            "modify": "arbitrate",
        }

        # Extraire les références réglementaires communes
        all_refs = set(new_precedent.regulatory_references)
        for p in similar:
            all_refs.update(p.regulatory_references)

        candidate = RuleCandidate(
            vertical=new_precedent.vertical,
            source_precedent_ids=all_ids[:5],  # Limiter à 5 sources
            suggested_condition={
                "and": [
                    {"==": [{"var": "vertical"}, new_precedent.vertical]},
                    # La condition exacte sera affinée par l'expert
                    {"var": "context.type"},
                ]
            },
            suggested_action=decision_to_action.get(majority_decision, "arbitrate"),
            suggested_severity="medium",
            suggested_message=(
                f"Règle auto-suggérée depuis {len(all_ids)} précédents: "
                f"{new_precedent.question[:100]}"
            ),
        )

        self._candidates[candidate.candidate_id] = candidate

        # Journaliser la suggestion
        journal.append(
            event_type=JournalEventType.ARBITRATION_PRECEDENT,
            client_id=new_precedent.client_id,
            vertical=new_precedent.vertical,
            agent_source="precedent_store",
            intention_id=new_precedent.intention_id,
            payload={
                "event": "rule_promotion_suggested",
                "candidate_id": candidate.candidate_id,
                "source_precedent_count": len(all_ids),
                "majority_decision": majority_decision,
                "suggested_action": candidate.suggested_action,
            },
        )

        logger.info(
            f"PrecedentStore: suggestion de règle {candidate.candidate_id[:8]}... "
            f"pour {new_precedent.vertical} ({len(all_ids)} précédents)"
        )


# Singleton
precedent_store = PrecedentStore()
