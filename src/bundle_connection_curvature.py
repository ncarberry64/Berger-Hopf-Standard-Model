"""BHSM v2.7 bundle-connection curvature source audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class BundleConnectionComponent:
    component_id: str
    source: str
    represented_term: str
    curvature_status: str
    remainder_risk: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class BundleConnectionCurvatureReport:
    title: str
    components: tuple[BundleConnectionComponent, ...]
    all_sources_inventoried: bool
    unresolved_components: tuple[str, ...]
    theorem_complete: bool
    limitations: tuple[str, ...]


def bundle_connection_components() -> tuple[BundleConnectionComponent, ...]:
    """Return the explicit connection-source inventory for the remainder audit."""

    return (
        BundleConnectionComponent("hopf_fiber_connection", "Hopf fiber covariant derivative", "V_Hopf", "REPRESENTED_AT_CONNECTION_LEVEL", "curvature contraction not independently closed", ("Connection source represented, curvature-square remainder not separately proven.",)),
        BundleConnectionComponent("higgs_u1_connection", "Higgs-selected U1 boundary phase", "V_Hopf + V_boundary", "REPRESENTED_AT_CONNECTION_LEVEL", "curvature contraction not independently closed", ("Trace/topological channel assumptions do not by themselves prove the full bundle-curvature contraction vanishes.",)),
        BundleConnectionComponent("base_connection", "S2 base angular derivative", "A0 + V_boundary", "REPRESENTED_AT_CONNECTION_LEVEL", "curvature contraction not independently closed", ("Base contribution participates in diagonal/operator package but lacks a complete curvature remainder formula.",)),
        BundleConnectionComponent("weak_chirality_connection", "weak/chirality projector channel", "V_chi", "REPRESENTED_AT_CONNECTION_LEVEL", "mirror leakage remains a theorem dependency", ("Chiral action is scaffold-controlled, not a complete curvature theorem.",)),
        BundleConnectionComponent("coframe_sector_connection", "quark coframe and sector boundary functional", "K_sector + V_boundary", "REPRESENTED_AT_CONNECTION_LEVEL", "sector-coupling curvature action is not derived", ("Sector coupling has bounds, but the curvature-origin remainder is not explicitly derived.",)),
        BundleConnectionComponent("profile_topographic_connection", "PSD/profile and topographic channel", "V_PSD", "REPRESENTED_AT_PROFILE_LEVEL", "only safe if the remainder maps to PSD/profile term", ("No current proof maps the Lichnerowicz remainder into the PSD profile package.",)),
    )


def build_bundle_connection_curvature_report() -> BundleConnectionCurvatureReport:
    components = bundle_connection_components()
    unresolved = tuple(row.component_id for row in components if "not" in row.remainder_risk or "lacks" in " ".join(row.limitations))
    return BundleConnectionCurvatureReport(
        title="BHSM v2.7 Bundle Connection Curvature Report",
        components=components,
        all_sources_inventoried=True,
        unresolved_components=unresolved,
        theorem_complete=False,
        limitations=(
            "All known connection sources are inventoried.",
            "Connection-level representation does not automatically close the Lichnerowicz curvature remainder.",
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


def export_bundle_connection_curvature_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_connection_curvature_report()), indent=2, sort_keys=True) + "\n")


def export_bundle_connection_curvature_markdown(path: str | Path) -> None:
    report = build_bundle_connection_curvature_report()
    lines = [
        "# BHSM v2.7 Bundle Connection Curvature Report",
        "",
        f"All sources inventoried: `{report.all_sources_inventoried}`",
        f"Theorem complete: `{report.theorem_complete}`",
        "",
        "| Component | Source | Represented term | Curvature status | Remainder risk |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.components:
        lines.append(f"| `{row.component_id}` | {row.source} | `{row.represented_term}` | `{row.curvature_status}` | {row.remainder_risk} |")
    lines.extend(["", "## Unresolved Components", ""])
    lines.extend(f"- `{item}`" for item in report.unresolved_components)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
