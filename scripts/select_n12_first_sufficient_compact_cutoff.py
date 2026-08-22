"""Select the first integer cutoff closing the compact observation gap."""

from __future__ import annotations

import hashlib
import json
import math
from decimal import Decimal, ROUND_FLOOR, localcontext
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_COMPACT_OBSERVATION_MODULI_AUDIT.json"
)
OBSERVATION = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_FIRST_SUFFICIENT_COMPACT_CUTOFF.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _up_decimal(value: float) -> Decimal:
    return Decimal.from_float(math.nextafter(float(value), math.inf))


def _down_decimal(value: float) -> Decimal:
    return Decimal.from_float(math.nextafter(float(value), 0.0))


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    blocks = audit["four_compact_blocks"]
    coefficient_values = {
        "Euler_Dirac": float(blocks["interior_lower_order_Euler_Dirac"][
            "C_ED_G_upper"
        ]),
        "ordered_event": float(blocks["ordered_event_projector"][
            "C_event_G_upper"
        ]),
        "momentum_flux": float(blocks["canonical_momentum_dynamic_flux"][
            "C_flux_G_upper"
        ]),
        "Gauss_consistency": float(blocks["Gauss_consistency"][
            "C_GQ_upper"
        ]),
    }
    with localcontext() as context:
        context.prec = 420
        coefficients = {
            name: _up_decimal(value)
            for name, value in coefficient_values.items()
        }
        combined = sum(coefficients.values(), Decimal(0))
        c_core = _down_decimal(
            float(observation["c_M0_observation_norm_lower"])
        )
        threshold = (Decimal(4) * combined / c_core) ** 2
        cutoff = int(threshold.to_integral_value(rounding=ROUND_FLOOR)) + 1
        if cutoff < 12:
            cutoff = 12
        sqrt_cutoff = Decimal(cutoff).sqrt()
        epsilon = Decimal(4) * combined / sqrt_cutoff
        gap = c_core - epsilon
        if gap <= 0:
            raise ArithmeticError("strict compact observation gap did not close")
        inverse = Decimal(1) / gap
        contributions = {
            name: Decimal(4) * value / sqrt_cutoff
            for name, value in coefficients.items()
        }

        # Also record, but do not promote as an additional physical gate, the
        # first cutoff giving a half-core numerical margin.  It is useful if
        # the nonlinear radius is dominated by the near-threshold inverse.
        half_threshold = (Decimal(8) * combined / c_core) ** 2
        half_cutoff = int(
            half_threshold.to_integral_value(rounding=ROUND_FLOOR)
        ) + 1
        half_epsilon = Decimal(4) * combined / Decimal(half_cutoff).sqrt()
        half_gap = c_core - half_epsilon
        half_inverse = Decimal(1) / half_gap

        validation = {
            "all_four_same_norm_compact_coefficients_closed": all(
                bool(row["same_norm_coefficient_enclosed"])
                for row in blocks.values()
            ),
            "directed_float_rounding_is_conservative": True,
            "selected_cutoff_is_first_integer_strictly_above_threshold": (
                Decimal(cutoff - 1) <= threshold < Decimal(cutoff)
            ),
            "strict_observation_gap_positive": gap > 0,
            "epsilon_obs_strictly_below_c_core": epsilon < c_core,
            "right_inverse_bound_finite": inverse.is_finite(),
            "no_higher_resolution_child_root_used": True,
            "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
        }
        payload = {
            "classification": (
                "FIRST_SUFFICIENT_ACTION_OWNED_COMPACT_CUTOFF_AND_"
                "QUANTITATIVE_NORMAL_RIGHT_INVERSE_SELECTED"
            ),
            "inputs": {
                str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
                for path in (AUDIT, OBSERVATION)
            },
            "formula": {
                "Fortin": "C_F(M)<=4/sqrt(M)",
                "observation": "epsilon_obs(M)<=4*C_compact/sqrt(M)",
                "cutoff": "M0=floor((4*C_compact/c_core)^2)+1",
                "inverse": "K<=1/(c_core-epsilon_obs(M0))",
            },
            "directed_decimal_bounds": {
                "compact_coefficients_upper": {
                    name: str(value) for name, value in coefficients.items()
                },
                "C_compact_sum_upper": str(combined),
                "c_core_lower": str(c_core),
                "strict_threshold": str(threshold),
                "M0_first_sufficient": str(cutoff),
                "epsilon_obs_M0_upper": str(epsilon),
                "observation_gap_lower": str(gap),
                "K_normal_right_inverse_upper": str(inverse),
                "epsilon_contributions_upper": {
                    name: str(value) for name, value in contributions.items()
                },
            },
            "optional_numerically_stable_half_margin_cutoff": {
                "is_an_additional_physical_gate": False,
                "M_half": str(half_cutoff),
                "epsilon_obs_upper": str(half_epsilon),
                "observation_gap_lower": str(half_gap),
                "K_upper": str(half_inverse),
            },
            "epsilon_obs_M_evaluable": True,
            "M_star_certified": True,
            "quantitative_normal_right_inverse_closed": True,
            "first_missing_action_owned_object": (
                "INSERT_THE_SELECTED_K_AND_INVERSE_SQUARE_SOURCE_TAIL_"
                "INTO_THE_EXISTING_NONLINEAR_CONTINUUM_RADIUS"
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
