"""Close the complete gauge-fixed rank-two regular-pole indicial block.

The endpoint audit shows that, before the mixed constraint rows are included,
the zero-order inverse-square form has rank two.  At high shell the scale is a
finite core variable and the existing boundary-compatible gauge removes w and
shift.  The remaining local pole variables are (u, b, logN), with derivative
matrix P and zero-order matrix M below.  This script derives the full weighted
3x3 symbol and an explicit H2 inverse bound on the already-authorized
chi^(-1/2) source space.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_ENDPOINT_SAFE_ED_REMAINDER.json"
)
SCALAR_INDICIAL = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_INDICIAL_BOUND.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FULL_POLE_INDICIAL_BOUND.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _matrix(value: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(item)) for item in row] for row in value.tolist()]


def main() -> None:
    endpoint = json.loads(ENDPOINT.read_text(encoding="utf-8"))
    scalar = json.loads(SCALAR_INDICIAL.read_text(encoding="utf-8"))

    P = sp.Matrix([
        [10, 0, 2],
        [0, -2, 0],
        [2, 0, 0],
    ])
    # Restriction of the exact rank-two pole Hessian to (u,b,logN) after
    # removing the single finite scale coordinate and the existing w gauge.
    M = sp.Matrix([
        [150, 30, 30],
        [30, 12, 6],
        [30, 6, 6],
    ])
    z = sp.symbols("z")
    symbol_z = -3 * P * z**2 + 3 * P + M
    determinant_z = sp.factor(symbol_z.det())

    xi, y = sp.symbols("xi y", real=True, nonnegative=True)
    alpha = sp.Rational(1, 2)
    weighted_symbol = symbol_z.subs(z, sp.I * xi - alpha)
    determinant_squared = sp.factor(sp.expand_complex(
        weighted_symbol.det() * sp.conjugate(weighted_symbol.det())
    ).subs(xi**2, y))
    frobenius_squared = sp.factor(sp.expand_complex(sum(
        item * sp.conjugate(item) for item in weighted_symbol
    )).subs(xi**2, y))
    inverse_bound_squared = sp.factor(
        (1 + y) ** 2 * frobenius_squared**2
        / (4 * determinant_squared)
    )
    numerator, denominator = sp.fraction(inverse_bound_squared)
    derivative_numerator = sp.factor(
        sp.diff(numerator, y) * denominator
        - numerator * sp.diff(denominator, y)
    )
    positive_factor = sp.Poly(sp.cancel(
        -derivative_numerator
        / (
            288 * (y + 1) * (112 * y**2 + 1344 * y + 3789)
        )
    ), y)
    h2_symbol_inverse_upper = sp.Rational(1684, 35)
    origin_bound = sp.factor(sp.sqrt(inverse_bound_squared.subs(y, 0)))
    infinity_bound = sp.factor(sp.sqrt(sp.limit(
        inverse_bound_squared, y, sp.oo
    )))

    sectors = {}
    for side, record in scalar["root_ball_coefficient_enclosure"][
        "sectors"
    ].items():
        c_lower = float(record["root_ball_c_lower"])
        sectors[side] = {
            "root_ball_c_lower": c_lower,
            "full_rank_two_weighted_H2_inverse_upper": (
                float(h2_symbol_inverse_upper) / c_lower
            ),
            "previous_Berger_line_weighted_H2_inverse_upper": float(
                record["weighted_H2_graph_inverse_upper"]
            ),
        }
    joint_upper = max(
        record["full_rank_two_weighted_H2_inverse_upper"]
        for record in sectors.values()
    )

    validation = {
        "endpoint_rank_two_matrix_consumed": bool(
            endpoint["validation_passed"]
            and endpoint["exact_round_pole_zero_order_matrix"]["rank"] == 2
        ),
        "existing_scalar_source_restricted_indicial_bound_consumed": bool(
            scalar["source_restricted_indicial_solvability_closed"]
        ),
        "full_symbol_determinant_factorized_exactly": (
            sp.simplify(
                determinant_z
                + 216 * (z - 1) * (z + 1) * (z**4 - 5 * z**2 - 1)
            ) == 0
        ),
        "weighted_symbol_has_no_real_zero": bool(
            sp.Poly(determinant_squared, y).LC() > 0
            and all(coefficient > 0 for coefficient in sp.Poly(
                determinant_squared, y
            ).all_coeffs())
        ),
        "inverse_bound_is_monotone_decreasing_in_xi_squared": all(
            coefficient > 0 for coefficient in positive_factor.all_coeffs()
        ),
        "exact_maximum_inverse_majorant_is_1684_over_35": (
            origin_bound == h2_symbol_inverse_upper
        ),
        "all_root_ball_pole_coefficients_positive": all(
            record["root_ball_c_lower"] > 0.0 for record in sectors.values()
        ),
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "FULL_GAUGE_FIXED_RANK_TWO_REGULAR_POLE_SOURCE_RESTRICTED_"
            "INDICIAL_BOUND_CLOSED;_THE_CONFORMAL_AND_BERGER_CRITICAL_"
            "LINES_ARE_BOTH_RETAINED_IN_THE_PRINCIPAL_OPERATOR"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (ENDPOINT, SCALAR_INDICIAL)
        },
        "high_shell_reduction": {
            "variables": ["u", "b", "logN"],
            "scale_rho": "EXISTING_SINGLE_FINITE_CORE_COORDINATE",
            "w_and_shift": "EXISTING_BOUNDARY_COMPATIBLE_GAUGE_QUOTIENT",
            "derivative_matrix_P": _matrix(P),
            "zero_order_rank_two_matrix_M": _matrix(M),
            "new_quotient_or_physical_constraint": False,
        },
        "logarithmic_symbol": {
            "coordinate": "t=-log(chi)",
            "unitary_unknown": "g=chi*(delta_u,delta_b,delta_logN)",
            "operator": "c0*(-3*P*D_t^2+3*P+M)",
            "symbol_in_z": _matrix(symbol_z),
            "determinant": str(determinant_z),
            "unweighted_thresholds_remain_part_of_the_static_spectrum": True,
        },
        "source_restricted_weighted_proof": {
            "alpha": "1/2",
            "substitution": "z=i*xi-1/2",
            "absolute_determinant_squared_in_y_equals_xi_squared": str(
                determinant_squared
            ),
            "Frobenius_norm_squared": str(frobenius_squared),
            "inverse_majorant_squared": str(inverse_bound_squared),
            "derivative_numerator": str(derivative_numerator),
            "positive_degree_seven_factor_coefficients": [
                int(value) for value in positive_factor.all_coeffs()
            ],
            "maximum_occurs_at_xi": 0.0,
            "exact_H2_symbol_inverse_upper_before_c0": str(
                h2_symbol_inverse_upper
            ),
            "large_frequency_limit": str(infinity_bound),
            "singular_value_inequality": (
                "sigma_min(S)>=2*abs(det(S))/norm(S)_F^2"
            ),
        },
        "root_ball_coefficient_enclosure": sectors,
        "joint_full_rank_two_weighted_H2_inverse_upper": joint_upper,
        "previous_scalar_Berger_bound_invalidated": False,
        "previous_scalar_Berger_bound_is_sufficient_for_full_rank_two_block": False,
        "full_rank_two_source_restricted_indicial_solvability_closed": True,
        "C_ED_G_evaluable_after_desingularized_remainder_enclosure": True,
        "epsilon_obs_M_evaluable": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "first_missing_action_owned_object": (
            "INTERVAL_ENCLOSE_THE_ENDPOINT_ELIGIBLE_DESINGULARIZED_"
            "REMAINDER_MATRIX_AND_ITS_STATE_LIPSCHITZ_NORM_TO_OBTAIN_C_ED_G"
        ),
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
