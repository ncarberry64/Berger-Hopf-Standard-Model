"""BHSM v6.0 S7 fibration and physical fiber-integration audit.

This module separates exact bundle geometry from the still-missing theorem
that would select one of those bundles as the physical BHSM action domain.
All numerical examples are convention checks, not physical BHSM inputs.
"""

from __future__ import annotations

import json
from math import pi
from pathlib import Path
from typing import Any


VERSION = "v6.0"
SPRINT = "bhsm-s7-fiber-integration-physical-localization-v6-0"
PRIMARY_RESULT = "BHSM_S7_ARCHITECTURE_AMBIGUOUS"
NESTED_RESULT = "BHSM_S7_NESTED_HOPF_TWISTOR_DIAGRAM_DERIVED"
PUSHFORWARD_RESULT = "BHSM_S7_FIBER_PUSHFORWARD_DERIVED_CONDITIONALLY"

ARTIFACT_FILES = {
    "source_inventory": "BHSM_s7_legacy_geometry_source_inventory_v6_0.json",
    "fibration_ledger": "BHSM_s7_canonical_fibration_ledger_v6_0.json",
    "nested_diagram": "BHSM_s7_nested_hopf_twistor_diagram_v6_0.json",
    "metric_measure": "BHSM_s7_metric_orientation_measure_v6_0.json",
    "pushforward": "BHSM_s7_fiber_pushforward_theorem_v6_0.json",
    "physical_domain": "BHSM_s7_physical_domain_ledger_v6_0.json",
    "action_localization": "BHSM_s7_action_collar_pushforward_v6_0.json",
    "report": "BHSM_s7_fiber_integration_physical_localization_report_v6_0.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "measured_scale_used": False,
    "probability_measure_substituted_for_action_measure": False,
    "unit_fiber_volume_assumed_physical": False,
    "normalized_rho_promoted_to_length": False,
    "s3_berger_geometry_relabelled_as_s7": False,
    "euclidean_s4_claimed_observed_spacetime": False,
    "absolute_unit_claimed": False,
    "particle_masses_derived": False,
    "gauge_couplings_derived": False,
    "ckm_completion_claimed": False,
    "rare_b_predictions_claimed": False,
    "full_bhsm_completion_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
}

OPEN_GATES = (
    "OPEN_MISSING_ACTION_SELECTED_S7_TOTAL_SPACE",
    "OPEN_MISSING_B8_BULK_ACTION_AND_SIGNATURE",
    "OPEN_MISSING_PHYSICAL_TIME_ASSIGNMENT",
    "OPEN_MISSING_S7_METRIC_AND_SQUASHING_SELECTION",
    "OPEN_MISSING_FIBER_ORIENTATION_NORMALIZATION",
    "OPEN_MISSING_PHYSICAL_FIBER_SCALE",
    "OPEN_MISSING_PUSHFORWARD_SOURCE_FOR_V5_ACTION",
    "OPEN_MISSING_BUNDLE_VALUED_PARALLEL_IDENTIFICATION",
    "OPEN_MISSING_COLLAR_TO_S7_MATCHING",
    "OPEN_MISSING_OBSERVED_BOUNDARY_MAP",
    "OPEN_MISSING_SCALAR_TOPOGRAPHIC_PHYSICAL_LOCALIZATION_MAP",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "FULL_BHSM_NOT_COMPLETE",
)


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "nested_result": NESTED_RESULT,
        "pushforward_result": PUSHFORWARD_RESULT,
        "claim_boundary": (
            "The nested Hopf-twistor bundle diagram and conditional fiber-"
            "integration theorem are exact. The current repository does not "
            "select S7, its metric, signature, orientation, physical fiber "
            "scale, or localization map as the BHSM action domain."
        ),
        **GUARDS,
    }


def validate_fibration_dimensions(total: int, base: int, fiber: int) -> bool:
    """Return whether local bundle dimensions close."""
    if min(total, base, fiber) < 0:
        raise ValueError("dimensions must be nonnegative")
    return total == base + fiber


