"""BHSM v9.0 action-selected eight-dimensional vacuum/flavor audit.

The v8.4--v8.9 modules establish a conditional representation and linear-
algebra pipeline.  This module asks the logically prior question: does the
current stratified action actually provide the stationary vacuum, composite
immersions, kinetic/Hessian pullbacks, and common parent current required by
that pipeline?  Missing arrows fail closed; proxy calculations are labelled
and never promoted to physical flavor data.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np
from scipy import linalg
from sympy import Symbol, solve, sqrt

from . import automatic_geometric_lens_theorem as v89
from . import classical_mode_stress_incidence as v83
from . import common_parent_charged_current_attachment as v88
from . import complex_profile_isospectral_attachment as v86
from . import composite_carrier_current_reduction as v84
from . import relative_channel_normalization as v87
from . import topographic_profile_component_selection as v85
from .common import deterministic_json


VERSION = "v9.0"
SPRINT = "bhsm-action-selected-8d-vacuum-flavor-completion-v9-0"
SOURCE_MAIN_SHA = "0721ee6a79f97cae5b3ac5bf040fa07ef9584678"
ARTIFACT_NAME = "BHSM_action_selected_8d_vacuum_flavor_completion_v9_0"
FINAL_VERDICT = (
    "BHSM_ACTION_SELECTED_8D_VACUUM_FLAVOR_MATRIX_NOT_DERIVABLE_"
    "FROM_CURRENT_STRATIFIED_ACTION"
)
NEXT_MISSING_OBJECT = (
    "ACTION_SELECTED_STATIONARY_8D_VACUUM_WITH_ACTION_OWNED_GLOBAL_"
    "COMPOSITE_IMMERSIONS_AND_COMMON_PARENT_CHARGED_CURRENT_KERNEL"
)
RELEASE_VERDICT = "BHSM_1_0_RELEASE_BLOCKED"

ARTIFACT_PAYLOADS = {
    "BHSM_composite_carrier_current_reduction_v8_4.json": v84.status_report,
    "BHSM_topographic_profile_component_selection_v8_5.json": v85.status_report,
    "BHSM_complex_profile_isospectral_attachment_v8_6.json": v86.status_report,
    "BHSM_master_action_relative_channel_normalization_v8_7.json": v87.payload,
    "BHSM_common_parent_charged_current_attachment_v8_8.json": v88.payload,
    "BHSM_automatic_geometric_lens_theorem_v8_9.json": v89.payload,
}


def integration_matrix() -> list[dict[str, Any]]:
    """Disposition of every candidate manual sprint against current main."""

    rows = [
        (
            "v8.4",
            "composite carrier and weak-current representation closure",
            "composite_carrier_current_reduction.py",
            "test_bhsm_composite_carrier_current_reduction_v8_4.py",
            "BHSM_composite_carrier_current_reduction_v8_4.json",
            "v8.2 frozen projector modules",
            "candidate lacked repository CLI/materializer registration",
            "INTEGRATED_CONDITIONALLY",
        ),
        (
            "v8.5",
            "Riesz component selector and full-S3 profile requirements",
            "topographic_profile_component_selection.py",
            "test_bhsm_topographic_profile_component_selection_v8_5.py",
            "BHSM_topographic_profile_component_selection_v8_5.json",
            "v8.4 normalized transition library",
            "heat profile is a proxy and direct mass dressing fails",
            "INTEGRATED_WITH_PROXY_FIREWALL",
        ),
        (
            "v8.6",
            "linear isospectral alignment and polar-current functor",
            "complex_profile_isospectral_attachment.py",
            "test_bhsm_complex_profile_isospectral_attachment_v8_6.py",
            "BHSM_complex_profile_isospectral_attachment_v8_6.json",
            "frozen screen retained as post-construction comparison only",
            "mixed-normalization near miss cannot be promoted",
            "INTEGRATED_CONDITIONALLY",
        ),
        (
            "v8.7",
            "canonical relative C3/G2 normalization",
            "relative_channel_normalization.py",
            "test_bhsm_master_action_relative_channel_normalization_v8_7.py",
            "BHSM_master_action_relative_channel_normalization_v8_7.json",
            "orthonormal C3 character basis",
            "Fourier 1/sqrt(3) is not a physical coupling",
            "INTEGRATED_CONDITIONALLY",
        ),
        (
            "v8.8",
            "common-parent charged-current interface",
            "common_parent_charged_current_attachment.py",
            "test_bhsm_common_parent_charged_current_attachment_v8_8.py",
            "BHSM_common_parent_charged_current_attachment_v8_8.json",
            "localized SU2 charged generator",
            "abstract K_CG is not derived from the current S8 action",
            "INTEGRATED_AS_CONDITIONAL_INTERFACE_CONSTRUCTION",
        ),
        (
            "v8.9",
            "automatic geometric lens theorem",
            "automatic_geometric_lens_theorem.py",
            "test_bhsm_automatic_geometric_lens_theorem_v8_9.py",
            "BHSM_automatic_geometric_lens_theorem_v8_9.json",
            "v7--v8 Hessian and current-pullback architecture",
            "all numerical matrices are explicit proxy stress tests",
            "INTEGRATED_AS_FAIL_CLOSED_FINITE_DIMENSIONAL_THEOREM",
        ),
    ]
    return [
        {
            "sprint": sprint,
            "theorem": theorem,
            "source": f"src/bhsm/interface/master_action/{source}",
            "test": f"tests/{test}",
            "artifact": f"artifacts/{artifact}",
            "current_repository_equivalent": equivalent,
            "conflict": conflict,
            "disposition": disposition,
        }
        for sprint, theorem, source, test, artifact, equivalent, conflict, disposition in rows
    ]


def action_configuration_inventory() -> list[dict[str, Any]]:
    """Increasing-complexity truncation inventory for the retained S8 action."""

    return [
        {
            "ansatz": "homogeneous static round or Berger-deformed S7",
            "closure": "SCALAR_SUBSECTOR_CLOSED_BUT_STATIC_PRODUCT_VACUUM_FAILS",
            "reason": "constant singlet scalars give cosmological-form stress, while R_t x S7 at finite radius is not Einstein",
        },
        {
            "ansatz": "Hopf-fiber anisotropic configuration",
            "closure": "OPEN_NO_CONSISTENT_TRUNCATION_THEOREM",
            "reason": "the current action has a general metric but no proved finite Hopf-anisotropy mode closure",
        },
        {
            "ansatz": "two-cap/equatorial wall",
            "closure": "LEVELWISE_M5_PROBLEM_NOT_AN_S8_VACUUM_REDUCTION",
            "reason": "the M8-to-M5 action map does not derive the cap fields and matcher from S8",
        },
        {
            "ansatz": "localized equivariant chi/sigma profiles",
            "closure": "OPEN_FULL_PDE_AND_BOUNDARY_DOMAIN",
            "reason": "no action-selected localization center, global boundary conditions, or retained-mode closure is supplied",
        },
        {
            "ansatz": "G2-polarized nonlinear state",
            "closure": "BLOCKED_FIELD_AND_CURRENT_NOT_OWNED_BY_S8",
            "reason": "G, chi, and sigma are singlets; S8 has no active G2/C3 polarization or charged-current field",
        },
        {
            "ansatz": "finite frozen-ledger mode reduction",
            "closure": "BLOCKED_NO_ACTION_DERIVED_SPECTRAL_INTERTWINER",
            "reason": v83.NEXT_MISSING_OBJECT,
        },
    ]


def stationary_equations() -> dict[str, Any]:
    return {
        "action": (
            "S8=int sqrt(-G)[kappa1 R8/2-kappa0/2-"
            "Zchi(1+g sigma^2)|dchi|^2/2-Zsigma|dsigma|^2/2-"
            "A0 sigma^2/2-G0 sigma^4/4]"
        ),
        "carrier_equation": "Zchi nabla_A[(1+g sigma^2)nabla^A chi]=0",
        "scalar_equation": (
            "Zsigma box sigma-Zchi g sigma |dchi|^2-A0 sigma-G0 sigma^3=0"
        ),
        "metric_equation": "kappa1 Einstein_AB+(kappa0/2)G_AB=T_AB[chi,sigma]",
        "homogeneous_scalar_roots": ["sigma=0", "sigma^2=-A0/G0 when real"],
        "carrier_zero_mode": "chi=constant is an unfixed shift-symmetric modulus",
        "coefficient_selection": "kappa0,kappa1,Zchi,Zsigma,g,A0,G0 remain independent theory inputs",
    }


def homogeneous_static_product_no_go() -> dict[str, Any]:
    """Exact obstruction for a finite-radius static R x round-S7 branch."""

    return {
        "ansatz": "ds8^2=-dt^2+r^2 ds^2(S7), dchi=dsigma=0",
        "ricci_components": {"R_tt": "0", "R_ij": "6 g_ij/r^2", "R8": "42/r^2"},
        "matter_stress": "T_AB=-V_eff(sigma) G_AB",
        "required_geometry": "Ric_AB proportional to G_AB",
        "contradiction": "R_tt/G_tt=0 but R_ij/G_ij=6/r^2 for finite r",
        "finite_radius_solution": False,
        "scope": "rules out this static homogeneous candidate, not all time-dependent or localized solutions",
    }


def scalar_topology_audit() -> dict[str, Any]:
    return {
        "active_scalar_target": "R_chi x R_sigma",
        "target_contractible": True,
        "pi_7_of_scalar_target": 0,
        "FR_sector_from_scalar_maps_alone": False,
        "scope": "does not rule out metric/geon topology; it rules out assigning FR quantization to chi/sigma profile topology alone",
    }


def vacuum_proxy_crosscheck() -> dict[str, Any]:
    """Two-method root check of the homogeneous scalar stationarity equation."""

    sigma = Symbol("sigma", real=True)
    cases = (("symmetric", 2, 1), ("broken", -2, 1))
    rows = []
    mp.mp.dps = 80
    for name, a0, g0 in cases:
        polynomial = a0 * sigma + g0 * sigma**3
        exact = sorted(
            [float(root.evalf(50)) for root in solve(polynomial, sigma) if root.is_real],
        )
        numeric_roots = mp.polyroots([g0, 0, a0, 0], maxsteps=200, error=False)
        numeric = sorted(
            float(mp.re(root)) for root in numeric_roots if abs(mp.im(root)) < mp.mpf("1e-60")
        )
        residual = max(abs(a0 * root + g0 * root**3) for root in numeric)
        rows.append(
            {
                "case": name,
                "A0": a0,
                "G0": g0,
                "symbolic_real_roots": exact,
                "mpmath_real_roots": numeric,
                "root_set_residual": residual,
                "methods_agree": np.allclose(exact, numeric, atol=1.0e-30, rtol=0.0),
            }
        )
    return {
        "classification": "PROXY_STRESS_TEST_ONLY",
        "physical_promotion": False,
        "coefficient_values_are_physical_inputs": False,
        "methods": ["exact symbolic factorization", "80-digit mpmath root solve"],
        "rows": rows,
        "all_methods_agree": all(row["methods_agree"] for row in rows),
    }


def composite_immersion_audit() -> dict[str, Any]:
    sectors = ("up", "down", "charged_lepton", "neutrino")
    return {
        "requested_maps": {sector: "C^3_family -> Q8_physical" for sector in sectors},
        "explicit_maps": {sector: None for sector in sectors},
        "Frechet_derivatives_A_f": {sector: None for sector in sectors},
        "global_patching": None,
        "chirality_transport": None,
        "representation_transport": None,
        "component_selection": "conditional Riesz selector exists; no action-selected point/frame",
        "reason": (
            "the S8 configuration bundle contains only the metric and real singlet scalars; "
            "the triality, sector, FR, chiral, and localized SM carriers are independently owned lower-stratum data"
        ),
    }


def action_ownership_obstruction() -> dict[str, Any]:
    return {
        "S8_active_fields": ["G_AB", "chi", "sigma"],
        "S8_SU2_connection": None,
        "S8_chiral_fermion_carrier": None,
        "S8_C3_family_field": None,
        "S8_G2_polarized_current": None,
        "localized_M4_fermions": "independently owned EFT fields",
        "localized_Yukawa_matrices": "independent EFT inputs",
        "v8_8_interface_term": "conditional construction; abstract K_CG is not derived from S8",
        "logical_result": (
            "variation of the current S8 action cannot produce D C_f or a bifundamental K_ud because neither object is defined on its active field bundle"
        ),
        "extension_added": False,
    }


def physical_pullback_forms() -> dict[str, Any]:
    return {
        "K8_gauge_fixed": None,
        "H8_gauge_fixed": None,
        "A_u": None,
        "A_d": None,
        "G_u": None,
        "Q_u": None,
        "G_d": None,
        "Q_d": None,
        "K_ud": None,
        "positivity_gate": "NOT_EVALUABLE",
        "simple_spectrum_gate": "NOT_EVALUABLE",
        "full_rank_gate": "NOT_EVALUABLE",
        "V_BHSM": None,
        "physical_matrix_promoted": False,
    }


def lens_numerical_crosscheck() -> dict[str, Any]:
    """Independent eigensolver and polar-decomposition checks on proxy forms."""

    G = np.array(
        [[2.2, 0.2j, 0.1], [-0.2j, 1.7, 0.15], [0.1, 0.15, 1.3]],
        dtype=complex,
    )
    Q = np.array(
        [[0.8, 0.12j, 0.03], [-0.12j, 1.9, 0.2], [0.03, 0.2, 3.4]],
        dtype=complex,
    )
    eigen_route = v89.sector_lens(G, Q)
    generalized_values, _ = linalg.eigh(Q, G)
    K = v88.proxy_parent_kernel()
    polar_eigen = v86.polar_unitary(K)
    polar_svd, _ = linalg.polar(K)
    return {
        "classification": "PROXY_STRESS_TEST_ONLY",
        "physical_promotion": False,
        "uses_historical_screen_kernel": True,
        "generalized_eigensolver_methods": ["kinetic whitening plus numpy.eigh", "scipy.linalg.eigh(Q,G)"],
        "eigenvalue_residual": float(np.linalg.norm(eigen_route["eigenvalues_ascending"] - generalized_values)),
        "polar_methods": ["positive-Gram spectral factor", "SVD polar decomposition"],
        "polar_cross_method_residual": float(np.linalg.norm(polar_eigen - polar_svd)),
        "polar_unitarity_residual": float(np.linalg.norm(polar_svd.conj().T @ polar_svd - np.eye(3))),
        "methods_agree": bool(
            np.linalg.norm(eigen_route["eigenvalues_ascending"] - generalized_values) < 1.0e-12
            and np.linalg.norm(polar_eigen - polar_svd) < 1.0e-11
        ),
    }


def parameter_input_ledger() -> list[dict[str, Any]]:
    return [
        {"symbol": symbol, "classification": "INDEPENDENT_THEORY_INPUT", "value": None, "flavor_data": False}
        for symbol in ("kappa0", "kappa1", "Zchi", "Zsigma", "g", "A0", "G0")
    ] + [
        {"symbol": "frozen (k,j,q) ledgers", "classification": "FROZEN_STRUCTURAL_INPUT", "value": "unchanged", "flavor_data": False},
        {"symbol": "Y_u,Y_d,Y_e", "classification": "INDEPENDENT_LOCALIZED_EFT_INPUT", "value": None, "flavor_data": True},
    ]


def completion_gate_payload() -> dict[str, Any]:
    gate = v83.completion_gate_payload()
    gate.update(
        {
            "version": VERSION,
            "sprint": SPRINT,
            "source_main_sha": SOURCE_MAIN_SHA,
            "current_verdict": FINAL_VERDICT,
            "next_highest_upstream_blocker": NEXT_MISSING_OBJECT,
            "action_selected_8d_vacuum_flavor_matrix": FINAL_VERDICT,
            "distinct_action_derived_prediction_exists": False,
            "BHSM_1_0_release_complete": False,
        }
    )
    gate["RB15"] = {"status": "BLOCKED_EXACT_ACTION_CHAIN_OBSTRUCTION", "resolution": FINAL_VERDICT}
    gate["RB16"] = {"status": "DOWNSTREAM_BLOCKED", "resolution": "release packaging remains ineligible while RB-15 is open"}
    return gate


def prediction_freeze() -> dict[str, Any]:
    payload = {
        "version": VERSION,
        "physical_matrix": None,
        "G_u": None,
        "Q_u": None,
        "G_d": None,
        "Q_d": None,
        "K_ud": None,
        "physical_promotion": False,
        "frozen_historical_predictions_changed": False,
        "verdict": FINAL_VERDICT,
    }
    payload["sha256"] = sha256(deterministic_json(payload).encode("utf-8")).hexdigest().upper()
    return payload


def status_report() -> dict[str, Any]:
    vacuum_proxy = vacuum_proxy_crosscheck()
    numerical = lens_numerical_crosscheck()
    forms = physical_pullback_forms()
    validations = {
        "v8_4_passed": v84.status_report()["validation_passed"],
        "v8_5_passed": v85.status_report()["validation_passed"],
        "v8_6_passed": v86.status_report()["validation_passed"],
        "v8_7_passed": v87.payload()["validation_passed"],
        "v8_8_passed": v88.payload()["validation_passed"],
        "v8_9_passed": v89.payload()["validation"]["all_passed"],
        "static_round_product_rejected": not homogeneous_static_product_no_go()["finite_radius_solution"],
        "scalar_FR_not_fabricated": not scalar_topology_audit()["FR_sector_from_scalar_maps_alone"],
        "vacuum_proxy_methods_agree": vacuum_proxy["all_methods_agree"],
        "lens_proxy_methods_agree": numerical["methods_agree"],
        "physical_forms_fail_closed": all(forms[key] is None for key in ("G_u", "Q_u", "G_d", "Q_d", "K_ud", "V_BHSM")),
        "no_physical_matrix_promoted": not forms["physical_matrix_promoted"],
    }
    return {
        "artifact": ARTIFACT_NAME,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "integration_matrix": integration_matrix(),
        "action_configuration_inventory": action_configuration_inventory(),
        "stationary_equations": stationary_equations(),
        "homogeneous_static_product_no_go": homogeneous_static_product_no_go(),
        "scalar_topology_audit": scalar_topology_audit(),
        "vacuum_result": {
            "action_selected_unique_vacuum": False,
            "stationary_full_PDE_solved": False,
            "branch_classification_complete": False,
            "reason": "the simplest static compact branch is obstructed and more general branches lack a proved consistent truncation, boundary domain, and coefficient selection",
        },
        "vacuum_proxy_crosscheck": vacuum_proxy,
        "composite_immersion": composite_immersion_audit(),
        "action_ownership_obstruction": action_ownership_obstruction(),
        "physical_pullback_forms": forms,
        "conditional_geometric_lens_theorem": v89.theorem_statement(),
        "lens_numerical_crosscheck": numerical,
        "parameter_input_ledger": parameter_input_ledger(),
        "prediction_freeze": prediction_freeze(),
        "validated": [
            "v8.4--v8.9 conditional representation, profile, normalization, current, and lens theorems",
            "exact failure of the finite-radius static R_t x round-S7 constant-scalar vacuum",
            "scalar-target topology cannot alone supply an FR sector",
            "basis-covariant fail-closed lens functor on admissible finite forms",
        ],
        "invalidated": [
            "promotion of any manual heat/profile matrix to physical CKM",
            "derivation of a parent charged current by merely writing the v8.8 interface term",
            "derivation of FR quantization from the contractible chi/sigma target alone",
            "claim that the current S8 action selects a unique numerical flavor matrix",
        ],
        "open": [
            NEXT_MISSING_OBJECT,
            "consistent nonhomogeneous S8 truncation and stationary branch theorem",
            "gauge-fixed physical K8 and H8 on that branch",
            "localized-carrier transport replacing independent M4 Yukawa ownership",
        ],
        "validation": validations,
        "validation_passed": all(validations.values()),
        "frozen_predictions_changed": False,
        "new_continuous_parameter_added": False,
        "measured_flavor_data_used": False,
        "new_fundamental_fermion_added": False,
        "physical_matrix_promoted": False,
        "release_status": RELEASE_VERDICT,
        "next_missing_object": NEXT_MISSING_OBJECT,
        "final_verdict": FINAL_VERDICT,
    }


def status_to_markdown(payload: dict[str, Any] | None = None) -> str:
    data = status_report() if payload is None else payload
    forms = data["physical_pullback_forms"]
    lines = [
        "# BHSM action-selected 8D vacuum/flavor completion v9.0",
        "",
        f"Primary verdict: `{data['final_verdict']}`",
        "",
        "The v8.4--v8.9 finite-dimensional functor is integrated and validated conditionally. The current S8 action does not select a unique stationary vacuum and does not own the composite immersions or bifundamental parent current needed to evaluate it.",
        "",
        "## Physical readout",
        "",
        f"- `G_u,Q_u,G_d,Q_d,K_ud`: `{forms['G_u']}`",
        f"- `V_BHSM`: `{forms['V_BHSM']}`",
        f"- physical promotion: `{str(forms['physical_matrix_promoted']).lower()}`",
        "",
        "## Exact next object",
        "",
        f"`{data['next_missing_object']}`",
        "",
        f"Validation passed: `{str(data['validation_passed']).lower()}`",
    ]
    return "\n".join(lines) + "\n"


def conditional_status_to_markdown(title: str, payload: dict[str, Any]) -> str:
    """Render one integrated v8.4--v8.9 conditional status compactly."""

    primary = payload.get("primary_result", payload.get("final_verdict"))
    final = payload.get("final_verdict", primary)
    next_object = payload.get("next_missing_object")
    passed = payload.get("validation_passed")
    if passed is None:
        passed = payload.get("validation", {}).get("all_passed")
    lines = [f"# {title}", "", f"Primary result: `{primary}`", ""]
    if final != primary:
        lines.extend([f"Boundary: `{final}`", ""])
    lines.extend(
        [
            f"Physical promotion: `{str(bool(payload.get('physical_CKM_promoted') or payload.get('physical_CKM_emitted'))).lower()}`",
            f"Validation passed: `{str(bool(passed)).lower()}`",
        ]
    )
    if next_object:
        lines.extend(["", "## Exact next object", "", f"`{next_object}`"])
    return "\n".join(lines) + "\n"


def materialize(root: Path | None = None) -> list[Path]:
    repository = Path(__file__).resolve().parents[4] if root is None else Path(root)
    target = repository / "artifacts"
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, factory in ARTIFACT_PAYLOADS.items():
        path = target / filename
        path.write_text(deterministic_json(factory()), encoding="utf-8", newline="\n")
        written.append(path)
    campaign = target / f"{ARTIFACT_NAME}.json"
    campaign.write_text(deterministic_json(status_report()), encoding="utf-8", newline="\n")
    written.append(campaign)
    gate = target / "BHSM_1_0_completion_gate.json"
    gate.write_text(deterministic_json(completion_gate_payload()), encoding="utf-8", newline="\n")
    written.append(gate)
    return written


__all__ = [
    "FINAL_VERDICT",
    "NEXT_MISSING_OBJECT",
    "completion_gate_payload",
    "conditional_status_to_markdown",
    "integration_matrix",
    "lens_numerical_crosscheck",
    "materialize",
    "status_report",
    "status_to_markdown",
    "vacuum_proxy_crosscheck",
]
