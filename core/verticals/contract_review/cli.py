"""
CLI pour la revue assistée de contrats.

Usage :
    python -m core.verticals.contract_review chemin/vers/contrat.txt
    python -m core.verticals.contract_review chemin/vers/contrat.pdf --type nda --json

Le mode CLI n'instancie aucun LLM concret. Pour une analyse LLM, injecter un
LLMProvider via l'API Python ou l'orchestration agent existante.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .models import ContractDocument, ContractLanguage, ContractType
from .reviewer import ContractReviewer


def main() -> int:
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(
        prog="python -m core.verticals.contract_review",
        description="Revue assistée non décisionnelle de contrats pour avocats.",
    )
    parser.add_argument("path", type=Path, help="Chemin vers un contrat .txt, .md ou .pdf.")
    parser.add_argument("--type", choices=[item.value for item in ContractType], default=ContractType.OTHER.value)
    parser.add_argument("--language", choices=[item.value for item in ContractLanguage], default=ContractLanguage.FRENCH.value)
    parser.add_argument("--jurisdiction", default=None, help="Juridiction attendue, ex. Suisse, France.")
    parser.add_argument("--governing-law", default=None, help="Droit applicable si connu.")
    parser.add_argument("--title", default=None, help="Titre du contrat.")
    parser.add_argument("--json", action="store_true", help="Affiche le résultat JSON complet.")
    args = parser.parse_args()

    text = _read_document(args.path)
    contract = ContractDocument(
        title=args.title or args.path.stem,
        contract_type=ContractType(args.type),
        jurisdiction=args.jurisdiction,
        governing_law=args.governing_law,
        language=ContractLanguage(args.language),
        text=text,
        source_path=str(args.path),
    )

    reviewer = ContractReviewer(llm_provider=None)
    result = asyncio.run(reviewer.review_contract(contract))

    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(_format_report(result))
    return 0


def _read_document(path: Path) -> str:
    """Lit un fichier texte ou PDF en UTF-8."""
    if not path.exists():
        raise FileNotFoundError(f"Document introuvable: {path}")
    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    raise ValueError("Format non supporté. Utiliser .txt, .md ou .pdf.")


def _read_pdf(path: Path) -> str:
    """Extrait le texte d'un PDF via pypdf si disponible."""
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:
        raise RuntimeError("Lecture PDF indisponible : installer pypdf ou fournir un .txt.") from exc

    reader = PdfReader(str(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        extracted = page.extract_text() or ""
        pages.append(f"\n\n--- Page {index} ---\n{extracted}")
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("Aucun texte extractible depuis le PDF. OCR requis avant revue.")
    return text


def _format_report(result) -> str:
    """Formate un rapport lisible pour usage CLI."""
    lines: list[str] = [
        "REVUE ASSISTÉE DE CONTRAT — CORTEX LEMAN v5",
        "=" * 56,
        f"Review ID      : {result.review_id}",
        f"Contract ID    : {result.contract_id}",
        f"Hash contrat   : {result.contract_hash}",
        f"Score risque   : {result.risk_score}/100 ({result.risk_level.value})",
        "",
        "SYNTHÈSE",
        "-" * 56,
        result.summary,
        "",
        "ISSUES DÉTECTÉES",
        "-" * 56,
    ]

    if not result.issues:
        lines.append("Aucune issue détectée par les contrôles exécutés.")
    else:
        for index, issue in enumerate(result.issues, start=1):
            location = issue.location.clause_ref or issue.location.section_title or "localisation à confirmer"
            lines.extend(
                [
                    f"{index}. [{issue.severity.value.upper()}] {issue.title}",
                    f"   Catégorie      : {issue.category.value}",
                    f"   Source         : {issue.source.value}",
                    f"   Action         : {issue.action or 'validation'}",
                    f"   Localisation   : {location}",
                    f"   Extrait        : {issue.location.excerpt or 'n/a'}",
                    f"   Base juridique : {', '.join(issue.legal_basis) if issue.legal_basis else 'à confirmer'}",
                    f"   Recommandation : {issue.recommendation}",
                    f"   Rationnel      : {issue.rationale}",
                    "",
                ]
            )

    lines.extend(
        [
            "",
            "POINTS À VALIDER PAR L'AVOCAT",
            "-" * 56,
            *[f"- {point}" for point in result.human_validation_points],
            "",
            "DISCLAIMERS",
            "-" * 56,
            *[f"- {disclaimer}" for disclaimer in result.disclaimers],
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
