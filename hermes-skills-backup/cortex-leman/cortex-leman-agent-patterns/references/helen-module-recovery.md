# HELEN Module Recovery Technique

## Context

HELEN Workflow Manager was a Swiss legal-tech project (2025). Its source repo survived as a rescue archive containing both `.py` files and `.pyc` (compiled bytecode) files. Some modules existed only as bytecode — their `.py` source was lost.

This document captures the technique used to recover, analyze, and adapt those modules for reuse in the `shared_ai_safety` package.

## Step 1: Inventory Available Sources

```bash
# Check what .py sources exist
search_files --path /path/to/HELEN --target files --pattern "*.py"

# Check restore points (may have fuller source trees)
search_files --path /path/to/HELEN/restore_points --target files --pattern "*.py"
```

**Finding**: Restore points (e.g. `PHASE_1_COMPLETE_METR_READY/`) often have MORE complete source than the main tree. Always check both.

## Step 2: Analyze .pyc Files When Source Is Missing

When only `.pyc` bytecode survives, use Python's `marshal` + `dis` modules to extract metadata:

```python
import os, marshal, struct

def load_pyc(path):
    """Load a .pyc file and extract the code object."""
    with open(path, "rb") as f:
        f.read(16)  # skip header (magic, flags, timestamp/hash, size)
        code = marshal.loads(f.read())
    return code

def extract_names(code_obj):
    """Extract function/class names and string constants."""
    funcs = []
    consts = set()
    for const in code_obj.co_consts:
        if isinstance(const, str) and len(const) > 10:
            consts.add(const[:120])  # docstrings, messages
        elif isinstance(const, type(code_obj)):
            name = const.co_name
            if not name.startswith('_') or name == '__init__':
                funcs.append(name)
            # Recurse into nested code objects
            f2, cs2 = extract_names(const)
            funcs.extend(f2)
            consts.update(cs2)
    return funcs, consts
```

**What you can extract from bytecode:**
- Function and class names
- Docstrings (full text — invaluable for understanding intent)
- String constants (messages, error text, patterns)
- Import statements (via `co_names`)
- Variable names (via `co_varnames`)

**What you CANNOT extract:**
- Comments
- Exact source formatting
- Type annotations (Python 3.12 stores some, but not reliably)

## Step 3: Adaptation Checklist

For each recovered module, apply this transformation:

| Aspect | HELEN original | Adapted version |
|--------|---------------|-----------------|
| **Coupling** | Imports from `helen.domain.entities.*`, `helen.domain.interfaces.*` | Self-contained dataclasses or Protocols |
| **Paths** | Windows paths (`D:/helen-data/logs`) | Platform-generic (`Path.home() / "logs"`) |
| **Config** | Hardcoded constants | Constructor parameters with sensible defaults |
| **Tests** | None in bytecode | Full test suite written from scratch |
| **Pydantic** | V1 (`class Config:`) | V2 (`model_config = {}`) |
| **Async** | Mixed sync/async without clear boundaries | Clear separation, sync wrappers for prototype use |

## Step 4: Validation

After adaptation, run the full test suite:

```bash
cd ~/shared_ai_safety && python test_safety.py
# Must show: ALL TESTS PASS
```

## Modules Successfully Recovered (2026-07-10)

| Module | Source available? | Recovery method | Adaptation effort |
|--------|------------------|-----------------|-------------------|
| `risk_matrix.py` | `.pyc` only | Bytecode analysis + reconstruction | Full rewrite |
| `risk_classifier.py` | `.pyc` only | Bytecode analysis + reconstruction | Full rewrite |
| `guardrails.py` | `.pyc` only | Bytecode analysis + reconstruction | Full rewrite |
| `structured_logger.py` | `.py` in restore point | Direct read + adaptation | Low — path fix, decoupling |
| `workflow_validator.py` | `.py` in restore point | Direct read + adaptation | Medium — removed entity coupling, added secret detection + cycle detection |
| `memory_service.py` | `.py` in restore point | Direct read + adaptation | Medium — replaced 4 HELEN dependencies with internal dataclasses + Protocol |

## Key Lessons

1. **Always check restore points** — they often have source that the main tree lost
2. **Bytecode docstrings survive** — they're your primary guide to module intent
3. **Decoupling is the main work** — HELEN modules had deep dependency trees (entities, interfaces, repositories). Replacing with self-contained dataclasses + Protocols is the cleanest approach
4. **Add features during adaptation** — the original `workflow_validator` only checked code execution and HTTP destinations. We added hardcoded secret detection and cycle detection during adaptation. The original `structured_logger` had no guardrail-specific logging; we added `log_guardrail()`
5. **Test from scratch** — bytecode gives you the implementation, not the test plan. Write tests that validate both the original behavior and your adaptations
