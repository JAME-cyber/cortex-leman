---
name: security-audit-cortex-leman
category: cortex-leman
description: Audit de securite codebase complet pour Cortex Leman. Scan OWASP Top 10 + LLM Top 10 + RGPD/AI Act. Genere rapports structures avec scoring CVSS et plan de remediation 90 jours.
tags: [security, audit, owasp, llm-security, rgpd, ai-act, cortex-leman, compliance]
---

# Security Audit - Cortex Leman

**Version:** 1.0
**Auteur:** Cortex Leman Security Team
**Usage:** Audit de securite complet d'une codebase pour PME FR-CH

## QUAND UTILISER

- Audit de securite pour un client Cortex Leman
- Scan pre-deploiement d'une application
- Audit RGPD-IA d'un systeme utilisant des LLMs
- Compliance check avant mise en production

## ARCHITECTURE

```
security-audit-cortex-leman/
  SKILL.md                           -- Ce fichier
  scripts/
    security_scanner.py              -- Scanner principal (Python, AST + patterns)
  templates/
    audit_report.md                  -- Template rapport d'audit
    finding_card.md                  -- Template par finding
```

## METHODOLOGIE D'AUDIT

### Phase 1 : Discovery

```bash
# Lister la structure du projet
find <target_dir> -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" -o -name "*.env" -o -name "*.conf" -o -name "*.cfg" -o -name "*.toml" -o -name "*.dockerfile" -o -name "Dockerfile" -o -name "*.sh" \) | head -200

# Compter les fichiers par type
find <target_dir> -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
```

### Phase 2 : Scan Automatise

```bash
# Executer le scanner
python3 ~/.hermes/skills/cortex-leman/security-audit-cortex-leman/scripts/security_scanner.py <target_dir>
```

Le scanner genere un JSON avec tous les findings.

### Phase 3 : Analyse Manuelle

Complementer le scan automatique avec :
1. Review des prompts systeme (si LLM present)
2. Analyse des flux de donnees personnelles
3. Verification des bases legales RGPD
4. Check des transferts internationaux

### Phase 4 : Rapport

Utiliser les templates pour generer le rapport final.

## CHECKS IMPLEMENTES

### OWASP Top 10 (A01-A10)

| ID | Categorie | Checks |
|----|-----------|--------|
| A01 | Broken Access Control | Routes sans auth, CORS wildcard, admin expose |
| A02 | Cryptographic Failures | MD5, SHA1, hardcoded secrets, TLS desactive, crypto faible |
| A03 | Injection | SQL injection, command injection, eval(), exec(), XSS patterns |
| A04 | Insecure Design | Absence rate limiting, pas de validation input |
| A05 | Security Misconfiguration | Debug=True, stack traces exposees, default credentials |
| A06 | Vulnerable Components | Versions obsoletes dans requirements/package.json |
| A07 | Auth Failures | JWT sans verif, sessions insecurees, mots de passe en clair |
| A08 | Integrity Failures | Deserialisation non sure (pickle, yaml.load), pas de signature |
| A09 | Logging Failures | Donnees sensibles dans logs, absence de logging |
| A10 | SSRF | fetch/requests vers URLs user-controlled |

### OWASP LLM Top 10

| ID | Risque | Checks |
|----|--------|--------|
| LLM01 | Prompt Injection | System prompts injectables, absence de guardrails |
| LLM02 | Insecure Output Handling | Output LLM passe a exec/eval sans validation |
| LLM03 | Training Data Poisoning | Donnees d'entrainement non verifiees |
| LLM04 | Denial of Service | Pas de rate limiting sur appels LLM, pas de timeout |
| LLM05 | Supply Chain | Modeles non signes, dependances IA non verifiees |
| LLM06 | Sensitive Info Disclosure | API keys dans prompts, PII dans logs, system prompt expose |
| LLM07 | Insecure Plugin Design | Plugins sans sandbox, permissions excessives |
| LLM08 | Excessive Agency | LLM avec acces direct a outils critiques sans HITL |
| LLM09 | Overreliance | Absence de validation output, confiance aveugle |
| LLM10 | Model Theft | Modeles exposes publiquement, absence d'auth sur endpoints |

### RGPD / AI Act (FR-CH)

