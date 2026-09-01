"""Family-hierarchy interface theorem for the assembled AE3 puzzle pieces."""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np

from bhsm.interface.aether_cycle_family_centrality_v15_87 import cyclic_shift


CLASSIFICATION = "AE3_FAMILY_HIERARCHY_NECESSARY_INTERFACE_THEOREM"


def family_projectors() -> tuple[np.ndarray, ...]:
    """Return the three frozen rank-one BHSM family projectors."""

    rows = []
    for index in range(3):
        projector = np.zeros((3, 3), dtype=complex)
        projector[index, index] = 1.0
        rows.append(projector)
    return tuple(rows)


def family_blind_composition(operators: Iterable[np.ndarray]) -> np.ndarray:
    """Compose spatial/internal maps after lifting each by the family identity."""

    values = [np.asarray(operator, dtype=complex) for operator in operators]
    if not values:
        raise ValueError("at least one operator is required")
    dimension = values[0].shape[0]
    if any(
        value.ndim != 2
        or value.shape != (dimension, dimension)
        or not np.all(np.isfinite(value))
        for value in values
    ):
        raise ValueError("finite square operators of one dimension required")
    result = np.eye(3 * dimension, dtype=complex)
    for value in values:
        result = np.kron(value, np.eye(3)) @ result
    return result


def family_blind_composition_certificate() -> dict[str, Any]:
    """Certify centrality of every presently attached family-blind map."""

    # Representative noncommuting maps show that no commutativity assumption
    # is needed in the non-family tensor factor.
    reset = np.asarray(((0.0, 1.0), (-1.0, 0.0)))
    enclosure = np.asarray(((0.75, 0.0), (0.0, 0.25)))
    quadratic = np.asarray(((2.0, -0.4), (-0.4, 1.5)))
    composed = family_blind_composition((reset, enclosure, quadratic))
    shift = np.kron(np.eye(2), cyclic_shift())
    lifted_projectors = [np.kron(np.eye(2), item) for item in family_projectors()]
    projector_residuals = [
        float(np.linalg.norm(composed @ item - item @ composed))
        for item in lifted_projectors
    ]
    shift_residual = float(np.linalg.norm(composed @ shift - shift @ composed))
    spatial_composition = quadratic @ enclosure @ reset
    factorization_residual = float(
        np.linalg.norm(composed - np.kron(spatial_composition, np.eye(3)))
    )
    return {
        "classification": CLASSIFICATION,
        "attached_maps": [
            "AE2_reset_lift",
            "AE3_enclosure_restriction_or_smooth_weight",
            "current_C2_lowest_Weyl_quadratic_and_reduced_source_jet",
            "historical_local_C3_equivariant_family_central_Yukawa_residue",
        ],
        "factorization": "A_attached=A_nonfamily_tensor_I3",
        "factorization_residual": factorization_residual,
        "family_projector_commutator_residuals": projector_residuals,
        "C3_shift_commutator_residual": shift_residual,
        "three_distinct_family_singular_values_possible": False,
        "reason": (
            "PRODUCTS_SUMS_ADJOINTS_LIMITS_AND_REGULATED_FUNCTIONALS_OF_"
            "A_TENSOR_I3_REMAIN_FAMILY_CENTRAL"
        ),
        "certificate_passed": (
            factorization_residual == 0.0
            and shift_residual == 0.0
            and max(projector_residuals) == 0.0
        ),
    }


def hierarchy_interface_decision_surface() -> dict[str, Any]:
    """Return the two coefficient-free structural routes out of centrality."""

    shift = cyclic_shift()
    local_breaking = np.diag((1.0, 2.0, 4.0)).astype(complex)
    omega = np.exp(2.0j * np.pi / 3.0)
    fourier = np.asarray(
        [[omega ** (row * column) for column in range(3)] for row in range(3)],
        dtype=complex,
    ) / np.sqrt(3.0)
    mixed_equivariant = fourier @ np.diag((1.0, 2.0, 4.0)) @ fourier.conj().T
    projectors = family_projectors()

    def row(matrix: np.ndarray) -> dict[str, Any]:
        singular_values = np.linalg.svd(matrix, compute_uv=False)
        return {
            "C3_commutator_norm": float(np.linalg.norm(matrix @ shift - shift @ matrix)),
            "maximum_projector_commutator_norm": float(
                max(np.linalg.norm(matrix @ p - p @ matrix) for p in projectors)
            ),
            "singular_values": sorted(float(value) for value in singular_values),
            "three_distinct_singular_values": bool(
                min(np.diff(np.sort(singular_values))) > 1.0e-12
            ),
        }

    return {
        "present_intersection": (
            "PROJECTOR_LOCAL_AND_C3_EQUIVARIANT_IMPLIES_SCALAR_MULTIPLE_OF_I3"
        ),
        "route_A_action_selected_C3_breaking": {
            **row(local_breaking),
            "structure": "FAMILY_PROJECTOR_LOCAL_BUT_NOT_C3_EQUIVARIANT",
            "interpretation": (
                "distinct_existing_family_fibers_remain_mass_eigenstates"
            ),
        },
        "route_B_triality_changing_intertwiner": {
            **row(mixed_equivariant),
            "structure": "C3_EQUIVARIANT_BUT_NOT_FAMILY_PROJECTOR_LOCAL",
            "interpretation": (
                "mass_eigenstates_are_action_selected_combinations_of_existing_fibers"
            ),
        },
        "required_common_conditions": [
            "operator_is_derived_from_the_retained_or_owner_authorized_action",
            "operator_lives_on_the_same_physical_background_and_domain",
            "three_distinct_singular_values_are_derived_without_family_fits",
            "particle_manifestation_map_is_transported_to_the_resulting_mass_basis",
        ],
        "continuous_family_coefficients_may_be_inserted": False,
        "route_selected_by_current_evidence": None,
    }


def family_hierarchy_puzzle_ledger() -> dict[str, Any]:
    centrality = family_blind_composition_certificate()
    decision = hierarchy_interface_decision_surface()
    return {
        "classification": CLASSIFICATION,
        "fitted_pieces": [
            "three_frozen_BHSM_family_projectors_per_charged_sector",
            "all_nine_current_C2_family_state_fibers",
            "reset_projector_enclosure_commuting_transport_square",
            "current_C2_family_central_product_Dirac_operator_piece",
            "locality_intersection_C3_family_centrality_theorem",
        ],
        "derived_result": (
            "THE_PRESENT_AE3_COMPOSITION_PRESERVES_FAMILY_IDENTITY_BUT_CANNOT_"
            "DERIVE_THE_THREE_DISTINCT_CHARGED_LEPTON_MASSES"
        ),
        "exact_missing_interface": (
            "ONE_ACTION_OWNED_FAMILY_NONCENTRAL_RETURNED_MASS_OPERATOR_VIA_"
            "EITHER_ACTION_SELECTED_C3_BREAKING_OR_A_TRIALITY_CHANGING_"
            "INTERTWINER_ON_THE_CURRENT_PHYSICAL_DOMAIN"
        ),
        "centrality_certificate": centrality,
        "decision_surface": decision,
        "family_modes_can_manifest_as_SM_particles": True,
        "family_mass_hierarchy_derived": False,
        "CKM_PMNS_derived": False,
        "particle_spectrum_rebuilt": False,
        "prediction_emitted": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "CLASSIFICATION",
    "family_blind_composition",
    "family_blind_composition_certificate",
    "family_hierarchy_puzzle_ledger",
    "family_projectors",
    "hierarchy_interface_decision_surface",
]
