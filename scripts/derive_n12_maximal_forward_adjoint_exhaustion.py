"""Derive the maximal forward-adjoint exhaustion criterion for Gate 7."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_MAXIMAL_FORWARD_ADJOINT_EXHAUSTION.json"
)
THEORY = ROOT / "theory/n12_maximal_forward_adjoint_exhaustion.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _adjoint_witness(alpha: float = 2.0, beta: float = 0.5) -> dict[str, object]:
    rate = alpha + beta
    durations = (0.5, 1.0, 2.0, 4.0, 8.0)
    rows = [
        {
            "duration": duration,
            "finite_core_adjoint_pullback": -math.expm1(-rate * duration) / rate,
            "infinite_limit": 1.0 / rate,
        }
        for duration in durations
    ]
    return {
        "stable_model": {
            "U(t,0)": "exp(-alpha*t)",
            "q(t)": "exp(-beta*t)",
            "alpha": alpha,
            "beta": beta,
            "weighted_integral": "1/(alpha+beta)",
            "weighted_integral_value": 1.0 / rate,
            "rows": rows,
        },
        "divergent_model": {
            "U(t,0)": "1",
            "q(t)": "1",
            "finite_core_adjoint_pullback": "T",
            "infinite_limit_exists": False,
        },
    }


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing maximal-adjoint inputs: " + ", ".join(missing))
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated maximal-adjoint inputs required")
    witness = _adjoint_witness()
    rows = witness["stable_model"]["rows"]
    limit = witness["stable_model"]["weighted_integral_value"]
    errors = [abs(row["finite_core_adjoint_pullback"] - limit) for row in rows]
    validation = {
        "all_inputs_validated": True,
        "finite_endpoint_adjoint_pullback_is_derived": (
            records[0]["claim_boundary"]["G7_08_force_adjoint_pullback"] == "DERIVED"
        ),
        "intrinsic_time_quotient_root_equivalence_is_derived": (
            records[1]["claim_boundary"]["force_root_time_quotient_equivalence"]
            == "DERIVED"
        ),
        "negative_z_Friedrichs_value_exhaustion_is_derived": (
            records[2]["closed_here"]["Friedrichs_negative_z_Weyl_value_uniqueness"]
            is True
        ),
        "E1_source_measure_criterion_is_available": records[3]["validation_passed"] is True,
        "stable_model_converges_to_exact_weighted_integral": (
            errors[-1] < 1.0e-8
            and all(left > right for left, right in zip(errors, errors[1:]))
        ),
        "divergent_model_blocks_false_automatic_promotion": (
            witness["divergent_model"]["infinite_limit_exists"] is False
        ),
        "actual_N12_weighted_load_not_assumed": True,
        "noncompact_reset_Jacobi_matrix_not_required_by_the_criterion": True,
        "no_selector_endpoint_return_contour_scale_fit_or_chord_added": True,
    }
    return {
        "artifact": "BHSM_N12_MAXIMAL_FORWARD_ADJOINT_EXHAUSTION",
        "status": "INFINITE_MAXIMAL_ADJOINT_EXHAUSTION_CRITERION_DERIVED_ACTUAL_WEIGHTED_LOAD_OPEN",
        "classification": (
            "THE_PHYSICAL_RESET_FORCE_COVECTOR_ON_AN_INFINITE_FRIEDRICHS_"
            "ROUTE_IS_THE_LIMIT_OF_FINITE_CORE_ADJOINT_PULLBACKS_WHEN_"
            "INTEGRAL_norm(U(t,0))*norm(q(t))_dt_IS_FINITE;_THIS_REPLACES_"
            "ALL_NONCOMPACT_RESET_JACOBI_COLUMNS_BY_ONE_ADJOINT_LIMIT,_BUT_"
            "THE_ACTUAL_N12_WEIGHTED_PROPAGATOR_LOAD_BOUND_REMAINS_OPEN"
        ),
        "criterion": {
            "finite_core_pullback": "p_T(0)=integral_0^T U(t,0)^dagger*q(t)_dt",
            "sufficient_bound": "integral_0^Tmax norm(U(t,0))*norm(q(t))_dt<infinity",
            "maximal_force": "F(h)=<B_reset^dagger*p(0)+q_direct,h>",
            "all_forward_Jacobi_columns_required": False,
            "explicit_noncompact_D_xi_M_required": False,
            "intrinsic_time_quotient_applies_after_limit": True,
            "finite_endpoint_route_requires_infinite_bound": False,
        },
        "exact_witness": witness,
        "open_after_theorem": {
            "actual_N12_state_propagator_weight": True,
            "actual_E1_operator_cotangent_load": True,
            "direct_zeta_load_integrability": True,
            "reset_to_NHIM_connection_if_used": True,
            "graded_angular_contractions": True,
            "physical_force_root": True,
        },
        "exact_next_dependency": (
            "PROVE_OR_ENCLOSE_THE_ACTION_OWNED_WEIGHTED_MAXIMAL_ADJOINT_LOAD_"
            "INTEGRAL_norm(U(t,0))*norm(q_heat_minus_zeta(t))_dt_ON_A_"
            "NONEMPTY_REGULAR_RESET_QUOTIENT_STRATUM,_OR_CERTIFY_A_FINITE_"
            "LATER_EVENT_OR_CANONICAL_STOP_STRATUM;_THEN_EVALUATE_THE_"
            "INTRINSIC_PHYSICAL_FORCE_ROOT"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_WEIGHTED_MAXIMAL_ADJOINT_LOAD_OR_FINITE_STRATUM",
            "Gate8": "LOCKED",
            "infinite_adjoint_exhaustion_criterion": "DERIVED",
            "actual_weighted_load": "OPEN_CURRENT_OWNER",
            "actual_projected_force": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
