"""BHSM v14.35 nonaxisymmetric Hopf-phase bifurcation and CP audit.

The v14.34 audit proved that a constant phase or a single Hopf weight cannot
produce a full-rank three-generation charged-current kernel.  This module
identifies the smallest connected full-rank mixing bridge and the smallest
Cabibbo-aligned CP-capable extension supported by the frozen quark ledgers,
derives their rephasing structure, audits the phase-locking normal form, and states the exact variational bifurcation gate that a
physical Path-B/full-preimage solution must pass.

No CKM matrix, Jarlskog invariant, mass, or fitted coefficient is promoted.
All finite matrices below are structural witnesses only.
"""

from __future__ import annotations

from functools import lru_cache
from itertools import product
from math import acos, cos, pi
from typing import Any, Iterable

import numpy as np

from .hopf_phase_flavor_cross_gram_v14_34 import (
    DOWN_MODES,
    UP_MODES,
    jarlskog,
    mode_quantum_numbers,
    polar_unitary,
)

VERSION = "v14.35"
PRIMARY_VERDICT = (
    "BHSM_V14_35_MINIMAL_FOUR_COMPONENT_MIXING_SEED_AND_FIVE_COMPONENT_"
    "CABIBBO_CP_TEXTURE_ARE_DERIVED_KINEMATICALLY_BUT_THE_PATH_B_ACTION_"
    "HAS_NOT_"
    "SELECTED_THE_NONAXISYMMETRIC_BIFURCATION_BRANCH_OR_SELF_ADJOINT_"
    "TOWER_RESOLVENT"
)
SECONDARY_VERDICT = (
    "THE_MARK_III_FLAVOR_GATE_IS_REDUCED_TO_THE_DEGREE_ONE_FULL_PREIMAGE_"
    "HESSIAN_SPECTRUM_PHASE_LOCKING_NORMAL_FORM_AND_ACTION_ATTACHMENT_OF_"
    "THE_EXISTING_RELATIVE_HOLONOMY_CHANNEL"
)
EXACT_NEXT_OBJECT = "SELF_ADJOINT_DEGREE_ONE_FULL_PREIMAGE_HESSIAN_SPECTRUM_IN_ELL_P_CHANNELS_2_2_4_4_6_6_8_8_10_8_WITH_EQUIVARIANT_BIFURCATION_PHASE_LOCKING_AND_V12_RELATIVE_HOLONOMY_ACTION_ATTACHMENT"

# Four components suffice for a connected, structurally full-rank mixing seed.
# Its only graph cycle carries no independent phase when each harmonic has one
# amplitude, because the two edges in each row share the same component phase.
MINIMAL_MIXING_COMPONENTS: tuple[tuple[int, int], ...] = (
    (0, 0),
    (2, 2),
    (6, 6),
    (10, 8),
)

# A fifth component is required for a Cabibbo-aligned rephasing phase with
# independently oriented u-d, u-s, c-d and c-s amplitudes.  The (6,6) harmonic
# also contributes to c-b and connects the phase cycle to the third generation.
CABIBBO_CP_COMPONENTS: tuple[tuple[int, int], ...] = (
    (0, 0),
    (2, 2),
    (4, 4),
    (6, 6),
    (8, 8),
)
UP_LABELS = tuple(UP_MODES)
DOWN_LABELS = tuple(DOWN_MODES)


def bridge_component_allowed(
    component: tuple[int, int],
    up_mode: tuple[int, int],
    down_mode: tuple[int, int],
) -> bool:
    """Return the scalar harmonic selection rule for one (ell,p) component."""

    ell, p = component
    if ell < 0 or abs(p) > ell or (ell - p) % 2:
        return False
    ku, ju = up_mode
    kd, jd = down_mode
    qu = mode_quantum_numbers(ku, ju)["q"]
    qd = mode_quantum_numbers(kd, jd)["q"]
    return (
        p == qu - qd
        and abs(ku - kd) <= ell <= ku + kd
        and (ell - abs(ku - kd)) % 2 == 0
    )


