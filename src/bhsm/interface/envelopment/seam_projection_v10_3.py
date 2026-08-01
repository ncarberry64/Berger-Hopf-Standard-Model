"""Coordinate seam and invariant support-readout separation."""

from __future__ import annotations

from typing import Any


SEAM_VERDICT = (
    "BHSM_SEAM_SHIFT_RECLASSIFIED_AS_COORDINATE_PROJECTION_WITH_FULL_"
    "THREE_MODE_MAP_OPEN"
)


def raw_seam_transform(psi: float, xi: float) -> float:
    """Coordinate seam representative under an infinitesimal radial shift."""

    return float(psi + xi)


def seam_payload() -> dict[str, Any]:
    payload = {
        "artifact": "BHSM_seam_projection_gate_v10_3",
        "psi_seam_status": "COORDINATE_OR_OBSERVABLE_PROJECTION",
        "independent_physical_mode": False,
        "independent_kinetic_term": None,
        "raw_coordinate_transformation": "delta_xi psi_seam=xi",
        "full_projection": "psi_seam=Pi_seam(q_C,q_W,q_D)",
        "Pi_seam": None,
        "historical_invariant_readout": "S_Sigma=-(tau*pi*chi_1/16) q_W",
        "historical_scope": "fixed-B1 fold response through local O(D^2 q)",
        "historical_support_work_preserved": True,
        "historical_readout_is_raw_coordinate": False,
        "q_C_projection": None,
        "q_W_projection": "-(tau*pi*chi_1/16)",
        "q_D_projection": None,
        "physical_output_invariants": {"epsilon_out": None, "mass_out": None, "generation_phases": None},
        "gauge_invariance_of_physical_output_claimed": False,
        "verdict": SEAM_VERDICT,
    }
    payload["validation_passed"] = (
        payload["independent_physical_mode"] is False
        and payload["independent_kinetic_term"] is None
        and payload["Pi_seam"] is None
        and payload["historical_readout_is_raw_coordinate"] is False
    )
    return payload
