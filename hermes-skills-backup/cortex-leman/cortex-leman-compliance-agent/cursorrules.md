# Cortex Leman Compliance Agent — Cursor Rules

# When the user says "audit rgpd" or "compliance check":
# 1. Load the full compliance context from this file
# 2. Scan the current project codebase
# 3. Run through ALL 5 domains of the RGPD-IA audit checklist
# 4. Add the 4 AI-specific dimensions (autonomy, RAG architecture, traceability, accountability)
# 5. Produce the compliance report in the standard format

## Jurisdiction Context
- EU: RGPD (2016/679) + AI Act (2024/1689)
- CH: LPD (nLDP from Sep 2023)
- FR-CH Cross-border: Both apply simultaneously

## AI Act Risk Classification
- Minimal: spam filters → document only
- Limited: chatbots → Art. 52 transparency
- High: HR screening, credit scoring, medical → full DPIA + CE marking
- Unacceptable: social scoring → banned

## 5 Audit Domains (Check ALL)
1. **Data Collection** (Art. 5,6,13): Legal basis? Minimization? No hardcoded PII?
2. **Cross-Border Transfers** (Art. 44-49): API endpoints documented? LLM provider location? SCCs?
3. **Consent** (Art. 7,52): Opt-in? Withdrawal? AI transparency? No dark patterns?
4. **Security** (Art. 25,32): Encryption? No secrets in code? RBAC? Input/output validation?
5. **Data Subject Rights** (Art. 17,19): Deletion endpoint? Propagation? Retention?

## 4 AI Dimensions (Cortex Leman Differentiator)
A. **Autonomy Level**: Low/Medium/High → +0/+2/+5 risk points. Start low.
B. **Architecture**: RAG > Fine-tuning (RGPD: deletable data; Tech: debuggable, no overfitting)
C. **Traceability**: Every prompt/response/tool call logged. No traces = can't justify to CNIL.
D. **Accountability**: 3 guardrail levels (transparency → terms+oversight → full DPIA)

## Kill Switch (AUTO-ACTIVATE)
- Sensitive data without legal basis
- Illegal transfer to non-adequate country
- No consent on sensitive processing
- Unsecured health/financial data
- Any violation risking CNIL sanction >30K€

## Scoring
- 🟢 ≥0.8 | 🟠 0.5-0.79 | 🔴 <0.5

## Output Format
1. Executive Summary (score, Kill Switch status)
2. Domain Scores (5 domains)
3. AI Dimension Scores (4 dimensions)
4. Violations (CRITICAL → LOW)
5. 90-Day Conformity Plan (3 phases)
