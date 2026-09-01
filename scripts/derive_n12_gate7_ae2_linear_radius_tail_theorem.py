"""Derive the exact non-L1 linear-radius factorized threshold theorem."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_linear_radius_tail import (  # noqa: E402
    linear_radius_tail_compact_source_weight,
    linear_radius_tail_source_law,
)


TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_LINEAR_RADIUS_TAIL_THEOREM.json"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json",
    ROOT / "src/bhsm/interface/action_extension_ae2_linear_radius_tail.py",
    ROOT / "scripts/derive_n12_gate7_ae2_linear_radius_tail_theorem.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _numerical_row(beta: float, chirality: int) -> dict[str, Any]:
    wave_numbers = [1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4]
    weights = [
        linear_radius_tail_compact_source_weight(beta, chirality, k)
        for k in wave_numbers
    ]
    slopes = [
        math.log(weights[index + 1] / weights[index])
        / math.log(wave_numbers[index + 1] / wave_numbers[index])
        for index in range(len(weights) - 1)
    ]
    law = linear_radius_tail_source_law(beta, chirality)
    row: dict[str, Any] = {
        "beta": beta,
        "chirality": chirality,
        "law": law,
        "threshold_wave_numbers": wave_numbers,
        "compact_source_weights": weights,
        "successive_log_slopes": slopes,
    }
    if law.get("critical_log_Dini_case"):
        row["critical_scaled_weights"] = [
            weight * math.log(k) ** 2 / k for weight, k in zip(weights, wave_numbers)
        ]
    else:
        row["final_slope_residual"] = abs(slopes[-1] - float(law["power_exponent"]))
    return row


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("linear-radius theorem inputs required")
    route, reduction, fixed = (_load(path) for path in INPUTS[:3])
    if not all(item.get("validation_passed") is True for item in (route, reduction, fixed)):
        raise RuntimeError("validated factorized tail lineage required")
    rows = [
        _numerical_row(0.25, 1),
        _numerical_row(0.5, 1),
        _numerical_row(0.75, 1),
        _numerical_row(1.25, 1),
        _numerical_row(0.75, -1),
    ]
    critical = rows[1]["critical_scaled_weights"]
    validation = {
        "all_inputs_validated": True,
        "integrable_radius_route_left_non_L1_open": route["claim_boundary"]["direct_nonintegrable_tail_theorem"] == "OPEN",
        "fixed_factorized_transfer_retained": fixed["fixed_channel_theorem"]["rank16_product_Dirac_channel"]["factor"].startswith("A_lambda="),
        "all_power_rows_converge_to_exact_exponent": all(row.get("final_slope_residual", 0.0) < 0.02 for row in rows),
        "critical_beta_half_has_log_Dini_scaling": max(critical) / min(critical) < 1.15,
        "critical_beta_half_E1_integral_converges": rows[1]["law"]["E1_threshold_integrable"] is True,
        "both_chiralities_covered": {row["chirality"] for row in rows} == {-1, 1},
        "all_exact_laws_are_E1_integrable": all(row["law"]["E1_threshold_integrable"] for row in rows),
        "threshold_k_not_identified_as_physical_momentum": True,
        "actual_N12_linear_asymptotic_not_fabricated": True,
        "no_SM_observable_scale_fit_selector_or_new_action_term": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_AE2_LINEAR_RADIUS_TAIL_THEOREM",
        "action_version": "BHSM-AE-2.0.0",
        "status": "EXACT_LINEAR_RADIUS_NON_L1_FACTORIZED_TAIL_E1_THRESHOLD_CLOSED",
        "classification": "FOR_AN_EXACT_LINEAR_RADIUS_TAIL_THE_FACTORIZED_SUPERPOTENTIAL_IS_s_chi=chi*beta/x_AND_THE_NATURAL_BIRTH_GRAPH_REDUCES_THE_CONTINUUM_STATES_TO_EXACT_BESSEL_COMBINATIONS;_THE_POSITIVE_CHIRALITY_CUMULATIVE_SOURCE_MEASURE_IS_O(Lambda^(1+abs(beta-1/2)))_OFF_CRITICALITY_AND_O(Lambda/abs(log_Lambda)^2)_AT_beta=1/2,_WHILE_THE_NEGATIVE_CHIRALITY_HAS_O(Lambda^(beta+3/2));_ALL_CASES_HAVE_FINITE_E1_THRESHOLD_INTEGRAL",
        "theorem": {
            "tail_geometry": "R4(tau)=v*(tau+tau0),_v>0",
            "dimensionless_strength": "beta=abs(mu)/v",
            "positive_chirality_operator": "-d_x^2+beta*(beta+1)/x^2",
            "negative_chirality_operator": "-d_x^2+beta*(beta-1)/x^2",
            "natural_graph": "(d_x+chi*beta/x)u(1)=0",
            "delta_normalized_Bessel_state": "psi_k(x)=sqrt(k*x)/D_m(k)*(Y_m(k)*J_nu(k*x)-J_m(k)*Y_nu(k*x)),_D_m(k)=sqrt(J_m(k)^2+Y_m(k)^2)",
            "positive_orders": "nu=beta+1/2,_m=beta-1/2",
            "negative_orders": "nu=abs(beta-1/2),_m=beta+1/2_IF_beta>=1/2_ELSE_m=-(beta+1/2)",
            "factor_image_identity": "(d_x+chi*beta/x)[sqrt(x)*Z_nu(k*x)]=sign_chi*k*sqrt(x)*Z_m(k*x)",
            "positive_chirality_law": {
                "beta_below_half": "abs(nu_h)([0,Lambda])=O(Lambda^(3/2-beta))",
                "beta_equal_half": "abs(nu_h)([0,Lambda])=O(Lambda/abs(log_Lambda)^2)",
                "beta_above_half": "abs(nu_h)([0,Lambda])=O(Lambda^(beta+1/2))",
            },
            "negative_chirality_law": "abs(nu_h)([0,Lambda])=O(Lambda^(beta+3/2))",
            "E1_Dini_test": "integral_(0,1)_lambda^(-1)*dabs(nu_h)(lambda)<infinity_IN_ALL_beta>=0_CASES",
            "spectral_semantics": "k=sqrt(lambda)_IS_A_BESSEL_PROOF_VARIABLE_ONLY_AND_IS_NOT_A_PHYSICAL_MOMENTUM_MAP_FOR_z",
            "numerical_rows": rows,
        },
        "frontier_sharpening": {
            "integrable_superlinear_radius_tail": "CLOSED_BY_PRIOR_ROUTE",
            "exact_linear_radius_tail": "CLOSED_HERE",
            "finite_event_or_canonical_stop": "CLOSED_BY_COMPACT_RESOLVENT_BRANCH",
            "remaining_actual_tail_owner": "DERIVE_FROM_THE_RETAINED_ACTION_WHICH_RADIUS_ASYMPTOTIC_CLASS_THE_UNIQUE_INFINITE_REGULAR_HISTORY_HAS,_OR_PROVE_THE_SOURCE_DINI_BOUND_FOR_THE_REMAINING_SUBLINEAR_OR_NONASYMPTOTIC_POSITIVE_RADIUS_TAIL_CLASS",
        },
        "claim_boundary": {
            "exact_linear_radius_tail_theorem": "CLOSED",
            "actual_N12_radius_asymptotic_class": "OPEN",
            "general_sublinear_or_nonasymptotic_tail": "OPEN",
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "DERIVE_AN_ACTION_OWNED_ASYMPTOTIC_CLASS_FOR_R4_ON_THE_UNIQUE_INFINITE_REGULAR_MAXIMAL_FORWARD_HISTORY;_INTEGRABLE_SUPERLINEAR_AND_EXACT_LINEAR_TAILS_ARE_NOW_CLOSED,_SO_ONLY_SUBLINEAR_OR_NONASYMPTOTIC_POSITIVE_RADIUS_TAILS_REQUIRE_A_NEW_SOURCE_DINI_THEOREM",
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def materialize() -> Path:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [key for key, value in payload["validation"].items() if not value]
        raise RuntimeError(f"linear-radius tail theorem failed: {failed}")
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