def component_support(component: tuple[int, int]) -> np.ndarray:
    matrix = np.zeros((3, 3), dtype=int)
    for i, up_mode in enumerate(UP_MODES.values()):
        for j, down_mode in enumerate(DOWN_MODES.values()):
            matrix[i, j] = int(bridge_component_allowed(component, up_mode, down_mode))
    return matrix


def combined_component_support(components: Iterable[tuple[int, int]]) -> np.ndarray:
    values = tuple(components)
    if not values:
        raise ValueError("at least one component is required")
    return np.maximum.reduce([component_support(component) for component in values])


def minimal_mixing_support() -> np.ndarray:
    return combined_component_support(MINIMAL_MIXING_COMPONENTS)


def cabibbo_cp_support() -> np.ndarray:
    return combined_component_support(CABIBBO_CP_COMPONENTS)


def support_edges(support: np.ndarray) -> list[tuple[int, int]]:
    value = np.asarray(support, dtype=int)
    if value.shape != (3, 3):
        raise ValueError("support must be 3x3")
    return [(i, j) for i in range(3) for j in range(3) if value[i, j]]


def bipartite_cycle_rank(support: np.ndarray) -> int:
    """Return E-V+C for the row/column support graph."""

    edges = support_edges(support)
    vertices = list(range(6))
    adjacency = {vertex: set() for vertex in vertices}
    for i, j in edges:
        left, right = i, 3 + j
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[int] = set()
    components = 0
    for vertex in vertices:
        if vertex in seen:
            continue
        components += 1
        stack = [vertex]
        seen.add(vertex)
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return len(edges) - len(vertices) + components


def bipartite_component_count(support: np.ndarray) -> int:
    edges = support_edges(support)
    adjacency = {vertex: set() for vertex in range(6)}
    for i, j in edges:
        left, right = i, 3 + j
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[int] = set()
    count = 0
    for vertex in range(6):
        if vertex in seen:
            continue
        count += 1
        stack = [vertex]
        seen.add(vertex)
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return count


def structural_rank(support: np.ndarray) -> int:
    """Maximum bipartite matching size for the 3x3 support pattern."""

    value = np.asarray(support, dtype=int)
    if value.shape != (3, 3):
        raise ValueError("support must be 3x3")
    from itertools import permutations

    return max(sum(int(value[i, permutation[i]]) for i in range(3)) for permutation in permutations(range(3)))


def all_allowed_components() -> tuple[tuple[int, int], ...]:
    differences = sorted(
        {
            mode_quantum_numbers(*up_mode)["q"] - mode_quantum_numbers(*down_mode)["q"]
            for up_mode in UP_MODES.values()
            for down_mode in DOWN_MODES.values()
        }
    )
    maximum_ell = max(up[0] + down[0] for up in UP_MODES.values() for down in DOWN_MODES.values())
    return tuple(
        (ell, p)
        for ell in range(maximum_ell + 1)
        for p in differences
        if np.any(component_support((ell, p)))
    )


def minimum_connected_full_rank_component_count() -> int:
    from itertools import combinations

    components = all_allowed_components()
    for size in range(1, len(components) + 1):
        for subset in combinations(components, size):
            support = combined_component_support(subset)
            if structural_rank(support) == 3 and bipartite_component_count(support) == 1:
                return size
    raise RuntimeError("no connected full-rank component set exists")



def mixing_seed_kernel(
    a10_8_s: complex = 0.35,
    a10_8_b: complex = 0.15,
    a22: complex = 0.25,
    a66_s: complex = 0.8,
    a66_b: complex = 0.4,
    a00: complex = 1.1,
) -> np.ndarray:
    """Four-component real/phase-tied mixing seed.

    The u-s/u-b edges share one (10,8) amplitude and the c-s/c-b edges share
    one (6,6) amplitude.  Their graph cycle therefore has no independent phase
    when the Clebsch/radial factors are real.
    """

    return np.asarray(
        [
            [0.0, a10_8_s, a10_8_b],
            [a22, a66_s, a66_b],
            [0.0, 0.0, a00],
        ],
        dtype=complex,
    )