def pushforward_degree(form_degree: int, fiber_dimension: int) -> int:
    """Degree of fiber integration, rejecting a form too small to integrate."""
    if form_degree < 0 or fiber_dimension < 0:
        raise ValueError("degrees must be nonnegative")
    if form_degree < fiber_dimension:
        raise ValueError("form degree is smaller than fiber dimension")
    return form_degree - fiber_dimension


def actual_fiber_integral(coefficient: float, fiber_volume: float) -> float:
    """Integrate a fiber-constant coefficient without probability normalization."""
    if fiber_volume <= 0:
        raise ValueError("fiber volume must be positive")
    return coefficient * fiber_volume


def orientation_reversal(value: float) -> float:
    """Reverse the declared fiber orientation."""
    return -value


def boundary_correction_sign(form_degree: int, fiber_dimension: int) -> int:
    """Sign in d pi_* w = pi_* dw + sign (pi_boundary)_* i*w."""
    return -1 if pushforward_degree(form_degree, fiber_dimension) % 2 else 1


def round_s1_volume(radius: float = 1.0) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return 2.0 * pi * radius


def round_s2_area(radius: float = 1.0) -> float:
    if radius <= 0:
        raise ValueError("radius must be positive")
    return 4.0 * pi * radius**2


def berger_s3_volume(radius: float = 1.0, anisotropy: float = 1.0) -> float:
    """Standard-convention Berger volume; not a selected BHSM physical volume."""
    if radius <= 0 or anisotropy <= 0:
        raise ValueError("radius and anisotropy must be positive")
    return 2.0 * pi**2 * radius**3 * anisotropy


def source_inventory_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_s7_legacy_geometry_source_inventory_v6_0"),
        "status": "NO_ACTION_SELECTED_S7_SOURCE_FOUND",
        "sources": [
            {"source": "theory/explicit_hopf_berger_boundary_oneforms.md", "content": "explicit SU(2)/S3 Hopf one-forms and U(1) connection", "selects_S7": False},
            {"source": "src/bhsm_hopf_berger_oneforms.py", "content": "S3 Berger/Hopf coordinate implementation", "selects_S7": False},
            {"source": "artifacts/berger_measure_domain_v1.json", "content": "internal Berger/Hopf domain with normalization fork open", "selects_S7": False},
            {"source": "artifacts/BHSM_unified_dynamical_action_configuration_space_v5_4.json", "content": "relative three-coordinate Berger/collar boundary", "selects_S7": False},
            {"source": "artifacts/BHSM_boundary_collar_measure_source_v4_1.json", "content": "conditional collar measure", "selects_S7": False},
        ],
        "repository_has_explicit_CP3_construction": False,
        "repository_has_explicit_S7_metric": False,
        "repository_has_B8_bulk_action": False,
        "legacy_architecture_inconsistent": False,
        "reason_not_inconsistent": "The legacy source is an S3 construction, not a contradictory S7 construction.",
    }


def fibration_ledger_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_s7_canonical_fibration_ledger_v6_0"),
        "status": "CANONICAL_MATHEMATICAL_FIBRATIONS_DERIVED_PHYSICAL_SELECTION_OPEN",
        "fibrations": [
            {"name": "quaternionic_Hopf", "sequence": "S3=Sp(1) -> S7 -> HP1=S4", "dimensions": [3, 7, 4], "structure": "principal Sp(1) bundle", "total_space": "unit sphere in H^2", "action": "right multiplication by unit quaternions", "characteristic_class": "c2=+1 after generator orientation and trace convention are declared"},
            {"name": "complex_Hopf", "sequence": "S1=U(1) -> S7 -> CP3", "dimensions": [1, 7, 6], "structure": "principal U(1) bundle", "total_space": "unit sphere in C^4", "action": "common phase multiplication", "characteristic_class": "c1=+1 after generator orientation is declared"},
            {"name": "twistor", "sequence": "S2=CP1 -> CP3 -> S4", "dimensions": [2, 6, 4], "structure": "associated homogeneous bundle Sp(1)/U(1), not a principal S2 bundle", "characteristic_class": "inherited from U(1) subset Sp(1) quotient data"},
        ],
        "all_dimension_checks_pass": True,
        "topology_selects_physical_BHSM_domain": False,
    }


