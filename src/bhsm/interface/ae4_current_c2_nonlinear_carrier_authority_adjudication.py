"""Adjudicate nonlinear authority for the current AE4 carrier candidates.

The affine-to-nonlinear transfer audit, same-center outward 74D calculation,
and coarse field/descriptor block screen are final upstream assets.  Their
composition rejects both the scalar and 73+1 block contraction routes without
turning either proof-coordinate obstruction into physical instability or root
nonexistence.
"""

from __future__ import annotations

from typing import Any

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION


CLASSIFICATION = "AE4_CURRENT_C2_NONLINEAR_CARRIER_AUTHORITY_ADJUDICATION"


def nonlinear_carrier_authority_contract(
    *,
    affine_transfer_allowed: bool,
    same_center_contraction_obstructed: bool,
    field_descriptor_block_obstructed: bool,
    root_nonexistence_claim: bool,
    physical_instability_claim: bool,
    another_center_or_trajectory_authorized: bool,
) -> dict[str, Any]:
    """Return the only claim-compatible composition of the two audits."""

    if root_nonexistence_claim or physical_instability_claim:
        raise ValueError("the upstream 74D result makes neither physical claim")
    if another_center_or_trajectory_authorized:
        raise ValueError("the frozen replay decision authorizes no new campaign")
    promoted = bool(
        affine_transfer_allowed
        and not same_center_contraction_obstructed
        and not field_descriptor_block_obstructed
    )
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "affine_to_nonlinear_transfer_allowed": bool(affine_transfer_allowed),
        "same_center_single_radius_contraction_obstructed": bool(
            same_center_contraction_obstructed
        ),
        "same_center_field_descriptor_block_contraction_obstructed": bool(
            field_descriptor_block_obstructed
        ),
        "current_affine_operator_jets_have_nonlinear_authority": promoted,
        "accepted_replay_center_or_trajectory_may_be_reselected": False,
        "physical_spacetime_instability_inferred": False,
        "root_nonexistence_inferred": False,
        "obstruction_scope": (
            "FROZEN_PRECONDITIONER_SINGLE_RADIUS_AND_COARSE_73_PLUS_1_"
            "FIELD_DESCRIPTOR_CONTRACTIONS_IN_THE_EVALUATED_PROOF_COORDINATES"
        ),
        "obstruction_scope_extended_to_all_existence_theorems": False,
        "next_proof_object": (
            "SAME_FROZEN_CENTER_COMPONENTWISE_OR_FINER_ACTION_OWNED_BLOCK_"
            "RADII_SCREEN_USING_DIRECTION_BY_OUTPUT_BLOCK_CURVATURE_ENVELOPES"
        ),
        "why_next": (
            "THE_COARSE_FIELD_DESCRIPTOR_SPLIT_IS_ALREADY_OBSTRUCTED_BY_A_"
            "FIELD_INPUT_WHOSE_RETURNED_FIELD_CURVATURE_MAKES_THE_NECESSARY_"
            "FIELD_POLYNOMIAL_DISCRIMINANT_NEGATIVE;_ONLY_A_FINER_ACTION_"
            "PARTITION_OR_COMPONENTWISE_TEST_REMAINS_WITHOUT_CHANGING_THE_"
            "CENTER_OR_TRAJECTORY"
        ),
        "independent_fit_or_new_physical_scale_inserted": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "G7_SAME_CENTER_OUTWARD_74D_OPERANDS_ALREADY_EVALUATED": True,
        "G7_SINGLE_RADIUS_74D_CONTRACTION_ROUTE_OBSTRUCTED": True,
        "G7_FIELD_DESCRIPTOR_BLOCK_CONTRACTION_ROUTE_OBSTRUCTED": True,
        "G7_ROOT_NONEXISTENCE_DERIVED": False,
        "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
        "NEW_CENTER_OR_TRAJECTORY_AUTHORIZED": False,
        "AE4_AFFINE_GAUGE_AND_PARTICLE_JETS_NONLINEAR_AUTHORITY_DERIVED": False,
        "G7_SAME_CENTER_ACTION_BLOCK_RADII_POLYNOMIAL_DERIVED": False,
        "G7_SAME_CENTER_COMPONENTWISE_OR_FINER_BLOCK_RADII_DERIVED": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "nonlinear_carrier_authority_contract",
]