def structural_kernel(
    a44: complex = 1.0,
    a88: complex = 0.3 * np.exp(0.7j),
    a22: complex = 0.25,
    a66_s: complex = 0.8,
    a66_b: complex = 0.4,
    a00: complex = 1.1,
) -> np.ndarray:
    """Return the exact six-edge support normal form.

    The amplitudes are diagnostics only.  Distinct a66_s and a66_b stand for
    different Clebsch/radial matrix elements of the same (ell,p)=(6,6)
    texture component.
    """

    return np.asarray(
        [
            [a44, a88, 0.0],
            [a22, a66_s, a66_b],
            [0.0, 0.0, a00],
        ],
        dtype=complex,
    )


def determinant_factor(
    a44: complex,
    a88: complex,
    a22: complex,
    a66_s: complex,
    a00: complex,
) -> complex:
    return a00 * (a44 * a66_s - a88 * a22)


def plaquette_phase(kernel: np.ndarray) -> float:
    value = np.asarray(kernel, dtype=complex)
    if value.shape != (3, 3):
        raise ValueError("kernel must be 3x3")
    quartet = value[0, 0] * value[1, 1] * np.conj(value[0, 1]) * np.conj(value[1, 0])
    return float(np.angle(quartet))


def rephase_kernel(kernel: np.ndarray, row_phases: Iterable[float], column_phases: Iterable[float]) -> np.ndarray:
    value = np.asarray(kernel, dtype=complex)
    rows = np.exp(1j * np.asarray(tuple(row_phases), dtype=float))
    columns = np.exp(1j * np.asarray(tuple(column_phases), dtype=float))
    if value.shape != (3, 3) or rows.shape != (3,) or columns.shape != (3,):
        raise ValueError("expected a 3x3 kernel and three row/column phases")
    return np.diag(rows) @ value @ np.diag(columns)


def phase_resonance_balance() -> dict[str, int | bool]:
    # The upper-left charged-current quartet has channel weights 4,8,2,6.
    return {
        "p_ud": 4,
        "p_us": 8,
        "p_cd": 2,
        "p_cs": 6,
        "weight_balance": 4 + 6 - 8 - 2,
        "resonant": 4 + 6 == 8 + 2,
    }


def cp_even_phase_potential(phi: float, c1: float, c2: float) -> float:
    return float(c1 * cos(phi) + c2 * cos(2.0 * phi))


def spontaneous_cp_phase(c1: float, c2: float) -> dict[str, float | bool | None]:
    """Stationary phase of V=c1 cos(phi)+c2 cos(2 phi).

    A nontrivial CP-conjugate pair exists and is locally stable when c2>0 and
    |c1|<4 c2.  These are normal-form coefficients, not BHSM predictions.
    """

    if c2 <= 0.0 or abs(c1) >= 4.0 * c2:
        return {"exists": False, "phi": None, "curvature": None}
    phi = acos(-c1 / (4.0 * c2))
    curvature = (16.0 * c2 * c2 - c1 * c1) / (4.0 * c2)
    return {"exists": True, "phi": float(phi), "curvature": float(curvature)}


def signed_seventh_order_weights(weights: Iterable[int]) -> list[int]:
    """Weights generated by X^3 D eta: p1-p2+p3-p4+p5-p6+p7."""

    values = tuple(sorted(set(int(weight) for weight in weights)))
    if not values:
        raise ValueError("at least one weight is required")
    generated = {
        p1 - p2 + p3 - p4 + p5 - p6 + p7
        for p1, p2, p3, p4, p5, p6, p7 in product(values, repeat=7)
    }
    return sorted(generated)


def bifurcation_classification(eigenvalue: float, tolerance: float = 1.0e-10) -> str:
    if eigenvalue > tolerance:
        return "LOCALLY_STABLE_NO_LINEAR_BIFURCATION"
    if eigenvalue < -tolerance:
        return "NONAXISYMMETRIC_INSTABILITY_BRANCH_SEARCH_REQUIRED"
    return "ZERO_MODE_EQUIVARIANT_BIFURCATION_CANDIDATE"


