"""
Cortex Leman v5 — Agent Skills (System Prompts)

Charge les prompts spécialisés pour chaque agent LLM.
Les agents programmatiques purs (Médiateur, Action, Superviseur)
n'utilisent PAS de prompt LLM.
"""
import os
from pathlib import Path
from typing import Optional

PROMPTS_DIR = Path(__file__).parent

# Agents qui utilisent un LLM (Sprint 2+)
LLM_AGENTS = {"reasoning", "orchestrator", "data", "le_leman"}

# Agents purement programmatiques (JAMAIS de LLM)
PROGRAMMATIC_AGENTS = {"action", "mediator", "supervisor"}


def load_skill(agent_name: str) -> Optional[str]:
    """
    Charger le skill (system prompt) d'un agent.
    Retourne None pour les agents programmatiques.
    """
    if agent_name in PROGRAMMATIC_AGENTS:
        return None

    skill_file = PROMPTS_DIR / f"{agent_name}.md"
    if not skill_file.exists():
        return None

    content = skill_file.read_text(encoding="utf-8")
    return content


def extract_section(skill_content: str, section: str) -> Optional[str]:
    """Extraire une section spécifique d'un skill"""
    lines = skill_content.split("\n")
    in_section = False
    section_lines = []

    for line in lines:
        if line.startswith(f"## {section}"):
            in_section = True
            continue
        if line.startswith("## ") and in_section:
            break
        if in_section:
            section_lines.append(line)

    return "\n".join(section_lines).strip() or None


def build_system_prompt(agent_name: str, vertical: str, context: dict) -> str:
    """
    Construire le system prompt complet pour un agent LLM.
    Combine le skill de base + les instructions verticales.
    Utilisé par LLMService.generate_for_agent().
    """
    skill = load_skill(agent_name)

    if skill:
        # Extraire les sections utiles
        role = extract_section(skill, "RÔLE") or agent_name
        ton = extract_section(skill, "TON") or "Professionnel"
        garde_fous = extract_section(skill, "GARDE-FOUS") or ""
    else:
        role = agent_name
        ton = "Professionnel"
        garde_fous = ""

    prompt = f"""Tu es un agent IA du système Cortex Leman v5.
Rôle: {role}
Verticale métier: {vertical}
Ton: {ton}

RÈGLES IMPÉRATIVES:
- Tu ne prends JAMAIS de décision autonome pour les tâches réglementées
- Tu signales TOUJOURS les risques de non-conformité
- Tu recommandes TOUJOURS une validation humaine pour les décisions critiques
- Tu respectes le RGPD, l'AI Act et le secret professionnel FR-CH
- Tu fournis des références réglementaires quand possible

CONTEXTE:
{context}
"""

    # Instructions verticales spécifiques
    vertical_map = {
        "avocat": "\nATTENTION: Secret professionnel Art. 321 CP. AUCUNE donnée client ne doit sortir.",
        "banque": "\nATTENTION: Secret bancaire Art. 47 LB. Infrastructure CH obligatoire.",
        "sante": "\nATTENTION: LPM + HDS. Données de santé: hébergement certifié requis.",
        "comptable": "\nATTENTION: Art. 22 RGPD. Pas de décision fiscale automatique.",
        "rh": "\nATTENTION: AI Act + anti-discrimination. Pas de décision RH automatique.",
        "startup": "\nCONTEXTE: RGPD standard. DPIA obligatoire si profiling.",
    }
    prompt += vertical_map.get(vertical, "")

    return prompt


def list_available_skills() -> dict:
    """Lister tous les skills disponibles"""
    skills = {}
    for f in PROMPTS_DIR.glob("*.md"):
        name = f.stem
        content = f.read_text(encoding="utf-8")
        skill_type = "PROGRAMMATIQUE" if name in PROGRAMMATIC_AGENTS else "LLM"
        skills[name] = {
            "file": str(f.name),
            "type": skill_type,
            "size": len(content),
        }
    return skills
