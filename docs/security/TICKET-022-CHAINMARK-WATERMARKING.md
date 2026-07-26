# TICKET-022 — ChainMark Watermarking pour AI Act Article 50

**Statut:** ✅ IMPLÉMENTÉ
**Priorité:** P0 (deadline légale: 2 août 2026)
**Date:** 2026-07-26
**Référence:** AI Act Art. 50(2), arXiv:2607.18445 (ChainMark)

## Menace

L'AI Act Article 50 impose que tout contenu généré par IA et destiné au public soit marqué de manière **machine-lisible**. Non-conformité = amende jusqu'à 8% du CA global.

## Solution implémentée

Watermarking 3-couches **model-free** (appliqué post-génération, indépendant du LLM) :

| Couche | Mécanisme | Robustesse |
|---|---|---|
| **Stéganographique** | Zero-width Unicode chars (U+200B/U+200C) encodant 72 bits (magic + tenant + timestamp + CRC-8) | Survit au copy-paste. Header contigu en début de texte pour détection fragments. |
| **Cryptographique** | Ed25519 (ou HMAC-SHA256 fallback) sur hash SHA-256 du contenu | Preuve d'origine + intégrité |
| **Visible** | Marqueur multilingue (FR/EN/DE/IT) configurable par tenant | Conformité explicite Art. 50 |

## Architecture

```
LLM Provider Pipeline:
  Phase 1: Guardrails IN (PII, injection)
  Phase 2: Model Router
  Phase 3: LiteLLM Call
  Phase 4: Journal (métadonnées)
  Phase 5: Guardrails OUT (safety)
  Phase 6: ChainMark Watermarking ← NOUVEAU (TICKET-022)
```

**Intégration:** `core/integrations/llm/provider.py` — la méthode `generate()` applique systématiquement le watermark après guardrails OUT. Non-bloquant (erreur loggée, texte retourné sans watermark).

## Fichiers

| Fichier | Rôle |
|---|---|
| `core/security/watermarker.py` | Module ChainMark (watermark, detect, verify) |
| `tests/test_watermarker.py` | 9 tests (readability, detect, copy-paste, signature, visible markers, edge cases, CRC corruption) |
| `core/integrations/llm/provider.py` | Intégration Phase 6 dans le pipeline LLM |

## Tests (9/9 ✅)

1. `test_watermark_preserves_readability` — le texte reste lisible
2. `test_detect_finds_watermark` — détection sur texte watermarked
3. `test_detect_non_watermarked_text` — pas de faux positifs
4. `test_watermark_survives_copy_paste` — copy-paste preserve le watermark
5. `test_metadata_signature_verification` — signature Ed25519 valide + tampering détecté
6. `test_visible_marker_fr_and_en` — marqueurs visibles multilingues
7. `test_no_spaces_edge_case` — texte sans espaces (fallback)
8. `test_short_text` — texte court (<10 mots)
9. `test_crc_validation_catches_corruption` — CRC détecte la corruption de bits

## Conformité AI Act Art. 50

| Exigence Art. 50 | Implémentation |
|---|---|
| Marquage machine-lisible | ✅ Zero-width Unicode + CRC-8 |
| Traçabilité de l'origine | ✅ Ed25519 signature + tenant_id |
| Intégrité du contenu | ✅ SHA-256 content hash |
| Multilingue | ✅ FR/EN/DE/IT |
| Configurable par tenant | ✅ visible on/off, tenant_id |
| Agnostique du modèle | ✅ Appliqué post-génération |

## Limites assumées

- **Substrings < 100 chars** : le watermark peut ne pas être détectable sur des fragments extraits du texte complet. Art. 50 porte sur le contenu complet généré, pas sur chaque fragment.
- **Reformulation agressive** : le watermark stéganographique ne survit pas à une réécriture complète. La couche cryptographique (metadata) reste la preuve d'origine.
- **Pas de stéganalyse adversariale** : le watermark Unicode est détectable par inspection technique. C'est un choix délibéré : Art. 50 exige un marquage *machine-lisible*, pas un marquage indétectable.
