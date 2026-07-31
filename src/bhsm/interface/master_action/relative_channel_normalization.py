"""BHSM v8.7 master-action relative-channel normalization audit.

This manual sprint separates canonical mode normalization from physical
channel coupling.  It derives the unique relative ratio obtained if the C3
character channels descend as orthonormal modes of one parent carrier and the
G2 complex structure supplies the polarization.  It then records why the
current stratified master action does not yet attach that ratio to the
localized charged current.
"""

from __future__ import annotations

from math import sqrt
from typing import Any

import numpy as np

from . import complex_profile_isospectral_attachment as v86
from . import topographic_profile_component_selection as v85

VERSION = "v8.7"
SPRINT = "bhsm-master-action-relative-channel-normalization-v8-7"
PRIMARY_RESULT = (
    "BHSM_CANONICAL_ORTHONORMAL_G2_C3_RELATIVE_NORMALIZATION_"
    "DERIVED_CONDITIONALLY"
)
FINAL_VERDICT = (
    "BHSM_MASTER_ACTION_PHYSICAL_G2_C3_CHANNEL_COUPLING_REMAINS_"
    "UNSELECTED"
)
NEXT_MISSING_OBJECT = (
    "ACTION_OWNED_COMMON_PARENT_CURRENT_TERM_ATTACHING_ORTHONORMAL_C3_"
    "MODES_TO_THE_G2_POLARIZED_LOCALIZED_CHARGED_CURRENT"
)


def c3_character_gram() -> np.ndarray:
    """Gram matrix of normalized C3 character vectors."""

    omega = np.exp(2j * np.pi / 3.0)
    vectors = np.array(
        [[omega ** (-k * n) / sqrt(3.0) for n in range(3)] for k in range(3)],
        dtype=complex,
    )
    return vectors @ vectors.conj().T


def point_character_identity() -> dict[str, Any]:
    """Verify delta_e=(chi0+chi1+chi2)/sqrt(3) in the transfer library."""

    point = v85.heat_kernel_cross_matrix().astype(complex)
    characters = [v86.c3_cross_matrix(k) for k in range(3)]
    reconstructed = sum(characters) / sqrt(3.0)
    residual = float(np.linalg.norm(point - reconstructed))
    return {
        "identity": "T_point=(T_chi0+T_chi1+T_chi2)/sqrt(3)",
        "residual_frobenius": residual,
        "verified": bool(residual < 1.0e-12),
        "interpretation": (
            "The 1/sqrt(3) is a Fourier basis-conversion coefficient, not a "
            "dynamical singlet-to-complex coupling."
        ),
    }


def parent_orthonormal_pushforward() -> dict[str, Any]:
    """Canonical coefficient matrix for orthonormal retained modes.

    For one parent quadratic term c <D Phi,D Phi> and orthonormal internal
    modes, c_ab=c integral u_a^*u_b=c delta_ab.  Common canonical rescaling
    removes c and leaves unit relative modulus.
    """

    gram = c3_character_gram()
    return {
        "parent_rule": "c_ab=c_parent integral_F u_a^* u_b dnu_F",
        "character_gram_real": np.real_if_close(gram, tol=1000).real.tolist(),
        "orthonormal": bool(np.allclose(gram, np.eye(3), atol=1.0e-13)),
        "common_parent_coefficient": "c_parent",
        "canonical_rescaling": "phi_a^c=sqrt(c_parent) phi_a for every a",
        "relative_modulus_chi1_over_chi0": 1.0,
        "new_continuous_parameter": False,
    }


def g2_normalized_complex_pair() -> dict[str, Any]:
    """Normalize Pi_10 x=(x-iJx)/2 for unit x perpendicular to u."""

    # In the G2 six-plane, ||x||=||Jx||=1 and <x,Jx>=0.
    raw_norm_sq = 0.5
    normalization = sqrt(2.0)
    return {
        "projector": "Pi_10=(Q-iJ)/2",
        "raw_projected_vector": "Pi_10 x=(x-iJx)/2",
        "raw_norm_squared_for_unit_x": raw_norm_sq,
        "normalized_vector": "z_+=(x-iJx)/sqrt(2)",
        "relative_phase": "-i",
        "relative_modulus": 1.0,
        "conjugate_branch": "z_-=(x+iJx)/sqrt(2)",
        "orientation_ambiguity": "+i versus -i until the action selects polarization/chirality",
        "overall_1_over_sqrt2_physical_for_polar_unitary": False,
    }


