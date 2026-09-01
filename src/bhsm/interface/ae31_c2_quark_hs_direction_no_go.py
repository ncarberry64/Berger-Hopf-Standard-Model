"""Quark HS channel-direction non-identifiability on current C2.

Canonical normalization of a multi-channel auxiliary field fixes a norm, not
the physical direction in channel space.  This remains true after tensoring
the current reduced vertex with the already-attached up/down family response
operators.  A full same-action channel Hessian or equivalent source selector
is required to determine the relative quark residue.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import ACTION_VERSION
from bhsm.interface.ae3_c2_hopf_semigroup_transport import (
    frozen_internal_semigroup_attachment,
)


CLASSIFICATION = "AE31_CURRENT_C2_QUARK_HS_CHANNEL_DIRECTION_NONIDENTIFIABILITY"


def normalized_quark_channel_direction(
    *, angle: float, up_kinetic: float = 9.0, down_kinetic: float = 9.0
) -> dict[str, Any]:
    """Parameterize every positive direction on a normalized kinetic ellipse."""

    theta = float(angle)
    z_up = float(up_kinetic)
    z_down = float(down_kinetic)
    if not all(math.isfinite(value) for value in (theta, z_up, z_down)):
        raise ValueError("finite channel data required")
    if not 0.0 < theta < math.pi / 2.0:
        raise ValueError("positive two-channel direction requires 0<angle<pi/2")
    if z_up <= 0.0 or z_down <= 0.0:
        raise ValueError("positive kinetic coefficients required")
    c_up = math.cos(theta) / math.sqrt(z_up)
    c_down = math.sin(theta) / math.sqrt(z_down)
    return {
        "action_version": ACTION_VERSION,
        "angle": theta,
        "up_kinetic": z_up,
        "down_kinetic": z_down,
        "c_up": c_up,
        "c_down": c_down,
        "kinetic_norm": z_up * c_up**2 + z_down * c_down**2,
        "relative_residue_c_up_over_c_down": c_up / c_down,
        "positive_direction": c_up > 0.0 and c_down > 0.0,
        "direction_action_selected": False,
    }


def kinetic_normalization_nullity_theorem() -> dict[str, Any]:
    """Derive the tangent null direction left by one normalization equation."""

    witness = normalized_quark_channel_direction(angle=math.pi / 4.0)
    c_up = float(witness["c_up"])
    c_down = float(witness["c_down"])
    z_up = float(witness["up_kinetic"])
    z_down = float(witness["down_kinetic"])
    gradient = np.asarray((2.0 * z_up * c_up, 2.0 * z_down * c_down))
    tangent = np.asarray((z_down * c_down, -z_up * c_up))
    first = normalized_quark_channel_direction(angle=math.pi / 6.0)
    second = normalized_quark_channel_direction(angle=math.pi / 3.0)
    return {
        "channel_coordinates": ["c_up", "c_down"],
        "normalization_equation": "Z_up*c_up^2+Z_down*c_down^2=1",
        "constraint_Jacobian_rank": int(np.linalg.matrix_rank(gradient[None, :])),
        "channel_direction_nullity": 1,
        "tangent_vector_at_equal_angle": tangent.tolist(),
        "gradient_dot_tangent": float(gradient @ tangent),
        "two_normalized_witnesses": [first, second],
        "witness_relative_residues_differ": not math.isclose(
            float(first["relative_residue_c_up_over_c_down"]),
            float(second["relative_residue_c_up_over_c_down"]),
            rel_tol=0.0,
            abs_tol=0.0,
        ),
        "kinetic_normalization_selects_relative_up_down_residue": False,
    }


def historical_four_channel_trace_reuse() -> dict[str, Any]:
    """Reuse the v16.02 multiplicity theorem without its obsolete residue."""

    return {
        "historical_channel_basis": [
            "up",
            "down",
            "charged_lepton",
            "neutrino",
        ],
        "historical_pairing_multiplicity_matrix": "diag(9,9,3,3)",
        "reusable_result": (
            "UP_AND_DOWN_HAVE_EQUAL_PAIRING_MULTIPLICITY_IN_THE_"
            "HISTORICAL_FOUR_CHANNEL_TRACE"
        ),
        "historical_numeric_Z_pair_promoted_to_current_C2": False,
        "historical_periodic_cycle_domain_promoted_to_current_C2": False,
        "quark_plane_quadratic_symmetry_when_no_other_terms_are_present": "O(2)",
        "equal_multiplicity_selects_equal_components": False,
        "reason": (
            "AN_O2_INVARIANT_QUADRATIC_FORM_IS_CONSTANT_ON_THE_NORMALIZED_"
            "CIRCLE_AND_HAS_NO_PREFERRED_ANGLE"
        ),
        "independent_channel_canonical_values_are_physical_single_Higgs_values": False,
    }


def family_tensor_pushforward_witness() -> dict[str, Any]:
    """Show that family attachment preserves, rather than removes, the angle."""

    attachment = frozen_internal_semigroup_attachment()
    up_shape = np.asarray(attachment["sectors"]["up"]["family_operator"])
    down_shape = np.asarray(attachment["sectors"]["down"]["family_operator"])
    first_direction = normalized_quark_channel_direction(angle=math.pi / 6.0)
    second_direction = normalized_quark_channel_direction(angle=math.pi / 3.0)

    def pair(direction: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
        return (
            float(direction["c_up"]) * up_shape,
            float(direction["c_down"]) * down_shape,
        )

    first_up, first_down = pair(first_direction)
    second_up, second_down = pair(second_direction)
    return {
        "candidate_pushforward": (
            "V_spatial_tensor[(c_up*T_u)_on_up_plus_(c_down*T_d)_on_down]"
        ),
        "first_up_ratios_to_heavy": (
            np.diag(first_up) / np.diag(first_up)[0]
        ).tolist(),
        "second_up_ratios_to_heavy": (
            np.diag(second_up) / np.diag(second_up)[0]
        ).tolist(),
        "first_down_ratios_to_heavy": (
            np.diag(first_down) / np.diag(first_down)[0]
        ).tolist(),
        "second_down_ratios_to_heavy": (
            np.diag(second_down) / np.diag(second_down)[0]
        ).tolist(),
        "within_sector_shapes_identical": bool(
            np.array_equal(
                np.diag(first_up) / np.diag(first_up)[0],
                np.diag(second_up) / np.diag(second_up)[0],
            )
            and np.array_equal(
                np.diag(first_down) / np.diag(first_down)[0],
                np.diag(second_down) / np.diag(second_down)[0],
            )
        ),
        "cross_sector_heavy_ratio_first": float(
            first_up[0, 0] / first_down[0, 0]
        ),
        "cross_sector_heavy_ratio_second": float(
            second_up[0, 0] / second_down[0, 0]
        ),
        "cross_sector_ratio_changes": bool(
            first_up[0, 0] / first_down[0, 0]
            != second_up[0, 0] / second_down[0, 0]
        ),
        "all_attachment_commutators_zero": attachment[
            "all_attachment_commutators_zero"
        ],
        "family_tensoring_selects_channel_angle": False,
        "measured_quark_mass_used": False,
    }


def exact_channel_selector() -> dict[str, Any]:
    return {
        "required_operator": (
            "H_qH_current_C2=D_(H_u,H_d)^2*Gamma_qH_on_the_same_AE3_1_domain"
        ),
        "minimum_block": "[[H_uu,H_ud],[H_du,H_dd]]",
        "required_result": (
            "A_UNIQUE_NORMALIZABLE_PHYSICAL_EIGENDIRECTION_WITH_NONZERO_"
            "UP_AND_DOWN_COMPONENTS_OR_AN_ACTION_DERIVED_EQUIVALENT_SOURCE"
        ),
        "must_be_derived_together_with": [
            "intrinsic_H_and_H_tilde_identification",
            "current_C2_dynamical_kinetic_residue",
            "up_down_family_pushforward",
            "boundary_and_BRST_domain",
        ],
        "diagonal_kinetic_trace_alone_sufficient": False,
        "equal_components_may_be_assumed": False,
        "historical_numeric_channel_residue_may_be_copied": False,
        "quark_mass_fit_allowed": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "CURRENT_C2_QUARK_HS_KINETIC_NORMALIZATION_NULLITY_DERIVED": True,
        "CURRENT_C2_QUARK_HS_CHANNEL_DIRECTION_NULLITY": 1,
        "HISTORICAL_FOUR_CHANNEL_MULTIPLICITIES_REUSED": True,
        "HISTORICAL_PERIODIC_CYCLE_RESIDUE_PROMOTED": False,
        "CURRENT_C2_QUARK_CHANNEL_DIRECTION_SELECTED": False,
        "CURRENT_C2_UP_DOWN_RELATIVE_YUKAWA_RESIDUE_DERIVED": False,
        "CURRENT_C2_UP_DOWN_ABSOLUTE_YUKAWA_PREFACTORS_DERIVED": False,
        "CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED": False,
        "CKM_MATRIX_DERIVED": False,
        "MEASURED_QUARK_MASS_USED": False,
        "particle_spectrum_rebuilt": False,
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "claim_boundary",
    "exact_channel_selector",
    "family_tensor_pushforward_witness",
    "historical_four_channel_trace_reuse",
    "kinetic_normalization_nullity_theorem",
    "normalized_quark_channel_direction",
]
