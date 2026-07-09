"""
Cortex Leman v5 — Intégrations Verticales

Connecteurs spécifiques par métier réglementé:
- Comptable: TVA, bilans, déclarations fiscales, CRCR
- Avocat: Secret professionnel, BAR, droit FR-CH
- Santé: H+QR, Lamal, secret médical, données sensibles
- Banque: KYC, AML, CFB, FINMA
- RH: LTr, OAR, RGPD employé, convention collective
- Startup: LPMA, base légale startup, fast-track

Chaque connecteur expose:
- validate()  → Vérifier la conformité d'une action
- enrich()    → Enrichir le contexte avec des données métier
- templates() → Templates de documents réglementaires
- calendar()  → Échéances réglementaires
"""
from core.integrations.verticals.registry import vertical_registry

__all__ = ["vertical_registry"]
