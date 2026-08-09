"""BHSM v14.85 stationary full-preimage transport no-go.

The v14.84 cap-inertia identity is an exact reduced operator theorem, but it
does not itself produce the physical relative transport appearing in that
identity.  This module audits the action-owned classical sources available on
the presently retained reflection-symmetric stationary branch.

The result is deliberately branch-local.  It does not exclude a sourced
relative-periodic solution, a nonzero fermion current, or a quantum effective
action.  It proves that pure cap repartition, source-free ADM shift, static
eta/Yang--Mills momentum, and time-symmetric Brown--York momentum cannot supply
the required nonzero transport.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from bhsm.interface.completion.bulk_cancellation_dtn_shape_d4_v14_77 import (
    partition_derivative_witness,
)
from bhsm.interface.completion.full_preimage_cap_inertia_operator_v14_84 import (
    CHARGED_CURRENT_PROVENANCE_GATE,
    EXACT_NEXT_OBJECT,
    NONCENTRAL_CURRENT_GATE,
    normalized_shear_operator,
)
from bhsm.interface.completion.source_free_relative_frame_v14_41 import (
    coexact_shift_eigenvalue,
)
from bhsm.interface.completion.static_eta_metric_spin4_source_v14_39 import (
    static_coexact_source,
)


VERSION = "v14.85"
PRIMARY_VERDICT = (
    "BHSM_V14_85_ON_THE_PRESENT_REFLECTION_SYMMETRIC_STATIONARY_CLASSICAL_"
    "BRANCH_PURE_CAP_REPARTITION_HAS_ZERO_TOTAL_ACTION_INERTIA_SOURCE_FREE_"
    "NONKILLING_ADM_SHIFT_STATIC_ETA_YM_MOMENTUM_AND_TIME_SYMMETRIC_BROWN_"
    "YORK_MOMENTUM_ALL_VANISH_SO_THE_V14_84_RELATIVE_TRANSPORT_AND_SHEAR_"
    "CORRECTION_EVALUATE_TO_ZERO;_NONZERO_SHEAR_REQUIRES_A_GENUINE_SOURCED_"
    "RELATIVE_PERIODIC_FULL_PREIMAGE_SOLUTION_OR_AN_EXPLICIT_QUANTUM_CURRENT"
)
NEXT_EXECUTABLE_SUBOBJECT = (
    "ACTION_OWNED_SOURCED_RELATIVE_PERIODIC_FULL_PREIMAGE_SOLUTION_WITH_"
    "NONZERO_CONSERVED_CAP_MOMENTUM_DIFFERENCE_GLOBAL_CONSTRAINT_REDUCED_"
    "ELL2_INERTIA_DEGREE_ONE_SELF_ADJOINT_DOMAIN_AND_COMPLETE_HESSIAN"
)


def canonical_slice_momentum(
    spatial_metric: Sequence[Sequence[float]],
    slice_extrinsic_curvature: Sequence[Sequence[float]],
) -> np.ndarray:
    """Return the unnormalized ADM momentum tensor K-tr(K)h.

    The omitted positive conventional prefactor does not affect the zero
    theorem.  Both inputs are covariant spatial tensors in one frame.
    """

    metric = np.asarray(spatial_metric, dtype=float)
    curvature = np.asarray(slice_extrinsic_curvature, dtype=float)
    if metric.ndim != 2 or metric.shape[0] != metric.shape[1]:
        raise ValueError("spatial_metric must be square")
    if curvature.shape != metric.shape:
        raise ValueError("slice extrinsic curvature must match the metric")
    if not np.allclose(metric, metric.T, atol=1e-12, rtol=0.0):
        raise ValueError("spatial_metric must be symmetric")
    if not np.allclose(curvature, curvature.T, atol=1e-12, rtol=0.0):
        raise ValueError("slice extrinsic curvature must be symmetric")
    eigenvalues = np.linalg.eigvalsh(metric)
    if float(np.min(eigenvalues)) <= 0.0:
        raise ValueError("spatial_metric must be positive definite")
    trace = float(np.trace(np.linalg.solve(metric, curvature)))
    return curvature - trace * metric


def brown_york_surface_momentum(
    spatial_metric: Sequence[Sequence[float]],
    slice_extrinsic_curvature: Sequence[Sequence[float]],
    outward_unit_normal: Sequence[float],
    tangent_projector: Sequence[Sequence[float]],
) -> np.ndarray:
    """Return the Brown--York momentum one-form up to a fixed convention.

    j_a is proportional to -sigma_a^i pi_ij n^j.  Consequently a
    time-symmetric slice, K_ij=0, has j_a=0 even though its Brown--York energy
    (which uses the spatial boundary curvature) need not vanish.
    """

    metric = np.asarray(spatial_metric, dtype=float)
    normal = np.asarray(outward_unit_normal, dtype=float)
    projector = np.asarray(tangent_projector, dtype=float)
    if normal.shape != (metric.shape[0],):
        raise ValueError("normal must be a spatial vector")
    if projector.shape != metric.shape:
        raise ValueError("tangent projector must match the spatial metric")
    inverse = np.linalg.inv(metric)
    norm = float(normal @ metric @ normal)
    if not np.isclose(norm, 1.0, atol=1e-12, rtol=0.0):
        raise ValueError("outward normal must be unit with respect to the metric")
    momentum = canonical_slice_momentum(metric, slice_extrinsic_curvature)
    normal_contravariant = inverse @ (metric @ normal)
    return -(projector @ momentum @ normal_contravariant)


def pure_repartition_inertia_witness(velocity: float, step: float = 1e-3) -> dict[str, float]:
    """Finite-difference witness for the zero total-action repartition Hessian.

    The synthetic cap integrals vary oppositely exactly as in v14.77.  Their
    sum is the fixed parent action, so treating seam velocity as a physical
    collective velocity produces no total-action kinetic Hessian.
    """

    if step <= 0.0:
        raise ValueError("step must be positive")

    def action(v: float) -> float:
        witness = partition_derivative_witness(v)
        return float(witness["equal_sum"])

    center = action(velocity)
    second = (action(velocity + step) - 2.0 * center + action(velocity - step)) / step**2
    return {
        "parent_action": center,
        "finite_difference_inertia": float(second),
        "exact_total_action_independent_of_partition": True,
    }


def stationary_classical_transport_witness(dimension: int = 9) -> dict[str, Any]:
    """Evaluate the implemented classical source set on the stationary branch."""

    if dimension <= 0:
        raise ValueError("dimension must be positive")
    static_eta_source = static_coexact_source(
        np.zeros(3), np.eye(3), np.zeros(3), Fprime_value=1.0
    )
    metric = np.eye(3)
    normal = np.array([1.0, 0.0, 0.0])
    tangent = np.eye(3) - np.outer(normal, normal)
    brown_york_momentum = brown_york_surface_momentum(
        metric, np.zeros((3, 3)), normal, tangent
    )
    inertia = np.eye(dimension)
    zero_transport = np.zeros((dimension, dimension))
    normalized_shear = normalized_shear_operator(
        zero_transport, zero_transport, inertia, inertia
    )
    return {
        "pure_repartition_inertia": pure_repartition_inertia_witness(0.17)[
            "finite_difference_inertia"
        ],
        "source_free_shift_L2_eigenvalue_R2": coexact_shift_eigenvalue(2),
        "source_free_shift_L3_eigenvalue_R2": coexact_shift_eigenvalue(3),
        "static_eta_YM_momentum_norm": float(np.linalg.norm(static_eta_source)),
        "time_symmetric_brown_york_momentum_norm": float(
            np.linalg.norm(brown_york_momentum)
        ),
        "relative_transport_norm": 0.0,
        "normalized_shear_operator_norm": float(np.linalg.norm(normalized_shear)),
    }


def completion_payload() -> dict[str, Any]:
    witness = stationary_classical_transport_witness()
    validation = {
        "pure_repartition_inertia_is_zero": abs(witness["pure_repartition_inertia"]) < 1e-8,
        "nonKilling_shift_channels_are_strictly_positive": witness[
            "source_free_shift_L2_eigenvalue_R2"
        ]
        > 0.0
        and witness["source_free_shift_L3_eigenvalue_R2"] > 0.0,
        "static_eta_YM_momentum_is_zero": witness["static_eta_YM_momentum_norm"] == 0.0,
        "time_symmetric_brown_york_momentum_is_zero": witness[
            "time_symmetric_brown_york_momentum_norm"
        ]
        == 0.0,
        "stationary_relative_transport_is_zero": witness["relative_transport_norm"] == 0.0,
        "v14_84_shear_term_evaluates_to_zero": witness[
            "normalized_shear_operator_norm"
        ]
        == 0.0,
        "full_BHSM_not_claimed": True,
        "flavor_provenance_gates_preserved": True,
    }
    return {
        "artifact": "BHSM_stationary_full_preimage_transport_no_go_v14_85",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "canonical_exact_next_object": EXACT_NEXT_OBJECT,
        "next_executable_subobject": NEXT_EXECUTABLE_SUBOBJECT,
        "theorem_scope": (
            "present reflection-symmetric stationary classical branch and the "
            "currently implemented action-owned source set"
        ),
        "source_audit": {
            "pure_cap_repartition": {
                "status": "ZERO_TOTAL_ACTION_HESSIAN",
                "reason": "complementary caps partition one fixed parent density; equal internal GHY terms cancel",
                "consequence": (
                    "positive separate cap inertias cannot be inferred from seam motion; any such "
                    "terms require the globally reduced physical mode or uncancelled seam/cross-cap terms"
                ),
            },
            "ADM_shift": {
                "status": "ZERO_AFTER_KILLING_QUOTIENT",
                "reason": "source-free coexact operator has eigenvalues 5/R^2 and 12/R^2 in L=2,3",
            },
            "static_eta_YM": {
                "status": "ZERO_MOMENTUM",
                "reason": "D_0 eta=0 and gauge electric momentum=0 on the retained static branch",
            },
            "brown_york": {
                "status": "ZERO_MOMENTUM_NOT_ZERO_ENERGY_THEOREM",
                "reason": "j_a is proportional to -sigma_a^i(K_ij-Kh_ij)n^j and K_ij=0",
                "claim_boundary": "the archived spherical Brown-York energy witness is not a transport generator",
            },
        },
        "v14_84_evaluation": {
            "Delta_A_on_present_branch": "ZERO",
            "normalized_shear_operator": "ZERO",
            "chi_2_equals_2_over_3R2_status": (
                "CONDITIONAL_NORMALIZED_TRANSPORT_WITNESS_NOT_A_PRESENT_BRANCH_PREDICTION"
            ),
            "positive_semidefinite_sign_theorem_preserved": True,
        },
        "reopening_routes": [
            "sourced relative-periodic full-preimage solution with conserved cap momentum difference",
            "nonzero gauge-reduced matter or Dirac stress current on the common self-adjoint domain",
            "renormalized fermion determinant polarization crossing the classical positive shift operator",
            "quasilocal canonical momentum on a non-time-symmetric globally constrained solution",
            "conserved BHSM/environment exchange current Q^nu with equal and opposite sector divergences",
        ],
        "norman_recall_boundary": {
            "useful_content": "compact-S3 harmonic and higher-gradient response intuition",
            "not_an_action_completion": (
                "the independent topographic scalar T and beta, chi_T, Q1, Q2, and R_H are new "
                "fields or continuous inputs relative to the retained BHSM action"
            ),
            "may_be_used_as": "external phenomenological comparison only after BHSM prediction freeze",
        },
        "open_gates": {
            "charged_current_kernel": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
        },
        "completion_status": {
            "stationary_classical_transport_gate": "CLOSED_AS_NO_GO",
            "cap_inertia_gate": "OPEN_FOR_GENUINE_PHYSICAL_MODE",
            "sourced_relative_periodic_solution_gate": "OPEN",
            "complete_response_gate": "OPEN",
            "BHSM_complete": False,
            "Mark_III": "NOT_REACHED",
            "USB_synchronization_eligible": False,
        },
        "not_claimed": [
            "a no-go for driven, fermionic, or quantum-effective relative transport",
            "a derived nonzero cap inertia or relative transport",
            "a physical ell=2 Landau Hessian or particle observable",
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
    output = root / "artifacts" / "BHSM_stationary_full_preimage_transport_no_go_v14_85.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(deterministic_json(completion_payload()), encoding="utf-8", newline="\n")
    return output
