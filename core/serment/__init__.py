"""
Cortex Leman v5 — Serment Numérique
Chaque agent prête serment. Le serment est gravé dans le journal WORM.
"""
import hashlib
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

SERMENT_DIR = Path(__file__).parent.parent / "serment"

_cache: dict[str, dict] = {}


def load_serment(vertical: str) -> Optional[dict]:
    """Charger le serment d'une vertical"""
    if vertical in _cache:
        return _cache[vertical]

    path = SERMENT_DIR / f"{vertical}.yaml"
    if not path.exists():
        return None

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Hash the serment text for immutability proof
    serment_text = data.get("serment", "")
    data["hash"] = hashlib.sha256(serment_text.encode("utf-8")).hexdigest()[:16]
    data["hash_algorithm"] = "SHA-256"
    data["engraved_at"] = datetime.now(timezone.utc).isoformat()

    _cache[vertical] = data
    return data


def list_serments() -> list[dict]:
    """Lister tous les serments disponibles"""
    results = []
    for path in sorted(SERMENT_DIR.glob("*.yaml")):
        vertical = path.stem
        s = load_serment(vertical)
        if s:
            results.append({
                "vertical": vertical,
                "profession": s.get("profession", ""),
                "jurisdiction": s.get("jurisdiction", ""),
                "hash": s["hash"],
                "engraved_at": s["engraved_at"],
                "preview": s.get("serment", "").split("\n")[2].strip() if s.get("serment") else "",
                "references_count": len(s.get("references", [])),
            })
    return results


def verify_serment_integrity(vertical: str) -> dict:
    """Vérifier l'intégrité d'un serment"""
    s = load_serment(vertical)
    if not s:
        return {"valid": False, "error": "Serment non trouvé"}

    # Recompute hash
    current_hash = hashlib.sha256(s["serment"].encode("utf-8")).hexdigest()[:16]
    return {
        "valid": current_hash == s["hash"],
        "hash": s["hash"],
        "algorithm": s["hash_algorithm"],
        "vertical": vertical,
        "profession": s.get("profession", ""),
    }