def nested_diagram_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_s7_nested_hopf_twistor_diagram_v6_0"),
        "status": NESTED_RESULT,
        "subgroup": "U(1) subset Sp(1)",
        "maps": {"p_C": "S7 -> CP3=S7/U(1)", "tau": "CP3 -> S4=S7/Sp(1)", "p_H": "S7 -> S4"},
        "commutative_identity": "p_H=tau o p_C",
        "fiber_quotient": "Sp(1)/U(1)=S2",
        "pushforward_composition": "(p_H)_*=tau_* o (p_C)_* for compatible base-before-fiber orientations and integrable forms",
        "unique_physical_selection": False,
    }


def metric_measure_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_s7_metric_orientation_measure_v6_0"),
        "status": "METRIC_FAMILIES_IDENTIFIED_ACTION_SELECTION_OPEN",
        "metric_families": {
            "complex_Hopf": "g_S7=p_C^*g_FS+eta^2 up to an explicitly declared normalization",
            "quaternionic_Hopf": "3-Sasakian horizontal metric plus three Sp(1)-vertical one-forms",
            "canonical_variation": "uniform vertical rescaling is available mathematically",
            "Berger_inside_S3_fiber": "anisotropic selection of U(1) inside Sp(1) requires extra reduction data",
        },
        "connection_candidates": {"complex": "eta=-i z^dagger dz", "quaternionic": "A_H=Im(sum conjugate(q_i)dq_i)"},
        "orientation_convention": "total orientation=base orientation followed by fiber orientation",
        "actual_measure_rule": "use the metric-derived Riemannian density or action top form; do not divide by fiber volume unless the action supplies that normalization",
        "standard_convention_checks": {"Vol_S1_unit": round_s1_volume(), "Area_S2_radius_half": round_s2_area(0.5), "Vol_S3_unit": berger_s3_volume(), "Hopf_S3_factorization": "2*pi times pi = 2*pi^2"},
        "physical_scale_selected": False,
        "existing_Berger_metric_is": "three-dimensional S3-type internal metric with two base directions and one Hopf-fiber direction",
    }


def pushforward_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_s7_fiber_pushforward_theorem_v6_0"),
        "status": PUSHFORWARD_RESULT,
        "hypotheses": ["pi:E->B is a proper smooth submersion", "compact oriented r-dimensional fibers", "integrable differential form", "declared base-before-fiber orientation"],
        "map": "pi_*:Omega^k(E)->Omega^(k-r)(B)",
        "definition": "integrate the vertical top-degree component over each oriented fiber",
        "product_rule": "pi_*(alpha wedge beta_top)=alpha integral_F beta_top",
        "closed_fiber_chain_rule": "d pi_* omega=pi_* d omega",
        "fiber_boundary_chain_rule": "d pi_* omega=pi_* d omega+(-1)^(k-r)(pi_boundary)_* i^*omega",
        "orientation_reversal": "pi_* changes sign",
        "metric_dependence": "integration of forms is metric independent; a metric-derived integrand or volume form carries metric and squashing dependence",
        "covariance": "natural under orientation-preserving bundle isomorphisms",
        "bundle_valued_limit": "canonical only for pullback/basic coefficients or after a connection/parallel identification and invariant trace are supplied",
        "normalization": "actual integral, not a probability average",
    }


def physical_domain_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_s7_physical_domain_ledger_v6_0"),
        "status": "PHYSICAL_ACTION_DOMAIN_UNRESOLVED",
        "candidates": [
            {"domain": "Euclidean B8 with boundary S7", "dimension": 8, "time": "absent", "signature": "Riemannian", "status": "mathematically coherent, not action-selected"},
            {"domain": "Lorentzian eight-dimensional bulk", "dimension": 8, "time": "included", "signature": "one or more timelike directions must be fixed", "status": "no stored action"},
            {"domain": "canonical spatial slice", "dimension": 7, "time": "external Hamiltonian parameter", "signature": "spatial Riemannian", "status": "no stored canonical split"},
            {"domain": "timelike or spatial boundary/collar", "dimension": "boundary plus collar", "time": "unresolved", "signature": "unresolved", "status": "v5 normalized collar does not decide"},
            {"domain": "static energy or action per unit time", "dimension": "depends on reduction", "time": "factored", "signature": "requires parent action", "status": "not derived"},
        ],
        "S4_is_observed_Lorentzian_spacetime": False,
        "coordinate_dimension_implies_physical_dimension": False,
    }


