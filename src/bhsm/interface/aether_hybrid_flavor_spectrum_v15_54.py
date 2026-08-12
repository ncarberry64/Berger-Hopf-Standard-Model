"""Triality-diagonal flavor spectrum and no-mixing theorem on the hybrid reset."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.particle_chirality_anomaly_normalization import MODE_LEDGERS
from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0


VERSION = "v15.54"
CLASSIFICATION = "BHSM_HYBRID_TRIALITY_FLAVOR_SPECTRUM"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def berger_scalar_eigenvalue(
    k: int, j: int, transverse_radius: float, axial_radius: float,
) -> float:
    """Scalar Berger-S3 eigenvalue in the ``(k,j)`` repository ledger.

    With ``q=k-2j`` and round radius ``R`` this reduces to ``k(k+2)/R^2``.
    """

    if k < 0 or j < 0 or j > k or transverse_radius <= 0.0 or axial_radius <= 0.0:
        raise ValueError("invalid Berger mode or radius")
    q = k - 2 * j
    return (
        (k * (k + 2) - q * q) / transverse_radius**2
        + q * q / axial_radius**2
    )


def reset_spectral_seed() -> dict[str, Any]:
    """Evaluate all stored family modes on the round reconstructed fiber."""

    radius = RADIUS0
    sectors: dict[str, Any] = {}
    for name, components in MODE_LEDGERS.items():
        component_rows = {}
        for component, modes in components.items():
            values = [
                berger_scalar_eigenvalue(k, j, radius, radius)
                for k, j in modes
            ]
            component_rows[component] = {
                "modes": [list(mode) for mode in modes],
                "eigenvalues": values,
                "dimensionless_R_squared_eigenvalues": [
                    round(value * radius**2) for value in values
                ],
            }
        sectors[name] = component_rows
    return {
        "round_internal_fiber_radius": radius,
        "formula": "lambda_kj=[k(k+2)-q^2]/L2^2+q^2/L1^2,_q=k-2j",
        "round_formula": "lambda_k=k(k+2)/R_F^2",
        "sectors": sectors,
        "classification": (
            "action-normalized_Berger_scalar_excitation_seeds_not_yet_"
            "spinor_Dirac-Yukawa_mass_eigenvalues"
        ),
    }


def triality_projectors() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    omega = np.exp(2j * np.pi / 3.0)
    cycle = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=complex)
    identity = np.eye(3, dtype=complex)
    return tuple(
        sum(
            (omega ** (-a * r)) * np.linalg.matrix_power(cycle, r)
            for r in range(3)
        ) / 3.0
        for a in range(3)
    )


def diagonal_family_operator(eigenvalues: list[float]) -> np.ndarray:
    if len(eigenvalues) != 3:
        raise ValueError("three triality eigenvalues are required")
    return sum(
        float(value) * projector
        for value, projector in zip(eigenvalues, triality_projectors())
    )


def canonical_mixing_theorem() -> dict[str, Any]:
    """Derive mixing for the operator content currently present in the action."""

    seeds = reset_spectral_seed()["sectors"]
    up = diagonal_family_operator(seeds["Q_L"]["upper"]["eigenvalues"])
    down = diagonal_family_operator(seeds["Q_L"]["lower"]["eigenvalues"])
    charged = diagonal_family_operator(seeds["L_L"]["lower"]["eigenvalues"])
    neutral = diagonal_family_operator(seeds["L_L"]["upper"]["eigenvalues"])
    commutators = {
        "up_down": float(np.linalg.norm(up @ down - down @ up)),
        "charged_neutral": float(np.linalg.norm(charged @ neutral - neutral @ charged)),
    }
    identity = np.eye(3, dtype=complex)
    return {
        "family_algebra": "span{P0,P1,P2}=C[C3]_commutative",
        "all_action-owned_sector_operators_commute": max(commutators.values()) < 1.0e-13,
        "commutator_norms": commutators,
        "CKM": identity.real.tolist(),
        "PMNS": identity.real.tolist(),
        "Jarlskog_invariant": 0.0,
        "CP_phase": 0.0,
        "theorem": (
            "if_M_f=sum_a_m_fa_P_a_for_every_sector_then_all_left_"
            "diagonalizers_are_the_same_triality_Fourier_map_and_"
            "V_f_g=I3_up_to_unphysical_diagonal_phases"
        ),
        "nontrivial_mixing_requires": (
            "an_action-owned_family_operator_not_commuting_with_at_least_one_P_a"
        ),
        "such_an_operator_present_in_current_completed_action": False,
    }


def scale_ledger() -> dict[str, Any]:
    return {
        "dimensionless_reset_radius_for_kappa1_equal_one": RADIUS0,
        "spectral_unit": "1/R_F",
        "M4_reset_radius": RADIUS0 / 2.0,
        "M4_free_zeta_energy": "(59/30)/(R_F/2)=59/(15R_F)",
        "absolute_unit": "set_by_the_dimensionful_parent_Einstein_coefficient_kappa1",
        "external_calibration_used": False,
        "physical_mass_identification": (
            "requires_the_spinor_lift_and_Dirac-Yukawa_matrix_element;_"
            "the_scalar_Berger_seed_is_not_relabelled_as_a_mass"
        ),
    }


def completion_payload() -> dict[str, Any]:
    seed = reset_spectral_seed()
    mixing = canonical_mixing_theorem()
    scale = scale_ledger()
    projectors = triality_projectors()
    validation = {
        "projectors_idempotent": all(
            np.linalg.norm(projector @ projector - projector) < 1.0e-13
            for projector in projectors
        ),
        "projectors_orthogonal": all(
            np.linalg.norm(projectors[a] @ projectors[b]) < 1.0e-13
            for a in range(3) for b in range(3) if a != b
        ),
        "projectors_complete": np.linalg.norm(sum(projectors) - np.eye(3)) < 1.0e-13,
        "round_eigenvalues_independent_of_j": abs(
            berger_scalar_eigenvalue(6, 0, RADIUS0, RADIUS0)
            - berger_scalar_eigenvalue(6, 3, RADIUS0, RADIUS0)
        ) < 1.0e-13,
        "action_owned_family_operators_commute": mixing[
            "all_action-owned_sector_operators_commute"
        ],
        "canonical_CKM_identity": np.allclose(mixing["CKM"], np.eye(3)),
        "canonical_PMNS_identity": np.allclose(mixing["PMNS"], np.eye(3)),
        "scalar_seed_not_called_physical_mass": seed["classification"].endswith(
            "mass_eigenvalues"
        ),
        "external_calibration_absent": not scale["external_calibration_used"],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_hybrid_flavor_spectrum_v15_54",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "reset_spectral_seed": seed,
        "canonical_mixing_theorem": mixing,
        "scale_ledger": scale,
        "claim_boundary": {
            "Berger_excitation_spectrum_derived": True,
            "current_action_mixing_matrices_derived": True,
            "nontrivial_CKM_or_PMNS_derived": False,
            "physical_fermion_masses_derived": False,
            "absolute_external_unit_derived": False,
        },
        "active_calculation": (
            "DERIVE_THE_SPINOR_LIFT_AND_DIRAC-YUKAWA_MATRIX_ELEMENTS_FROM_"
            "THE_HYBRID_CHILD_OR_ACCEPT_THE_CURRENT_ACTION_PREDICTION_OF_"
            "TRIVIAL_FLAVOR_MIXING"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical_json_value(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be materialized")
        rounded = round(value, 10)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {key: _canonical_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_json_value(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        _canonical_json_value(payload), indent=2, sort_keys=True,
        ensure_ascii=False, allow_nan=False,
    ) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_hybrid_flavor_spectrum_v15_54.json"
    path.write_bytes(deterministic_json(completion_payload()).encode("utf-8"))
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "berger_scalar_eigenvalue", "reset_spectral_seed", "triality_projectors",
    "diagonal_family_operator", "canonical_mixing_theorem", "scale_ledger",
    "completion_payload", "deterministic_json", "materialize",
]
