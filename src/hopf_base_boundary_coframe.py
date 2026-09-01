"""BHSM v2.10 mixed Hopf/base/boundary/coframe sector audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from mixed_connection_coefficients import MIXED_COEFFICIENT_OPEN, build_mixed_connection_coefficients_report


@dataclass(frozen=True)
class MixedSectorFeature:
    feature_id: str
    status: str
    conclusion: str
    limitation: str


@dataclass(frozen=True)
class HopfBaseBoundaryCoframeReport:
    title: str
    coefficient_status: str
    features: tuple[MixedSectorFeature, ...]
    status: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def build_hopf_base_boundary_coframe_report() -> HopfBaseBoundaryCoframeReport:
    coeffs = build_mixed_connection_coefficients_report()
    features = (
        MixedSectorFeature("hopf_fiber_base_cross_terms", "OPEN", "symbolic slot identified", "coefficient rule is not derived"),
        MixedSectorFeature("base_boundary_cross_terms", "OPEN", "symbolic slot identified", "base/boundary phase coefficient is not derived"),
        MixedSectorFeature("boundary_coframe_cross_terms", "OPEN", "symbolic slot identified", "coframe coefficient is not derived"),
        MixedSectorFeature("hopf_boundary_coframe_mixed_terms", "OPEN", "symbolic slot identified", "triple mixed coefficient is not derived"),
        MixedSectorFeature("chirality_dependence", "OPEN", "chirality dependence is identified but not computed", "mirror-channel action remains open"),
        MixedSectorFeature("sector_dependence", "OPEN", "sector dependence is identified but not computed", "lepton/up/down weights remain open"),
        MixedSectorFeature("formal_kernel_action", "OPEN", "not proven to vanish on formal kernel", "requires explicit mixed coefficients"),
        MixedSectorFeature("h_perp_preservation", "OPEN", "not proven to preserve H_perp", "requires explicit mixed coefficients"),
    )
    return HopfBaseBoundaryCoframeReport(
        title="BHSM v2.10 Hopf/Base/Boundary/Coframe Report",
        coefficient_status=coeffs.status,
        features=features,
        status="HOPF_BASE_BOUNDARY_COFRAME_OPEN" if coeffs.status == MIXED_COEFFICIENT_OPEN else "HOPF_BASE_BOUNDARY_COFRAME_DERIVED",
        theorem_complete=False,
        limitations=(
            "The mixed sector is formalized but not derived.",
            "No formal-kernel or H_perp safety follows without coefficients.",
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


def export_hopf_base_boundary_coframe_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_hopf_base_boundary_coframe_report()), indent=2, sort_keys=True) + "\n")


def export_hopf_base_boundary_coframe_markdown(path: str | Path) -> None:
    report = build_hopf_base_boundary_coframe_report()
    lines = [
        "# BHSM v2.10 Hopf/Base/Boundary/Coframe Report",
        "",
        f"Coefficient status: `{report.coefficient_status}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Feature | Status | Conclusion | Limitation |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.features:
        lines.append(f"| `{row.feature_id}` | `{row.status}` | {row.conclusion} | {row.limitation} |")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
