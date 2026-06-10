"""BHSM v2.9 complete bundle-connection component inventory."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


DERIVED_FROM_EXISTING_BHSM_STRUCTURE = "DERIVED_FROM_EXISTING_BHSM_STRUCTURE"
REPRESENTED_BY_EXISTING_TERM = "REPRESENTED_BY_EXISTING_TERM"
ZERO_BY_SYMMETRY = "ZERO_BY_SYMMETRY"
SCREENED_OR_LIFTED = "SCREENED_OR_LIFTED"
CONDITIONAL = "CONDITIONAL"
OPEN = "OPEN"
MISSING = "MISSING"

BLOCKING_COMPONENT_STATUSES = {OPEN, MISSING, CONDITIONAL}


@dataclass(frozen=True)
class BundleConnectionComponent:
    component_id: str
    role: str
    represented_by: str
    status: str
    curvature_contribution: str
    evidence: tuple[str, ...]
    limitation: str


@dataclass(frozen=True)
class BundleConnectionComponentsReport:
    title: str
    components: tuple[BundleConnectionComponent, ...]
    all_components_classified: bool
    blocking_components: tuple[str, ...]
    exact_missing_component: str
    theorem_complete: bool
    limitations: tuple[str, ...]


def bundle_connection_components() -> tuple[BundleConnectionComponent, ...]:
    """Return the current BHSM bundle-connection component inventory."""

    return (
        BundleConnectionComponent("berger_metric_spin_connection", "Berger metric/spin connection", "A0", DERIVED_FROM_EXISTING_BHSM_STRUCTURE, "diagonal_curvature_contribution", ("diagonal reference operator and Berger core are represented",), "Does not determine mixed bundle curvature by itself."),
        BundleConnectionComponent("hopf_twist_connection", "Hopf twist connection", "V_Hopf", REPRESENTED_BY_EXISTING_TERM, "hopf_curvature_contribution", ("Hopf twist is represented in the perturbation package",), "Curvature contraction is represented only at the symbolic term level."),
        BundleConnectionComponent("u1_fiber_connection", "U1/fiber connection", "V_Hopf + V_boundary", REPRESENTED_BY_EXISTING_TERM, "fiber_curvature_contribution", ("Higgs-selected U1 and Hopf/fiber data are represented",), "Trace/nondynamical assumptions must be retained."),
        BundleConnectionComponent("base_s2_connection", "base/S2 connection", "A0 + V_boundary", REPRESENTED_BY_EXISTING_TERM, "base_curvature_contribution", ("base contribution is represented in diagonal and boundary scaffolds",), "Complete mixed base/fiber commutators are not derived."),
        BundleConnectionComponent("boundary_functional_connection", "boundary functional connection", "V_boundary", DERIVED_FROM_EXISTING_BHSM_STRUCTURE, "boundary_curvature_contribution", ("v1.2/v2 action-origin scaffolds supply the boundary functional",), "Global derivation from a full action remains a separate limitation."),
        BundleConnectionComponent("chirality_projector_connection", "chirality/projector connection", "V_chi", REPRESENTED_BY_EXISTING_TERM, "chirality_curvature_contribution", ("chiral projector channel is represented and tested",), "Does not prove all mixed curvature contractions preserve chirality."),
        BundleConnectionComponent("sector_lepton_up_down_connection", "sector lepton/up/down connection", "K_sector + V_boundary", REPRESENTED_BY_EXISTING_TERM, "sector_mixing_curvature_contribution", ("sector-labeled formal kernel and sector-coupling scaffolds are represented",), "Complete sector curvature coefficients remain symbolic."),
        BundleConnectionComponent("higgs_u1_connection", "Higgs-U1 connection", "V_Hopf + V_boundary", REPRESENTED_BY_EXISTING_TERM, "higgs_u1_curvature_contribution", ("Higgs-selected U1 channel is represented",), "Standalone curvature action on mirrors remains conditional."),
        BundleConnectionComponent("lift_profile_heat_connection", "lift/profile/heat connection", "P_perp_lift + V_PSD", SCREENED_OR_LIFTED, "lift_profile_curvature_contribution", ("lift/profile channels are screened, lifted, or PSD-controlled in scaffolds",), "Only applies once the remainder is mapped into this package."),
        BundleConnectionComponent("scalar_topographic_leakage_channel", "scalar/topographic leakage channel", "scalar/topographic screened sector", SCREENED_OR_LIFTED, "scalar_topographic_curvature_contribution", ("scalar/topographic screening scaffold excludes low-energy leakage at audit level",), "Full scalar action proof remains separate."),
        BundleConnectionComponent("mirror_channel_connection", "mirror channel", "V_chi + Higgs-U1 + boundary channels", CONDITIONAL, "mirror_curvature_contribution", ("mirror candidates are scaffold-excluded by chiral projector, with Higgs-U1/boundary channels conditional",), "Complete curvature action on mirror channels is not independently proven."),
        BundleConnectionComponent("mixed_hopf_base_boundary_coframe_connection", "mixed Hopf/base/boundary/coframe connection", "not represented", MISSING, "mixed_curvature_remainder", ("no repo object specifies the full mixed connection coefficients and Clifford contraction",), "Single missing connection component blocking the complete curvature formula."),
    )


def build_bundle_connection_components_report() -> BundleConnectionComponentsReport:
    components = bundle_connection_components()
    blocking = tuple(row.component_id for row in components if row.status in BLOCKING_COMPONENT_STATUSES)
    exact_missing = "mixed_hopf_base_boundary_coframe_connection" if "mixed_hopf_base_boundary_coframe_connection" in blocking else ""
    return BundleConnectionComponentsReport(
        title="BHSM v2.9 Bundle Connection Components Report",
        components=components,
        all_components_classified=all(row.status for row in components),
        blocking_components=blocking,
        exact_missing_component=exact_missing,
        theorem_complete=not blocking,
        limitations=(
            "Every listed connection component is classified.",
            "The mixed Hopf/base/boundary/coframe connection remains the first missing geometric input.",
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


def export_bundle_connection_components_json(path: str | Path) -> None:
    Path(path).write_text(json.dumps(_jsonable(build_bundle_connection_components_report()), indent=2, sort_keys=True) + "\n")


def export_bundle_connection_components_markdown(path: str | Path) -> None:
    report = build_bundle_connection_components_report()
    lines = [
        "# BHSM v2.9 Bundle Connection Components Report",
        "",
        f"All components classified: `{report.all_components_classified}`",
        f"Theorem complete: `{report.theorem_complete}`",
        f"Exact missing component: `{report.exact_missing_component}`",
        "",
        "| Component | Role | Represented by | Status | Curvature contribution | Limitation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.components:
        lines.append(f"| `{row.component_id}` | {row.role} | `{row.represented_by}` | `{row.status}` | `{row.curvature_contribution}` | {row.limitation} |")
    lines.extend(["", "## Blocking Components", ""])
    lines.extend(f"- `{item}`" for item in report.blocking_components)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    lines.append("")
    Path(path).write_text("\n".join(lines))
