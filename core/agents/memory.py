"""
Cortex Leman v5 — Mémoire Agent (Procedural + Failure)

Deux couches de mémoire pour les agents:
1. ProceduralMemory: instructions apprises par agent/verticale après chaque mission
2. FailureMemory: erreurs passées avec causes racines et corrections

Inspiré du Reflection Engine SocialPulse, adapté pour l'architecture event-driven Cortex Leman.
Intégration: journal append-only pour traçabilité, isolation par client (RGPD).

Configuration:
- MEMORY_PATH=./data/agent_memory (défaut)
- MEMORY_ENABLED=true
"""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.journal.append_only_journal import journal
from core.journal.models import JournalEventType

logger = logging.getLogger(__name__)


# ── PROCEDURAL MEMORY ────────────────────────────────────────

class ProceduralMemory:
    """
    Mémoire procédurale par agent/verticale.
    
    Stocke les instructions apprises après chaque cycle de réflexion.
    Un agent qui a traité 50 dossiers "avocat" sait mieux que son prompt de base.
    
    Structure:
    memory/procedural/{agent_name}/{vertical}.json
    """
    
    def __init__(self, base_path: str = None):
        self._path = Path(base_path or os.getenv("MEMORY_PATH", "./data/agent_memory")) / "procedural"
        self._path.mkdir(parents=True, exist_ok=True)
    
    def get_instructions(self, agent_name: str, vertical: str) -> str:
        """Récupérer les instructions apprises pour un agent/verticale"""
        mem_file = self._path / agent_name / f"{vertical}.json"
        if not mem_file.exists():
            return ""
        
        try:
            data = json.loads(mem_file.read_text())
            return data.get("instructions", "")
        except (json.JSONDecodeError, KeyError):
            return ""
    
    def update_instructions(self, agent_name: str, vertical: str, 
                           instructions: str, insight_summary: str = "") -> None:
        """Mettre à jour les instructions procédurales"""
        mem_dir = self._path / agent_name
        mem_dir.mkdir(parents=True, exist_ok=True)
        
        mem_file = mem_dir / f"{vertical}.json"
        
        existing = {}
        if mem_file.exists():
            try:
                existing = json.loads(mem_file.read_text())
            except json.JSONDecodeError:
                pass
        
        data = {
            "agent_name": agent_name,
            "vertical": vertical,
            "instructions": instructions,
            "insight_summary": insight_summary,
            "mission_count": existing.get("mission_count", 0) + 1,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "created_at": existing.get("created_at", datetime.now(timezone.utc).isoformat()),
        }
        
        mem_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        
        journal.append(
            event_type=JournalEventType.AGENT_RESULT,
            client_id="system",
            vertical=vertical,
            agent_source=agent_name,
            intention_id="procedural_update",
            payload={"action": "procedural_memory_updated", "vertical": vertical},
        )
        
        logger.info(f"ProceduralMemory: {agent_name}/{vertical} mis à jour (mission #{data['mission_count']})")
    
    def list_all(self) -> list[dict]:
        """Lister toutes les mémoires procédurales"""
        results = []
        for agent_dir in self._path.iterdir():
            if not agent_dir.is_dir():
                continue
            for mem_file in agent_dir.glob("*.json"):
                try:
                    data = json.loads(mem_file.read_text())
                    results.append({
                        "agent": agent_dir.name,
                        "vertical": mem_file.stem,
                        "mission_count": data.get("mission_count", 0),
                        "last_updated": data.get("last_updated"),
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
        return results


# ── FAILURE MEMORY ────────────────────────────────────────────

class FailureRecord:
    """Enregistrement d'un échec agent"""
    
    def __init__(
        self,
        agent_name: str,
        error_type: str,
        error_message: str,
        vertical: str = "",
        client_id: str = "",
        intention_id: str = "",
        context: dict = None,
    ):
        self.failure_id = f"fail-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{agent_name}"
        self.agent_name = agent_name
        self.error_type = error_type
        self.error_message = error_message
        self.vertical = vertical
        self.client_id = client_id
        self.intention_id = intention_id
        self.context = context or {}
        self.occurred_at = datetime.now(timezone.utc).isoformat()
        self.root_cause = ""
        self.fix = ""
        self.resolved = False
        self.occurrence_count = 1
    
    def to_dict(self) -> dict:
        return {
            "failure_id": self.failure_id,
            "agent_name": self.agent_name,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "vertical": self.vertical,
            "client_id": self.client_id,
            "intention_id": self.intention_id,
            "context": self.context,
            "occurred_at": self.occurred_at,
            "root_cause": self.root_cause,
            "fix": self.fix,
            "resolved": self.resolved,
            "occurrence_count": self.occurrence_count,
        }


class FailureMemory:
    """
    Mémoire des échecs — 3ème couche de mémoire.
    
    Avant chaque mission, un agent consulte les échecs passés similaires.
    Après un échec, la cause racine et la correction sont enregistrées.
    
    Structure:
    memory/failures/{agent_name}.jsonl
    """
    
    def __init__(self, base_path: str = None):
        self._path = Path(base_path or os.getenv("MEMORY_PATH", "./data/agent_memory")) / "failures"
        self._path.mkdir(parents=True, exist_ok=True)
    
    def record_failure(self, record: FailureRecord) -> str:
        """Enregistrer un nouvel échec (ou incrémenter si doublon)"""
        fail_file = self._path / f"{record.agent_name}.jsonl"
        
        # Vérifier si un échec similaire existe déjà
        existing = self._load_failures(record.agent_name)
        for ex in existing:
            if ex["error_type"] == record.error_type and ex.get("resolved") is False:
                # Incrémenter le compteur
                ex["occurrence_count"] = ex.get("occurrence_count", 1) + 1
                ex["last_occurrence"] = record.occurred_at
                self._rewrite_failures(record.agent_name, existing)
                journal.append(
                    event_type=JournalEventType.AGENT_ERROR,
                    client_id=record.client_id,
                    vertical=record.vertical,
                    agent_source=record.agent_name,
                    intention_id=record.intention_id,
                    payload={"action": "failure_repeated", "error_type": record.error_type, 
                             "count": ex["occurrence_count"]},
                )
                logger.warning(f"FailureMemory: {record.error_type} répété pour {record.agent_name} (x{ex['occurrence_count']})")
                return ex["failure_id"]
        
        # Nouvel échec
        data = record.to_dict()
        with open(fail_file, "a") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        
        journal.append(
            event_type=JournalEventType.AGENT_ERROR,
            client_id=record.client_id,
            vertical=record.vertical,
            agent_source=record.agent_name,
            intention_id=record.intention_id,
            payload={"action": "failure_recorded", "error_type": record.error_type},
        )
        
        logger.warning(f"FailureMemory: {record.error_type} enregistré pour {record.agent_name}")
        return record.failure_id
    
    def get_unresolved(self, agent_name: str, vertical: str = "") -> list[dict]:
        """Récupérer les échecs non résolus pour un agent"""
        failures = self._load_failures(agent_name)
        unresolved = [f for f in failures if not f.get("resolved")]
        
        if vertical:
            unresolved = [f for f in unresolved if f.get("vertical") in (vertical, "", "all")]
        
        return unresolved
    
    def get_warnings(self, agent_name: str, vertical: str = "") -> list[str]:
        """Récupérer les avertissements pour un agent avant une mission"""
        failures = self.get_unresolved(agent_name, vertical)
        warnings = []
        
        for f in failures:
            if f.get("occurrence_count", 1) >= 3:
                warnings.append(
                    f"⚠️ {f['error_type']}: échec {f['occurrence_count']}x. "
                    f"Cause probable: {f.get('root_cause', 'non diagnostiquée')}. "
                    f"Correction: {f.get('fix', 'non encore trouvée')}"
                )
            elif f.get("occurrence_count", 1) >= 2:
                warnings.append(
                    f"⚡ {f['error_type']}: déjà rencontré {f['occurrence_count']}x. "
                    f"Surveiller ce point."
                )
        
        return warnings
    
    def resolve_failure(self, failure_id: str, root_cause: str, fix: str) -> bool:
        """Résoudre un échec avec cause racine et correction"""
        # Trouver dans quel fichier
        for fail_file in self._path.glob("*.jsonl"):
            failures = self._load_failures(fail_file.stem)
            for f in failures:
                if f["failure_id"] == failure_id:
                    f["root_cause"] = root_cause
                    f["fix"] = fix
                    f["resolved"] = True
                    f["resolved_at"] = datetime.now(timezone.utc).isoformat()
                    self._rewrite_failures(fail_file.stem, failures)
                    logger.info(f"FailureMemory: {failure_id} résolu ({root_cause})")
                    return True
        return False
    
    def get_error_patterns(self, agent_name: str = "") -> dict:
        """Analyser les patterns d'erreurs"""
        if agent_name:
            agents = [agent_name]
        else:
            agents = [f.stem for f in self._path.glob("*.jsonl")]
        
        patterns = {}
        for agent in agents:
            failures = self._load_failures(agent)
            for f in failures:
                etype = f.get("error_type", "unknown")
                if etype not in patterns:
                    patterns[etype] = {"count": 0, "agents": set(), "resolved": 0}
                patterns[etype]["count"] += f.get("occurrence_count", 1)
                patterns[etype]["agents"].add(agent)
                if f.get("resolved"):
                    patterns[etype]["resolved"] += 1
        
        # Convertir sets en lists pour JSON
        return {k: {**v, "agents": list(v["agents"])} for k, v in patterns.items()}
    
    def _load_failures(self, agent_name: str) -> list[dict]:
        """Charger les échecs d'un agent"""
        fail_file = self._path / f"{agent_name}.jsonl"
        if not fail_file.exists():
            return []
        
        results = []
        for line in fail_file.read_text().strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return results
    
    def _rewrite_failures(self, agent_name: str, failures: list[dict]) -> None:
        """Réécrire le fichier d'échecs d'un agent"""
        fail_file = self._path / f"{agent_name}.jsonl"
        with open(fail_file, "w") as f:
            for failure in failures:
                f.write(json.dumps(failure, ensure_ascii=False) + "\n")


# ── SINGLETONS ───────────────────────────────────────────────

procedural_memory = ProceduralMemory()
failure_memory = FailureMemory()
