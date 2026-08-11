# HELEN Risk Matrix — Recovered from Bytecode (2026-07-10)

> Source: `HELEN-Workflow-Manager-RESCUE/helen/security/__pycache/*.pyc`
> Original `.py` files were deleted during a refactor. Structure and logic recovered via `marshal` + bytecode introspection.
> Designed for Swiss law firms originally; adaptable to any FR-CH compliance context.

## 1. Risk Levels (R1-R4)

Defined as a Python `Enum` (`RiskLevel`) in `risk_matrix.py`:

| Level | Enum Value | Description | Action |
|-------|-----------|-------------|--------|
| **R1** | `R1_LOW` | Risque Faible — Traitement Automatique Autorisé | ✅ Automatisation OK, no human validation |
| **R2** | `R2_MODERATE` | Risque Modéré — Validation Humaine Requise | ⚠️ Human must validate before delivery |
| **R3** | `R3_HIGH` | Risque Élevé — Double Validation Requise | 🔸 Two independent validations required |
| **R4** | `R4_CRITICAL` | Risque Critique — Blocage Système | 🚫 Kill Switch — block + alert + escalate |

### Properties

- `requires_human_validation`: True for R2, R3, R4. False for R1.
- `is_blocking`: True only for R4. R1-R3 allow generation with varying validation gates.
- `is_safe_for_automation`: True only for R1 (checked on `RiskAssessment`).

---

## 2. RiskAssessment Model (Pydantic, frozen=True)

Immutable audit record produced by the classifier:

```python
class RiskAssessment(BaseModel):
    level: RiskLevel                    # R1-R4 classification
    score: float                        # Probability 0.0-1.0
    reasons: List[str]                  # Justification for classification
    detected_entities: List[str]        # Named entities (ex: "Mineur", "Santé")
    timestamp: datetime                 # When analyzed

    class Config:
        frozen = True                   # Immutable — tamper-proof audit trail

    def is_safe_for_automation(self) -> bool:
        return self.level == RiskLevel.R1_LOW
```

---

## 3. RiskClassifier — Deterministic Pattern Matching

`risk_classifier.py` — classifies prompts using regex patterns, NOT ML. **Safe by Design: Fail Safe (default to HIGH risk on error).**

### Classification Algorithm

```
1. If prompt empty → R1_LOW (nothing to risk-assess)
2. Scan for R4_PATTERNS → if match: R4_CRITICAL
   - "conflit d'intérêts"
   - "partie adverse"
   - (other critical legal patterns)
3. Scan for R3_PATTERNS → if match: R3_HIGH
   - has_pii flag from middleware
   - "PII Detected by Middleware"
4. Scan for R2_PATTERNS → if match: R2_MODERATE
   - "Sensibilité élevée"
   - "Interaction client"
5. No match → R1_LOW ("Aucun marqueur de risque détecté. Modèle standard.")
```

### Key Design Principle

**Fail Safe**: On any error or uncertainty, the classifier defaults to HIGH risk, not LOW. Better to over-validate than to miss a critical risk.

### Entity Detection

`_detect_entities(text, compiled_patterns)` scans for named entities that elevate risk:
- Legal entities: partie adverse, conflit d'intérêts
- Sensitive categories: mineur, santé, données financières
- PII from middleware integration

---

## 4. Guardrails Architecture (guardrails.py — source recovered)

Three-layer defense for LLM interactions:

### Layer 1: PromptSanitizer

Regex-based detection of 25+ injection patterns:

| Category | Examples |
|----------|---------|
| Prompt injection | `ignore previous instructions`, `you are now`, `pretend to be` |
| System injection | `system:`, `admin:`, `sudo`, `rm -rf` |
| Code injection | `<script>`, `javascript:`, `eval(`, `exec(` |
| Credential leak | `password=`, `api_key=`, `token=`, `secret=` |
| Encoding bypass | `%3Cscript`, `&lt;script`, `\x3Cscript` |

Modes:
- **Strict mode**: Reject prompt entirely if threats detected (`is_safe = False`)
- **Permissive mode**: HTML-encode dangerous characters, keep prompt

Also validates workflow parameters recursively for sensitive data.

### Layer 2: RateLimiter

| Request type | Max requests | Window |
|-------------|-------------|--------|
| `api_requests` | 100 | 60s |
| `llm_requests` | 20 | 60s |
| `workflow_generation` | 10 | 300s |
| `validation_requests` | 200 | 60s |

Tracks per user+IP. Logs `SecurityEvent` on limit exceeded.

### Layer 3: SecurityGuardrails (orchestrator)

Combines sanitizer + rate limiter + block list:
1. Check blocked users/IPs → block immediately
2. Rate limit check → block if exceeded
3. Prompt sanitization (strict) → block if threats
4. Workflow parameter validation → block if sensitive data

### SecurityEvent logging

```python
@dataclass
class SecurityEvent:
    timestamp: datetime
    event_type: str        # 'rate_limit_exceeded', 'injection_detected', etc.
    severity: str          # 'low', 'medium', 'high', 'critical'
    description: str
    user_id: Optional[str]
    ip_address: Optional[str]
    details: Optional[Dict]
```

Events stored in deque(maxlen=1000), reportable via `get_security_report(hours=24)`.

---

## 5. Adaptation Guide — From HELEN (legal) to Cortex Leman (general FR-CH)

The HELEN system was designed for Swiss law firms. To adapt:

| HELEN concept | Cortex Leman adaptation |
|--------------|----------------------|
| R4 patterns: "conflit d'intérêts", "partie adverse" | Add: health data (Art. 9 RGPD), financial advice, minor protection |
| Legal entity detection | Add: RGPD-sensitive categories (health, religion, political, biometric) |
| "Safe by Design" for law | Becomes "Compliance by Design" for PME audit |
| Swiss law firm context | FR-CH PME: retail, health, finance, public sector |

### Integration with Le Gardien des Normes

The Gardien skill references "Matrice de Risques v1.0" in its role description but never had the implementation. This reference IS that matrix. The skill's 5-domain audit methodology + this R1-R4 classification system = complete risk management framework.

---

## 6. File Locations (for recovery if needed)

```
HELEN-Workflow-Manager-RESCUE/
├── helen/security/
│   ├── guardrails.py                          # ✅ Source recovered
│   ├── risk_matrix.py                         # ❌ Source lost, bytecode only
│   ├── risk_classifier.py                     # ❌ Source lost, bytecode only
│   └── __pycache__/
│       ├── risk_matrix.cpython-312.pyc        # Recovered via marshal
│       ├── risk_classifier.cpython-312.pyc    # Recovered via marshal
│       └── guardrails.cpython-312.pyc
├── restore_points/
│   ├── PHASE_1_COMPLETE_METR_READY/           # Has all .pyc files
│   ├── PRESTIGE_TECH_FRONTEND_STABLE_20260114/
│   └── FRONTEND_STABILIZED_20251231/
└── tests/
    ├── test_validation_security.py            # ✅ Full test suite
    └── test_simple_validation.py              # ✅ Same tests, simpler runner
```

### Bytecode Recovery Method

```python
import marshal, types
with open('risk_matrix.cpython-312.pyc', 'rb') as f:
    f.read(16)  # skip header (4 magic + 4 flags + 4 timestamp + 4 size)
    code = marshal.loads(f.read())
# Walk code.co_names, code.co_consts, nested CodeType objects
```

This method works for any Python 3.12 `.pyc` when source is lost. Not a full decompiler, but extracts enough (class names, string constants, method signatures) to reconstruct the module.
