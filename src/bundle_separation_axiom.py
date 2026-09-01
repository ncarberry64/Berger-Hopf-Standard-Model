"""BHSM v2.11 bundle-separation/topographic-representation axiom."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION = "BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION"

BUNDLE_SEPARATION_AXIOM_FORMALIZED = "BUNDLE_SEPARATION_AXIOM_FORMALIZED"
BUNDLE_SEPARATION_AXIOM_CONDITIONAL = "BUNDLE_SEPARATION_AXIOM_CONDITIONAL"
BUNDLE_SEPARATION_AXIOM_OPEN = "BUNDLE_SEPARATION_AXIOM_OPEN"
BUNDLE_SEPARATION_AXIOM_FAILS = "BUNDLE_SEPARATION_AXIOM_FAILS"


@dataclass(frozen=True)
class BundleSeparationClause:
    clause_id: str
    statement: str
    consequence: str
    status: str
    limitation: str


@dataclass(frozen=True)
class BundleSeparationAxiomReport:
    title: str
    axiom_id: str
    status: str
    clauses: tuple[BundleSeparationClause, ...]
    forbids_free_mixed_coefficient: bool
    allows_topographic_representation: bool
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_bundle_separation_axiom_report() -> BundleSeparationAxiomReport:
    clauses = (
        BundleSeparationClause(
            "local_sm_bundle_unchanged",
            "Local Standard Model bundle, gauge, and Dirac dynamics remain locally unchanged.",
            "Mixed Hopf/base/topographic structure cannot introduce an independent SM gauge curvature source.",
            BUNDLE_SEPARATION_AXIOM_FORMALIZED,
            "This is a BHSM structural axiom, not an external theorem of the Standard Model.",
        ),
        BundleSeparationClause(
            "topographic_representation",
            "Mixed topographic/geometric effects enter through existing scalar, boundary, profile, screening, or lift sectors.",
            "Mixed coefficient slots must map to existing BHSM operator packages or remain a real missing term.",
            BUNDLE_SEPARATION_AXIOM_FORMALIZED,
            "The axiom classifies representation channels but does not prove the full H_T theorem by itself.",
        ),
        BundleSeparationClause(
            "no_free_mixed_coefficient",
            "No new free Hopf/base/boundary/coframe coefficient may be introduced or fit.",
            "A fitted or independent mixed coefficient is forbidden.",
            BUNDLE_SEPARATION_AXIOM_FORMALIZED,
            "If representation fails, the result is a theorem gap or failure, not a tunable parameter.",
        ),
    )
    return BundleSeparationAxiomReport(
        title="BHSM v2.11 Bundle-Separation / Topographic-Representation Axiom Report",
        axiom_id=BUNDLE_CONNECTION_SEPARATION_WITH_TOPOGRAPHIC_REPRESENTATION,
        status=BUNDLE_SEPARATION_AXIOM_FORMALIZED,
        clauses=clauses,
        forbids_free_mixed_coefficient=True,
        allows_topographic_representation=True,
        theorem_complete=True,
        limitations=(
            "The axiom is internal to BHSM and does not prove the complete H_T theorem alone.",
            "It forbids fitted mixed coefficients and forces representation, screening, lift, PSD/profile control, or an explicit failure.",
        ),
    )


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def export_bundle_separation_axiom_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_separation_axiom_report()), indent=2, sort_keys=True) + "\n")


def export_bundle_separation_axiom_markdown(path: str | Path) -> None:
    report = build_bundle_separation_axiom_report()
    lines = [
        "# BHSM v2.11 Bundle-Separation / Topographic-Representation Axiom Report",
        "",
        f"Axiom: `{report.axiom_id}`",
        f"Status: `{report.status}`",
        f"Forbids free mixed coefficient: `{report.forbids_free_mixed_coefficient}`",
        f"Allows topographic representation: `{report.allows_topographic_representation}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Clause | Statement | Consequence | Status | Limitation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.clauses:
        lines.append(f"| `{row.clause_id}` | {row.statement} | {row.consequence} | `{row.status}` | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