| Article | Check |
|---------|-------|
| Art. 5,6,13 | Base legale de collecte, information des personnes |
| Art. 7 | Consentement libre, eclaire, specifique, non ambigu |
| Art. 17 | Droit a l'oubli implemente |
| Art. 22 | Decision automatisee — niveau d'autonomie IA (voir ci-dessous) |
| Art. 25,32 | Chiffrement, securite des donnees |
| Art. 30 | Registre des traitements — traces LLM obligatoires |
| Art. 35 | DPIA si autonomie IA haute |
| Art. 44-49 | Transferts internationaux documents |
| AI Act 10,52 | Documentation systeme IA, transparence |

### Dimension IA : Niveau d'Autonomie (Source: Stanford CS230)

| Niveau | Description | Risque RGPD | Action audit |
|--------|-------------|-------------|--------------|
| Low | Humain approuve chaque action | Minimal | Standard |
| Medium | Agent agit, humain reveise | Traabilite obligatoire | Verifier logs + reseau humain |
| High | Agent autonome, alertes exceptions | **DPIA obligatoire** | DPIA + traces + Kill Switch + Art. 22 |

Commencer a basse autonomie. Ne pas valider haute autonomie sans DPIA.

### Dimension IA : Architecture Recommandee (RAG > Fine-Tuning)

**Position Cortex Leman :** RAG systematiquement recommande pour PME FR-CH.

- RAG : donnees dans index controlable, auditable, supprimable (Art. 17)
- Fine-tuning : donnees bakees dans modele opaque, suppression impossible
- Fine-tuning justifie UNIQUEMENT si : format ultra-specifique + 1000+ exemples + tache stable + latence critique

### Dimension IA : Exigences de Traabilite

**Sans traces LLM = impossible de justifier une decision IA (Art. 22 RGPD).**

Exigences minimales :
- Traces completes (chaque prompt, reponse, appel d'outil)
- Evals composants (objectif : assertions Python / subjectif : LLM judges)
- Evals end-to-end (workflow complet pre-deploy)
- Outils recommandes : LangSmith, Braintrust, Helicone, Arize

Matrice 2x2 : Component-based x Objectif/Subjectif + End-to-end x Objectif/Subjectif

## SCORING

### Severity (basee sur CVSS simplifie)

- **Critical** (9.0-10.0) : RCE, data breach, auth bypass
- **High** (7.0-8.9) : Injection, crypto weakness, privilege escalation
- **Medium** (4.0-6.9) : Misconfiguration, info disclosure partielle
- **Low** (0.1-3.9) : Best practice, hardening recommandation
- **Info** (0.0) : Observation, pas de risque direct

### Score Global

```
Score = (1 - (sum(critical*10 + high*5 + medium*2 + low*0.5) / max_possible)) * 100
```

- 0-30 : CRITIQUE (deployment bloque)
- 31-60 : INSUFFISANT (corrections urgentes)
- 61-80 : ACCEPTABLE (ameliorations necessaires)
- 81-95 : BON (minorites a corriger)
- 96-100 : EXCELLENT

## INTEGRATION CORTEX LEMAN

Ce skill s'integre avec :

- **Le Gardien des Normes** : Validation compliance RGPD/AI Act
- **L'Oeil de Cortex** : Analyse des donnees et visualisation
- **Le Narrateur Augmente** : Generation rapport premium
- **L'Ingenieur de Flux** : Orchestration pipeline d'audit

## PITFALLS

- Le scanner automatique ne remplace PAS l'analyse manuelle
- Toujours verifier les resultats du scanner (false positives possibles)
- Pour les audits RGPD, le consentement et les bases legales doivent etre verifies manuellement
- Les scores LLM Top 10 sont en partie subjectifs - documenter le raisonnement
- Toujours generer le rapport depuis les templates pour rester coherent

## REFERENCES

- OWASP Top 10 2021 : https://owasp.org/Top10/
- OWASP LLM Top 10 : https://genai.owasp.org/
- OWASP ASVS v4.0 : https://owasp.org/www-project-application-security-verification-standard/
- RGPD : Reglement UE 2016/679
- AI Act : Reglement UE 2024/1689
- CNIL : https://www.cnil.fr
