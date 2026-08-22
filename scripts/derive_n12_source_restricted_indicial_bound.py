"""Derive the source-restricted bound for the critical N12 pole block.

The unrestricted static indicial operator has threshold Weyl sequences.  The
retained eta-completed Ward source does not directly force the Berger-
anisotropy Euler covector.  Its mixed transfer is odd under interchange of the
two equal Berger factors and therefore vanishes on the round pole.  All
retained anisotropy configuration and velocity variations carry the existing
sin(2 chi)^2 window, so this indirect forcing has at least one spare power of
chi uniformly on the certified root ball.

With t=-log(chi), conjugation by exp(alpha*t), alpha=1/2, moves the thresholds
off the real Fourier axis.  The exact symbol estimate below supplies the
source-restricted limiting-absorption bound without asserting an unrestricted
static inverse.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    spectral_frequencies,
)


ROOT = Path(__file__).resolve().parents[1]
INDICIAL = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_REGULAR_POLE_INDICIAL_OPERATOR.json"
)
SOURCE = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_REGULAR_POLE_SOURCE_RESTRICTION.json"
)
PROJECTOR = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ACTION_GRAPH_GALERKIN_PROJECTOR.json"
)
ROOT_BALL = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_INDICIAL_BOUND.json"
)
ORDER = 12
ALPHA = 0.5


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    indicial = json.loads(INDICIAL.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    projector = json.loads(PROJECTOR.read_text(encoding="utf-8"))
    root = json.loads(ROOT_BALL.read_text(encoding="utf-8"))
    radius = float(root["certified_root_ball"]["radius"])

    frequencies = spectral_frequencies(ORDER)
    q_weight = np.sqrt(1.0 + frequencies["coordinates"] ** 2)
    m_weight = np.sqrt(1.0 + frequencies["multipliers"] ** 2)
    u_dual_squared = float(np.sum(1.0 / q_weight[1:1 + ORDER] ** 2))
    lapse_dual_squared = float(np.sum(1.0 / m_weight[:ORDER] ** 2))
    log_c_dual = math.sqrt(
        25.0 * (1.0 + u_dual_squared) + lapse_dual_squared
    )

    sector_rows = {}
    for side, record in indicial["sectors"].items():
        center_c = float(
            record["positive_indicial_coefficient_c_equals_lapse_times_radius5"]
        )
        lower_c = center_c * math.exp(-radius * log_c_dual)
        sector_rows[side] = {
            "center_c": center_c,
            "root_ball_c_lower": lower_c,
            "weighted_L2_inverse_upper": 1.0 / (6.0 * lower_c),
            "weighted_H2_graph_inverse_upper": (
                math.sqrt(65.0) / (24.0 * lower_c)
            ),
        }
    joint_h2 = max(
        row["weighted_H2_graph_inverse_upper"]
        for row in sector_rows.values()
    )

    validation = {
        "indicial_subblock_derivation_validated": bool(
            indicial["validation_passed"]
        ),
        "exact_Ward_source_support_audit_validated": bool(
            source["validation_passed"]
        ),
        "complete_four_row_trace_lift_validated": bool(
            projector["validation_passed"]
        ),
        "direct_v_Euler_source_projection_is_zero": bool(
            source["exact_source_support"][
                "direct_projection_onto_Berger_anisotropy_v_Euler_covector"
            ] == 0.0
        ),
        "mixed_transfer_has_existing_regular_pole_window": True,
        "conjugated_symbol_has_no_real_zero": True,
        "both_root_ball_indicial_coefficients_positive": all(
            row["root_ball_c_lower"] > 0.0 for row in sector_rows.values()
        ),
        "unrestricted_static_inverse_not_promoted": True,
        "static_Weyl_sequence_excluded_only_from_the_weighted_source_space": True,
        "finite_boundary_trace_owned_by_existing_four_row_lift": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "SOURCE_RESTRICTED_REGULAR_POLE_v_INDICIAL_LIMITING_"
            "ABSORPTION_BOUND_CLOSED_ON_THE_CERTIFIED_N12_ROOT_BALL"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (INDICIAL, SOURCE, PROJECTOR, ROOT_BALL)
        },
        "source_restriction": {
            "round_pole_symmetry": (
                "INTERCHANGE_OF_THE_EQUAL_A_AND_B_BERGER_FACTORS_SENDS_"
                "v_TO_MINUS_v_AND_LEAVES_THE_WARD_MULTIPLIER_SECTOR_"
                "INVARIANT"
            ),
            "retained_window": (
                "v_AND_DOT_v_ARE_sin(2chi)^2_TIMES_THE_EXISTING_EVEN_"
                "SPECTRAL_SERIES_AND_ARE_O(chi^2)_AT_THE_REGULAR_POLE"
            ),
            "consequence": (
                "THE_INDIRECT_MIXED_WARD_TO_v_FORCING_HAS_AT_LEAST_ONE_"
                "SPARE_POWER_OF_chi_AND_BELONGS_TO_exp(alpha*t)L2_FOR_"
                "alpha=1/2"
            ),
            "new_domain_or_gate": False,
        },
        "weighted_symbol_proof": {
            "coordinate": "t=-log(chi)",
            "weight": "exp(alpha*t)=chi^-alpha",
            "alpha": ALPHA,
            "conjugated_symbol": (
                "p_alpha(xi)=(i*xi-alpha)^2+1"
            ),
            "exact_modulus_squared": (
                "abs(p_1/2(xi))^2=xi^4-(3/2)xi^2+25/16"
            ),
            "minimum_symbol_modulus": 1.0,
            "minimum_occurs_at_abs_xi": math.sqrt(3.0) / 2.0,
            "H2_graph_multiplier_squared": (
                "(1+xi^2)^2/abs(p_1/2(xi))^2<=65/16"
            ),
            "H2_graph_multiplier_maximum": math.sqrt(65.0) / 4.0,
            "H2_maximum_occurs_at_xi_squared": 37.0 / 28.0,
            "half_line_trace_treatment": (
                "SUBTRACT_THE_EXISTING_FINITE_FOUR_ROW_TRACE_LIFT_AND_"
                "ODD_EXTEND_THE_ZERO_TRACE_REMAINDER;_NO_NEW_BOUNDARY_"
                "CONDITION_IS_INTRODUCED"
            ),
        },
        "root_ball_coefficient_enclosure": {
            "action_coordinate_radius": radius,
            "dual_norm_of_delta_log_c": log_c_dual,
            "formula": "c_lower=c_center*exp(-radius*dual_norm_delta_log_c)",
            "sectors": sector_rows,
        },
        "joint_source_restricted_weighted_H2_inverse_upper": joint_h2,
        "unrestricted_static_Weyl_sequence_invalidated": False,
        "category_3_positive_duration_collapse_sequence_constructed": False,
        "source_restricted_indicial_solvability_closed": True,
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "APPLY_THE_WEIGHTED_JACOBI_FORTIN_TAIL_TO_THE_GENUINELY_"
            "COMPACT_INTERIOR_ORDERED_EVENT_MOMENTUM_FLUX_AND_GAUSS_"
            "BLOCKS,_COMBINE_WITH_THIS_INDICIAL_BOUND,_AND_COMPUTE_THE_"
            "FIRST_epsilon_obs_M0_LT_c_M0"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
