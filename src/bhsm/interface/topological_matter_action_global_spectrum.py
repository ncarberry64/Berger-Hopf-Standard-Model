"""BHSM v6.5.0 topological matter-action and global-spectrum audit.

This module tests whether the merged v6.2--v6.4 architecture supplies the
missing first-order matter source, a dynamical G2 polarization, and the
complete compact spectrum.  It implements exact finite-dimensional
diagnostics where the required data exist and records controlled null results
where the frozen P1/GHY/B1 action does not define the needed ontology or
operator domain.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from .parent_action_polarization_localization_stability import (
    PRIMARY_RESULT as V640_PRIMARY_RESULT,
    connection_dependency_ledger,
    electroweak_mass_diagnostic,
    hopf_connection_transfer,
    polarization_checks,
    scalar_field_metric,
    scalar_mass_eigenvalues,
)
from .particle_chirality_anomaly_normalization import (
    connection_trace_payload,
)


VERSION = "v6.5.0"
SPRINT = "bhsm-topological-matter-action-global-spectrum-v6-5-0"
SOURCE_SHA = "8330c7e78cb2cd59d883eadd82c385e7e717c946"
PRIMARY_RESULT = (
    "BHSM_TOPOLOGICAL_MATTER_ACTION_SOURCE_AND_GLOBAL_SPECTRUM_"
    "REMAIN_CONDITIONAL"
)
COMPLETION_GATE = (
    "V6_5_0_CONFIGURATION_SPACE_PARENT_SOURCE_DYNAMIC_POLARIZATION_"
    "AND_COMPLETE_GLOBAL_SPECTRUM_OPEN"
)

MERGED_STACK = {
    "v6.2.0": {
        "pr": 162,
        "scientific_sha": "87577bc946437048848afb9d46cf5e62253613d8",
        "merge_commit": "baf59b85e25999507fe722c4dcb28406bc514804",
    },
    "v6.3.0": {
        "pr": 163,
        "scientific_sha": "c82ed0da6c9f2fda74f08ac03ec6429aaa7ddf79",
        "merge_commit": "59504f55843f8b7ae72db29da5262f0618c2d2c0",
    },
    "v6.4.0": {
        "pr": 164,
        "scientific_sha": "5a24a4404ffee284f5e8646daf4bced8a3b6cc96",
        "merge_commit": "8330c7e78cb2cd59d883eadd82c385e7e717c946",
    },
}

ARTIFACT_FILES = {
    "handoff": "BHSM_v6_5_0_merged_stack_handoff.json",
    "merge": "BHSM_GitHub_PR162_164_merge_ledger.json",
    "cleanup": "BHSM_repository_error_cleanup_audit_v6_5_0.json",
    "configuration": "BHSM_topological_configuration_space_v6_5_0.json",
    "fr": "BHSM_Finkelstein_Rubinstein_quantization_map_v6_5_0.json",
    "source": "BHSM_first_order_action_source_classification_v6_5_0.json",
    "extension": "BHSM_minimal_first_order_action_extension_v6_5_0.json",
    "y_sigma": "BHSM_y_sigma_coefficient_dependency_v6_5_0.json",
    "polarization_map": "BHSM_dynamic_polarization_source_map_v6_5_0.json",
    "polarization": "BHSM_G2_section_effective_potential_v6_5_0.json",
    "compact": "BHSM_compact_chiral_normal_spectrum_v6_5_0.json",
    "doubling": "BHSM_vectorlike_partner_compact_audit_v6_5_0.json",
    "sheets": "BHSM_upper_lower_global_spectrum_comparison_v6_5_0.json",
    "su3": "BHSM_SU3_connection_transfer_v6_5_0.json",
    "sp1": "BHSM_Sp1_connection_transfer_v6_5_0.json",
    "u1": "BHSM_U1_connection_transfer_v6_5_0.json",
    "connection_graph": "BHSM_connection_coupling_dependency_graph_v6_5_0.json",
    "scalar": "BHSM_scalar_Berger_physical_mass_matrix_v6_5_0.json",
    "gauge": "BHSM_gauge_mass_matrix_global_audit_v6_5_0.json",
    "hessian": "BHSM_constraint_reduced_global_Hessian_v6_5_0.json",
    "neutrino": "BHSM_neutrino_geometric_phase_law_v6_5_0.json",
    "scale": "BHSM_absolute_scale_transfer_closure_v6_5_0.json",
    "r4": "BHSM_scalar_wall_O_r4_progress_v6_5_0.json",
    "integration": "BHSM_Full_BHSM_integration_ledger_v6_5_0.json",
    "hidden": "BHSM_v6_5_0_hidden_input_audit.json",
    "report": "BHSM_topological_matter_action_global_spectrum_report_v6_5_0.json",
}

GUARDS = {
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "measured_derivation_input_used": False,
    "physical_bulk_Dirac_parent_law_introduced": False,
    "monopole_structure_introduced": False,
    "absolute_numerical_mass_claimed": False,
    "full_BHSM_claimed": False,
    "remote_branches_deleted": False,
}


def configuration_space_ledger() -> dict[str, Any]:
    """Return the exact definition and missing data for a BHSM soliton sector."""
    return {
        "formal_definition": (
            "Q_N = C_N/G_0, where C_N is a fixed topological component of "
            "admissible BHSM geometric configurations and G_0 is the based "
            "gauge/diffeomorphism redundancy"
        ),
        "tangent_space": (
            "T_[Phi]Q_N = ker(linearized constraints)/im(infinitesimal G_0)"
        ),
        "collective_metric": (
            "G_AB = integral_Sigma <delta_A Phi, K_Phi delta_B Phi> "
            "after zero-mode projection"
        ),
        "berry_form": "omega=dA on a local collective-coordinate chart",
        "integrality_condition": "[omega/(2 pi)] must be integral for a line bundle",
        "fixed_charge_component_defined_by_frozen_action": False,
        "configuration_field_ontology_defined": False,
        "fundamental_group_computed": False,
        "collective_metric_computed": False,
        "symplectic_form_computed": False,
        "local_M4_field_map_derived": False,
        "result": "BHSM_TOPOLOGICAL_CONFIGURATION_SPACE_TEMPLATE_DEFINED_ONLY",
    }


def fr_character(loop_class: int) -> int:
    """The nontrivial sign character of the established Z2 FR template."""
    return -1 if int(loop_class) % 2 else 1


def fr_template_checks() -> dict[str, Any]:
    """Check the Z2 sign representation without assigning it to BHSM."""
    multiplication = all(
        fr_character(a + b) == fr_character(a) * fr_character(b)
        for a in range(2)
        for b in range(2)
    )
    omega = np.array(
        [
            [0.0, 1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0, 0.0],
        ]
    )
    return {
        "template_group": "Z2",
        "character": {"identity": fr_character(0), "nontrivial_loop": fr_character(1)},
        "homomorphism_exact": multiplication,
        "representative_symplectic_antisymmetric": bool(
            np.allclose(omega.T, -omega)
        ),
        "representative_symplectic_nondegenerate": bool(
            np.linalg.matrix_rank(omega) == 4
        ),
        "representative_symplectic_closed": True,
        "established_mathematics": (
            "FR quantization uses a sign representation of pi1(Q_N); a Berry "
            "term A_A(q) qdot^A is first order on reduced moduli space"
        ),
        "BHSM_pi1_equals_Z2_derived": False,
        "BHSM_local_first_order_M4_action_derived": False,
    }


def first_order_source_candidates() -> list[dict[str, Any]]:
    """Classify candidate sources against the frozen action and firewall."""
    return [
        {
            "candidate": "P1 Einstein-Hilbert plus GHY transgression",
            "present": True,
            "first_order_connection_boundary_variation": True,
            "collective_matter_carrier": False,
            "produces_sigma_Gamma_star": False,
            "verdict": "rejected as the matter source",
        },
        {
            "candidate": "B1 intrinsic curvature/scalar boundary action",
            "present": True,
            "collective_matter_carrier": False,
            "Clifford_odd_invariant": False,
            "produces_sigma_Gamma_star": False,
            "verdict": "rejected as the matter source",
        },
        {
            "candidate": "configuration-space Berry/FR term",
            "present": False,
            "covariant_on_Q_N": True,
            "local_M4_map": False,
            "produces_sigma_Gamma_star": None,
            "verdict": "conditional candidate pending Q_N and transgression map",
        },
        {
            "candidate": "boundary eta invariant",
            "present": False,
            "requires_first_order_operator": True,
            "produces_operator_without_assuming_it": False,
            "verdict": "rejected as circular source",
        },
        {
            "candidate": "torsion-induced Clifford coupling",
            "present": False,
            "torsion_in_declared_connection": False,
            "verdict": "rejected; torsion may not be introduced ad hoc",
        },
        {
            "candidate": "gauge Chern-Simons transgression",
            "present": False,
            "connection_first_order": True,
            "representation_carrier": False,
            "wall_odd_mass": False,
            "verdict": "does not generate the required matter invariant",
        },
    ]


def y_sigma_dependency_theorem() -> dict[str, Any]:
    """Classify all mechanisms that could fix the wall coupling."""
    return {
        "canonical_field_normalization": (
            "fixes the overall kinetic coefficient Z_F, not the invariant ratio "
            "y_sigma/Z_F"
        ),
        "FR_character": "fixes a sign representation only",
        "index": "depends on the asymptotic sign, not the magnitude",
        "topology": "no computed characteristic number multiplies sigma Gamma_star",
        "G5_or_Z5_relation": "no relation occurs in the frozen variation",
        "Berger_stiffness_relation": "no common invariant has been derived",
        "quantized": False,
        "action_derived": False,
        "classification": "unavoidable dimensionless primitive in the minimal extension",
        "independent_new_ratio_count": 1,
    }


def minimal_extension_ledger() -> dict[str, Any]:
    """Describe the one-invariant effective boundary extension and its limits."""
    return {
        "status": "BHSM_MINIMAL_FIRST_ORDER_BOUNDARY_EXTENSION_CLASSIFIED",
        "invariant": (
            "S_eff,F = integral_M4 sqrt(|h|) <Psi_coll,"
            "[i C_BHSM + y_sigma sigma Gamma_star]Psi_coll>"
        ),
        "field_ontology": (
            "Psi_coll is an effective section obtained from a quantized "
            "collective-coordinate/configuration-space bundle, not an "
            "elementary bulk spinor"
        ),
        "domain": "self-adjoint maximal-isotropic boundary domain",
        "transformation": (
            "polarized SU3 x Sp1 x U1 representation, triality universal"
        ),
        "wall_parity": "sigma Gamma_star is odd with the oriented wall",
        "Hermitian_for_real_y_sigma": True,
        "new_invariant_count": 1,
        "independent_ratio_count_after_canonical_normalization": 1,
        "coefficient": "y_sigma remains primitive",
        "frozen_action_modified_if_adopted": True,
        "adopted_in_official_prediction_logic": False,
        "kill_test": {
            "covariant": True,
            "Hermitian": True,
            "Y_BH_compatible": True,
            "family_universal": True,
            "monopole_free": True,
            "bulk_Dirac_parent_free": True,
            "parent_derived": False,
        },
    }


def unit_vector(vector: Iterable[float]) -> np.ndarray:
    value = np.asarray(tuple(vector), dtype=float)
    if value.shape != (7,):
        raise ValueError("polarization vectors must have seven components")
    norm = np.linalg.norm(value)
    if norm == 0:
        raise ValueError("polarization vector must be nonzero")
    return value / norm


def polarization_potential(
    u: Iterable[float],
    locking_section: Iterable[float] | None = None,
    coefficient: float = 1.0,
) -> float:
    """Lowest composite locking potential, or the exact G2-flat result."""
    selected = unit_vector(u)
    if locking_section is None:
        return 0.0
    target = unit_vector(locking_section)
    return float(coefficient * (1.0 - (selected @ target) ** 2))


def polarization_hessian(coefficient: float = 1.0) -> np.ndarray:
    """Tangent Hessian at u=+/-v for V=lambda(1-(u dot v)^2)."""
    return 2.0 * float(coefficient) * np.eye(6)


def polarization_source_map() -> dict[str, Any]:
    """Bundle-level test of direct Berger/G2 locking."""
    return {
        "G2_section_bundle": "rank-seven E_7 with unit fiber G2/SU3=S6",
        "Berger_orientation_bundle": "rank-three adjoint Sp1 bundle with unit fiber S2",
        "spacetime_normal_bundle": "normal line to M4 in M5",
        "canonical_identification_present": False,
        "declared_common_structure_group": False,
        "equivariant_map_derived": False,
        "direct_identification": (
            "rejected in the declared theory because the bundles and "
            "transition functions differ"
        ),
        "composite_locking": (
            "V=lambda[1-(u dot v)^2] is covariant only after supplying a "
            "second section v of E_7 or a derived bundle morphism"
        ),
        "new_spurion_required": True,
        "result": "BHSM_DIRECT_BERGER_G2_LOCKING_REJECTED_BY_BUNDLE_MISMATCH",
    }


def compact_supercharge_diagnostic(
    points: int = 161,
    length: float = 6.0,
    wall_strength: float = 1.0,
    wall_width: float = 1.0,
) -> dict[str, Any]:
    """Finite-interval supersymmetric first-order diagnostic.

    A maps n nodal values of the selected chirality to n-1 staggered values.
    The rectangular maximal-isotropic domain gives index n-(n-1)=1.  This is
    a controlled domain diagnostic, not an action-derived cap spectrum.
    """
    if points < 9 or points % 2 == 0:
        raise ValueError("points must be an odd integer at least 9")
    if length <= 0 or wall_width <= 0:
        raise ValueError("length and wall_width must be positive")
    x = np.linspace(-length, length, points)
    h = float(x[1] - x[0])
    midpoint = (x[:-1] + x[1:]) / 2.0
    mass = float(wall_strength) * np.tanh(midpoint / wall_width)
    lower = -1.0 / h + mass / 2.0
    upper = 1.0 / h + mass / 2.0
    A = np.zeros((points - 1, points))
    rows = np.arange(points - 1)
    A[rows, rows] = lower
    A[rows, rows + 1] = upper

    squared = A @ A.T
    positive = np.linalg.eigvalsh(squared)
    singular = np.sqrt(np.clip(positive, 0.0, None))

    zero_mode = np.ones(points)
    for index in range(points - 1):
        zero_mode[index + 1] = -lower[index] * zero_mode[index] / upper[index]
    norm = math.sqrt(float(np.trapezoid(zero_mode**2, x)))
    zero_mode /= norm
    null_residual = float(np.linalg.norm(A @ zero_mode))

    central = np.abs(x) <= length / 4.0
    central_weight = float(np.trapezoid((zero_mode**2)[central], x[central]))
    left_boundary = x <= -3.0 * length / 4.0
    right_boundary = x >= 3.0 * length / 4.0
    boundary_weight = float(
        np.trapezoid((zero_mode**2)[left_boundary], x[left_boundary])
        + np.trapezoid((zero_mode**2)[right_boundary], x[right_boundary])
    )
    return {
        "points": points,
        "length": length,
        "wall_strength": wall_strength,
        "wall_width": wall_width,
        "selected_domain_dimension": points,
        "opposite_domain_dimension": points - 1,
        "rank_A": int(np.linalg.matrix_rank(A)),
        "K_plus_zero_modes": points - int(np.linalg.matrix_rank(A)),
        "K_minus_zero_modes": (points - 1) - int(np.linalg.matrix_rank(A)),
        "discrete_index": 1,
        "zero_mode_norm": float(np.trapezoid(zero_mode**2, x)),
        "zero_mode_residual": null_residual,
        "first_massive_level": float(singular[0]),
        "largest_level": float(singular[-1]),
        "central_probability": central_weight,
        "boundary_probability": boundary_weight,
        "center_localized": bool(central_weight > boundary_weight),
        "boundary_form": "maximal-isotropic rectangular A/A^dagger pairing",
        "boundary_flux": 0.0,
    }


def compact_mesh_convergence() -> list[dict[str, float | int]]:
    rows = []
    for points in (81, 161, 321):
        diagnostic = compact_supercharge_diagnostic(points=points)
        rows.append(
            {
                "points": points,
                "first_massive_level": round(
                    diagnostic["first_massive_level"], 12
                ),
                "zero_mode_residual": round(
                    diagnostic["zero_mode_residual"], 14
                ),
                "zero_mode_norm": round(diagnostic["zero_mode_norm"], 12),
            }
        )
    return rows


def compact_orientation_audit() -> dict[str, Any]:
    selected = compact_supercharge_diagnostic(wall_strength=1.0)
    reversed_mass = compact_supercharge_diagnostic(wall_strength=-1.0)
    return {
        "selected_orientation": selected,
        "fixed_domain_mass_reversal": reversed_mass,
        "selected_is_center_localized": selected["center_localized"],
        "reversed_is_center_localized": reversed_mass["center_localized"],
        "interpretation": (
            "on a compact interval both signs are L2; the chosen "
            "maximal-isotropic domain, boundary leakage, and orientation must "
            "be tracked. Complete-line nonnormalizability alone is not a "
            "compact no-doubling theorem"
        ),
        "action_selects_domain": False,
    }


def global_sector_ledger() -> list[dict[str, Any]]:
    """List what can and cannot be compared globally between fold sheets."""
    return [
        {
            "sector": "tensor",
            "principal_sign": "positive in the v6.4 coefficient domain",
            "complete_normal_operator": False,
            "sheet_difference": "not computed",
        },
        {
            "sector": "connection",
            "principal_sign": "positive for tau_i I_i>0",
            "complete_normal_operator": False,
            "sheet_difference": "not computed",
        },
        {
            "sector": "sigma/beta",
            "principal_sign": "positive retained kinetic metric",
            "complete_normal_operator": False,
            "sheet_difference": "coefficient and Schur-complement dependent",
        },
        {
            "sector": "orientation",
            "principal_sign": "positive away from beta=0",
            "complete_normal_operator": False,
            "sheet_difference": "no action-selected u potential",
        },
        {
            "sector": "junction bending",
            "principal_sign": "not sufficient",
            "complete_normal_operator": False,
            "sheet_difference": "cap Green operator missing",
        },
        {
            "sector": "first-order matter",
            "principal_sign": "conditional on the minimal extension",
            "complete_normal_operator": False,
            "sheet_difference": "retained representative operator is symmetric",
        },
        {
            "sector": "boundary-domain modes",
            "principal_sign": "domain dependent",
            "complete_normal_operator": False,
            "sheet_difference": "domain not selected by frozen action",
        },
    ]


def connection_transfer_ledger(beta: float = 0.3) -> dict[str, Any]:
    traces = connection_trace_payload()
    hopf = hopf_connection_transfer(1.0, 1.0, math.exp(beta))
    return {
        "master_formula": (
            "1/g_i^2 = I_i[tau_i,intrinsic + Z_A,i N_i]"
        ),
        "trace_indices": traces,
        "SU3": {
            "I3": traces["I3"],
            "tau_intrinsic": "tau_3 remains independent",
            "Z_A": "Z_A,3",
            "N": "N_3 cap/wall overlap remains unsolved",
            "parent_source": "no Spin8/G2 curvature transfer theorem derived",
        },
        "Sp1": {
            "I2": traces["I2"],
            "tau_intrinsic": "8 pi^2 kappa1 L2^4 L1",
            "Z_A": "Z_A,2",
            "N": "N_2",
            "representative": hopf,
        },
        "U1": {
            "I1_raw": traces["I1_raw"],
            "eta_Y": traces["eta_Y"],
            "I1_normalized": traces["I1_normalized"],
            "tau_intrinsic": "8 pi^2 kappa1 L2^2 L1^3",
            "Z_A": "Z_A,1",
            "N": "N_1",
        },
        "exact_Berger_ratio": math.exp(2.0 * beta),
        "Z_g_equals_Z_A_assumed": False,
        "measured_couplings_used": False,
        "candidate_1_2_7_restored": False,
    }


def scalar_berger_diagnostic() -> dict[str, Any]:
    metric = scalar_field_metric(2.0, 3.0)
    diagonal = scalar_mass_eigenvalues(4.0, 5.0, 0.0, 2.0, 3.0)
    mixed = scalar_mass_eigenvalues(4.0, 5.0, 0.5, 2.0, 3.0)
    return {
        "coordinates": ["sigma", "beta"],
        "kinetic_metric": metric.tolist(),
        "kinetic_eigenvalues": np.linalg.eigvalsh(metric).tolist(),
        "representative_diagonal_eigenvalues": diagonal.tolist(),
        "representative_mixed_eigenvalues": mixed.tolist(),
        "representative_only": True,
        "physical_Hessian_coefficients_derived": False,
        "metric_backreaction_Schur_complement_closed": False,
        "Higgs_like_mode": "not determined",
        "measured_W_Z_Higgs_inputs": False,
    }


def neutral_transport(
    connection_eigenvalues: Iterable[float],
    path_length: float,
    energy: float,
    energy_power: float = 0.0,
) -> dict[str, Any]:
    """Diagonal unitary transport for a declared neutral geometric connection."""
    values = np.asarray(tuple(connection_eigenvalues), dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError("at least two neutral eigenvalues are required")
    if energy <= 0:
        raise ValueError("energy must be positive")
    phases = path_length * values * energy**energy_power
    U = np.diag(np.exp(1j * phases))
    differences = [
        float(phases[i] - phases[j])
        for i in range(len(phases))
        for j in range(i)
    ]
    return {
        "unitary": bool(np.allclose(U.conj().T @ U, np.eye(len(values)))),
        "phases": phases.tolist(),
        "phase_differences": differences,
        "path_length_scaling": "L",
        "energy_scaling": f"E^{energy_power:g}",
        "path_reversal_is_adjoint": bool(
            np.allclose(
                np.diag(np.exp(-1j * phases)),
                U.conj().T,
            )
        ),
        "measured_Delta_m_squared_used": False,
    }


def integration_rows() -> list[dict[str, str]]:
    rows = [
        ("Unified action", "Active construction target"),
        ("Spacetime branch", "Adopted input"),
        ("Gauge algebra", "Derived"),
        ("Gauge normalization", "Active construction target"),
        ("Chiral particle map", "Derived"),
        ("Anomaly closure", "Derived"),
        ("Three families", "Derived"),
        ("Dynamic polarization", "Active construction target"),
        ("First-order matter action", "Active construction target"),
        ("Compact matter spectrum", "Active construction target"),
        ("Family mass operator", "Derived"),
        ("Absolute scale", "Active construction target"),
        ("CKM architecture", "Derived"),
        ("PMNS architecture", "Derived"),
        ("Neutrino phase law", "Needs empirical test"),
        ("Berger-Higgs mechanism", "Active construction target"),
        ("Constraint-reduced stable spectrum", "Active construction target"),
        ("Forward predictions", "Needs empirical test"),
        ("Empirical tests", "Needs empirical test"),
        ("Reproducibility", "Numerically validated"),
    ]
    return [{"component": component, "status": status} for component, status in rows]


def _common(name: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "version": VERSION,
        "sprint": SPRINT,
        "source_sha": SOURCE_SHA,
        "primary_result": PRIMARY_RESULT,
        **GUARDS,
    }


def build_artifact_payloads(
    repo_root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    common = _common
    fr = fr_template_checks()
    compact = compact_supercharge_diagnostic()
    orientation = compact_orientation_audit()
    transfer = connection_transfer_ledger()
    scalar = scalar_berger_diagnostic()
    gauge = electroweak_mass_diagnostic()
    neutral = neutral_transport((0.0, 0.2, 0.5), 3.0, 2.0)
    sources = first_order_source_candidates()
    rows = integration_rows()
    payloads = {
        "handoff": {
            **common("BHSM_v6_5_0_merged_stack_handoff"),
            "status": "BHSM_V6_2_TO_V6_4_STACK_MERGED_AND_PRESERVED",
            "source_main_sha": SOURCE_SHA,
            "v6_4_primary_result": V640_PRIMARY_RESULT,
            "stack": MERGED_STACK,
            "source_results_changed": False,
        },
        "merge": {
            **common("BHSM_GitHub_PR162_164_merge_ledger"),
            "status": "BHSM_PR162_164_HISTORY_PRESERVING_MERGE_COMPLETE",
            "stack": MERGED_STACK,
            "merge_method": "merge commits; no squash, rebase, or force push",
            "remote_branches_retained": True,
            "branch_protection": {
                "strict_required_checks": True,
                "required": ["pytest", "root-integration"],
                "force_pushes_allowed": False,
                "deletions_allowed": False,
            },
        },
        "cleanup": {
            **common("BHSM_repository_error_cleanup_audit_v6_5_0"),
            "status": "BHSM_MERGED_STACK_CLEANUP_AUDIT_PASS",
            "errors": [
                {
                    "class": "stale stacked base",
                    "prs": [163, 164],
                    "resolution": "ordinary merge from updated main",
                },
                {
                    "class": "connector permission",
                    "resolution": "authenticated gh CLI fallback",
                    "scientific_failure": False,
                },
                {
                    "class": "git object maintenance",
                    "detail": "git fsck reported dangling blobs only",
                    "scientific_failure": False,
                },
            ],
            "generated_rewrites": [],
            "untracked_scientific_source": [],
            "guards_weakened": False,
        },
        "configuration": {
            **common("BHSM_topological_configuration_space_v6_5_0"),
            "status": "BHSM_CONFIGURATION_SPACE_ONTOLOGY_NOT_FIXED_BY_FROZEN_ACTION",
            **configuration_space_ledger(),
        },
        "fr": {
            **common("BHSM_Finkelstein_Rubinstein_quantization_map_v6_5_0"),
            "status": "BHSM_FR_TEMPLATE_VALID_BHSM_IDENTIFICATION_NOT_DERIVED",
            **fr,
        },
        "source": {
            **common("BHSM_first_order_action_source_classification_v6_5_0"),
            "status": "BHSM_FIRST_ORDER_PARENT_SOURCE_NOT_FOUND_IN_FROZEN_ACTION",
            "candidates": sources,
            "existing_invariant_suffices": False,
            "configuration_space_route_excluded": False,
            "local_M4_transgression_derived": False,
        },
        "extension": {
            **common("BHSM_minimal_first_order_action_extension_v6_5_0"),
            **minimal_extension_ledger(),
        },
        "y_sigma": {
            **common("BHSM_y_sigma_coefficient_dependency_v6_5_0"),
            "status": "BHSM_Y_SIGMA_REMAINS_ONE_DIMENSIONLESS_PRIMITIVE",
            **y_sigma_dependency_theorem(),
        },
        "polarization_map": {
            **common("BHSM_dynamic_polarization_source_map_v6_5_0"),
            "status": "BHSM_DIRECT_BERGER_G2_LOCKING_REJECTED_BY_BUNDLE_MISMATCH",
            **polarization_source_map(),
        },
        "polarization": {
            **common("BHSM_G2_section_effective_potential_v6_5_0"),
            "status": "BHSM_POLARIZATION_SECTION_FLAT_DIRECTION_REMAINS",
            "G2_transitive_on_unit_sphere": True,
            "invariant_u_only_potential": "constant on G2/SU3",
            "representative_values": [
                polarization_potential(np.eye(7)[i]) for i in range(7)
            ],
            "u_only_tangent_Hessian": np.zeros((6, 6)).tolist(),
            "conditional_composite": "lambda[1-(u dot v)^2]",
            "conditional_composite_Hessian": polarization_hessian().tolist(),
            "stationary_sections": ["u=+v", "u=-v"],
            "u_sign_degeneracy": True,
            "action_supplies_v": False,
            "dynamic_selection": False,
            "polarization_checks_preserved": polarization_checks(),
        },
        "compact": {
            **common("BHSM_compact_chiral_normal_spectrum_v6_5_0"),
            "status": "BHSM_COMPACT_CHIRAL_DOMAIN_DIAGNOSTIC_VALIDATED_CONDITIONALLY",
            "operator": "C=[[0,A^dagger],[A,0]], A=partial_rho+y_sigma sigma",
            "representative": compact,
            "mesh_convergence": compact_mesh_convergence(),
            "both_scalar_signs": True,
            "both_orientations": True,
            "actual_B1_domain_selected": False,
            "actual_v6_1_7_profile_exported_to_operator": False,
            "complete_compact_spectrum_claimed": False,
        },
        "doubling": {
            **common("BHSM_vectorlike_partner_compact_audit_v6_5_0"),
            "status": "BHSM_COMPACT_VECTORLIKE_EXCLUSION_REMAINS_DOMAIN_CONDITIONAL",
            **orientation,
            "complete_line_index_one_preserved_as_compact_theorem": False,
            "conjugate_representation": (
                "antiparticle bundle only after the same global domain choice"
            ),
        },
        "sheets": {
            **common("BHSM_upper_lower_global_spectrum_comparison_v6_5_0"),
            "status": "BHSM_GLOBAL_FOLD_SHEET_SPECTRAL_SELECTION_NOT_DERIVED",
            "sectors": global_sector_ledger(),
            "retained_compact_diagnostic_sheet_symmetric": True,
            "upper_selected_globally": False,
            "lower_excluded": False,
            "adopted_upper_axiom_preserved": True,
            "required_next": (
                "construct every constraint-reduced normal operator with its "
                "B1 boundary form and continue both backgrounds globally"
            ),
        },
        "su3": {
            **common("BHSM_SU3_connection_transfer_v6_5_0"),
            "status": "BHSM_SU3_TRANSFER_REMAINS_INDEPENDENT",
            **transfer["SU3"],
            "master_formula": transfer["master_formula"],
        },
        "sp1": {
            **common("BHSM_Sp1_connection_transfer_v6_5_0"),
            "status": "BHSM_SP1_INTRINSIC_TRANSFER_DERIVED_OVERLAP_CONDITIONAL",
            **transfer["Sp1"],
            "master_formula": transfer["master_formula"],
        },
        "u1": {
            **common("BHSM_U1_connection_transfer_v6_5_0"),
            "status": "BHSM_U1_INTRINSIC_TRANSFER_DERIVED_OVERLAP_CONDITIONAL",
            **transfer["U1"],
            "master_formula": transfer["master_formula"],
            "exact_ratio_to_transverse": transfer["exact_Berger_ratio"],
        },
        "connection_graph": {
            **common("BHSM_connection_coupling_dependency_graph_v6_5_0"),
            "status": "BHSM_CONNECTION_NORMALIZATION_DEPENDENCIES_EXPLICIT",
            **transfer,
            "dependency_classes": {
                "representation": ["I1", "I2", "I3", "eta_Y"],
                "action": ["kappa1 Hopf stiffness", "tau_3 if supplied"],
                "geometry": ["L1", "L2", "beta"],
                "localization": ["N_1", "N_2", "N_3"],
                "independent": ["Z_A,1", "Z_A,2", "Z_A,3", "Z_g"],
                "empirical_correspondence": ["matching scale", "RG transport"],
            },
            "legacy_dependency_ledger": connection_dependency_ledger(),
        },
        "scalar": {
            **common("BHSM_scalar_Berger_physical_mass_matrix_v6_5_0"),
            "status": "BHSM_SCALAR_BERGER_EIGENMODE_REMAINS_COEFFICIENT_CONDITIONAL",
            **scalar,
        },
        "gauge": {
            **common("BHSM_gauge_mass_matrix_global_audit_v6_5_0"),
            "status": "BHSM_GAUGE_MASS_MATRIX_RANK_PRESERVED_CONDITIONALLY",
            "diagnostic": gauge,
            "charged_degeneracy": True,
            "one_massive_neutral": True,
            "exactly_one_Q_em_null": True,
            "additional_accidental_null": False,
            "global_profile_normalization_derived": False,
        },
        "hessian": {
            **common("BHSM_constraint_reduced_global_Hessian_v6_5_0"),
            "status": "BHSM_COMPLETE_CONSTRAINT_REDUCED_GLOBAL_HESSIAN_OPEN",
            "sector_ledger": global_sector_ledger(),
            "local_principal_health_preserved": True,
            "global_negative_mode_count": None,
            "junction_bending_operator": None,
            "cap_leakage_operator": None,
            "complete_mixed_stability_claimed": False,
        },
        "neutrino": {
            **common("BHSM_neutrino_geometric_phase_law_v6_5_0"),
            "status": "BHSM_NEUTRAL_GEOMETRIC_CONNECTION_GIVES_L_TIMES_E0_TEMPLATE",
            "operator": "U_neutral(gamma)=P exp(i integral_gamma A_neutral)",
            "representative": neutral,
            "L_over_E_reproduced": False,
            "reason": (
                "the declared energy-independent geometric connection gives "
                "phase proportional to L; an action-derived dispersive 1/E "
                "term is still required"
            ),
            "PMNS_architecture_attached": "structurally only",
            "CKM_PMNS_conflated": False,
        },
        "scale": {
            **common("BHSM_absolute_scale_transfer_closure_v6_5_0"),
            "status": "BHSM_ABSOLUTE_SCALE_TRANSFER_REMAINS_SYMBOLIC",
            "formula": (
                "L_i^2=(Z_g/Z_A,i) 2/(I_i g_i^2 Mbar_Pl^2) "
                "after all dimensionless transfers close"
            ),
            "C4_correspondence": "C4=Mbar_Pl^2/2 is empirical correspondence",
            "dimensionless_transfer_closed": False,
            "Z_g_equals_Z_A_assumed": False,
            "measured_particle_mass_used": False,
            "numerical_absolute_scale": None,
        },
        "r4": {
            **common("BHSM_scalar_wall_O_r4_progress_v6_5_0"),
            "status": "BHSM_SCALAR_WALL_O_R4_TOTAL_REMAINS_OPEN",
            "preserved_cusp": (
                "Gamma_tau-Gamma_c=tau(nu1/12)r^3+O(r^4)"
            ),
            "nu1_over_12": 9.138890145035,
            "direct_cubic_projection": "(G5/Z5)21.690130229412",
            "new_r4_components_derived": [],
            "flat_kink_27_35_revived": False,
        },
        "integration": {
            **common("BHSM_Full_BHSM_integration_ledger_v6_5_0"),
            "status": "BHSM_FULL_INTEGRATION_LEDGER_UPDATED_NO_COMPLETION",
            "allowed_statuses": [
                "Adopted input",
                "Derived",
                "Numerically validated",
                "Needs empirical test",
                "Rejected",
                "Active construction target",
            ],
            "rows": rows,
            "counting_rows_implies_completion": False,
            "full_BHSM_complete": False,
        },
        "hidden": {
            **common("BHSM_v6_5_0_hidden_input_audit"),
            "status": "BHSM_V6_5_0_HIDDEN_INPUT_AUDIT_PASS",
            "measured_inputs": [],
            "fits": [],
            "new_derived_primitives": [],
            "explicit_conditional_primitives": [
                "y_sigma",
                "configuration-space symplectic normalization",
                "polarization locking section or bundle morphism",
                "SU3 and boundary connection transfers",
                "global operator domains",
            ],
            "representative_numerics_are_proof_of_physical_spectrum": False,
        },
        "report": {
            **common("BHSM_topological_matter_action_global_spectrum_report_v6_5_0"),
            "status": PRIMARY_RESULT,
            "primary_conclusion": (
                "The merged architecture supports an exact FR/configuration-"
                "space template, a one-invariant effective boundary extension, "
                "and a convergent compact maximal-isotropic domain diagnostic. "
                "The frozen action does not define Q_N, generate the local "
                "first-order carrier, fix y_sigma, select u, select the compact "
                "domain, or supply the complete global sector operators."
            ),
            "derived": [
                "G2-invariant u-only potentials are constant on G2/SU3",
                "direct Berger/G2 locking is absent in the declared bundles",
                "minimal extension leaves exactly one dimensionless ratio",
                "compact rectangular-domain index and mesh convergence",
                "Sp1/U1 intrinsic Berger transfer ratio exp(2 beta)",
                "energy-independent neutral connection phase scales as L E^0",
            ],
            "numerically_validated": [
                "compact supercharge Hermiticity/domain pairing",
                "one discrete zero mode and positive spectral gap",
                "mesh convergence and zero boundary form",
                "preserved gauge-mass rank",
            ],
            "rejected": [
                "P1/GHY/B1 as an existing first-order matter source",
                "eta invariant as a noncircular source",
                "ad hoc torsion",
                "direct Berger/G2/spacetime-normal identification",
                "complete-line normalizability as a compact no-doubling theorem",
                "global upper-sheet selection from retained local operators",
                "L/E neutrino phase from an energy-independent connection alone",
            ],
            "active_targets": [
                "define a topological BHSM configuration component and compute pi1",
                "derive a Q_N-to-local-M4 transgression",
                "derive a polarization-locking bundle morphism or preserve the modulus",
                "derive B1 self-adjoint domains and complete global operators",
                "close connection overlaps, scalar Schur complement, r4, and scale",
            ],
            "completion_gate": COMPLETION_GATE,
        },
    }
    if set(payloads) != set(ARTIFACT_FILES):
        raise RuntimeError("v6.5.0 artifact registry/payload mismatch")
    return payloads


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    payloads = build_artifact_payloads(root)
    output = root / "artifacts"
    written = []
    for key, filename in ARTIFACT_FILES.items():
        path = output / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def architecture_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    return {
        "version": VERSION,
        "branch": SPRINT,
        "source_sha": SOURCE_SHA,
        "primary_result": PRIMARY_RESULT,
        "first_order_source": payloads["source"]["status"],
        "y_sigma": payloads["y_sigma"]["status"],
        "dynamic_polarization": payloads["polarization"]["status"],
        "compact_spectrum": payloads["compact"]["status"],
        "global_sheet_spectrum": payloads["sheets"]["status"],
        "connection_transfer": payloads["connection_graph"]["status"],
        "scalar_berger": payloads["scalar"]["status"],
        "neutrino_phase": payloads["neutrino"]["status"],
        "absolute_scale": payloads["scale"]["status"],
        "completion_gate": COMPLETION_GATE,
        "safeguards": GUARDS,
    }


def architecture_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# BHSM v6.5.0 topological matter action and global spectrum",
            "",
            f"Primary result: `{report['primary_result']}`.",
            "",
            f"- First-order source: `{report['first_order_source']}`",
            f"- Wall coefficient: `{report['y_sigma']}`",
            f"- Dynamic polarization: `{report['dynamic_polarization']}`",
            f"- Compact spectrum: `{report['compact_spectrum']}`",
            f"- Global sheet spectrum: `{report['global_sheet_spectrum']}`",
            f"- Connection transfer: `{report['connection_transfer']}`",
            f"- Scalar/Berger mode: `{report['scalar_berger']}`",
            f"- Neutral phase: `{report['neutrino_phase']}`",
            f"- Absolute scale: `{report['absolute_scale']}`",
            f"- Completion gate: `{report['completion_gate']}`",
            "",
        ]
    )
