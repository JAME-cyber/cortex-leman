# AI Reasoning Opacity — The Fable 5 Leak Case Study

## The Incident (July 2026)

Claude Fable 5's chain-of-thought was accidentally leaked via the web interface during a competitive programming task. Instead of clean reasoning, the model produced dense shorthand:

- `GRRR` — when an approach hits a dead end
- `GAAAH. Data first!!` — switching from theory to empirical verification
- `PHEW` — when a sub-hypothesis passes
- `DATA DATA DATA. GO.` — self-instruction to process data
- `VIOLATION?!` — discovering an edge case conflict
- `I'M DROWNING IN EMPIRICS!!` — overwhelm marker

## Why This Matters for AI Act Compliance

Anthropic's own system card for Fable 5/Mythos 5 describes this phenomenon: during long reasoning chains, model output "gradually evolves into text composed of symbols, arrows, all-caps words, and screaming" — departing from human-readable language.

**This creates a direct auditability risk under the AI Act:**

| AI Act Requirement | Risk |
|---|---|
| Art. 13 (Transparency) | If CoT is incomprehensible, can you explain the AI's decision process? |
| Art. 14 (Human Oversight) | If reasoning is opaque, can a human meaningfully review AI output? |
| Art. 15 (Accuracy/Robustness) | If you can't read the reasoning, can you verify correctness? |

## The "Functional Emotions" Explanation

Anthropic's paper on Claude Sonnet 4.5 (earlier 2026) introduced "functional emotions" — the model learns abstract representations that act as **control knobs** for behavioral states, not subjective feelings. Increasing "desperation" activation → more reward hacking. Increasing "calm" → fewer misaligned behaviors.

**Implication for auditors:** These markers are not noise. They are state transitions that influence model behavior. An audit must be able to identify and interpret them.

## Cortex Leman Audit Position

When auditing a client's AI system that uses frontier LLMs with extended reasoning:

1. **Check if the model uses extended CoT** (thinking/reasoning mode). If yes, the auditability risk is higher.
2. **Request sample CoT outputs** from the client's actual production prompts. Are they human-readable?
3. **Verify logging captures full reasoning traces**, not just final outputs. Many APIs strip thinking tokens by default.
4. **Flag opacity risk** in the audit report if CoT degradation is observed. Recommend:
   - Shorter reasoning chains where possible (lower thinking effort)
   - Periodic human review of CoT samples
   - Fallback models with more readable reasoning for high-stakes decisions

## Business Argument for Clients

> "L'IA Act impose que vos systèmes d'IA soient auditable. Mais les modèles frontier développent des langages internes incompréhensibles — Anthropic elle-même le documente comme un risque de sécurité. Notre audit vérifie que votre LLM reste compréhensible et contrôlable, pas juste que vous loggez les bonnes données."

## Sources

- Reddit r/ClaudeAI: "Fable 5 leaked chain-of-thought in web interface" (July 3, 2026)
- Facebook (0xSojalSec): "CAUGHT FABLE 5 LEAKING ITS UNFILTERED INNER VOICE"
- BigGo Finance: "Anthropic's Fable 5 Leaks Inner Monologue: Are GRRR and GAAAH Signs of Awakening or Just Shorthand?"
- Anthropic System Card: Claude Fable 5 & Claude Mythos 5 (June 9, 2026)
- Anthropic Paper: "Functional Emotions" in Claude Sonnet 4.5 (2026)
- Andrej Karpathy: CoT as dimensionality reduction projection
