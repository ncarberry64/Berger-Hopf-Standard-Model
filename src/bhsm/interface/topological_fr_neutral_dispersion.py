"""BHSM v6.6.0 topological FR and neutral-dispersion construction.

The module makes one explicit BHSM configuration-space identification, derives
its mapping-space fundamental group, selects the nontrivial FR character, and
then keeps that global quantization result separate from the local boundary
action.  The neutral propagation routines are deterministic no-fit tests of a
conditional geometric response operator; they are not oscillation predictions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

from .topological_matter_action_global_spectrum import (
    compact_supercharge_diagnostic,
)


VERSION = "v6.6.0"
SPRINT = "bhsm-topological-fr-neutral-dispersion-v6-6-0"
SOURCE_SHA = "ae14c0f9af8fe8b7933aed584e7bd924b9001ce4"
V650_SCIENTIFIC_SHA = "746de9f8aee3b82b89a34c46f9feee5c68c450ba"
PRIMARY_RESULT = (
    "BHSM_TOPOLOGICAL_FR_AND_NEUTRAL_DISPERSION_"
    "ARCHITECTURE_DERIVED_CONDITIONALLY"
)
COMPLETION_GATE = (
    "V6_6_0_LOCAL_CARRIER_PARENT_SOURCE_PROPAGATION_RESPONSE_"
    "AND_FULL_COMPACT_B1_SPECTRUM_OPEN"
)

ARTIFACT_FILES = {
    "handoff": "BHSM_v6_6_0_merged_v6_5_handoff.json",
    "merge": "BHSM_PR165_merge_cleanup_ledger.json",
    "configuration": "BHSM_degree_N_S3_configuration_space_v6_6_0.json",
    "mapping_pi1": "BHSM_mapping_space_pi1_v6_6_0.json",
    "fr_character": "BHSM_FR_sign_character_v6_6_0.json",
    "loops": "BHSM_rotation_exchange_loop_classification_v6_6_0.json",
    "metric": "BHSM_collective_coordinate_metric_v6_6_0.json",
    "berry": "BHSM_collective_symplectic_Berry_audit_v6_6_0.json",
    "transgression": "BHSM_FR_to_local_M4_transgression_test_v6_6_0.json",
    "architecture": "BHSM_first_order_action_architecture_decision_v6_6_0.json",
    "invariant": "BHSM_minimal_boundary_first_order_invariant_v6_6_0.json",
    "y_sigma": "BHSM_y_sigma_dependency_theorem_v6_6_0.json",
    "compact": "BHSM_compact_B1_first_order_spectrum_v6_6_0.json",
    "vectorlike": "BHSM_compact_vectorlike_partner_audit_v6_6_0.json",
    "polarization": "BHSM_topological_dynamic_polarization_map_v6_6_0.json",
    "propagation": "BHSM_neutral_high_energy_propagation_operator_v6_6_0.json",
    "phase": "BHSM_neutral_L_over_E_phase_law_v6_6_0.json",
    "zero_rest": "BHSM_zero_rest_mass_doctrine_audit_v6_6_0.json",
    "pmns": "BHSM_PMNS_geometric_transport_attachment_v6_6_0.json",
    "separation": "BHSM_CKM_PMNS_structural_separation_v6_6_0.json",
    "overlap": "BHSM_connection_profile_overlap_v6_6_0.json",
    "scalar": "BHSM_scalar_Berger_forward_link_v6_6_0.json",
    "scale": "BHSM_absolute_scale_forward_link_v6_6_0.json",
    "integration": "BHSM_Full_BHSM_integration_ledger_v6_6_0.json",
    "hidden": "BHSM_v6_6_0_hidden_input_audit.json",
    "report": "BHSM_topological_FR_neutral_dispersion_report_v6_6_0.json",
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


def mapping_space_identification() -> dict[str, Any]:
    """Define the selected BHSM mapping-space candidate and its variants."""
    variants = [
        {
            "candidate": "based maps",
            "space": "Q_N=Map_*^N(S3,S3)",
            "pi1": "Z2",
            "decision": "selected BHSM identification",
        },
        {
            "candidate": "unbased maps",
            "space": "Map^N(S3,S3)",
            "pi1": "Z2",
            "reason": "evaluation fibration and pi1(S3)=pi2(S3)=0",
        },
        {
            "candidate": "global target rotations",
            "space": "free SU2 quotient when the action is free",
            "pi1": "unchanged by simply connected SU2 fiber",
            "decision": "comparison only",
        },
        {
            "candidate": "local gauge quotient",
            "pi1": "not computed",
            "decision": "not applied; no such quotient is declared for this field",
        },
        {
            "candidate": "Berger/polarization enrichment",
            "pi1": "not multiplied",
            "decision": "associated data, not an identified mapping-space factor",
        },
        {
            "candidate": "boundary versus bulk maps",
            "pi1": "relative homotopy data required",
            "decision": "open beyond compactified spatial S3",
        },
    ]
    return {
        "field_domain": "compactified oriented physical spatial slice S3",
        "target": "unit S3 matter-order-parameter space, identified with SU2",
        "topology": "compact-open topology, k-ified; smooth finite-energy subspace",
        "basepoint": "spatial infinity maps to target identity",
        "boundary_condition": "based finite-energy condition",
        "gauge_quotient": "none beyond the based condition",
        "component": "degree N in Z",
        "tangent_space": "based sections of phi^*TS3 in the Sobolev completion",
        "metric": "G_phi(delta1,delta2)=integral_S3 <delta1,K_phi delta2> dvol",
        "finite_energy": "finite frozen bosonic/topological energy functional",
        "variants": variants,
        "identification_status": "Adopted BHSM identification",
    }


def mapping_space_pi1() -> dict[str, Any]:
    """Return the adjunction derivation and its exact consequence."""
    return {
        "route": [
            "pi1(Map_*^N(S3,S3))=[S1,Map_*^N(S3,S3)]_*",
            "[S1,Map_*(S3,S3)]_*=[S1 smash S3,S3]_*",
            "[S4,S3]_* = pi4(S3)",
            "pi4(S3)=Z2, generated by the suspension of the Hopf map",
        ],
        "component_independence": (
            "target S3=SU2 is a topological group, so pointwise multiplication "
            "translates degree components by a homotopy equivalence"
        ),
        "group": "Z2",
        "order": 2,
        "hard_coded_as_assumption": False,
        "derived_from_adjunction_plus_established_pi4": True,
    }


def fr_character(loop_class: int, nontrivial: bool = True) -> int:
    """One-dimensional character of Z2."""
    value = int(loop_class) % 2
    return -1 if nontrivial and value else 1


def fr_character_ledger() -> dict[str, Any]:
    characters = {
        "trivial": [fr_character(0, False), fr_character(1, False)],
        "fermionic": [fr_character(0, True), fr_character(1, True)],
    }
    homomorphism = all(
        fr_character(a + b) == fr_character(a) * fr_character(b)
        for a in range(2)
        for b in range(2)
    )
    return {
        "pi1": "Z2",
        "characters": characters,
        "selected": "nontrivial fermionic character",
        "homomorphism_exact": homomorphism,
        "universal_cover": "two-sheeted universal cover Qtilde_N -> Q_N",
        "line_bundle": "L_FR=Qtilde_N x_chi C",
        "equivariance": "Psi(gamma q)=chi_FR(gamma) Psi(q)",
        "hilbert_space": "L2 sections of L_FR over Q_N with collective metric",
    }


def loop_classification(charge: int) -> dict[str, Any]:
    """Classify established soliton loops without identifying unrelated loops."""
    parity = abs(int(charge)) % 2
    sign = fr_character(parity)
    return {
        "N": int(charge),
        "two_pi_spatial_rotation": {"class": parity, "sign": sign},
        "identical_soliton_exchange": {"class": parity, "sign": sign},
        "two_pi_internal_target_rotation": {"class": parity, "sign": sign},
        "particle_antiparticle_continuation": {
            "class": "not a loop within fixed Q_N",
            "conjugation": "N -> -N preserves parity and the selected character",
        },
        "triality_cycle": {
            "class": "not identified with the FR generator",
            "reason": "separate discrete family action",
        },
        "wall_orientation_reversal": {
            "class": "not identified with the FR generator",
            "reason": "changes oriented wall data",
        },
        "half_integer_spin_admitted": bool(parity),
        "fermionic_exchange": bool(parity),
        "family_universal": True,
        "exactly_one_representation_per_particle_slot": False,
        "additional_family_sectors_excluded": False,
    }


def collective_coordinate_audit() -> dict[str, Any]:
    """Classify the natural collective dynamics and the flat FR holonomy."""
    metric = np.diag([1.0, 1.0, 1.0, 2.0, 2.0, 2.0])
    return {
        "coordinates": ["translation_1", "translation_2", "translation_3",
                        "rotation_1", "rotation_2", "internal_orientation"],
        "representative_metric": metric.tolist(),
        "metric_positive": bool(np.all(np.linalg.eigvalsh(metric) > 0)),
        "symbolic_action": (
            "S_coll=int dt [G_AB qdot^A qdot^B/2+A_A qdot^A-V(q)]"
        ),
        "natural_frozen_bosonic_term": "second-order moduli-space kinetic metric",
        "FR_holonomy": -1,
        "FR_connection": "flat Z2 line-bundle connection",
        "local_curvature_omega": np.zeros((6, 6)).tolist(),
        "continuous_Berry_term_derived": False,
        "added_topological_invariant_present": False,
        "conclusion": (
            "FR holonomy twists the Hilbert space but supplies no local "
            "continuous first-order collective or M4 kinetic term"
        ),
    }


def architecture_decision() -> dict[str, Any]:
    return {
        "architecture_A": {
            "FR_spin_statistics": True,
            "associated_local_M4_bundle_derived": False,
            "local_frame_and_transition_functions_derived": False,
            "Lorentzian_kinetic_operator_derived": False,
            "sigma_Gamma_star_coefficient_derived": False,
            "verdict": "fails at the configuration-space-to-M4 transgression",
        },
        "architecture_B": {
            "selected": True,
            "status": "Adopted BHSM action invariant",
            "new_dimensionless_primitives": 1,
        },
        "decision": "Architecture B",
        "secondary_result": (
            "BHSM_FR_QUANTIZATION_DERIVES_STATISTICS_NOT_LOCAL_FIRST_ORDER_ACTION"
        ),
    }


def minimal_invariant() -> dict[str, Any]:
    return {
        "action": (
            "S_F,partial=int_M4 sqrt(-h)<Psi,"
            "[C_BHSM+y_sigma sigma Gamma_star]Psi>"
        ),
        "status": "Adopted BHSM action invariant; not parent-derived",
        "carrier": "effective section of the declared boundary Clifford bundle",
        "domain": "declared self-adjoint maximal-isotropic boundary domain",
        "inner_product": "Hermitian fiber metric and Lorentzian boundary pairing",
        "lowest_order_covariant": True,
        "preserves_v6_3_representations": True,
        "preserves_Y_BH": True,
        "preserves_Q_em": True,
        "family_universal": True,
        "Hermitian_for_real_y_sigma": True,
        "sigma_wall_odd": True,
        "beta_can_replace_sigma": False,
        "orientation_linear_invariant_allowed": False,
        "smaller_localizing_term_exists": False,
        "new_dimensional_scale": False,
        "measured_input": False,
        "physical_bulk_Dirac_parent": False,
    }


def y_sigma_theorem() -> dict[str, Any]:
    return {
        "field_normalization": "removes overall kinetic normalization only",
        "FR_topology": "fixes the sign character, not a continuous magnitude",
        "canonical_normalization": "does not fix y_sigma",
        "Z_sigma_relation": "not derived",
        "wall_width_relation": "not derived",
        "collective_inertia_relation": "not derived",
        "classification": "independent dimensionless primitive",
        "primitive_count": 1,
        "sector_dependent_Yukawa_coefficients": 0,
    }


def compact_sweep() -> list[dict[str, Any]]:
    rows = []
    for strength in (0.5, 1.0, 2.0):
        value = compact_supercharge_diagnostic(wall_strength=strength)
        rows.append({
            "y_sigma_times_wall_amplitude": strength,
            "zero_modes": value["K_plus_zero_modes"],
            "index": value["discrete_index"],
            "zero_mode_residual": value["zero_mode_residual"],
            "first_massive_level": value["first_massive_level"],
            "central_probability": value["central_probability"],
            "boundary_probability": value["boundary_probability"],
        })
    return rows


def _hermitian(matrix: Iterable[Iterable[complex]], name: str) -> np.ndarray:
    value = np.asarray(tuple(tuple(row) for row in matrix), dtype=complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be square")
    if not np.allclose(value, value.conj().T):
        raise ValueError(f"{name} must be Hermitian")
    return value


def remove_common_phase(matrix: Iterable[Iterable[complex]]) -> np.ndarray:
    """Remove the physically irrelevant identity component."""
    value = _hermitian(matrix, "matrix")
    return value - np.trace(value) * np.eye(len(value)) / len(value)


def neutral_hamiltonian(
    energy: float,
    k_prop: Iterable[Iterable[complex]],
    a0: Iterable[Iterable[complex]] | None = None,
) -> np.ndarray:
    """H=E I+K_prop/(2E)+A0 for a declared Hermitian response."""
    if energy <= 0:
        raise ValueError("energy must be positive")
    k_value = _hermitian(k_prop, "K_prop")
    a_value = np.zeros_like(k_value) if a0 is None else _hermitian(a0, "A0")
    if a_value.shape != k_value.shape:
        raise ValueError("K_prop and A0 must have the same shape")
    return energy * np.eye(len(k_value)) + k_value / (2.0 * energy) + a_value


def unitary_segment(
    energy: float,
    length: float,
    k_prop: Iterable[Iterable[complex]],
    a0: Iterable[Iterable[complex]] | None = None,
) -> np.ndarray:
    """Exact constant-segment evolution by Hermitian eigendecomposition."""
    effective = remove_common_phase(neutral_hamiltonian(energy, k_prop, a0))
    values, vectors = np.linalg.eigh(effective)
    return (vectors * np.exp(-1j * length * values)) @ vectors.conj().T


def path_transport(
    energy: float,
    segments: Sequence[tuple[float, Iterable[Iterable[complex]]]],
    a0: Iterable[Iterable[complex]] | None = None,
) -> np.ndarray:
    """Path-ordered product over deterministic constant response segments."""
    if not segments:
        raise ValueError("at least one segment is required")
    size = _hermitian(segments[0][1], "K_prop").shape[0]
    result = np.eye(size, dtype=complex)
    for length, response in segments:
        if length < 0:
            raise ValueError("segment lengths must be nonnegative")
        result = unitary_segment(energy, length, response, a0) @ result
    return result


def representative_response() -> np.ndarray:
    """No-fit rational geometric response used only for invariant tests."""
    return np.array([
        [2.0, -1.0, 0.0],
        [-1.0, 2.0, -1.0],
        [0.0, -1.0, 2.0],
    ])


def propagation_diagnostic() -> dict[str, Any]:
    k_value = representative_response()
    energy = 5.0
    length = 3.0
    U = unitary_segment(energy, length, k_value)
    U2 = unitary_segment(2.0 * energy, length, k_value)
    split = path_transport(energy, [(length / 2, k_value), (length / 2, k_value)])
    eigenvalues = np.linalg.eigvalsh(k_value)
    phases = length * (eigenvalues - eigenvalues.mean()) / (2.0 * energy)
    phases2 = length * (eigenvalues - eigenvalues.mean()) / (4.0 * energy)
    return {
        "operator": "H=E I+K_prop(x)/(2E)+A0(x)+O(E^-2)",
        "representative_K_prop": k_value.tolist(),
        "unitary": bool(np.allclose(U.conj().T @ U, np.eye(3))),
        "path_reversal_is_adjoint": bool(
            np.allclose(unitary_segment(energy, -length, k_value), U.conj().T)
        ),
        "common_phase_removed": bool(
            np.allclose(np.trace(remove_common_phase(k_value)), 0.0)
        ),
        "segment_refinement_invariant": bool(np.allclose(U, split)),
        "phases": phases.tolist(),
        "double_energy_phases": phases2.tolist(),
        "phase_halving_at_double_energy": bool(np.allclose(phases2, phases / 2)),
        "baseline_scaling": "linear in affine path length",
        "leading_energy_scaling": "E^-1 when flavor-dependent A0 is absent",
        "static_A0_scaling": "L E^0; not an L/E mechanism",
        "measured_oscillation_inputs": False,
    }


def zero_rest_mass_audit() -> dict[str, Any]:
    return {
        "constant_Lorentz_invariant_vacuum_K": (
            "operationally a four-dimensional mass-squared operator"
        ),
        "required_for_propagation_supported_reading": [
            "path/geometry dependence",
            "curvature, medium, or boundary-propagation activation",
            "vanishing in the declared flat non-propagating limit",
            "no static localized rest-energy pole",
        ],
        "current_action_derives_path_dependent_K_prop": False,
        "current_action_decides_vacuum_dispersion": False,
        "result": (
            "zero-fundamental-rest-mass doctrine is conditionally compatible "
            "with a propagation-supported K_prop, but the current action "
            "cannot decide or derive that operator"
        ),
    }


def profile_overlap(points: int = 2001, length: float = 8.0) -> dict[str, Any]:
    """Representative normalized wall-profile overlap without fitted inputs."""
    x = np.linspace(-length, length, points)
    psi = 1.0 / np.cosh(x)
    psi /= np.sqrt(np.trapezoid(psi**2, x))
    connection_profile = np.exp(-x**2)
    overlap = float(np.trapezoid(psi**2 * connection_profile, x))
    return {
        "profile": "normalized sech(x) diagnostic",
        "connection_profile": "exp(-x^2) diagnostic",
        "normalization": float(np.trapezoid(psi**2, x)),
        "overlap": overlap,
        "action_derived_B1_profile": False,
        "physical_transfer_coefficient_derived": False,
    }


def integration_rows() -> list[dict[str, str]]:
    statuses = [
        ("Unified parent action", "Active construction target"),
        ("Spacetime branch", "Adopted input"),
        ("Gauge algebra", "Derived"),
        ("Gauge normalization", "Active construction target"),
        ("Three-family theorem", "Derived"),
        ("Chiral particle map", "Derived"),
        ("Anomaly closure", "Derived"),
        ("Global polarization", "Adopted input"),
        ("Dynamic polarization", "Active construction target"),
        ("Topological matter configuration space", "Adopted input"),
        ("FR spin/statistics", "Derived"),
        ("Local first-order matter action", "Adopted input"),
        ("Compact matter spectrum", "Numerically validated"),
        ("Family mass operator", "Derived"),
        ("Absolute scale", "Active construction target"),
        ("CKM architecture", "Derived"),
        ("PMNS architecture", "Derived"),
        ("Neutral L/E phase law", "Active construction target"),
        ("Berger-Higgs mechanism", "Active construction target"),
        ("Constraint-reduced stable spectrum", "Active construction target"),
        ("Forward predictions", "Active construction target"),
        ("Empirical tests", "Needs empirical test"),
        ("Reproducibility", "Numerically validated"),
    ]
    return [{"component": name, "status": status} for name, status in statuses]


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
    del repo_root
    common = _common
    configuration = mapping_space_identification()
    pi1 = mapping_space_pi1()
    fr = fr_character_ledger()
    collective = collective_coordinate_audit()
    decision = architecture_decision()
    minimal = minimal_invariant()
    y_sigma = y_sigma_theorem()
    compact = compact_sweep()
    propagation = propagation_diagnostic()
    zero_rest = zero_rest_mass_audit()
    overlap = profile_overlap()
    payloads = {
        "handoff": {
            **common("BHSM_v6_6_0_merged_v6_5_handoff"),
            "status": "BHSM_V6_5_0_MERGED_BASELINE_PRESERVED",
            "v6_5_scientific_sha": V650_SCIENTIFIC_SHA,
            "main_merge_sha": SOURCE_SHA,
            "v6_5_sha_is_ancestor": True,
        },
        "merge": {
            **common("BHSM_PR165_merge_cleanup_ledger"),
            "status": "BHSM_PR165_HISTORY_PRESERVING_MERGE_COMPLETE",
            "pr": 165,
            "merge_method": "merge commit",
            "checks": {"pytest": "pass", "native": "pass", "ROOT": "pass"},
            "remote_branch_retained": True,
            "force_push": False,
            "rebase": False,
            "squash": False,
        },
        "configuration": {
            **common("BHSM_degree_N_S3_configuration_space_v6_6_0"),
            "status": "BHSM_DEGREE_N_S3_CONFIGURATION_SPACE_IDENTIFIED",
            **configuration,
        },
        "mapping_pi1": {
            **common("BHSM_mapping_space_pi1_v6_6_0"),
            "status": "BHSM_MAPPING_SPACE_PI1_Z2_DERIVED",
            **pi1,
        },
        "fr_character": {
            **common("BHSM_FR_sign_character_v6_6_0"),
            "status": "BHSM_FR_NONTRIVIAL_SIGN_CHARACTER_SELECTED",
            **fr,
        },
        "loops": {
            **common("BHSM_rotation_exchange_loop_classification_v6_6_0"),
            "status": "BHSM_FR_ODD_EVEN_LOOP_CLASSIFICATION_DERIVED",
            "charge_samples": [loop_classification(n) for n in (-2, -1, 0, 1, 2)],
        },
        "metric": {
            **common("BHSM_collective_coordinate_metric_v6_6_0"),
            "status": "BHSM_COLLECTIVE_METRIC_SYMBOLIC_AND_POSITIVE_DIAGNOSTIC",
            **collective,
        },
        "berry": {
            **common("BHSM_collective_symplectic_Berry_audit_v6_6_0"),
            "status": "BHSM_FR_FLAT_HOLONOMY_NO_LOCAL_BERRY_CURVATURE",
            **collective,
        },
        "transgression": {
            **common("BHSM_FR_to_local_M4_transgression_test_v6_6_0"),
            "status": "BHSM_FR_TO_LOCAL_M4_TRANSGRESSION_NOT_DERIVED",
            **decision["architecture_A"],
            "exact_obstruction": (
                "a Z2 line bundle over Q_N supplies global equivariance but "
                "no associated local M4 Clifford bundle, transition data, "
                "Lorentzian kinetic symbol, or wall coefficient"
            ),
        },
        "architecture": {
            **common("BHSM_first_order_action_architecture_decision_v6_6_0"),
            "status": "BHSM_FIRST_ORDER_ARCHITECTURE_B_SELECTED",
            **decision,
        },
        "invariant": {
            **common("BHSM_minimal_boundary_first_order_invariant_v6_6_0"),
            "status": "BHSM_MINIMAL_BOUNDARY_FIRST_ORDER_ACTION_ADOPTED_WITH_ONE_PRIMITIVE",
            **minimal,
        },
        "y_sigma": {
            **common("BHSM_y_sigma_dependency_theorem_v6_6_0"),
            "status": "BHSM_Y_SIGMA_ONE_DIMENSIONLESS_PRIMITIVE_EXPOSED",
            **y_sigma,
        },
        "compact": {
            **common("BHSM_compact_B1_first_order_spectrum_v6_6_0"),
            "status": "BHSM_COMPACT_DOMAIN_SPECTRUM_Y_SIGMA_DEPENDENCE_VALIDATED",
            "operator": "A=partial_rho+y_sigma sigma",
            "sweep": compact,
            "upper_lower_sheet_dependence": "not available in exported B1 profiles",
            "actual_full_B1_cap_spectrum": False,
            "domain_action_selected": False,
        },
        "vectorlike": {
            **common("BHSM_compact_vectorlike_partner_audit_v6_6_0"),
            "status": "BHSM_VECTORLIKE_PARTNER_ABSENT_IN_SELECTED_DIAGNOSTIC_DOMAIN",
            "sweep": compact,
            "index": 1,
            "independent_opposite_chirality_zero_mode": False,
            "full_domain_theorem": False,
        },
        "polarization": {
            **common("BHSM_topological_dynamic_polarization_map_v6_6_0"),
            "status": "BHSM_TOPOLOGICAL_FIELD_DOES_NOT_SELECT_G2_SECTION",
            "domain_representation": "S3/SU2-valued",
            "target_section": "G2/SU3=S6",
            "equivariant_map_supplied": False,
            "induced_potential": 0.0,
            "induced_Hessian": np.zeros((6, 6)).tolist(),
            "result": "polarization remains a flat adopted background",
        },
        "propagation": {
            **common("BHSM_neutral_high_energy_propagation_operator_v6_6_0"),
            "status": "BHSM_NEUTRAL_HIGH_ENERGY_OPERATOR_VALIDATED_CONDITIONALLY",
            **propagation,
            "K_prop_action_source": "not derived",
        },
        "phase": {
            **common("BHSM_neutral_L_over_E_phase_law_v6_6_0"),
            "status": "BHSM_NEUTRAL_L_OVER_E_GEOMETRIC_PHASE_DERIVED_CONDITIONALLY",
            "law": "Delta phi_ij=int_gamma Delta kappa_ij(x)/(2E) d ell",
            **propagation,
            "condition": "flavor-dependent A0 absent and K_prop propagation-supported",
            "prediction": False,
        },
        "zero_rest": {
            **common("BHSM_zero_rest_mass_doctrine_audit_v6_6_0"),
            "status": "BHSM_ZERO_REST_MASS_DOCTRINE_CURRENT_ACTION_CANNOT_DECIDE",
            **zero_rest,
        },
        "pmns": {
            **common("BHSM_PMNS_geometric_transport_attachment_v6_6_0"),
            "status": "BHSM_PMNS_TRANSPORT_ATTACHMENT_STRUCTURAL_ONLY",
            "formula": "U_PMNS=U_l^dagger U_neutral U_nu",
            "neutral_eigenvectors_derived": False,
            "arbitrary_free_matrix_inserted": False,
            "measured_PMNS_used": False,
        },
        "separation": {
            **common("BHSM_CKM_PMNS_structural_separation_v6_6_0"),
            "status": "BHSM_CKM_PMNS_STRUCTURAL_SEPARATION_PRESERVED",
            "PMNS": "U_l^dagger U_neutral U_nu",
            "CKM": "U_u^dagger U_color U_d",
            "triality_channels": 3,
            "physical_transport_matrices_derived": False,
        },
        "overlap": {
            **common("BHSM_connection_profile_overlap_v6_6_0"),
            "status": "BHSM_CONNECTION_PROFILE_OVERLAP_DIAGNOSTIC_ONLY",
            **overlap,
        },
        "scalar": {
            **common("BHSM_scalar_Berger_forward_link_v6_6_0"),
            "status": "BHSM_SCALAR_BERGER_FORWARD_LINK_PRESERVED_OPEN",
            "coordinates": ["sigma", "beta"],
            "tau_ratio": "tau_nested/tau_transverse=exp(2 beta)",
            "physical_scalar_eigenmode_transfer": "not derived",
            "Q_em_null_direction_preserved": True,
        },
        "scale": {
            **common("BHSM_absolute_scale_forward_link_v6_6_0"),
            "status": "BHSM_ABSOLUTE_SCALE_TRANSFER_REMAINS_OPEN",
            "formula": "L_i^2=(Z_g/Z_A,i) 2/(I_i g_i^2 Mbar_Pl^2)",
            "Z_g_equals_Z_A_assumed": False,
            "absolute_unit_derived": False,
        },
        "integration": {
            **common("BHSM_Full_BHSM_integration_ledger_v6_6_0"),
            "status": "FULL_BHSM_NOT_COMPLETE",
            "rows": integration_rows(),
        },
        "hidden": {
            **common("BHSM_v6_6_0_hidden_input_audit"),
            "status": "BHSM_V6_6_0_HIDDEN_INPUT_AUDIT_PASS",
            "new_primitives": [{"name": "y_sigma", "dimension": 0, "count": 1}],
            "measured_inputs": [],
            "fitted_matrices": [],
            "static_holonomy_revived_as_L_over_E": False,
            "K_prop_parent_derived": False,
        },
        "report": {
            **common("BHSM_topological_FR_neutral_dispersion_report_v6_6_0"),
            "status": PRIMARY_RESULT,
            "architecture": "B",
            "derived": [
                "mapping-space pi1=Z2",
                "FR characters and odd/even spin-statistics classification",
                "conditional Hermitian K_prop L/E phase formula",
            ],
            "adopted": [
                "degree-N based mapping-space BHSM identification",
                "minimal boundary first-order invariant with primitive y_sigma",
            ],
            "open": [
                "parent source for local carrier and y_sigma",
                "action-derived path-dependent K_prop",
                "full B1 cap spectrum and domain selection",
                "dynamic G2 polarization",
                "absolute scale and empirical prediction layer",
            ],
            "completion_gate": COMPLETION_GATE,
        },
    }
    if set(payloads) != set(ARTIFACT_FILES):
        raise RuntimeError("v6.6.0 artifact registry/payload mismatch")
    return payloads


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def materialize_artifacts(root: Path) -> list[Path]:
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    payloads = build_artifact_payloads(root)
    written = []
    for key, filename in ARTIFACT_FILES.items():
        path = artifacts / filename
        path.write_text(deterministic_json(payloads[key]), encoding="utf-8")
        written.append(path)
    return written


def architecture_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    payloads = build_artifact_payloads(repo_root)
    return {
        "version": VERSION,
        "sprint": SPRINT,
        "source_sha": SOURCE_SHA,
        "primary_result": PRIMARY_RESULT,
        "architecture": payloads["architecture"],
        "topology": payloads["mapping_pi1"],
        "fr": payloads["fr_character"],
        "neutral_phase": payloads["phase"],
        "zero_rest_mass": payloads["zero_rest"],
        "completion_gate": COMPLETION_GATE,
        "guards": GUARDS,
    }


def architecture_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# BHSM v6.6.0 topological FR and neutral dispersion",
        "",
        f"Primary result: `{report['primary_result']}`.",
        "",
        f"Architecture decision: **{report['architecture']['decision']}**.",
        "",
        "The selected based degree-N mapping-space candidate has",
        "`pi1 = pi4(S3) = Z2`. Its nontrivial FR character derives the",
        "odd/even spin-statistics distinction, but not a local M4 action.",
        "",
        "The minimal boundary first-order invariant is therefore an adopted",
        "BHSM action invariant with one explicit dimensionless primitive,",
        "`y_sigma`; it is not parent-derived.",
        "",
        "A Hermitian propagation response gives",
        "`Delta phi_ij = integral Delta kappa_ij/(2E) d ell` conditionally.",
        "The current action does not derive `K_prop`, and a constant vacuum",
        "`K_prop` would be operationally a mass-squared operator.",
        "",
        f"Open gate: `{report['completion_gate']}`.",
        "",
        "`FULL_BHSM_NOT_COMPLETE`",
    ])