def canonical_relative_ratio() -> dict[str, Any]:
    """Return the unique kinematic ratio under the common-parent premise."""

    return {
        "premises": [
            "chi0 and chi1 are orthonormal retained modes of the same parent carrier term",
            "the same parent quadratic coefficient multiplies both modes",
            "the Pi_10 G2 polarization is selected for the particle branch",
        ],
        "ratio_c_chi1_over_c_chi0": {"real": 0.0, "imag": -1.0},
        "formula": "c_chi1/c_chi0=-i",
        "modulus": 1.0,
        "phase": "-pi/2",
        "conjugate_formula": "c_chi1/c_chi0=+i on the conjugate branch",
        "canonical_profile": "T_chi0-i T_chi1",
        "overall_normalization_irrelevant_to_polar_unitary": True,
        "status": PRIMARY_RESULT,
    }


def c3_commutant_freedom() -> dict[str, Any]:
    """Exact symmetry-only coefficient freedom from the C3 commutant."""

    return {
        "general_hermitian_C3_commutant": (
            "J=a I+x(C+C^2)+i y(C-C^2)=a I+b C+b* C^2"
        ),
        "independent_real_coefficients": ["a", "x", "y"],
        "fourier_eigenvalues": [
            "a+2x",
            "a-x-sqrt(3)y",
            "a-x+sqrt(3)y",
        ],
        "symmetry_fixes_relative_norm": False,
        "current_minimal_action_value": "nontrivial junction/current generator absent",
    }


def physical_action_attachment_audit() -> dict[str, Any]:
    return {
        "S8_parent_carrier_term_present": True,
        "S8_parent_carrier_expression": (
            "-Zchi(1+g sigma^2)|dchi|^2/2"
        ),
        "orthonormal_mode_pushforward_rule_present": True,
        "localized_M4_fields_intrinsic": True,
        "triality_character_to_Berger_current_map_present": False,
        "G2_polarization_dynamically_selected": False,
        "common_parent_current_term_present": False,
        "localized_Yukawa_matrices_independent": True,
        "physical_relative_channel_ratio_selected": False,
        "reason": (
            "The master action can normalize orthonormal modes equally, but it "
            "does not identify chi0/chi1 as co-components of one localized "
            "charged-current operator. Therefore -i is a canonical kinematic "
            "ratio under a missing attachment theorem, not a current action output."
        ),
    }


def normalized_candidate_audit() -> dict[str, Any]:
    """Record the already kill-tested canonical profile without retuning."""

    chi0 = v86.c3_cross_matrix(0)
    chi1 = v86.c3_cross_matrix(1)
    candidate = v86.weighted_cross_polar(chi0 - 1j * chi1)
    comparison = v86.compare_to_frozen(candidate)
    return {
        "profile": "T_chi0-i T_chi1",
        "matrix_magnitudes": np.abs(candidate).tolist(),
        "jarlskog": v86.jarlskog(candidate),
        "comparison_to_frozen_screen": comparison,
        "passes_frozen_ten_percent_gate": comparison[
            "all_within_declared_ten_percent"
        ],
        "interpretation": (
            "The canonical normalization is not a successful frozen-CKM "
            "completion under the present profile/oriented-transfer map. The "
            "profile/current attachment must change; the normalization must not "
            "be tuned to repair the residuals."
        ),
    }


def payload() -> dict[str, Any]:
    point = point_character_identity()
    parent = parent_orthonormal_pushforward()
    g2 = g2_normalized_complex_pair()
    ratio = canonical_relative_ratio()
    commutant = c3_commutant_freedom()
    action = physical_action_attachment_audit()
    candidate = normalized_candidate_audit()
    validation = {
        "point_character_identity": point["verified"],
        "C3_characters_orthonormal": parent["orthonormal"],
        "canonical_ratio_unit_modulus": ratio["modulus"] == 1.0,
        "G2_phase_fixed_conditionally": g2["relative_phase"] == "-i",
        "symmetry_alone_leaves_coefficients": not commutant[
            "symmetry_fixes_relative_norm"
        ],
        "master_action_physical_attachment_absent": not action[
            "physical_relative_channel_ratio_selected"
        ],
        "no_frozen_promotion": not candidate["passes_frozen_ten_percent_gate"],
    }
    return {
        "artifact": "BHSM_master_action_relative_channel_normalization_v8_7",
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "final_verdict": FINAL_VERDICT,
        "point_character_identity": point,
        "parent_orthonormal_pushforward": parent,
        "G2_normalized_complex_pair": g2,
        "canonical_relative_ratio": ratio,
        "C3_commutant_freedom": commutant,
        "physical_action_attachment": action,
        "canonical_candidate_kill_test": candidate,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "new_continuous_parameter_added": False,
        "frozen_predictions_changed": False,
        "physical_CKM_promoted": False,
        "next_missing_object": NEXT_MISSING_OBJECT,
    }


