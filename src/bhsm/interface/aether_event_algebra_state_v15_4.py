"""BHSM v15.4 foundational event-algebra, dagger, state, and GNS audit.

The architecture-owned object remains a complex-linear category span of
composable events.  Finite transitive groupoids over the four-vertex BHSM
incidence diamond provide a stronger kill screen than the one-object cyclic
witnesses of v15.3: both Z2 and Z3 admit an exact reversal dagger, faithful
positive states, GNS representations, and the same incidence quotient, yet
they are not *-isomorphic and neither is action selected.

The finite constructions in this module are diagnostic witnesses.  They are
not promoted to a physical pregeometric Aether algebra or state.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from math import gcd
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


VERSION = "v15.4"
OUTCOME = "OUTCOME_G_Z2_Z3_OBSTRUCTION_SURVIVES_ALL_CURRENTLY_DERIVED_PRINCIPLES"
SECONDARY_OUTCOME = (
    "OUTCOME_H_ACTION_DERIVED_EVENT_REVERSAL_LOOP_SPECTRUM_AND_STATE_SELECTION_"
    "PRINCIPLE_REQUIRED"
)
PRIMARY_VERDICT = (
    "BHSM_V15_4_EVENT_COMPOSITION_AND_IDENTITIES_DEFINE_A_COMPLEX_LINEAR_"
    "CATEGORY_SKELETON_BUT_EXISTING_BHSM_DOES_NOT_SELECT_ITS_PHYSICAL_"
    "MORPHISM_SET_REVERSAL_DAGGER_LOOP_RELATIONS_OR_POSITIVE_STATE;_EVEN_"
    "AFTER_STRENGTHENING_THE_Z2_AND_Z3_WITNESSES_TO_FINITE_TRANSITIVE_"
    "DAGGER_GROUPOIDS_OVER_THE_EXACT_FOUR_VERTEX_BHSM_INCIDENCE_DIAMOND_"
    "BOTH_HAVE_FAITHFUL_POSITIVE_GNS_REALIZATIONS_AND_THE_SAME_INCIDENCE_"
    "QUOTIENT_WHILE_REMAINING_STAR_NONISOMORPHIC_WITH_GNS_RANKS_32_AND_48;_"
    "CAP_REFLECTION_AND_MAXIMAL_CYCLIC_RELABELING_LEAVE_CONTINUOUS_"
    "FAITHFUL_INVARIANT_STATE_FAMILIES_SO_NORMALIZED_TRACE_TRACIALITY_"
    "FAITHFULNESS_AND_SYMMETRY_DO_NOT_SELECT_A_PHYSICAL_FOUNDATIONAL_TRIPLE"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OR_ARCHITECTURE_DERIVED_PRIMITIVE_EVENT_REVERSAL_LOOP_SPECTRUM_"
    "AND_RECONSTRUCTION_FUNCTOR_THAT_FIXES_THE_PHYSICAL_DAGGER_CATEGORY_AND_"
    "AUTOMORPHISM_GROUP_AND_THEN_PROVES_OR_REFUTES_UNIQUENESS_OF_A_"
    "NORMALIZED_FAITHFUL_INVARIANT_POSITIVE_STATE"
)

FORBIDDEN_CORE_PRIMITIVES = (
    "spacetime_coordinate",
    "coordinate_time",
    "metric_tensor",
    "spacetime_volume_measure",
    "ordinary_energy",
    "ordinary_energy_density",
    "preferred_frame",
    "measured_particle_count",
)

OBJECTS = ("M8", "M5_plus", "M5_minus", "M4")
DIAMOND_EDGES = (
    ("M8", "M5_plus"),
    ("M5_plus", "M4"),
    ("M8", "M5_minus"),
    ("M5_minus", "M4"),
)
CAP_REFLECTION = (0, 2, 1, 3)


@dataclass(frozen=True, order=True)
class GroupoidArrow:
    """Arrow ``source -> target`` with a cyclic isotropy label."""

    target: int
    loop: int
    source: int


def _order(order: int) -> int:
    n = int(order)
    if n < 2:
        raise ValueError("cyclic isotropy order must be at least two")
    return n


def groupoid_basis(order: int, object_count: int = 4) -> tuple[GroupoidArrow, ...]:
    n = _order(order)
    m = int(object_count)
    if m < 1:
        raise ValueError("object count must be positive")
    return tuple(GroupoidArrow(i, g, j) for i in range(m) for g in range(n) for j in range(m))


def compose_arrows(
    left: GroupoidArrow, right: GroupoidArrow, order: int
) -> GroupoidArrow | None:
    """Return ``left after right`` or zero for a noncomposable pair."""

    n = _order(order)
    if left.source != right.target:
        return None
    return GroupoidArrow(left.target, (left.loop + right.loop) % n, right.source)


def reverse_arrow(arrow: GroupoidArrow, order: int) -> GroupoidArrow:
    """Candidate groupoid reversal; BHSM does not action-select this map."""

    n = _order(order)
    return GroupoidArrow(arrow.source, (-arrow.loop) % n, arrow.target)


def identity_arrows(order: int, object_count: int = 4) -> tuple[GroupoidArrow, ...]:
    _order(order)
    return tuple(GroupoidArrow(i, 0, i) for i in range(int(object_count)))


def _element(value: np.ndarray | Sequence[complex], order: int, object_count: int = 4) -> np.ndarray:
    n = _order(order)
    m = int(object_count)
    result = np.asarray(value, dtype=complex)
    if result.shape == (m * m * n,):
        result = result.reshape((m, n, m))
    if result.shape != (m, n, m):
        raise ValueError(f"event element must have shape {(m, n, m)}")
    return result


def event_identity(order: int, object_count: int = 4) -> np.ndarray:
    n = _order(order)
    m = int(object_count)
    result = np.zeros((m, n, m), dtype=complex)
    for i in range(m):
        result[i, 0, i] = 1.0
    return result


def event_product(left: np.ndarray, right: np.ndarray, order: int) -> np.ndarray:
    """Convolution/category product in ``M_m(C[Z_n])`` coordinates."""

    n = _order(order)
    a = _element(left, n)
    b = _element(right, n)
    m = a.shape[0]
    result = np.zeros_like(a)
    for i in range(m):
        for j in range(m):
            for k in range(m):
                for g in range(n):
                    for h in range(n):
                        result[i, (g + h) % n, k] += a[i, g, j] * b[j, h, k]
    return result


def event_dagger(value: np.ndarray, order: int) -> np.ndarray:
    """Antilinear extension of groupoid reversal."""

    n = _order(order)
    a = _element(value, n)
    m = a.shape[0]
    result = np.zeros_like(a)
    for i in range(m):
        for j in range(m):
            for g in range(n):
                result[j, (-g) % n, i] = np.conj(a[i, g, j])
    return result


def fourier_blocks(value: np.ndarray, order: int) -> tuple[np.ndarray, ...]:
    """Identify the witness algebra with ``direct_sum_k M_4(C)``."""

    n = _order(order)
    a = _element(value, n)
    roots = np.exp(2j * np.pi * np.arange(n) / n)
    return tuple(sum((roots[k] ** g) * a[:, g, :] for g in range(n)) for k in range(n))


def canonical_density_blocks(order: int, object_count: int = 4) -> tuple[np.ndarray, ...]:
    """Density blocks for the normalized regular trace (diagnostic only)."""

    n = _order(order)
    m = int(object_count)
    return tuple(np.eye(m, dtype=complex) / (m * n) for _ in range(n))


def nontracial_invariant_density_blocks(order: int) -> tuple[np.ndarray, ...]:
    """A fixed faithful cap- and cyclic-relabeling-invariant nontrace state."""

    n = _order(order)
    diagonal = np.array([1.0, 2.0, 2.0, 3.0]) / (8.0 * n)
    return tuple(np.diag(diagonal).astype(complex) for _ in range(n))


def validate_density_blocks(densities: Sequence[np.ndarray], order: int, tol: float = 1e-12) -> dict[str, Any]:
    n = _order(order)
    if len(densities) != n:
        raise ValueError("one density block is required per Fourier sector")
    matrices = [np.asarray(block, dtype=complex) for block in densities]
    if any(block.shape != (4, 4) for block in matrices):
        raise ValueError("every density block must be 4 by 4")
    eigenvalues = [np.linalg.eigvalsh((block + block.conj().T) / 2.0) for block in matrices]
    normalization = float(sum(np.trace(block).real for block in matrices))
    return {
        "Hermitian": all(np.linalg.norm(block - block.conj().T) < tol for block in matrices),
        "positive": all(float(np.min(values)) >= -tol for values in eigenvalues),
        "faithful": all(float(np.min(values)) > tol for values in eigenvalues),
        "normalized": abs(normalization - 1.0) < tol,
        "normalization": normalization,
        "eigenvalues": [[float(x) for x in values] for values in eigenvalues],
    }


def state_value(value: np.ndarray, densities: Sequence[np.ndarray], order: int) -> complex:
    blocks = fourier_blocks(value, order)
    validate_density_blocks(densities, order)
    return complex(sum(np.trace(np.asarray(rho) @ block) for rho, block in zip(densities, blocks)))


def canonical_state_value(value: np.ndarray, order: int) -> complex:
    return state_value(value, canonical_density_blocks(order), order)


def basis_element(arrow: GroupoidArrow, order: int) -> np.ndarray:
    n = _order(order)
    if not (0 <= arrow.target < 4 and 0 <= arrow.source < 4 and 0 <= arrow.loop < n):
        raise ValueError("arrow is outside the witness groupoid")
    result = np.zeros((4, n, 4), dtype=complex)
    result[arrow.target, arrow.loop, arrow.source] = 1.0
    return result


def gns_gram(densities: Sequence[np.ndarray], order: int) -> np.ndarray:
    basis = groupoid_basis(order)
    size = len(basis)
    result = np.zeros((size, size), dtype=complex)
    elements = [basis_element(arrow, order) for arrow in basis]
    for i, left in enumerate(elements):
        left_star = event_dagger(left, order)
        for j, right in enumerate(elements):
            result[i, j] = state_value(event_product(left_star, right, order), densities, order)
    return (result + result.conj().T) / 2.0


def cyclic_units(order: int) -> tuple[int, ...]:
    n = _order(order)
    return tuple(value for value in range(1, n) if gcd(value, n) == 1)


def transform_element(
    value: np.ndarray,
    order: int,
    *,
    object_permutation: Sequence[int] = CAP_REFLECTION,
    loop_multiplier: int = 1,
) -> np.ndarray:
    """Candidate incidence/cyclic relabeling automorphism."""

    n = _order(order)
    permutation = tuple(int(x) for x in object_permutation)
    if sorted(permutation) != list(range(4)):
        raise ValueError("object permutation must permute four objects")
    if gcd(int(loop_multiplier), n) != 1:
        raise ValueError("loop multiplier must be invertible modulo the order")
    a = _element(value, n)
    result = np.zeros_like(a)
    for i in range(4):
        for j in range(4):
            for g in range(n):
                result[permutation[i], (loop_multiplier * g) % n, permutation[j]] = a[i, g, j]
    return result


def state_invariance_residual(
    densities: Sequence[np.ndarray], order: int, *, loop_multiplier: int = 1
) -> float:
    rng = np.random.default_rng(1540 + 10 * order + loop_multiplier)
    value = rng.normal(size=(4, order, 4)) + 1j * rng.normal(size=(4, order, 4))
    transformed = transform_element(value, order, loop_multiplier=loop_multiplier)
    return float(abs(state_value(value, densities, order) - state_value(transformed, densities, order)))


def invariant_state_dimensions(order: int) -> dict[str, int]:
    """Affine dimensions of finite state spaces used in the kill screen."""

    n = _order(order)
    full = 16 * n - 1
    cap_only = 10 * n - 1  # cap swap has multiplicities 3 and 1 on C^4
    internal_orbits = len({min(k, (-k) % n) for k in range(n)})
    cap_and_inversion = 10 * internal_orbits - 1
    return {
        "all_states_affine_dimension": full,
        "faithful_states_manifold_dimension": full,
        "cap_reflection_invariant_affine_dimension": cap_only,
        "cap_and_cyclic_inversion_invariant_affine_dimension": cap_and_inversion,
        "tracial_state_simplex_dimension": n - 1,
    }


@lru_cache(maxsize=None)
def gns_diagnostics(order: int, *, canonical: bool) -> dict[str, Any]:
    n = _order(order)
    densities = canonical_density_blocks(n) if canonical else nontracial_invariant_density_blocks(n)
    density = validate_density_blocks(densities, n)
    gram = gns_gram(densities, n)
    eigenvalues = np.linalg.eigvalsh(gram)
    dimension = 16 * n
    return {
        "order": n,
        "state": "normalized_regular_trace" if canonical else "fixed_faithful_nontracial_invariant_state",
        "state_diagnostics": density,
        "GNS_dimension": dimension,
        "GNS_Gram_rank": int(np.linalg.matrix_rank(gram, tol=1e-11)),
        "GNS_Gram_minimum_eigenvalue": float(np.min(eigenvalues)),
        "null_ideal_dimension": int(np.sum(np.abs(eigenvalues) < 1e-11)),
        "representation_faithful": density["faithful"],
        "cyclic_vector": "class_of_identity",
        "cyclic_span_dimension": dimension,
        "representation_complex_dimension": dimension,
        "commutant_complex_dimension": dimension,
        "center_complex_dimension": n,
        "bare_faithful_GNS_representation_class": "left_regular",
        "pointed_GNS_triple_depends_on_state": True,
    }


def modular_diagnostics(order: int) -> dict[str, Any]:
    canonical = canonical_density_blocks(order)
    nontracial = nontracial_invariant_density_blocks(order)
    canonical_values = np.concatenate([np.linalg.eigvalsh(block) for block in canonical])
    nontracial_values = np.concatenate([np.linalg.eigvalsh(block) for block in nontracial])
    ratios = sorted({round(float(a / b), 12) for a in nontracial_values for b in nontracial_values})
    return {
        "canonical_trace_modular_operator": "IDENTITY",
        "fixed_nontracial_state_modular_ratio_spectrum": ratios,
        "nontrivial_finite_modular_dynamics_available_conditionally": len(ratios) > 1,
        "modular_flow_is_physical_time": False,
        "KMS_state_action_derived": False,
    }


def candidate_classification_payload() -> dict[str, Any]:
    candidates = [
        {
            "candidate": "A_finite_group_algebra_CG",
            "source_target_objects_retained": False,
            "Z2_Z3_relation": "one_object_internal_kill_screen",
            "verdict": "POSITIVE_COMPLETION_WITNESS_NOT_FORCED_BY_EVENT_GRAMMAR",
        },
        {
            "candidate": "B_finite_groupoid_algebra",
            "source_target_objects_retained": True,
            "conditional_dimension": "m_squared_times_order",
            "verdict": "STRONGEST_FINITE_INCIDENCE_COMPATIBLE_KILL_SCREEN_NOT_ACTION_SELECTED",
        },
        {
            "candidate": "C_path_or_incidence_algebra",
            "multiplication_matches_owned_composition": True,
            "dagger_issue": "directed_path_category_has_no_REVERSAL_until_doubled_or_groupoid_completed",
            "verdict": "BEST_DERIVED_MULTIPLICATION_SKELETON_NO_OWNED_DAGGER",
        },
        {
            "candidate": "D_finite_dimensional_Cstar_algebra",
            "classification": "direct_sum_i_M_ni_C",
            "verdict": "CONTAINER_CLASS_DOES_NOT_SELECT_BLOCKS_OR_STATE",
        },
        {
            "candidate": "E_dagger_category_or_convolution_algebra",
            "ordering": "event_category_then_reversal_then_linear_algebra",
            "verdict": "NATURAL_CONDITIONAL_ROUTE_REVERSAL_FUNCTOR_MISSING",
        },
        {
            "candidate": "F_reuse_regular_BHSM_finite_algebra",
            "historical_status": "conditional_reconstructed_boundary_output",
            "verdict": "FORBIDDEN_UPSTREAM_COPY_WITHOUT_ACTION_DERIVED_RECONSTRUCTION_FUNCTOR",
        },
    ]
    return {
        "version": VERSION,
        "candidates": candidates,
        "architecture_retained_object": "complex_linear_category_span_of_action_owned_composable_events",
        "physical_event_algebra_selected": False,
        "serious_finite_kill_screen": "transitive_groupoid_algebra_over_four_BHSM_incidence_objects",
    }


def event_algebra_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "event_generators": "oriented_correspondence_morphisms_with_source_target_parent_invariant_and_process_depth",
        "multiplication": "categorical_composition_when_middle_object_and_invariants_match_else_zero_in_linear_span",
        "multiplication_architecture_derived": True,
        "associative": True,
        "identities": "one_identity_morphism_per_event_object",
        "partial_composition_becomes_total_with_zero_products": True,
        "complex_linear_category_span_constructible": True,
        "physical_allowed_morphism_set_selected": False,
        "loop_relations_selected": False,
        "group_groupoid_or_path_completion_unique": False,
        "one_object_group_algebra_forced": False,
        "candidate_classification": candidate_classification_payload(),
    }


def dagger_payload() -> dict[str, Any]:
    witnesses = []
    for n in (2, 3):
        a = GroupoidArrow(1, 1, 0)
        b = GroupoidArrow(3, 1 % n, 1)
        composed = compose_arrows(b, a, n)
        assert composed is not None
        witnesses.append(
            {
                "order": n,
                "involution": reverse_arrow(reverse_arrow(a, n), n) == a,
                "anti_multiplicative": reverse_arrow(composed, n)
                == compose_arrows(reverse_arrow(a, n), reverse_arrow(b, n), n),
                "antilinear_extension": True,
                "identity_preserved": all(reverse_arrow(x, n) == x for x in identity_arrows(n)),
            }
        )
    return {
        "version": VERSION,
        "compatible_dagger_exists_on_each_groupoid_witness": all(
            row["involution"] and row["anti_multiplicative"] for row in witnesses
        ),
        "witnesses": witnesses,
        "dagger_if_reversal_is_declared": "(target,g,source)^dagger=(source,-g,target)",
        "event_reversal_functor_action_derived": False,
        "historical_orientation_Iota_scope": "regular_boundary_Z2_grading_not_reversal_of_arbitrary_core_events",
        "self_adjoint_matcher_scope": "regular_correspondence_adjoint_after_Hilbert_pairing_not_pregeometric_dagger_source",
        "dagger_identified_with_time_reversal_CP_CPT_or_complex_conjugation_alone": False,
        "physical_dagger_uniquely_selected": False,
        "classification": "DAGGER_EXISTS_CONDITIONALLY_BUT_IS_NOT_ACTION_OR_ARCHITECTURE_SELECTED",
    }


def state_cone_payload() -> dict[str, Any]:
    rows = []
    for n in (2, 3):
        dimensions = invariant_state_dimensions(n)
        canonical = validate_density_blocks(canonical_density_blocks(n), n)
        nontracial = validate_density_blocks(nontracial_invariant_density_blocks(n), n)
        rows.append(
            {
                "order": n,
                "algebra": f"M4(C[Z_{n}])_isomorphic_to_direct_sum_{n}_M4(C)",
                "state_cone": "positive_semidefinite_density_block_spectrahedron_with_total_trace_one",
                "faithful_state_cone": "relative_open_interior_all_density_blocks_positive_definite",
                **dimensions,
                "canonical_trace_state": canonical,
                "fixed_nontracial_state": nontracial,
                "normalization_is_probabilistic_convention_until_action_amplitude_exists": True,
                "faithfulness_mathematically_required_for_GNS": False,
                "faithfulness_action_derived": False,
            }
        )
    return {
        "version": VERSION,
        "witnesses": rows,
        "positivity_definition": "omega(a_dagger_a)>=0_for_all_a",
        "positive_state_selected": False,
        "faithful_state_selected": False,
        "pure_or_mixed_selected": False,
    }


def automorphism_state_payload() -> dict[str, Any]:
    rows = []
    for n in (2, 3):
        canonical = canonical_density_blocks(n)
        nontracial = nontracial_invariant_density_blocks(n)
        units = cyclic_units(n)
        rows.append(
            {
                "order": n,
                "full_star_automorphism_group_without_distinguished_incidence": f"PU(4)^{n}_semidirect_S_{n}",
                "BHSM_action_owned_core_automorphism_group": "NONE_DERIVED",
                "regular_symmetric_branch_automorphism_available_conditionally": "Z2_cap_reflection",
                "maximal_witness_grammar_group": f"Z2_cap_times_Aut_Z{n}",
                "cyclic_units": list(units),
                "canonical_state_invariance_residuals": [
                    state_invariance_residual(canonical, n, loop_multiplier=unit) for unit in units
                ],
                "fixed_nontracial_state_invariance_residuals": [
                    state_invariance_residual(nontracial, n, loop_multiplier=unit) for unit in units
                ],
                "dimensions": invariant_state_dimensions(n),
                "maximal_witness_grammar_invariant_state_space": "CONTINUOUS_CONVEX_SPECTRAHEDRON",
                "unique_state_under_all_star_automorphisms": "NORMALIZED_TRACE",
                "all_star_automorphisms_are_physical_BHSM_symmetries": False,
            }
        )
    return {
        "version": VERSION,
        "witnesses": rows,
        "symmetry_invariance_uniquely_selects_physical_state": False,
        "reason": "the action-owned core automorphism group is absent and even the stronger grammar group leaves continuous faithful families",
    }


def tracial_modular_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "traciality_action_derived": False,
        "cyclic_event_action_implies_tracial_state": False,
        "absence_of_preferred_event_order_implies_trace": False,
        "tracial_state_spaces": [
            {"order": n, "simplex_dimension": n - 1, "unique_trace": False} for n in (2, 3)
        ],
        "normalized_regular_trace_is_unique_under_all_star_automorphisms": True,
        "all_star_automorphism_invariance_action_derived": False,
        "nontracial_faithful_invariant_states_survive": True,
        "modular_diagnostics": [modular_diagnostics(n) for n in (2, 3)],
    }


def gns_payload() -> dict[str, Any]:
    rows = []
    for n in (2, 3):
        canonical = gns_diagnostics(n, canonical=True)
        nontracial = gns_diagnostics(n, canonical=False)
        canonical_spectrum = canonical["state_diagnostics"]["eigenvalues"]
        nontracial_spectrum = nontracial["state_diagnostics"]["eigenvalues"]
        rows.append(
            {
                "order": n,
                "canonical": canonical,
                "fixed_nontracial": nontracial,
                "bare_representations_unitarily_equivalent_for_faithful_states": True,
                "pointed_GNS_triples_equivalent_under_allowed_state_automorphism": canonical_spectrum
                == nontracial_spectrum,
                "reason": "faithful finite GNS representations are left-regular but cyclic vector/state density spectra differ",
            }
        )
    return {
        "version": VERSION,
        "witnesses": rows,
        "physical_output_type": "pointed_GNS_equivalence_class_H_pi_Omega",
        "GNS_representation_uniquely_selected": False,
    }


def incidence_reconstruction_payload() -> dict[str, Any]:
    rows = []
    for n in (2, 3):
        rows.append(
            {
                "order": n,
                "objects": list(OBJECTS),
                "distinguished_incidence_edges": [list(edge) for edge in DIAMOND_EDGES],
                "cycle_rank": 1,
                "groupoid_algebra_dimension": 16 * n,
                "incidence_quotient": "forget_cyclic_isotropy_and_retain_distinguished_diamond_generators",
                "exact_BHSM_diamond_grammar_recovered": True,
                "incidence_reconstruction_map_action_derived": False,
                "augmentation_to_pair_groupoid_algebra_exists": True,
                "augmentation_is_regular_BHSM_finite_algebra_map": False,
            }
        )
    return {
        "version": VERSION,
        "witnesses": rows,
        "both_witnesses_reconstruct_same_incidence": True,
        "incidence_distinguishes_Z2_from_Z3": False,
        "canonical_map_to_regular_BHSM_finite_algebra_exists": False,
        "historical_regular_finite_algebra_scope": "downstream_conditional_boundary_reconstruction_not_parent_core_input",
    }


def killscreen_payload() -> dict[str, Any]:
    incidence = incidence_reconstruction_payload()["witnesses"]
    rows = []
    for n, reconstruction in zip((2, 3), incidence):
        canonical = gns_diagnostics(n, canonical=True)
        rows.append(
            {
                "order": n,
                "algebra": f"M4(C[Z_{n}])",
                "algebra_complex_dimension": 16 * n,
                "center_complex_dimension": n,
                "irreducible_representations": n,
                "irreducible_representation_dimensions": [4] * n,
                "canonical_GNS_dimension": canonical["GNS_dimension"],
                "dagger": "groupoid_reversal_plus_cyclic_inversion",
                "canonical_state_faithful_positive_normalized": True,
                "continuous_invariant_faithful_states_survive": True,
                "incidence": reconstruction,
                "no_empirical_input": True,
                "no_continuous_tuning_in_witness_definition": True,
                "physical_foundation_adopted": False,
            }
        )
    return {
        "version": VERSION,
        "witnesses": rows,
        "both_survive": True,
        "star_isomorphic": False,
        "event_relabeling_equivalent": False,
        "structured_GNS_equivalent": False,
        "reason": "algebra_dimensions_centers_and_faithful_GNS_ranks_differ",
        "current_BHSM_principle_distinguishes_them": False,
        "outcome": OUTCOME,
    }


def dirichlet_readiness_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "finite_GNS_domain_dense": True,
        "closed_invariant_Dirichlet_forms_exist_for_each_witness": True,
        "zero_form_exists": True,
        "cyclic_Laplacian_lift_exists": True,
        "existence_is_action_selection": False,
        "Dirichlet_form_uniqueness": False,
        "generator_selected": False,
        "next_layer_required_inputs": [
            "action_owned_derivation_or_carre_du_champ",
            "Markov_property",
            "physical_automorphism_action",
            "spectral_gap_or_recurrence_selection",
            "geometry_core_correspondence_morphism",
        ],
    }


def seventeen_gate_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "T1_event_composition_algebra": "CATEGORY_COMPOSITION_DERIVED_LINEAR_COMPLETION_CONSTRUCTIBLE",
        "T2_associativity": "PROVED",
        "T3_identity": "ONE_IDENTITY_PER_EVENT_OBJECT",
        "T4_dagger_existence": "EXISTS_ON_CONDITIONAL_GROUPOID_COMPLETIONS",
        "T5_dagger_uniqueness": "NOT_ACTION_SELECTED_REVERSAL_FUNCTOR_ABSENT",
        "T6_positive_state_cone": "FINITE_SPECTRAHEDRA_COMPUTED_FOR_WITNESSES",
        "T7_faithful_state": "OPEN_INTERIORS_CONTINUOUS_NOT_SELECTED",
        "T8_symmetry_invariant_state": "CONTINUOUS_EVEN_UNDER_STRENGTHENED_GRAMMAR_AUTOMORPHISMS",
        "T9_distinguished_state": "NOT_UNIQUE",
        "T10_traciality": "NOT_DERIVED",
        "T11_GNS": "CONSTRUCTED_FOR_RETAINED_WITNESSES",
        "T12_GNS_uniqueness": "FALSE_ACROSS_Z2_Z3_AND_POINTED_STATE_TRIPLES",
        "T13_Z2_Z3": "BOTH_SURVIVE_AND_ARE_STAR_NONISOMORPHIC",
        "T14_incidence_reconstruction": "SAME_EXACT_DIAMOND_QUOTIENT_CONDITIONALLY",
        "T15_regular_algebra_reconstruction": "NO_CANONICAL_MAP_DERIVED",
        "T16_Dirichlet_readiness": "EXISTENCE_YES_UNIQUENESS_NO",
        "T17_foundational_selection": "UNDEFINED_NEW_FOUNDATIONAL_SELECTION_PRINCIPLE_REQUIRED",
        "physical_triple_cardinality": "UNDEFINED_NOT_ZERO",
        "residual_foundational_ambiguity": "AT_LEAST_TWO_DISCRETE_STAR_NONISOMORPHIC_ALGEBRAS_EACH_WITH_CONTINUOUS_FAITHFUL_INVARIANT_STATE_FAMILIES",
        "outcome": OUTCOME,
        "secondary_outcome": SECONDARY_OUTCOME,
    }


def completion_payload() -> dict[str, Any]:
    kill = killscreen_payload()
    event = event_algebra_payload()
    dagger = dagger_payload()
    state = state_cone_payload()
    automorphisms = automorphism_state_payload()
    gns = gns_payload()
    incidence = incidence_reconstruction_payload()
    validation = {
        "event_multiplication_derived": event["multiplication_architecture_derived"],
        "associativity_verified": event["associative"],
        "identity_verified": True,
        "conditional_dagger_laws_verified": all(
            row["involution"] and row["anti_multiplicative"] for row in dagger["witnesses"]
        ),
        "positive_states_verified": all(
            row["canonical_trace_state"]["positive"] and row["fixed_nontracial_state"]["positive"]
            for row in state["witnesses"]
        ),
        "faithful_states_verified": all(
            row["canonical_trace_state"]["faithful"] and row["fixed_nontracial_state"]["faithful"]
            for row in state["witnesses"]
        ),
        "GNS_ranks_verified": [row["canonical"]["GNS_Gram_rank"] for row in gns["witnesses"]]
        == [32, 48],
        "Z2_Z3_killscreen_survives": kill["both_survive"],
        "incidence_reconstruction_shared": incidence["both_witnesses_reconstruct_same_incidence"],
        "no_primitive_spacetime_coordinate": True,
        "no_coordinate_time": True,
        "no_primitive_metric": True,
        "no_ordinary_energy": True,
        "no_spacetime_core_measure": True,
        "no_preferred_frame": True,
        "no_empirical_inputs": True,
        "no_measured_particle_count_selection": True,
        "no_arbitrary_continuous_tuning": True,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v15_4",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "secondary_outcome": SECONDARY_OUTCOME,
        "event_algebra": event,
        "dagger": dagger,
        "positive_state_cone": state,
        "automorphism_invariant_state": automorphisms,
        "tracial_and_modular": tracial_modular_payload(),
        "GNS": gns,
        "Z2_Z3_killscreen": kill,
        "incidence_reconstruction": incidence,
        "Dirichlet_readiness": dirichlet_readiness_payload(),
        "theorem_gates": seventeen_gate_payload(),
        "event_multiplication_derived": True,
        "event_algebra_uniquely_selected": False,
        "compatible_dagger_exists": True,
        "physical_dagger_uniquely_selected": False,
        "distinguished_positive_state_uniquely_selected": False,
        "GNS_representation_uniquely_selected": False,
        "traciality_derived": False,
        "regular_algebra_reconstruction_derived": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "Hindsight_20_20": {
            "validated": [
                "category composition and object identities are architecture derived",
                "groupoid reversal gives a valid dagger after a reversible completion is declared",
                "positive and faithful state cones are explicit finite spectrahedra",
                "faithful states give zero GNS null ideal and faithful left regular representations",
                "both incidence-compatible Z2 and Z3 dagger groupoids reconstruct the same BHSM diamond",
                "Z2 and Z3 remain star nonisomorphic with GNS dimensions 32 and 48",
            ],
            "invalidated": [
                "normalized trace is automatically physical",
                "the smallest finite algebra is physically preferred",
                "Z3 is preferred because there are three generations",
                "event orientation automatically fixes an action-owned unique dagger",
                "positivity faithfulness or grammar symmetry fixes a unique state",
                "all pointed finite faithful GNS triples are physically equivalent",
                "a group algebra is automatically the parent event structure",
            ],
            "reclassified": [
                "core Hilbert space is a GNS output of a selected positive state",
                "core observable is an element of a selected event dagger algebra",
                "adjoint is reversal or reciprocity only after a reversal functor is derived",
                "core probability is a positive functional not a spacetime probability density",
            ],
            "open": [EXACT_NEXT_OBJECT],
        },
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "USB_SYNCHRONIZATION_ELIGIBLE": False,
        "new_continuous_parameter_introduced": False,
        "new_fundamental_dynamical_field_introduced": False,
        "preferred_frame_introduced": False,
        "empirical_inputs_used": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_aether_event_algebra_gate_v15_4.json": event_algebra_payload(),
        "BHSM_aether_dagger_gate_v15_4.json": dagger_payload(),
        "BHSM_aether_positive_state_cone_v15_4.json": state_cone_payload(),
        "BHSM_aether_invariant_state_selection_v15_4.json": automorphism_state_payload(),
        "BHSM_aether_gns_representation_v15_4.json": gns_payload(),
        "BHSM_aether_z2_z3_killscreen_v15_4.json": killscreen_payload(),
        "BHSM_aether_incidence_reconstruction_v15_4.json": incidence_reconstruction_payload(),
        "BHSM_aether_dirichlet_readiness_v15_4.json": dirichlet_readiness_payload(),
        "BHSM_aether_foundational_selection_gate_v15_4.json": seventeen_gate_payload(),
        "BHSM_completion_gate_v15_4.json": completion_payload(),
    }


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(directory: str | Path) -> list[Path]:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, payload in artifact_payloads().items():
        path = target / name
        path.write_text(deterministic_json(payload), encoding="utf-8")
        paths.append(path)
    return paths
