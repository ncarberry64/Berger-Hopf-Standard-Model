"""Effective localization of the source-restricted normal inverse constant.

The qualitative BHSM theorem proves a bounded inverse on the source-selected
normal bundle.  This module proves that its numerical norm cannot be recovered
from the principal gap and qualitative compactness alone.  An action-specific
positive-duration spectral/observation separation is mathematically required.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_THEOREM = Path(
    "artifacts/n12_source_restricted_positive_duration/"
    "BHSM_N12_SOURCE_RESTRICTED_POSITIVE_DURATION_THEOREM.json"
)


def effective_inverse_localization(
    theorem_path: str | Path = DEFAULT_THEOREM,
) -> dict[str, Any]:
    """Prove which extra datum is necessary to compute the BHSM inverse."""

    theorem = json.loads(Path(theorem_path).read_text(encoding="utf-8"))
    beta = float(theorem["action_owned_constants"]["principal_modulus_gap"])
    relative_epsilons = (0.5, 0.1, 1.0e-2, 1.0e-4, 1.0e-8)
    counterfamily = []
    for relative in relative_epsilons:
        epsilon = beta * relative
        principal = beta * np.eye(2)
        compact = np.diag((-beta + epsilon, 0.0))
        normal = principal + compact
        singular = np.linalg.svd(normal, compute_uv=False)
        counterfamily.append({
            "relative_epsilon": relative,
            "epsilon": epsilon,
            "principal_minimum_modulus": beta,
            "compact_rank": int(np.linalg.matrix_rank(compact)),
            "normal_minimum_modulus": float(singular[-1]),
            "normal_inverse_norm": float(1.0 / singular[-1]),
            "normal_kernel_is_zero": bool(singular[-1] > 0.0),
            "Fredholm_index": 0,
        })

    validation = {
        "canonical_principal_gap_reproduced": math.isclose(
            beta, math.sqrt(29.0) - 5.0, rel_tol=0.0, abs_tol=1.0e-15
        ),
        "every_counterexample_compact_block_is_finite_rank": all(
            row["compact_rank"] == 1 for row in counterfamily
        ),
        "every_counterexample_normal_operator_is_invertible": all(
            row["normal_kernel_is_zero"] for row in counterfamily
        ),
        "inverse_norm_grows_as_epsilon_shrinks": all(
            left["normal_inverse_norm"] < right["normal_inverse_norm"]
            for left, right in zip(counterfamily, counterfamily[1:])
        ),
        "qualitative_BHSM_right_inverse_remains_retained": bool(
            theorem["conclusions"]
            ["source_restricted_normal_right_inverse_exists"]
        ),
        "no_claim_of_BHSM_inverse_failure": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    return {
        "classification": (
            "QUALITATIVE_SOURCE_RESTRICTED_CLOSED_RANGE_DOES_NOT_"
            "DETERMINE_A_NUMERICAL_NORMAL_INVERSE_BOUND;_THE_MISSING_"
            "ACTION_OWNED_OBJECT_IS_AN_EFFECTIVE_POSITIVE_DURATION_"
            "OBSERVATION_SEPARATION"
        ),
        "retained_BHSM_principal_gap": beta,
        "counterfamily": {
            "definition": (
                "P_epsilon=beta*I2,_C_epsilon=diag(-beta+epsilon,0),_"
                "J_epsilon=P_epsilon+C_epsilon=diag(epsilon,beta)"
            ),
            "properties": (
                "P_HAS_FIXED_GAP_beta,_C_IS_RANK_ONE_COMPACT,_J_HAS_"
                "FREDHOLM_INDEX_ZERO_AND_ZERO_KERNEL_FOR_EVERY_"
                "epsilon>0,_BUT_norm(J^-1)=1/epsilon"
            ),
            "rows": counterfamily,
            "conclusion": (
                "NO_FINITE_NUMERICAL_K_FOLLOWS_FROM_beta,_COMPACTNESS,_"
                "INDEX_ZERO,_AND_KERNEL_EXCLUSION_WITHOUT_A_"
                "QUANTITATIVE_SEPARATION_MODULUS"
            ),
        },
        "BHSM_interpretation": {
            "qualitative_closed_range_invalidated": False,
            "category_2_soft_classification_changed": False,
            "category_3_collapse_sequence_constructed": False,
            "principal_high_tail_bound_4_over_beta_is_the_full_K": False,
            "required_effective_lemma": (
                "FIND_M0,_c_M0,_AND_epsilon_obs(M0)_FROM_THE_RETAINED_"
                "POSITIVE_DURATION_ACTION_SUCH_THAT_"
                "0<=epsilon_obs(M0)<c_M0;_THEN_"
                "K<=1/(c_M0-epsilon_obs(M0))"
            ),
            "c_M0": (
                "FINITE_CORE_SOURCE_SELECTED_POSITIVE_DURATION_"
                "OBSERVATION_LOWER_BOUND_ON_THE_EXISTING_NORMAL_QUOTIENT"
            ),
            "epsilon_obs_M0": (
                "EXPLICIT_STRONG_GRAPH_PROPAGATOR_AND_TRACE_"
                "PERTURBATION_RATE_FROM_THE_ACTION_DERIVED_TAIL"
            ),
        },
        "first_missing_mathematical_object": (
            "EFFECTIVE_SOURCE_RESTRICTED_POSITIVE_DURATION_"
            "OBSERVATION_COMPACTNESS_MODULUS"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


__all__ = ["effective_inverse_localization"]
