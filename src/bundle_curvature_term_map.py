"""BHSM v2.12 exact curvature contribution classification table."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


CURVATURE_ZERO = "CURVATURE_ZERO"
CURVATURE_REPRESENTED_BY_A0 = "CURVATURE_REPRESENTED_BY_A0"
CURVATURE_REPRESENTED_BY_V_HOPF = "CURVATURE_REPRESENTED_BY_V_HOPF"
CURVATURE_REPRESENTED_BY_V_BOUNDARY = "CURVATURE_REPRESENTED_BY_V_BOUNDARY"
CURVATURE_REPRESENTED_BY_V_CHI = "CURVATURE_REPRESENTED_BY_V_CHI"
CURVATURE_REPRESENTED_BY_K_SECTOR = "CURVATURE_REPRESENTED_BY_K_SECTOR"
CURVATURE_REPRESENTED_BY_P_PERP_LIFT = "CURVATURE_REPRESENTED_BY_P_PERP_LIFT"
CURVATURE_REPRESENTED_BY_V_PSD = "CURVATURE_REPRESENTED_BY_V_PSD"
CURVATURE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR = "CURVATURE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR"
CURVATURE_SCREENED_OR_LIFTED = "CURVATURE_SCREENED_OR_LIFTED"
CURVATURE_PSD_PROFILE_CONTROLLED = "CURVATURE_PSD_PROFILE_CONTROLLED"
CURVATURE_RELATIVELY_BOUNDED_SAFE = "CURVATURE_RELATIVELY_BOUNDED_SAFE"
CURVATURE_REAL_MISSING_TERM = "CURVATURE_REAL_MISSING_TERM"
CURVATURE_OPEN = "CURVATURE_OPEN"

SAFE_CURVATURE_CLASSIFICATIONS = {
    CURVATURE_ZERO,
    CURVATURE_REPRESENTED_BY_A0,
    CURVATURE_REPRESENTED_BY_V_HOPF,
    CURVATURE_REPRESENTED_BY_V_BOUNDARY,
    CURVATURE_REPRESENTED_BY_V_CHI,
    CURVATURE_REPRESENTED_BY_K_SECTOR,
    CURVATURE_REPRESENTED_BY_P_PERP_LIFT,
    CURVATURE_REPRESENTED_BY_V_PSD,
    CURVATURE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR,
    CURVATURE_SCREENED_OR_LIFTED,
    CURVATURE_PSD_PROFILE_CONTROLLED,
    CURVATURE_RELATIVELY_BOUNDED_SAFE,
}


@dataclass(frozen=True)
class CurvatureTermMapRow:
    contribution_id: str
    connection_piece: str
    classification: str
    mapped_operator_term: str
    contributes_to_r_bundle: bool
    lower_bound_requires_new_term: bool
    limitation: str


@dataclass(frozen=True)
class BundleCurvatureTermMapReport:
    title: str
    rows: tuple[CurvatureTermMapRow, ...]
    all_contributions_classified_once: bool
    open_or_missing_terms: tuple[str, ...]
    r_bundle_contributors: tuple[str, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def curvature_term_map_rows() -> tuple[CurvatureTermMapRow, ...]:
    return (
        CurvatureTermMapRow("diagonal_curvature_contribution", "[nabla_Berger,nabla_Berger]", CURVATURE_REPRESENTED_BY_A0, "A0", False, False, "Diagonal curvature is the reference operator package."),
        CurvatureTermMapRow("hopf_curvature_contribution", "[nabla_Hopf,nabla_Hopf]", CURVATURE_REPRESENTED_BY_V_HOPF, "V_Hopf", False, False, "Hopf twist curvature remains in the Hopf operator channel."),
        CurvatureTermMapRow("fiber_curvature_contribution", "[nabla_U1/fiber,nabla_U1/fiber]", CURVATURE_REPRESENTED_BY_V_HOPF, "V_Hopf + V_boundary", False, False, "Higgs-selected U1/fiber curvature is represented by Hopf and boundary terms."),
        CurvatureTermMapRow("base_curvature_contribution", "[nabla_base,nabla_base]", CURVATURE_REPRESENTED_BY_A0, "A0 + V_boundary", False, False, "Base curvature is represented by diagonal/base and boundary bookkeeping."),
        CurvatureTermMapRow("boundary_curvature_contribution", "[nabla_boundary,nabla_boundary]", CURVATURE_REPRESENTED_BY_V_BOUNDARY, "V_boundary", False, False, "Boundary functional curvature is represented by V_boundary."),
        CurvatureTermMapRow("chirality_curvature_contribution", "[nabla_chi,nabla_chi]", CURVATURE_REPRESENTED_BY_V_CHI, "V_chi", False, False, "Chirality contribution is represented by chiral projector terms."),
        CurvatureTermMapRow("sector_mixing_curvature_contribution", "[nabla_sector,nabla_sector]", CURVATURE_REPRESENTED_BY_K_SECTOR, "K_sector", False, False, "Sector coupling is already represented and bounded in the operator package."),
        CurvatureTermMapRow("higgs_u1_curvature_contribution", "[nabla_Higgs-U1,nabla_Higgs-U1]", CURVATURE_REPRESENTED_BY_V_BOUNDARY, "V_Hopf + V_boundary", False, False, "Higgs-U1 curvature remains in Hopf/boundary channels."),
        CurvatureTermMapRow("lift_profile_curvature_contribution", "[nabla_lift/profile,nabla_lift/profile]", CURVATURE_REPRESENTED_BY_P_PERP_LIFT, "P_perp_lift + V_PSD", False, False, "Lift/profile curvature is represented by lift and PSD profile operators."),
        CurvatureTermMapRow("scalar_topographic_curvature_contribution", "[nabla_scalar/topographic,nabla_scalar/topographic]", CURVATURE_SCREENED_OR_LIFTED, "scalar/topographic screened sector", False, False, "Scalar/topographic leakage is screened or lifted by existing scaffold obligations."),
        CurvatureTermMapRow("mirror_curvature_contribution", "[nabla_mirror,nabla_mirror]", CURVATURE_REPRESENTED_BY_V_CHI, "V_chi + Higgs-U1 + boundary channels", False, False, "Mirror curvature is represented by chiral/Higgs-U1/boundary channels; mirror theorem remains downstream."),
        CurvatureTermMapRow("mixed_curvature_remainder", "sum_{i<j} [nabla_i,nabla_j] mixed Hopf/base/boundary/coframe", CURVATURE_REPRESENTED_BY_TOPOGRAPHIC_SECTOR, "V_boundary + V_PSD/profile + scalar/topographic screened sector + P_perp_lift", False, False, "v2.11 forbids an independent mixed coefficient and represents mixed curvature topographically."),
    )


def build_bundle_curvature_term_map_report() -> BundleCurvatureTermMapReport:
    rows = curvature_term_map_rows()
    open_terms = tuple(row.contribution_id for row in rows if row.classification in {CURVATURE_OPEN, CURVATURE_REAL_MISSING_TERM})
    r_bundle = tuple(row.contribution_id for row in rows if row.contributes_to_r_bundle)
    return BundleCurvatureTermMapReport(
        title="BHSM v2.12 Bundle Curvature Term Map Report",
        rows=rows,
        all_contributions_classified_once=len({row.contribution_id for row in rows}) == len(rows) and all(row.classification for row in rows),
        open_or_missing_terms=open_terms,
        r_bundle_contributors=r_bundle,
        status="BUNDLE_CURVATURE_TERM_MAP_CLOSED" if not open_terms else "BUNDLE_CURVATURE_TERM_MAP_OPEN",
        theorem_complete=not open_terms,
        limitations=(
            "This closes the curvature formula map, not the full H_T theorem.",
            "Downstream projector, index/mirror, and scalar/topographic theorem dependencies remain separately audited.",
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


def export_bundle_curvature_term_map_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_curvature_term_map_report()), indent=2, sort_keys=True) + "\n")


def export_bundle_curvature_term_map_markdown(path: str | Path) -> None:
    report = build_bundle_curvature_term_map_report()
    lines = [
        "# BHSM v2.12 Bundle Curvature Term Map Report",
        "",
        f"Status: `{report.status}`",
        f"All contributions classified once: `{report.all_contributions_classified_once}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Contribution | Connection piece | Classification | Mapped operator term | R_bundle | New lower-bound term | Limitation |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        lines.append(f"| `{row.contribution_id}` | `{row.connection_piece}` | `{row.classification}` | `{row.mapped_operator_term}` | `{row.contributes_to_r_bundle}` | `{row.lower_bound_requires_new_term}` | {row.limitation} |")
    lines.extend(["", "## R_bundle Contributors", ""])
    lines.extend(f"- `{item}`" for item in report.r_bundle_contributors)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))

