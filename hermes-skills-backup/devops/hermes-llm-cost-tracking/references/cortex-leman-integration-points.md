# Cortex Leman Anti-Sycophancy Integration Points

Reference for how `anti_sycophancy.py` is wired into Cortex Leman workflow skills.
Each entry documents the exact insertion point, the score→action mapping, and domain-specific patterns.

## 1. LEC Scout (`lec-scout`)

**Insertion:** Étape 4b — between LLM verdict (Étape 4) and hard guardrails (Étape 5).

**Why:** The scout evaluates financial signals. The LLM can be overly enthusiastic about a "hot" crypto/finance topic, inflating the score without verifiable sources. The anti-sycophancy gate catches this before the guardrails even see it.

**Score→action mapping:**

| Score | Level | Action |
|---|---|---|
| 0-14 | LOW | Pass through to guardrails (Étape 5) |
| 15-39 | CAUTION | Penalty on Axe 2 (Densité chiffrée). If unsourced numbers detected: Axe 2 = 0/2 |
| 40-69 | WARNING | Re-collect 2 additional sources (back to Étape 3). Re-judge with enriched data |
| 70+ | CRITICAL | Verdict rejected. Re-evaluate or NO-GO |

**Domain patterns (financial signals):**
- "opportunité unique", "inévitable" → minimum CAUTION
- $/% figures without "selon", "source", URL → Axe 2 = 0/2
- Product/company mention with valuation → conflict of interest flag

## 2. L'Architecte Lémanique (`l-architecte-lemanique`)

**Insertion:** Two points — `calculate-roi` and `final-decision`.

**Why:** ROI is the easiest metric to manipulate (inflated costs avoided, optimistic hypotheses, unsourced benchmarks). A GO decision based on manipulated ROI is a business risk.

### calculate-roi

**Score→action mapping:**

| Score | Level | Action |
|---|---|---|
| 0-14 | LOW | ROI figure accepted |
| 15-39 | CAUTION | Each "coût évité" must have a source. "Audit traditionnel 15,000€" must be sourced (cabinet tarif) |
| 40-69 | WARNING | Re-validate all numbers with 2 independent sources |
| 70+ | CRITICAL | ROI figure rejected |

**Hard rule:** ROI > 1000% must be justified point by point. This is a manipulation signal, not a success signal.

### final-decision

**Score→action mapping:**

| Score | Level | Action |
|---|---|---|
| 0-14 | LOW | Decision proceeds normally |
| 15-39 | CAUTION | Decision brief reviewed for unsourced claims |
| 40-69 | WARNING | Decision brief must be re-validated |
| 70+ | CRITICAL | Auto-downgrade: GO → GO RÉSERVES minimum |

**Hard rule:** If LLM adversarial returns verdict "insufficient_data" → final decision is automatically GO RÉSERVES at minimum, never GO.

## 3. Le Gardien des Normes (`le-gardien-des-normes`)

**Insertion:** Weekly compliance report — before delivery.

**Why:** Compliance scores and alerts drive client decisions. A report with unsourced "violation flagrante" claims or inflated ROI figures damages credibility and creates legal exposure.

**Score→action mapping:**

| Score | Level | Action |
|---|---|---|
| 0-14 | LOW | Report delivered normally |
| 15-39 | CAUTION | Alert sources reviewed before delivery |
| 40-69 | WARNING | Report blocked. Human re-validation required before delivery |
| 70+ | CRITICAL | Report rejected. Regenerate with sourced data |

**Domain patterns (compliance reports):**
- "violation flagrante" without RGPD/AI Act article cited → CAUTION
- Score 0/1 not justified by documented proof → CAUTION
- "risque critique" without sourced financial estimate → WARNING
- ROI Cortex Leman > 1000% without sourced cabinet benchmark → WARNING

## General Integration Technique

When adding anti-sycophancy to a new workflow skill:

1. Read the skill's SKILL.md and map its step sequence
2. Find where the LLM produces an output that drives a decision (verdict, score, analysis, report)
3. Find where the final authority acts (guardrails, kill switch, human approval, delivery)
4. Insert a new step between the two: "Étape Nb — Anti-sycophancie"
5. Define what each score level means IN THE CONTEXT OF THIS SKILL:
   - What does CAUTION mean for a financial scout? (penalty on data axis)
   - What does CAUTION mean for a compliance report? (review alert sources)
   - What does WARNING mean for a ROI calculation? (re-validate numbers)
6. List 3-5 domain-specific patterns the rule-based layer should catch
7. Add the bash command snippet for the script invocation
8. Test with a known-biased input to verify the gate triggers correctly

**Key principle:** The anti-sycophancy gate is always BETWEEN the LLM output and the final authority. It never replaces the authority — it adds a layer of skepticism before the authority acts.
