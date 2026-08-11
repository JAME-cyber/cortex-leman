# TabICLv2 — Tabular Foundation Model (INRIA)

## What it is

TabICLv2 is a foundation model for tabular data (CSV, databases). Pre-trained on millions of
synthetic datasets, it performs **in-context learning**: give it training rows, it predicts on
new rows via a single forward pass — no gradient descent, no hyperparameter tuning.

- **Repo**: https://github.com/soda-inria/tabicl (1,163 stars, Jul 2026)
- **Paper**: ICML 2026 (arXiv:2602.11139)
- **Lab**: INRIA (same team behind scikit-learn)
- **License**: "Other" (permissive but verify for commercial use)
- **Version**: v2.1.1 (Apr 2026, added fine-tuning support)

## Key claim

> Outperforms heavily tuned XGBoost, CatBoost, LightGBM on ~80% of datasets — WITHOUT any
> hyperparameter tuning. Validated on TabArena and TALENT benchmarks.

## Install (on TARS Docker host)

```bash
# Create venv (system Python has PEP 668)
uv venv tabicl_env && source tabicl_env/bin/activate

# Install — note: tabicl pulls torch (CUDA build by default, ~3GB)
uv pip install tabicl

# CRITICAL: numpy>=2.3 ships X86_V2 baseline. TARS CPU doesn't support X86_V2.
# Must pin numpy<2.3 or get: RuntimeError: NumPy was built with baseline optimizations: (X86_V2)
uv pip install "numpy<2.3" --force-reinstall
```

## API (scikit-learn compatible)

```python
from tabicl import TabICLClassifier, TabICLRegressor

# Classification (zero config)
clf = TabICLClassifier(n_estimators=4, device="cpu")
clf.fit(X_train, y_train)     # downloads HF checkpoint on first call (~minutes)
clf.predict(X_test)            # in-context learning happens here
clf.predict_proba(X_test)      # probabilities

# Regression
reg = TabICLRegressor()
reg.fit(X_train, y_train)
reg.predict(X_test)

# KV caching for repeated inference on same training data
clf = TabICLClassifier(kv_cache=True)
clf.fit(X_train, y_train)     # caches KV projections
clf.predict(X_test)           # fast: only processes test data

# Save/load
clf.save("model.pkl", save_model_weights=False, save_training_data=True)
clf = TabICLClassifier.load("model.pkl")
```

### Fine-tuning (when a single dataset matters enough)

```bash
pip install tabicl[finetune]
```

```python
from tabicl import FinetunedTabICLClassifier

clf = FinetunedTabICLClassifier(
    epochs=50, learning_rate=1e-5, early_stopping=True, patience=10,
    eval_metric="roc_auc",
)
clf.fit(X_train, y_train, X_val=X_val, y_val=y_val, output_dir="./ckpts")
```

Multi-GPU via `torchrun --nproc-per-node=2 finetune_script.py`.

## Performance characteristics

| Metric | Value |
|--------|-------|
| Scale | 300 → 100K samples, up to 2,000 features |
| GPU recommended for | >10K samples |
| CPU (H100) fit+predict 50K×100 | <10 seconds |
| CPU (TARS Docker, 2-core) | Minutes for 2K samples |
| First-run overhead | Checkpoint download from HuggingFace (~minutes, one-time) |
| Offloading | CPU + disk offload for datasets >500K (accuracy may degrade) |

## Optional extras

```bash
pip install tabicl[forecast]   # time series forecasting
pip install tabicl[shap]       # SHAP explainability
pip install tabicl[finetune]   # fine-tuning on single dataset
pip install tabicl[pretrain]   # pre-training (open source)
pip install tabicl[all]        # everything
```

## Tutorials in repo

- `getting_started.py` — classification + regression basics
- `finetune_classifier.py` / `finetune_regressor.py` — fine-tuning
- `interpretability.py` — SHAP
- `string_handling.py` — string columns
- `time_series_forecasting.py` — forecasting
- `unsupervised_learning.py` — clustering/embeddings
- `classification_2D_proba.py` — probability visualization

## Measured benchmark (TARS Docker, Jul 2026)

Real numbers from running `scripts/tabicl_benchmark.py` on the actual host:

| Metric | Value |
|--------|-------|
| Dataset | 2,000 samples, 20 features, 5.6% positive |
| ROC-AUC (zero config) | **0.818** |
| Accuracy | 0.975 (misleading — 94.4% baseline predicting all-negative) |
| Fit time | 1.9s |
| Predict time (400 test samples) | **334s** (~0.84s/sample) |
| Device | CPU only (no GPU on TARS Docker) |

**Operational takeaway**: CPU inference is ~0.84s/sample. For 2,382 leads → ~30min per batch.
Usable for weekly batch scoring, NOT for real-time API scoring. GPU (H100) brings this to <10s
for 50K samples.

## SocialPulse use case: lead scoring

### Data reality (verified Jul 2026)

Dataset: 2,382 leads in `lead-queue.json`. Pipeline statuses:
- scored: 2,352 / diagnosed: 20 / flagged: 5 / pitched: 5
- **0 actual conversions labellized** (processed-leads.json is empty)
- Existing deterministic score: 43-82 (rule-based: website, review gap, sector, location)
- 748 leads have phone + website; 14 sectors; 5 cities (Gaillard, Annemasse, Ville-la-Grand, etc.)

TabICL CANNOT be trained directly — there is no target variable (y).

### Cold-start solution: synthetic data generation

When you have zero labeled conversions, generate a synthetic training set from industry-known
B2B conversion patterns, then train TabICL on it as a placeholder until real data arrives.

**Pattern** (reusable for any B2B cold-start lead scoring):

1. Extract real feature distributions from existing leads (sector, website status, channel, city, etc.)
2. Define base conversion rates per sector from industry benchmarks (Restaurants 2.5%, Salons 6.5%, etc.)
3. Apply known multipliers (no website = 1.8x more likely to buy, Instagram channel = 1.3x, etc.)
4. Add logistic noise (σ=0.3) to make labels realistic, not perfectly separable
5. Bootstrap-augment real leads (sample with replacement + perturb scores) to reach 5K+ samples
6. Train TabICL on synthetic labels → score all real leads → output ranked priority list

**Scripts** (in SocialPulse repo at `annemasse-agency/ml/`):
- `synthetic_data_generator.py` — generates `training_data.csv` (5,382 samples, 7.2% conversion)
- `lead_scorer.py` — full pipeline: train TabICL → score 2,382 leads → output JSON/CSV/top-100

**Swapping in real data**: when 100+ leads are contacted and labeled (interested/not interested),
replace `training_data.csv` with the real CSV (same feature columns) and re-run:
```bash
python lead_scorer.py --real-data mes_vraies_conversions.csv
```
Zero code changes — TabICL handles the rest.

### Output format

The pipeline produces:
- `output/scored_leads.json` — all 2,382 leads with `ml_score` and `ml_rank`
- `output/top_100_priority.csv` — top 100 for agent outreach
- `output/outreach_priority.json` — structured format with rank, score, contact info

## What TabICL does NOT do

- No NLP (use LLMs for text)
- No computer vision
- No native time series (optional `tabicl[forecast]` module)
- No text feature engineering — encode text columns first
- No causal inference — correlations only

## Benchmark script

See `scripts/tabicl_benchmark.py` for a ready-to-run TabICL vs XGBoost comparison on
imbalanced synthetic data matching SocialPulse's positive rate.
