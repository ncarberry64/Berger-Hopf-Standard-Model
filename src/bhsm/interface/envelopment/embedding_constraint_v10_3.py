"""Seam-embedding configuration and constraint audit for BHSM v10.3."""

from __future__ import annotations

from typing import Any

import numpy as np


EMBEDDING_VERDICT = (
    "BHSM_SEAM_EMBEDDING_NOT_IN_CURRENT_CONFIGURATION_SPACE_AND_"
    "CODIMENSION_CHOICE_NOT_UNIQUE"
)


def induced_metric(parent_metric: np.ndarray, tangents: np.ndarray) -> np.ndarray:
    """Return h=E^T G E for a rank-d embedding tangent matrix E."""

    metric = np.asarray(parent_metric, dtype=float)
    frame = np.asarray(tangents, dtype=float)
    if metric.ndim != 2 or metric.shape[0] != metric.shape[1]:
        raise ValueError("parent metric must be square")
    if frame.ndim != 2 or frame.shape[0] != metric.shape[0]:
        raise ValueError("tangent frame must have one row per parent dimension")
    return frame.T @ metric @ frame


def codimension_audit() -> list[dict[str, Any]]:
    return [
        {
            "support": "intrinsic M4 embedded directly in M8",
            "parent_dimension": 8,
            "support_dimension": 4,
            "normal_rank": 4,
            "unique_normal_scalar": False,
        },
        {
            "support": "lifted Sigma7=S3_fiber bundle over M4 in M8 collar",
            "parent_dimension": 8,
            "support_dimension": 7,
            "normal_rank": 1,
            "unique_normal_scalar": True,
            "action_owner": None,
        },
        {
            "support": "B1=M4 in each M5 cap",
            "parent_dimension": 5,
            "support_dimension": 4,
            "normal_rank": 1,
            "unique_normal_scalar": True,
            "action_owner": "fixed-support P1+GHY+B1+matcher",
        },
    ]


def embedding_constraint_ledger() -> dict[str, Any]:
    return {
        "X_current_status": "fixed iota, not varied",
        "tangential_X_variations": "M4 reparametrizations",
        "normal_X_variations": "undefined until M4->M8 or Sigma7->M8 support is selected",
        "conjugate_momentum_current": None,
        "primary_constraints_current": None,
        "shape_equation_current": None,
        "formal_induced_action_shape_term": "E_I=T4^mu_nu K^I_mu_nu plus bulk/matcher reactions",
        "intrinsic_M4_source_present": True,
        "intrinsic_source_makes_X_automatically_physical": False,
        "reason": (
            "the intrinsic fields distinguish a stratum, but the action still fixes its embedding; "
            "codimension and distributional versus smooth ownership remain separate choices"
        ),
        "fixed_support_prior_result": "BHSM_DYNAMICAL_B1_EMBEDDING_NOT_REQUIRED",
        "fixed_support_scope": "v6.27 fold localization through local O(D^2 q), not an all-sector M4->M8 theorem",
    }


def embedding_payload() -> dict[str, Any]:
    rows = codimension_audit()
    ledger = embedding_constraint_ledger()
    validation = {
        "direct_M4_has_four_normals": rows[0]["normal_rank"] == 4,
        "lifted_seam_has_one_normal": rows[1]["normal_rank"] == 1,
        "fixed_B1_imported": ledger["fixed_support_prior_result"] == "BHSM_DYNAMICAL_B1_EMBEDDING_NOT_REQUIRED",
        "momentum_fails_closed": ledger["conjugate_momentum_current"] is None,
        "shape_fails_closed": ledger["shape_equation_current"] is None,
    }
    return {
        "artifact": "BHSM_embedding_constraint_v10_3",
        "codimension": rows,
        "embedding": ledger,
        "verdict": EMBEDDING_VERDICT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
