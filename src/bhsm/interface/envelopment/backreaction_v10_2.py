"""Localized-to-global stress ownership and backreaction obstruction."""

from __future__ import annotations

from typing import Any

import numpy as np


BACKREACTION_VERDICT = "BHSM_LOCALIZED_NORMAL_STRESS_PULLBACK_NOT_DERIVED"


def normal_stress(stress: np.ndarray, normal: np.ndarray) -> float:
    """Return T_AB n^A n^B on a common declared tensor domain."""

    tensor = np.asarray(stress, dtype=float)
    vector = np.asarray(normal, dtype=float)
    if tensor.ndim != 2 or tensor.shape[0] != tensor.shape[1] or vector.shape != (tensor.shape[0],):
        raise ValueError("stress must be square and normal must match")
    return float(vector @ tensor @ vector)


def stress_ownership() -> list[dict[str, Any]]:
    return [
        {"sector": "geometry", "domain": "M8/M5/M4 by action stratum", "stress_or_equation": "Einstein tensor/metric Euler equation", "common_M8_tensor": False},
        {"sector": "chi", "domain": "M8", "stress_or_equation": "explicit from S8^env", "common_M8_tensor": True},
        {"sector": "sigma", "domain": "M8 plus independent M5 wall scalar", "stress_or_equation": "explicit per owner; equality across strata not proved", "common_M8_tensor": False},
        {"sector": "eta", "domain": "M8", "stress_or_equation": "explicit unit-spinor texture stress", "common_M8_tensor": True},
        {"sector": "gauge", "domain": "M4 intrinsic and conditional retained bundles", "stress_or_equation": "intrinsic stress only", "common_M8_tensor": False},
        {"sector": "M4 matter", "domain": "M4 intrinsic seam", "stress_or_equation": "intrinsic EFT stress", "common_M8_tensor": False},
        {"sector": "matcher", "domain": "M4 compatibility locus", "stress_or_equation": "algebraic metric matching response", "common_M8_tensor": False},
    ]


def cross_stratum_gate() -> dict[str, Any]:
    return {
        "complete_T_AB_total_on_one_domain": None,
        "M4_to_M8_stress_pushforward": None,
        "M4_to_M5_normal_stress": "metric junction response exists, but fixed embedding has no shape equation",
        "delta2S_da_F_delta_Psi": 0,
        "delta2S_da_F_delta_H": 0,
        "source": "v7.3 action-incidence audit",
        "localized_eta_backreacts_on_M8_metric": "formal stress source yes; localized orbit solution no",
        "localized_source_zero_recovers_background": True,
        "localized_source_modifies_physical_buoyancy_equation": False,
    }


def compactness_gate() -> dict[str, Any]:
    return {
        "E_perp_candidate": "T_AB n^A n^B",
        "T_parallel_candidate": "h^AB T_AB",
        "C_env_candidate": "localized action energy/effective support volume",
        "action_selected_support": None,
        "common_stress_domain": None,
        "gauge_invariant_compactness_observable": None,
        "compactness_value": None,
        "d_psi_star_d_C_env": None,
        "d_a_F_star_d_C_env": None,
        "sign": "UNDERDETERMINED",
        "desired_negative_sign_inserted": False,
    }


def backreaction_payload() -> dict[str, Any]:
    rows = stress_ownership()
    gate = cross_stratum_gate()
    compactness = compactness_gate()
    validation = {
        "eta_owner_present": next(row for row in rows if row["sector"] == "eta")["common_M8_tensor"],
        "complete_stress_absent": gate["complete_T_AB_total_on_one_domain"] is None,
        "cross_blocks_zero": gate["delta2S_da_F_delta_Psi"] == gate["delta2S_da_F_delta_H"] == 0,
        "zero_source_background": gate["localized_source_zero_recovers_background"],
        "compactness_fails_closed": compactness["gauge_invariant_compactness_observable"] is None,
        "sign_not_inserted": not compactness["desired_negative_sign_inserted"],
    }
    return {
        "artifact": "BHSM_local_envelopment_backreaction_v10_2",
        "stress_ownership": rows,
        "cross_stratum_gate": gate,
        "compactness": compactness,
        "verdict": BACKREACTION_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
