from __future__ import annotations

from dataclasses import asdict, dataclass
from math import pi
from typing import Dict, Tuple

import numpy as np


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

STATUS_TABLE = {
    "single_sector_spectrum_phase_invariance": (
        "DERIVED_CONDITIONAL_ON_TRIDIAGONAL_TREE_REPHASING"
    ),
    "boundary_relative_holonomy_CP_source": "STRUCTURALLY_MOTIVATED_CANDIDATE",
    "Z6_boundary_phase_holonomy": "STRUCTURALLY_MOTIVATED_CANDIDATE",
    "CKM_CP_closure": "OPEN",
    "PMNS_CP_closure": "OPEN",
}


@dataclass(frozen=True)
class RelativeHolonomyDiagnostic:
    phi_a_01: float
    phi_a_12: float
    phi_b_01: float
    phi_b_12: float
    relative_holonomy: float
    nontrivial: bool
    primitive_phase: str
    cp_smallness_note: str


def complex_tridiagonal(
    lambda0: float,
    lambda1: float,
    lambda2: float,
    beta: float,
    kappa: float,
    phi01: float,
    phi12: float,
) -> np.ndarray:
    edge01 = beta * np.exp(1j * phi01)
    edge12 = kappa * np.exp(1j * phi12)
    return np.array(
        [
            [lambda0, edge01, 0.0],
            [np.conjugate(edge01), lambda1, edge12],
            [0.0, np.conjugate(edge12), lambda2],
        ],
        dtype=complex,
    )


def real_tridiagonal(
    lambda0: float,
    lambda1: float,
    lambda2: float,
    beta: float,
    kappa: float,
) -> np.ndarray:
    return complex_tridiagonal(lambda0, lambda1, lambda2, beta, kappa, 0.0, 0.0)


def rephasing_matrix(phi01: float, phi12: float) -> np.ndarray:
    return np.diag([1.0, np.exp(-1j * phi01), np.exp(-1j * (phi01 + phi12))])


def rephase_real_chain(real_matrix: np.ndarray, phi01: float, phi12: float) -> np.ndarray:
    phase = rephasing_matrix(phi01, phi12)
    return phase @ real_matrix @ np.conjugate(phase.T)


def single_sector_eigenvalues_preserved(
    phi01: float = pi / 3,
    phi12: float = pi / 6,
) -> bool:
    real = real_tridiagonal(0.0, 3.0, 5.0, 1.0 / 3.0, 1.0 / 6.0)
    complex_matrix = complex_tridiagonal(0.0, 3.0, 5.0, 1.0 / 3.0, 1.0 / 6.0, phi01, phi12)
    return bool(np.allclose(np.linalg.eigvalsh(real), np.linalg.eigvalsh(complex_matrix)))


def relative_holonomy(phi_a_01: float, phi_a_12: float, phi_b_01: float, phi_b_12: float) -> float:
    return (phi_b_01 + phi_b_12) - (phi_a_01 + phi_a_12)


def primitive_z6_phase() -> complex:
    return np.exp(1j * pi / 3)


def diagnostic() -> RelativeHolonomyDiagnostic:
    phi = relative_holonomy(0.0, 0.0, pi / 3, 0.0)
    return RelativeHolonomyDiagnostic(
        phi_a_01=0.0,
        phi_a_12=0.0,
        phi_b_01=pi / 3,
        phi_b_12=0.0,
        relative_holonomy=phi,
        nontrivial=abs(phi) > 1e-12,
        primitive_phase="exp(i*pi/3)",
        cp_smallness_note="No direct 0<->2 bridge; CP-odd leakage is second order in beta*kappa.",
    )


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-boundary-relative-holonomy-CP-v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "single_sector_eigenvalues_preserved": single_sector_eigenvalues_preserved(),
        "diagnostic": asdict(diagnostic()),
        "statuses": STATUS_TABLE,
        "claim_boundary": "Boundary relative holonomy is a CP source candidate only; CP numerical closure remains open.",
    }