def action_localization_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_s7_action_collar_pushforward_v6_0"),
        "status": "ACTION_PUSHFORWARD_FORMULA_CONDITIONAL_SOURCE_ATTACHMENT_OPEN",
        "top_form_rule": "L_E vol_E maps to (integral_fiber L_E vol_fiber) vol_B when the metric and horizontal/vertical split are declared",
        "fiber_constant_zero_mode": "the reduced coefficient is multiplied by the actual physical fiber volume",
        "nested_rule": "S7->S4 direct integration agrees with S7->CP3 then CP3->S4 under compatible orientations and Fubini hypotheses",
        "collar_rule": "a fiber with boundary contributes the declared Stokes endpoint term; rho_star=1 is not a physical length",
        "v5_action_attachment": None,
        "physical_boundary_tension_from_pushforward": None,
        "absolute_scale_from_pushforward": None,
        "reason": "No B8/S7 parent action, physical fiber radius, metric normalization, signature, or collar matching map is stored.",
    }


def report_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_s7_fiber_integration_physical_localization_report_v6_0"),
        "status": PRIMARY_RESULT,
        "central_answer": "The canonical nested S7 Hopf-twistor diagram is exact, and fiber pushforward is derived under explicit geometric hypotheses. Current BHSM sources select only an S3-type Berger/Hopf geometry and a normalized collar scaffold; they do not select an S7 physical action domain. The v6.0 architecture therefore remains ambiguous.",
        "derived": ["the three exact fibration sequences and dimensions", "the U(1) subset Sp(1) nested commutative diagram", "actual, orientation-sensitive fiber integration and its degree", "closed-fiber and fiber-boundary chain rules in one declared convention", "standard metric-volume convention checks"],
        "conditional": ["composition of nested pushforwards under compatible orientations and Fubini hypotheses", "metric-derived action reduction after a physical S7 metric and parent action are supplied", "bundle-valued reduction after parallel identification and invariant trace are supplied"],
        "invalidated_or_downgraded": ["an S3 Berger source is not evidence for an S7 physical metric", "topology alone does not select a probability or action measure", "S4 in the quaternionic Hopf map is not thereby observed Lorentzian spacetime", "rho_star=1 is not a collar length", "a unit-radius fiber volume is not an absolute unit"],
        "remaining_open_blockers": list(OPEN_GATES),
        "absolute_scale": None,
        "physical_action_domain": None,
        "recommended_next_construction_sprint": "bhsm-b8-s7-physical-domain-action-source-closure-v6-0-1",
    }


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {
        "source_inventory": source_inventory_payload(),
        "fibration_ledger": fibration_ledger_payload(),
        "nested_diagram": nested_diagram_payload(),
        "metric_measure": metric_measure_payload(),
        "pushforward": pushforward_payload(),
        "physical_domain": physical_domain_payload(),
        "action_localization": action_localization_payload(),
        "report": report_payload(),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    target = root / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    written = []
    for key, name in ARTIFACT_FILES.items():
        path = target / name
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def s7_fiber_integration_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _ = repo_root
    report = report_payload()
    report["artifacts"] = {key: f"artifacts/{name}" for key, name in ARTIFACT_FILES.items()}
    return report


def s7_fiber_integration_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.0 S7 Fiber Integration and Physical Localization",
        "",
        f"Primary result: `{report['primary_result']}`.",
        f"Nested geometry: `{report['nested_result']}`.",
        f"Pushforward theorem: `{report['pushforward_result']}`.",
        "",
        report["central_answer"],
        "",
        "## Open gates",
        "",
        *[f"- `{gate}`" for gate in report["remaining_open_blockers"]],
    ]) + "\n"
