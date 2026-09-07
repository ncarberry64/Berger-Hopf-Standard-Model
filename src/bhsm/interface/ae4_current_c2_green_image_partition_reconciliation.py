"""Recover the BHSM-native anisotropic Gate-7 proof partition."""

from __future__ import annotations

from typing import Any

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import ACTION_VERSION


CLASSIFICATION = "AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION"


def green_image_partition_contract(
    *,
    historical_green_mechanism_present: bool,
    historical_values_are_current_authority: bool,
    current_green_image_nonzero_after_reset: bool,
    coarse_field_descriptor_route_obstructed: bool,
) -> dict[str, Any]:
    """Return the fail-closed recovery of the old Green-image mechanism."""

    if not historical_green_mechanism_present:
        raise ValueError("the historical Green-image mechanism is required")
    if historical_values_are_current_authority:
        raise ValueError("the historical 48-seam values are not current-center authority")
    if not current_green_image_nonzero_after_reset:
        raise ValueError("the current causal Green image must define the partition")
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "recovered_partition": (
            "SIGNED_GREEN_IMAGE_LONGITUDINAL_DIRECTION_PLUS_ITS_CAUSAL_"
            "ORTHOGONAL_TRANSVERSE_COMPLEMENT"
        ),
        "partition_is_BHSM_native": True,
        "partition_selected_from_current_center_defect_image": True,
        "historical_48_seam_numerical_values_reused": False,
        "coarse_field_descriptor_route_obstructed": bool(
            coarse_field_descriptor_route_obstructed
        ),
        "green_image_anisotropic_route_obstructed": False,
        "green_image_anisotropic_route_derived": False,
        "new_center_or_trajectory_authorized": False,
        "fitted_partition_or_scale_inserted": False,
        "next_proof_object": (
            "SAME_FROZEN_CENTER_GREEN_IMAGE_LONGITUDINAL_TRANSVERSE_RADII_"
            "SCREEN_WITH_OUTWARD_DIRECTIONAL_MIXED_AND_TRANSVERSE_REMAINDERS"
        ),
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "G7_BHSM_NATIVE_GREEN_IMAGE_PARTITION_RECOVERED": True,
        "G7_HISTORICAL_48_SEAM_ANISOTROPIC_VALUES_CURRENT_AUTHORITY": False,
        "G7_CURRENT_CENTER_GREEN_IMAGE_ANISOTROPIC_RADII_DERIVED": False,
        "G7_ROOT_NONEXISTENCE_DERIVED": False,
        "G7_PHYSICAL_SPACETIME_INSTABILITY_DERIVED": False,
        "NEW_CENTER_OR_TRAJECTORY_AUTHORIZED": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "green_image_partition_contract",
]
