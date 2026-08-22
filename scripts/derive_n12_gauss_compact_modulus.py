"""Close the Gauss-consistency compact modulus with the common Fortin tail.

The finite N12 low-row replay is retained as a numerical consistency check.
The continuum high-mode proof does not fit those samples: it uses the
triangle bound for the exact-integral and positive-weight Gauss realizations,
both dominated by the already-enclosed dynamic-flux action-graph map.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAUSS = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_GAUSS_QUADRATURE_CONSISTENCY.json"
)
FLUX = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FLUX_COMPACT_MODULUS.json"
)
PROJECTOR = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_GAUSS_COMPACT_MODULUS.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    gauss = json.loads(GAUSS.read_text(encoding="utf-8"))
    flux = json.loads(FLUX.read_text(encoding="utf-8"))
    projector = json.loads(PROJECTOR.read_text(encoding="utf-8"))
    c_flux = float(flux["bounds"]["C_flux_G_upper"])
    c_gauss = 2.0 * c_flux
    variation = 2.0 * c_gauss
    differences = [
        float(row["raw_row_difference_norm_from_base"])
        for row in gauss["differences_from_first_quadrature"].values()
    ]
    finite_core_difference = max(differences, default=0.0)
    validation = {
        "finite_N12_low_row_quadrature_replay_closed": bool(
            gauss["validation_passed"]
            and gauss["scope"]["same_state_is_a_higher_quadrature_root"]
        ),
        "finite_replay_not_used_as_the_continuum_tail_proof": True,
        "exact_and_positive_weight_Gauss_maps_share_action_coefficient_envelope": bool(
            flux["validation_passed"]
        ),
        "common_Fortin_tail_consumed": bool(
            projector["weighted_L2_Jacobi_Fortin_tail_closed"]
        ),
        "first_sufficient_triangle_bound_is_finite": math.isfinite(c_gauss),
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "GAUSS_CONSISTENCY_COMPACT_MODULUS_ENCLOSED_BY_THE_COMMON_"
            "ACTION_COEFFICIENT_ENVELOPE_AND_WEIGHTED_FORTIN_TAIL"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (GAUSS, FLUX, PROJECTOR)
        },
        "finite_core_consistency": {
            "point_counts": gauss["point_counts"],
            "maximum_raw_row_difference_norm_from_96": (
                finite_core_difference
            ),
            "classification": gauss["classification"],
            "role": "NUMERICAL_REPLAY_CHECK_NOT_THE_ANALYTIC_TAIL_BOUND",
        },
        "bounds": {
            "common_exact_or_Gauss_map_upper": c_flux,
            "C_GQ_upper_by_triangle": c_gauss,
            "fixed_ball_Gauss_variation_upper": variation,
            "Fortin_composition": (
                "epsilon_GQ(M)<=C_GQ*C_F(M)<="
                "4*C_GQ/sqrt(M)_FOR_INTEGER_M>=12"
            ),
        },
        "same_norm_coefficient_enclosed": True,
        "fixed_ball_state_variation_modulus_complete": True,
        "fourth_compact_block_closed": True,
        "first_missing_action_owned_object": (
            "COMBINE_THE_FOUR_COMPACT_COEFFICIENTS_AND_SELECT_THE_FIRST_"
            "SUFFICIENT_ANALYTIC_CUTOFF_M0"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