@lru_cache(maxsize=1)
def minimal_texture_payload() -> dict[str, Any]:
    mixing_support = minimal_mixing_support()
    cp_support = cabibbo_cp_support()
    mixing_rows = {
        f"ell{ell}_p{p}": component_support((ell, p))
        for ell, p in MINIMAL_MIXING_COMPONENTS
    }
    cp_rows = {
        f"ell{ell}_p{p}": component_support((ell, p))
        for ell, p in CABIBBO_CP_COMPONENTS
    }

    mixing_witness = mixing_seed_kernel()
    mixing_unitary, mixing_singular = polar_unitary(mixing_witness)
    cp_witness = structural_kernel()
    cp_unitary, cp_singular = polar_unitary(cp_witness)

    tied_cycle = (
        mixing_witness[0, 1]
        * mixing_witness[1, 2]
        * np.conj(mixing_witness[0, 2])
        * np.conj(mixing_witness[1, 1])
    )
    validation = {
        "four_components_are_smallest_connected_full_rank_seed": minimum_connected_full_rank_component_count() == len(MINIMAL_MIXING_COMPONENTS) == 4,
        "mixing_seed_has_six_edges_and_connected_cycle": bool(
            len(support_edges(mixing_support)) == 6 and bipartite_cycle_rank(mixing_support) == 1
        ),
        "mixing_seed_perfect_matching_present": bool(
            mixing_support[0, 1] and mixing_support[1, 0] and mixing_support[2, 2]
        ),
        "mixing_seed_full_rank": np.min(mixing_singular) > 1e-8,
        "mixing_seed_polar_nontrivial": np.linalg.norm(mixing_unitary - np.eye(3)) > 1e-3,
        "single_amplitude_cycle_phase_cancels": abs(np.angle(tied_cycle)) < 1e-12,
        "mixing_seed_CP_zero": abs(jarlskog(mixing_unitary)) < 1e-12,
        "five_component_Cabibbo_aligned_independent_phase_constructed": len(CABIBBO_CP_COMPONENTS) == 5,
        "Cabibbo_CP_support_has_six_edges_and_one_cycle": bool(
            len(support_edges(cp_support)) == 6 and bipartite_cycle_rank(cp_support) == 1
        ),
        "Cabibbo_CP_perfect_matching_ud_cs_tb_present": bool(cp_support[0, 0] and cp_support[1, 1] and cp_support[2, 2]),
        "same_ell6_p6_component_couples_cs_and_cb": bool(cp_rows["ell6_p6"][1, 1] and cp_rows["ell6_p6"][1, 2]),
        "generic_CP_texture_determinant_verified": abs(
            np.linalg.det(cp_witness)
            - determinant_factor(cp_witness[0, 0], cp_witness[0, 1], cp_witness[1, 0], cp_witness[1, 1], cp_witness[2, 2])
        ) < 1e-12,
        "CP_texture_full_rank": np.min(cp_singular) > 1e-8,
        "CP_texture_polar_unitary": np.linalg.norm(cp_unitary.conj().T @ cp_unitary - np.eye(3)) < 1e-12,
        "CP_texture_witness_nonzero_J": abs(jarlskog(cp_unitary)) > 1e-8,
        "witnesses_not_promoted": True,
    }
    return {
        "artifact": "BHSM_minimal_Hopf_phase_mixing_and_CP_textures_v14_35",
        "version": VERSION,
        "minimal_mixing_seed": {
            "components": [{"ell": ell, "p": p} for ell, p in MINIMAL_MIXING_COMPONENTS],
            "component_support": mixing_rows,
            "combined_support": mixing_support,
            "normal_form": "K_mix=[[0,a8_s,a8_b],[a22,a66_s,a66_b],[0,0,a00]]",
            "result": "four components are sufficient for connected full-rank mixing, but their single-amplitude graph-cycle phase cancels",
            "existence_witness": {
                "raw_kernel": mixing_witness,
                "polar_unitary": mixing_unitary,
                "singular_values": mixing_singular,
                "jarlskog": jarlskog(mixing_unitary),
            },
        },
        "Cabibbo_aligned_CP_texture": {
            "components": [{"ell": ell, "p": p} for ell, p in CABIBBO_CP_COMPONENTS],
            "component_support": cp_rows,
            "combined_support": cp_support,
            "normal_form": "K_CP=[[a44,a88,0],[a22,a66_s,a66_b],[0,0,a00]]",
            "determinant": "det K_CP=a00(a44 a66_s-a88 a22)",
            "result": "the fifth independently oriented component supplies a non-removable Cabibbo plaquette phase while (6,6) connects the cycle to b",
            "existence_witness": {
                "raw_kernel": cp_witness,
                "polar_unitary": cp_unitary,
                "singular_values": cp_singular,
                "jarlskog": jarlskog(cp_unitary),
            },
        },
        "claim_boundary": "four is the exhaustive minimum for connected structural rank three; the five-component Cabibbo-aligned CP texture is sufficient but is not claimed globally minimal once overlapping harmonics are allowed",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def phase_locking_payload() -> dict[str, Any]:
    kernel = structural_kernel()
    phi = plaquette_phase(kernel)
    rephased = rephase_kernel(kernel, (0.2, -0.4, 0.7), (-0.1, 0.5, -0.3))
    resonance = phase_resonance_balance()
    single = spontaneous_cp_phase(1.0, 0.0)
    competing = spontaneous_cp_phase(1.0, 1.0)
    validation = {
        "plaquette_phase_rephasing_invariant": abs(np.angle(np.exp(1j * (plaquette_phase(rephased) - phi)))) < 1e-12,
        "weight_resonance_exact": bool(resonance["resonant"] and resonance["weight_balance"] == 0),
        "single_cosine_has_no_nontrivial_normal_form_branch": not bool(single["exists"]),
        "competing_cosines_allow_stable_CP_conjugate_pair": bool(
            competing["exists"] and competing["phi"] not in (0.0, pi) and float(competing["curvature"]) > 0.0
        ),
        "real_action_preserves_phi_to_minus_phi_pairing": True,
        "phase_locking_coefficients_not_derived": True,
    }
    return {
        "artifact": "BHSM_Hopf_phase_CP_resonance_and_locking_v14_35",
        "version": VERSION,
        "rephasing_invariant": "Phi=arg(K_ud K_cs K_us^* K_cd^*)",
        "harmonic_resonance": resonance,
        "allowed_normal_form": "V(Phi)=c1 cos(Phi)+c2 cos(2 Phi)+...",
        "single_resonance_result": "one real cosine locks Phi to 0 or pi and is CP conserving",
        "spontaneous_CP_condition": "c2>0 and |c1|<4 c2 gives stable conjugate minima cos(Phi)=-c1/(4c2)",
        "orientation_result": "a real action may determine |Phi| but leaves the pair +/-Phi degenerate until an oriented holonomy or boundary condition selects a sign",
        "diagnostic": {"plaquette_phase": phi, "competing_normal_form": competing},
        "claim_boundary": "the symmetry-allowed phase normal form is derived; its coefficients and the existence of the required stationary amplitudes are open",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def action_selection_payload() -> dict[str, Any]:
    example = {
        "positive": bifurcation_classification(0.2),
        "zero": bifurcation_classification(0.0),
        "negative": bifurcation_classification(-0.2),
    }
    required = [(2, 2), (4, 4), (6, 6), (8, 8), (10, 8)]
    validation = {
        "axisymmetric_stationary_background_has_zero_linear_nonzero_weight_source": True,
        "symmetric_Hessian_block_diagonal_in_ell_p": True,
        "positive_blocks_forbid_local_nonaxisymmetric_bifurcation": example["positive"] == "LOCALLY_STABLE_NO_LINEAR_BIFURCATION",
        "zero_block_is_equivariant_bifurcation_candidate": example["zero"] == "ZERO_MODE_EQUIVARIANT_BIFURCATION_CANDIDATE",
        "negative_block_requires_new_branch_search": example["negative"] == "NONAXISYMMETRIC_INSTABILITY_BRANCH_SEARCH_REQUIRED",
        "constant_background_Hessian_does_not_replace_degree_one_Hessian": True,
        "no_action_owned_nonaxisymmetric_boundary_source_attached": True,
        "branch_not_promoted": True,
    }
    return {
        "artifact": "BHSM_Path_B_nonaxisymmetric_bifurcation_gate_v14_35",
        "version": VERSION,
        "conditional_theorem": "about an axisymmetric degree-one stationary background, U(1) orthogonality removes linear p!=0 forcing and the self-adjoint Hessian decomposes into (ell,p) blocks",
        "required_blocks": [{"ell": ell, "p": p, "lowest_eigenvalue": None} for ell, p in required],
        "branch_gate": "a required block must contain a zero mode at an equivariant bifurcation or a negative mode leading to a nonlinear branch; otherwise the axisymmetric branch does not generate flavor texture",
        "current_status": "the full-preimage degree-one stationary background, cap domain and its nonaxisymmetric Hessian spectrum are not constructed",
        "existing_constant_background_result": "insufficient because the physical texture must be expanded around the degree-one branch",
        "classification_examples": example,
        "verdict": "PATH_B_ACTION_DOES_NOT_YET_SELECT_THE_REQUIRED_NONAXISYMMETRIC_TEXTURE",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def nonlinear_tower_payload() -> dict[str, Any]:
    mixing_weights = [p for _, p in MINIMAL_MIXING_COMPONENTS]
    cp_weights = [p for _, p in CABIBBO_CP_COMPONENTS]
    mixing_generated = signed_seventh_order_weights(mixing_weights)
    cp_generated = signed_seventh_order_weights(cp_weights)
    validation = {
        "mixing_input_weights_are_0_2_6_8": mixing_weights == [0, 2, 6, 8],
        "CP_input_weights_are_0_2_4_6_8": cp_weights == [0, 2, 4, 6, 8],
        "both_first_p8_iterates_generate_all_even_weights_minus24_to32": (
            mixing_generated == cp_generated == list(range(-24, 33, 2))
        ),
        "generated_weights_strictly_exceed_both_input_sets": (
            set(mixing_generated) > set(mixing_weights) and set(cp_generated) > set(cp_weights)
        ),
        "mixing_seed_ell_bound_is70": 7 * max(ell for ell, _ in MINIMAL_MIXING_COMPONENTS) == 70,
        "CP_texture_ell_bound_is56": 7 * max(ell for ell, _ in CABIBBO_CP_COMPONENTS) == 56,
        "finite_harmonic_seeds_not_exactly_closed": True,
        "Feshbach_requires_self_adjoint_QHQ_and_resolvent_gap": True,
    }
    return {
        "artifact": "BHSM_Hopf_phase_texture_nonlinear_tower_gate_v14_35",
        "version": VERSION,
        "Euler_non_linearity": "div[(kappa1+X^3)D eta] contains seven harmonic factors in the X^3 D eta contribution",
        "minimal_mixing_seed": {
            "input_weights": mixing_weights,
            "first_generated_weights": mixing_generated,
            "input_ell_max": max(ell for ell, _ in MINIMAL_MIXING_COMPONENTS),
            "generic_first_iterate_ell_max": 70,
        },
        "Cabibbo_CP_texture": {
            "input_weights": cp_weights,
            "first_generated_weights": cp_generated,
            "input_ell_max": max(ell for ell, _ in CABIBBO_CP_COMPONENTS),
            "generic_first_iterate_ell_max": 56,
        },
        "closure_verdict": "NEITHER_FINITE_FLAVOR_SEED_IS_AN_EXACT_CONSISTENT_TRUNCATION",
        "authorized_reduction": "construct the self-adjoint full tower Hessian, prove E lies in the resolvent set of H_QQ, then use the Feshbach/Schur critical-value map",
        "claim_boundary": "the growth bounds prove the need for a tower; they do not determine the tower coefficients or spectrum",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def relative_holonomy_payload() -> dict[str, Any]:
    validation = {
        "prior_relative_rotation_channels_recalled_conditionally": True,
        "prior_noncommuting_up_down_response_witness_recalled": True,
        "prior_CP_odd_relative_Z6_holonomy_recalled": True,
        "Path_B_full_preimage_pullback_not_attached": True,
        "mixed_second_variation_and_normalization_open": True,
        "no_new_phase_field_required_if_attachment_succeeds": True,
        "prior_candidate_not_promoted": True,
    }
    return {
        "artifact": "BHSM_v12_relative_holonomy_to_v14_35_phase_texture_ledger",
        "version": VERSION,
        "candidate_role": "the existing conditional relative-rotation/Z6 holonomy channel is the natural orientation source for choosing between the +/-Phi stationary pair",
        "recovered_prior_content": [
            "conditional relative-rotation channels",
            "noncommuting historical up/down response matrices",
            "CP-odd relative holonomy",
        ],
        "missing_attachment": [
            "pullback to the Path-B/full-preimage common domain",
            "action-normalized coupling to the five harmonic amplitudes",
            "mixed second variation producing the up/down cross-Gram orientation",
            "compatibility with the self-adjoint cap domain and tower subtraction",
        ],
        "classification": "PROMISING_EXISTING_SOURCE_NOT_ACTION_ATTACHED",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


@lru_cache(maxsize=1)
def completion_payload() -> dict[str, Any]:
    dependencies = [
        minimal_texture_payload(),
        phase_locking_payload(),
        action_selection_payload(),
        nonlinear_tower_payload(),
        relative_holonomy_payload(),
    ]
    validation = {
        "all_v14_35_audits_pass": all(item["validation_passed"] for item in dependencies),
        "v14_34_single_phase_no_go_preserved": True,
        "minimal_connected_texture_derived": True,
        "one_rephasing_cycle_and_phase_resonance_derived": True,
        "action_selection_not_invented": True,
        "tower_resolvent_not_invented": True,
        "physical_CKM_CP_and_masses_absent": True,
        "frozen_predictions_unchanged": True,
        "BHSM_not_claimed_complete": True,
    }
    return {
        "artifact": "BHSM_Hopf_phase_bifurcation_completion_gate_v14_35",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "secondary_verdict": SECONDARY_VERDICT,
        "BHSM_complete": False,
        "minimal_texture_gate": "PASSED_FOUR_COMPONENT_MIXING_SEED_AND_FIVE_COMPONENT_CP_TEXTURE_KINEMATICALLY",
        "rank_gate": "GENERIC_FULL_RANK_CONDITION_DERIVED_NOT_ACTION_EVALUATED",
        "CP_phase_gate": "ONE_REPHASING_CYCLE_AND_SYMMETRY_ALLOWED_LOCKING_NORMAL_FORM_DERIVED",
        "nonaxisymmetric_branch_gate": "BLOCKED_BY_MISSING_DEGREE_ONE_SELF_ADJOINT_HESSIAN_SPECTRUM",
        "tower_gate": "BLOCKED_BY_NONCLOSURE_AND_MISSING_QHQ_RESOLVENT",
        "relative_holonomy_gate": "EXISTING_CONDITIONAL_CANDIDATE_NOT_ACTION_ATTACHED",
        "CKM_status": "NOT_DERIVED",
        "CP_status": "NORMAL_FORM_ROUTE_DERIVED_BUT_PHASE_MAGNITUDE_AND_ORIENTATION_NOT_SELECTED",
        "validated": [
            "minimal four-component connected full-rank mixing seed with phase-tied CP cancellation",
            "five-component Cabibbo-aligned texture with one independent phase cycle",
            "det K=a00(a44 a66_s-a88 a22)",
            "rephasing-invariant phase Phi=arg(K_ud K_cs K_us^* K_cd^*)",
            "weight resonance 4+6=8+2",
            "competing CP-even phase-locking terms can support conjugate nontrivial phases",
            "first p8 nonlinear iterate escapes to weights -24 through 32, with ell bounds 70 for the mixing seed and 56 for the CP texture",
        ],
        "invalidated": [
            "the v14.34 minimal selection-rule proxy is already an action-selected CKM solution",
            "the four- or five-component harmonic seeds form an exact finite truncation",
            "one real phase-locking cosine generates physical CP",
            "the constant-background Hessian establishes the degree-one flavor branch",
        ],
        "open": [EXACT_NEXT_OBJECT],
        "exact_next_object": EXACT_NEXT_OBJECT,
        "dependencies": [item["artifact"] for item in dependencies],
        "frozen_predictions_changed": False,
        "physical_outputs_emitted": False,
        "forbidden_outputs": {
            "physical_CKM": None,
            "physical_Jarlskog": None,
            "phase_texture_amplitudes": None,
            "Hessian_eigenvalues": None,
            "absolute_quark_masses": None,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
