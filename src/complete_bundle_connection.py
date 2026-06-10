"""BHSM v2.9 complete bundle-connection definition audit."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bundle_connection_components import build_bundle_connection_components_report


@dataclass(frozen=True)
class CompleteBundleConnectionReport:
    title: str
    connection_symbol: str
    decomposition: str
    component_count: int
    blocking_components: tuple[str, ...]
    status: str
    theorem_complete: bool
    exact_missing_component: str
    limitations: tuple[str, ...]


def build_complete_bundle_connection_report() -> CompleteBundleConnectionReport:
    components = build_bundle_connection_components_report()
    status = "COMPLETE_BUNDLE_CONNECTION_OPEN" if components.blocking_components else "COMPLETE_BUNDLE_CONNECTION_DEFINED"
    return CompleteBundleConnectionReport(
        title="BHSM v2.9 Complete Bundle Connection Report",
        connection_symbol="nabla_BH",
        decomposition="nabla_BH = nabla_Berger + nabla_Hopf + nabla_boundary + nabla_chirality + nabla_sector + nabla_lift/profile + nabla_mixed",
        component_count=len(components.components),
        blocking_components=components.blocking_components,
        status=status,
        theorem_complete=not components.blocking_components,
        exact_missing_component=components.exact_missing_component,
        limitations=(
            "The complete connection is formalized as a sum of repository-supported components plus a mixed component.",
            "The mixed component is not defined strongly enough to compute its curvature.",
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


def export_complete_bundle_connection_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_complete_bundle_connection_report()), indent=2, sort_keys=True) + "\n")


def export_complete_bundle_connection_markdown(path: str | Path) -> None:
    report = build_complete_bundle_connection_report()
    lines = [
        "# BHSM v2.9 Complete Bundle Connection Report",
        "",
        f"Connection: `{report.connection_symbol}`",
        f"Decomposition: `{report.decomposition}`",
        f"Status: `{report.status}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Exact missing component: `{report.exact_missing_component}`",
        "",
        "## Blocking Components",
        "",
    ]
    lines.extend(f"- `{item}`" for item in report.blocking_components)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
