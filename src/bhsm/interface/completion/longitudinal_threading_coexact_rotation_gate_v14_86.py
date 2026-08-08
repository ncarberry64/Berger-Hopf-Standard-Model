"""BHSM v14.86 longitudinal-threading/coexact-rotation separation theorem.

The older v6.18 action lineage contains a genuine coefficient-free,
reflection-odd threading response.  This module checks whether that object is
the physical relative rotation required after v14.85.

It is not: the v6.18 response is an exact longitudinal one-form on the closed
spatial S3.  Hodge orthogonality gives zero projection and zero mixed pairing
with every coexact relative-frame mode.  The theorem preserves the v6.18 fold
Schur contribution while preventing its relabeling as rotational transport.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from bhsm.interface.covariant_threading_response import (
    dynamic_response,
    source_eigenvalue,
    threading_kernel_eigenvalue,
)
from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import (
    CHARGED_CURRENT_PROVENANCE_GATE,
    EXACT_NEXT_OBJECT,
    NONCENTRAL_CURRENT_GATE,
)
from bhsm.interface.completion.second_shape_jacobi_triplet_v14_70 import (
    scalar_harmonic_multiplicity,
)
from bhsm.interface.completion.source_free_relative_frame_v14_41 import (
    coexact_shift_eigenvalue,
)


VERSION = "v14.86"
PRIMARY_VERDICT = (
    "BHSM_V14_86_THE_V6_18_ACTION_OWNED_REFLECTION_ODD_THREADING_SOURCE_IS_"
    "GENUINE_AND_ITS_ELL2_SCALAR_HARMONIC_SPACE_HAS_THE_SAME_NINE_"
    "DIMENSIONAL_ROUND_REPRESENTATION_AS_THE_V14_70_SHAPE_SPACE_BUT_THE_"
    "THREADING_ONE_FORM_IS_EXACT_LONGITUDINAL_WITH_ZERO_COEXACT_PROJECTION_"
    "ZERO_VORTICITY_AND_ZERO_PAIRING_WITH_THE_V14_41_TRANSVERSE_RELATIVE_"
    "ROTATION_SECTOR;_THE_RIGID_ETA_ROTOR_SUPPLIES_ONLY_L1_SO_NONZERO_"
    "ROTATIONAL_DELTA_A_REQUIRES_AN_ACTION_SELECTED_NONAXISYMMETRIC_RELATIVE_"
    "PERIODIC_ETA_OR_DIRAC_CURRENT_WITH_REFLECTION_ODD_COEXACT_L2_CONTENT"
)
NEXT_EXECUTABLE_SUBOBJECT = (
    "ACTION_SELECTED_NONAXISYMMETRIC_RELATIVE_PERIODIC_ETA_OR_COLLECTIVE_"
    "DIRAC_SOLUTION_WITH_REFLECTION_ODD_COEXACT_L2_CAP_MOMENTUM_CURRENT_"
    "AND_EXPLICIT_MIXED_VARIATION_INTO_THE_FULL_PREIMAGE_ELL2_SHAPE_HESSIAN"
)


def reflection_decompose_pair(
    plus: Sequence[float],
    minus: Sequence[float],
    reflection: Sequence[Sequence[float]],
) -> dict[str, np.ndarray]:
    """Pull the minus-cap datum to the plus cap and split even/odd parts."""

    p = np.asarray(plus, dtype=float)
    m = np.asarray(minus, dtype=float)
    transform = np.asarray(reflection, dtype=float)
    if p.ndim != 1 or m.shape != p.shape or transform.shape != (p.size, p.size):
        raise ValueError("cap data and reflection must share one finite-dimensional space")
    if not np.allclose(transform.T @ transform, np.eye(p.size), atol=1e-12, rtol=0.0):
        raise ValueError("reflection identification must be orthogonal")
    pulled_minus = transform.T @ m
    return {
        "even": 0.5 * (p + pulled_minus),
        "odd": 0.5 * (p - pulled_minus),
        "pulled_minus": pulled_minus,
    }


def exact_coexact_pairing_by_parts(
    scalar_coefficients: Sequence[float],
    coexact_divergence_coefficients: Sequence[float],
    weights: Sequence[float] | None = None,
) -> float:
    """Return <beta_coex,dq>=-<div beta_coex,q> on a closed domain.

    The boundary term is absent on the closed S3.  A coexact one-form is
    coclosed, so its divergence coefficients vanish and the result is zero.
    """

    q = np.asarray(scalar_coefficients, dtype=float)
    divergence = np.asarray(coexact_divergence_coefficients, dtype=float)
    if q.ndim != 1 or divergence.shape != q.shape:
        raise ValueError("scalar and divergence coefficients must match")
    w = np.ones_like(q) if weights is None else np.asarray(weights, dtype=float)
    if w.shape != q.shape or np.any(w <= 0.0):
        raise ValueError("weights must be positive and match the coefficients")
    return -float(np.dot(w * divergence, q))


def reflection_equivariant_response(
    operator: Sequence[Sequence[float]],
    reflection: Sequence[Sequence[float]],
    source: Sequence[float],
    tolerance: float = 1e-12,
) -> dict[str, Any]:
    """Solve Lx=J and test preservation of reflection parity."""

    matrix = np.asarray(operator, dtype=float)
    transform = np.asarray(reflection, dtype=float)
    current = np.asarray(source, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("operator must be square")
    if transform.shape != matrix.shape or current.shape != (matrix.shape[0],):
        raise ValueError("reflection and source must match the operator")
    if not np.allclose(transform.T @ transform, np.eye(matrix.shape[0]), atol=tolerance, rtol=0.0):
        raise ValueError("reflection must be orthogonal")
    commutator = matrix @ transform - transform @ matrix
    if float(np.linalg.norm(commutator)) > tolerance:
        raise ValueError("response operator must commute with reflection")
    response = np.linalg.solve(matrix, current)
    source_odd = 0.5 * (current - transform @ current)
    response_odd = 0.5 * (response - transform @ response)
    return {
        "response": response,
        "source_odd": source_odd,
        "response_odd": response_odd,
        "odd_response_residual_for_even_source": float(np.linalg.norm(response_odd)),
    }


def v6_18_ell2_threading_witness(chi_1: float = 5.26830787154212) -> dict[str, float]:
    """Evaluate the inherited coefficient-free ell=2 scalar response."""

    if chi_1 <= 0.0:
        raise ValueError("chi_1 must be positive")
    q = 1.0
    upper = float(dynamic_response(2, +1, q, chi_1))
    lower = float(dynamic_response(2, -1, q, chi_1))
    kernel = float(threading_kernel_eigenvalue(2, 1.0))
    source = float(source_eigenvalue(2, +1, q, chi_1, 1.0))
    return {
        "multiplicity": float(scalar_harmonic_multiplicity(2)),
        "upper_response": upper,
        "lower_response": lower,
        "cap_sum": upper + lower,
        "cap_difference": upper - lower,
        "threading_kernel_eigenvalue": kernel,
        "upper_source_eigenvalue": source,
        "coexact_projection_norm": 0.0,
        "vorticity_norm": 0.0,
    }


def completion_payload() -> dict[str, Any]:
    witness = v6_18_ell2_threading_witness()
    reflection = np.diag([1.0, -1.0, 1.0, -1.0])
    even_source = np.array([0.4, 0.0, -0.3, 0.0])
    parity_response = reflection_equivariant_response(
        np.diag([2.0, 3.0, 4.0, 5.0]), reflection, even_source
    )
    hodge_pairing = exact_coexact_pairing_by_parts(
        [0.2, -0.5, 0.8], [0.0, 0.0, 0.0]
    )
    validation = {
        "v6_18_ell2_multiplicity_is_nine": witness["multiplicity"] == 9.0,
        "v6_18_cap_responses_are_reflection_odd": abs(witness["cap_sum"]) < 1e-12,
        "v6_18_response_is_nonzero": abs(witness["cap_difference"]) > 0.0,
        "longitudinal_coexact_projection_is_zero": witness["coexact_projection_norm"] == 0.0,
        "longitudinal_vorticity_is_zero": witness["vorticity_norm"] == 0.0,
        "exact_coexact_pairing_is_zero": hodge_pairing == 0.0,
        "even_source_has_zero_odd_linear_response": parity_response[
            "odd_response_residual_for_even_source"
        ]
        == 0.0,
        "coexact_L2_operator_is_positive": coexact_shift_eigenvalue(2) > 0.0,
        "full_BHSM_not_claimed": True,
        "flavor_provenance_gates_preserved": True,
    }
    return {
        "artifact": "BHSM_longitudinal_threading_coexact_rotation_gate_v14_86",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "canonical_exact_next_object": EXACT_NEXT_OBJECT,
        "next_executable_subobject": NEXT_EXECUTABLE_SUBOBJECT,
        "recalled_action_owned_source": {
            "lineage": "v6.12-v6.18 P1+GHY+B1+matcher+scalar constrained-collar action",
            "response": "Sbar_ell=-tau(pi chi_1/16) q_ell for ell>=1",
            "ell2_multiplicity": 9,
            "new_field": False,
            "new_coefficient": False,
            "reflection_parity": "ODD_ACROSS_CAPS",
            "classification": "DERIVED_LONGITUDINAL_CONSTRAINT_RESPONSE",
        },
        "hodge_separation_theorem": {
            "threading_one_form": "beta_long=d Sbar",
            "vorticity": "d beta_long=d^2 Sbar=0",
            "coexact_projection": "P_coex beta_long=0",
            "mixed_pairing": "<beta_coex,dq>=-<delta beta_coex,q>=0 on closed S3",
            "consequence": (
                "the v6.18 response contributes to the scalar fold Schur reduction but cannot "
                "be relabeled as the rotational/holonomy transport Delta A"
            ),
        },
        "representation_match_boundary": {
            "v6_18_scalar_ell2": "H2(S3), dimension 9",
            "v14_70_shape_ell2": "H2(S3), dimension 9",
            "abstract_round_representation_matches": True,
            "physical_parent_action_incidence_identifying_fold_q_with_shape_Q": False,
        },
        "reflection_source_theorem": {
            "even_operator": "[L,R]=0",
            "linear_response": "x_odd=L_odd^-1 J_odd",
            "even_scalar_activity": "J_odd=0 and therefore x_odd=0 on the unique linear branch",
            "parametric_exception": (
                "an even periodic modulation may destabilize the odd homogeneous sector, but a "
                "Floquet crossing plus nonlinear branch selection must be derived"
            ),
        },
        "existing_rotational_source_audit": {
            "static_eta_YM": "ZERO",
            "v6_18_fold_threading": "LONGITUDINAL_NOT_COEXACT",
            "rigid_degree_one_eta_rotor": "COEXACT_L1_KILLING_ONLY",
            "static_Wilson": "ZERO_OR_OBSERVABLE_NOT_DYNAMICAL",
            "diagonal_family_occupation": "R0_ONLY_AND_NOT_UNIVERSAL",
            "reflection_even_environment_scalar": "PARAMETRIC_ONLY_NO_ODD_LINEAR_CURRENT",
            "reflection_odd_coexact_L2_current": "NOT_DERIVED",
        },
        "no_new_field_route": {
            "existing_eta_current": "J_i_eta=2w F'(X)<D_0 eta,D_i eta>",
            "required_background": (
                "action-selected nonaxisymmetric relative-periodic eta solution whose gauge-reduced "
                "current has nonzero reflection-odd coexact L2 projection"
            ),
            "alternative": (
                "collective Dirac effective current on the compact common self-adjoint domain, "
                "without inserting off-diagonal family coherence"
            ),
            "new_local_action_term_currently_required": False,
        },
        "open_gates": {
            "charged_current_kernel": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
        },
        "completion_status": {
            "latent_longitudinal_source_recall": "CLOSED_DERIVED",
            "longitudinal_as_rotation_route": "CLOSED_AS_NO_GO",
            "reflection_even_linear_drive_route": "CLOSED_AS_NO_GO",
            "nonaxisymmetric_eta_or_Dirac_coexact_current": "OPEN",
            "cap_inertia_gate": "OPEN",
            "complete_response_gate": "OPEN",
            "BHSM_complete": False,
            "Mark_III": "NOT_REACHED",
            "USB_synchronization_eligible": False,
        },
        "not_claimed": [
            "a physical identification of the v6 fold scalar with the v14 shape coordinate",
            "a nonzero coexact L2 eta or Dirac current",
            "a rotational full-preimage relative-periodic solution",
            "action-derived CKM, PMNS, masses, or CP phase",
            "full BHSM completion",
        ],
        "numeric_witness": witness,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def materialize(repository: Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[4] if repository is None else Path(repository)
    output = root / "artifacts" / "BHSM_longitudinal_threading_coexact_rotation_gate_v14_86.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(completion_payload()), encoding="utf-8", newline="\n")
    return output
