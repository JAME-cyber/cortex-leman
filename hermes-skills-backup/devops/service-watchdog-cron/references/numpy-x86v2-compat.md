# NumPy X86_V2 Compatibility — Old CPU Crash

## Problem

NumPy >= 2.0 (releases from ~mid-2024 onward) ships wheels built with **baseline optimizations requiring X86_V2** instruction set. On CPUs older than ~2013 (e.g. Intel Core 2 Duo P8700, 2008), importing NumPy crashes:

```
RuntimeError: NumPy was built with baseline optimizations:
(X86_V2) but your machine doesn't support:
(X86_V2).
```

## Detecting the CPU generation

```bash
cat /proc/cpuinfo | grep flags | head -1 | grep -o 'sse4_2\|avx\|ssse3'
# If sse4_2 is absent → pre-X86_V2 → will crash on numpy >=2.0
```

X86_V2 baseline ≈ SSE4.2. Core 2 Duo only has up to SSSE3 → crash guaranteed.

## Fix

Pin NumPy below 2.0. Version 1.26.4 is the last stable 1.x release and is compatible with SSE2-only CPUs:

```bash
python3.12 -m pip install --user "numpy<2.0" --force-reinstall --break-system-packages
```

**Note on PEP 668:** On Debian/Ubuntu system Python, you need `--break-system-packages` (or use a venv). This is safe for a controlled server where you own the Python install.

## Downstream impact

A broken NumPy cascades silently across the entire Python ML/data stack:

| Package | Dependency | Symptom |
|---|---|---|
| ChromaDB | `from numpy.typing import NDArray` | Crash at import → RAG store fails to load |
| OpenCV (`cv2`) | numpy at runtime | Import may work but operations crash |
| kokoro-onnx | numpy >=2.0.2 | Warning only (not crash) |
| pandas, scipy, scikit-learn | numpy | All fail at import |

## The silent cron trap

When NumPy crashes on `python3.12` but works on `python3.11`, a cron job using `python3.12` will crash at every tick. But the cron system marks `last_status: "ok"` because the **agent** successfully ran, diagnosed the error, and reported it in its response. The actual task (indexing, ingestion) never executes.

**Diagnostic rule:** If a cron shows `ok` but `+0` items processed for multiple consecutive runs, suspect a crash in the underlying script/dependency — not a logic bug.

**The canari cron:** Any cron that runs a Python script importing numpy-heavy libraries (chromadb, pandas, sklearn) is a canari for this crash. If it stops producing output, check numpy first:

```bash
python3.12 -c "import numpy; print(numpy.__version__)"
```

## Prevention

After any `pip install` that might have pulled numpy >=2.0, verify on the target Python:

```bash
python3.12 -c "import numpy; print('OK', numpy.__version__)"
# If crash → reinstall numpy<2.0
```

Consider pinning numpy in the project's `requirements.txt` or `pyproject.toml`:

```
numpy<2.0  # CPU = Core 2 Duo (no X86_V2)
```
