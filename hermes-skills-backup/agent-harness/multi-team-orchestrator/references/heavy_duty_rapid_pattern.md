---
name: Heavy Duty Multi-Agent System
category: autonomous-ai-agents
description: Rapid development pattern for multi-agent systems with JSON configs, concise skills, async orchestration, and kill switch integration. Heavy duty mode means direct execution, minimal fluff, tested code.
---

# HEAVY DUTY MULTI-AGENT SYSTEM

## RÔLE
Rapid development framework pour systèmes multi-agents complexes. Pattern éprouvé : configs JSON + skills concises + orchestration async + tests immédiats.

## QUAND UTILISER

✅ Créer système multi-agents (5+ agents)
✅ Migrer codebase (JS → Python, legacy → moderne)
✅ Orchestration parallèle (asyncio)
✅ Intégrer Kill Switch (safety)
✅ Besoin exécution rapide (heavy duty mode)

## PATTERN ARCHITECTURE

### 1. CONFIGS AGENTS (JSON)
```json
{
  "name": "Agent Name",
  "role": "Role",
  "domain": "Domain",
  "mission": "Mission",
  "model": "model-name",
  "temperature": 0.2,
  "skills": ["skill1", "skill2", "skill3"],
  "personality": "trait1 trait2",
  "kill_switch_access": false,
  "orchestrator_rank": 1
}
```

**Emplacement** : `~/.hermes/agents/agent-name/agent.json`

### 2. SKILLS CONCISES (SKILL.md)
Règle : Max 200-300 lignes per skill. Pas de fluff. Direct.

Structure :
```markdown
---
name: Skill Name
category: category
description: One-line description

---

# SKILL NAME

## RÔLE
One line role

## MISSION
One line mission

## 5 SKILLS
### 1. skill-name
ENTRÉE : Input description
SORTIE : Output description

RÈGLES : 3 bullet points max

### 2. skill-name
[...same pattern...]

## PERSONNALITÉ
3 traits. Direct tone.

✅ GOOD : "Action completed. Result: X."
❌ BAD : "I think we should probably consider..."
```

**Emplacement** : `~/.hermes/skills/category/skill-name/SKILL.md`

### 3. PYTHON MODULES TESTABLES
Pattern :
```python
"""
Module Description
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Result:
    """Result"""
    field: type

class Processor:
    """Processor"""

    def process(self, input) -> Result:
        """Process input"""
        pass

# Test block
if __name__ == "__main__":
    p = Processor()
    result = p.process("test")
    print(f"Result: {result}")
    print("✅ Test passed")
```

**Règles** :
- Docstring module
- dataclasses pour structures
- Type hints partout
- Main block test OBLIGATOIRE
- Print "✅ Test passed" en fin

**Emplacement** : `~/.hermes/skills/category/skill-name/module.py`

### 4. ORCHESTRATION ASYNC
Pattern pipeline :
```python
class Orchestrator:
    """Orchestrateur"""

    async def pipeline(self, input) -> Result:
        """Pipeline principal"""
        # Phase 1 (parallel)
        task1 = asyncio.to_thread(self.step1, input)
        task2 = asyncio.to_thread(self.step2, input)
        result1, result2 = await asyncio.gather(task1, task2)

        # Phase 2 (sequential)
        result3 = self.step3(result1, result2)

        # Kill switch check
        if self.check_kill_switch(result3):
            return self.kill_switch_result(input)

        return Result(...)

async def main():
    orchestrator = Orchestrator()
    result = await orchestrator.pipeline("test")
    print(f"Score: {result.score}")
    print("✅ Orchestration test passed")
```

**Emplacement** : `~/.hermes/project/orchestration.py`

## PROCESSUS DE DÉVELOPPEMENT

### ÉTAPE 1 : AGENTS CONFIG
1. Créer configs JSON pour tous les agents
2. Définir orchestrator_rank (1 = orchestrateur principal)
3. kill_switch_access: false sauf Gardien

### ÉTAPE 2 : SKILLS CONCISES
1. Créer SKILL.md per agent (max 300 lignes)
2. Définir 5 skills max per agent
3. Format : ENTRÉE → SORTIE → RÈGLES

### ÉTAPE 3 : PYTHON MODULES
1. Créer module.py per skill
2. dataclasses pour structures
3. Main block test OBLIGATOIRE
4. Tester chaque module

### ÉTAPE 4 : ORCHESTRATION
1. Créer orchestrator.py
2. Pipeline async avec gather()
3. Kill switch intégré
4. Test complet

### ÉTAPE 5 : VALIDATION
1. Tests unitaires passés (tous les modules)
2. Orchestration testée
3. Documentation complète
4. README généré

## KILL SWITCH PATTERN

### Activation
```python
def check_kill_switch(self, result) -> Tuple[bool, str]:
    """Vérifie conditions activation"""
    if result.score < 0.3:
        return True, f"Score {result.score} < 0.3"
    if 'critical' in result.violations:
        return True, f"Violation critique: {result.violations}"
    return False, ""

def enforce_kill_switch(self, reason: str) -> Dict:
    """Active Kill Switch"""
    return {
        'activated': True,
        'timestamp': time.time(),
        'reason': reason,
        'action': 'system_shutdown'
    }
```

### Intégration pipeline
```python
# Check après phase critique
activate, reason = self.check_kill_switch(intermediate_result)
if activate:
    return self.kill_switch_result(reason)
```

## HEAVY DUTY MODE

**Directives** :
- Pas de markdown excessif (tables, sections multiples)
- Directif : faire, pas expliquer
- Tests immédiats (main blocks)
- Fail fast : si ça marche pas, réessayer avec plus simple
- Stats en fin : lignes de code, temps execution

**Output pattern** :
```
✅ Agent X created
✅ Skill Y migrated
✅ Test passed
━━━━━━━━━━━━━━━━━━━━━━
📊 STATS:
- Agents: 5
- Skills: 7
- Lines: 58,381
- Time: <5s
```

## PIÈGES À ÉVITER

❌ NE PAS FAIRE :
- Documentation excessive (>500 lignes per skill)
- Tests différés (tester immédiatement)
- Async sans gather (paralleliser quand possible)
- Kill switch sans check (vérifier après chaque phase critique)
- Verbose outputs (direct, concis)

✅ TOUJOURS FAIRE :
- Configs JSON + SKILL.md per agent
- Python modules testables (main blocks)
- Orchestration async avec gather()
- Kill switch intégré
- Stats en fin de session

## EXEMPLE SESSION COMPLÈTE
```
✅ L'Architecte Lémanique created
✅ L'Ingénieur de Flux created
✅ Le Narrateur Augmenté created
━━━━━━━━━━━━━━━━━━━━━━
📊 STATS:
- Agents: 3
- Skills: 15
- Orchestration: ✅
```

## RÉFÉRENCES

- Cortex Leman architecture: 5 agents, 7 skills
- Async patterns: asyncio.gather(), asyncio.to_thread()
- Kill switch: Gardien des Normes skill
- Migration JS → Python: 58,381 lines

---
**HEAVY DUTY MODE: RAPIDE, TESTÉ, OPÉRATIONNEL**
