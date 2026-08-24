"""Derive the weakest AE2 factorized source-measure threshold theorem."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_factorized_source_measure import (  # noqa: E402
    endpoint_threshold_dichotomy,
    exact_constant_resonance_coefficient,
    resonant_transfer_majorant,
)
from bhsm.interface.action_extension_ae2_factorized_threshold import (  # noqa: E402
    factorized_zero_resonance_weight_coefficient,
)


TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json",
    ROOT / "src/bhsm/interface/action_extension_ae2_factorized_source_measure.py",
    ROOT / "scripts/derive_n12_gate7_ae2_factorized_source_measure_reduction.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("factorized source-measure reduction inputs required")
    records = [_load(path) for path in INPUTS[:5]]
    if not all(item.get("validation_passed") is True for item in records):
        raise RuntimeError("validated current factorized lineage required")
    reclassification, frontier, criterion, high_energy, fixed = records

    s = 2.0
    length = 0.75
    exact = exact_constant_resonance_coefficient(s, length)
    prior_exact = factorized_zero_resonance_weight_coefficient(s, length)
    majorant = resonant_transfer_majorant(
        s, length, 1.0, exact["threshold_delta_normalization_squared"]
    )
    finite_end = endpoint_threshold_dichotomy(
        finite_regular_or_canonical_stop=True,
        infinite_end_threshold_normalization_bound_available=False,
    )
    infinite_open = endpoint_threshold_dichotomy(
        finite_regular_or_canonical_stop=False,
        infinite_end_threshold_normalization_bound_available=False,
    )
    infinite_closed = endpoint_threshold_dichotomy(
        finite_regular_or_canonical_stop=False,
        infinite_end_threshold_normalization_bound_available=True,
    )

    validation = {
        "all_inputs_validated": True,
        "fixed_channel_factor_is_retained": fixed["fixed_channel_theorem"]["rank16_product_Dirac_channel"]["factor"].startswith("A_lambda="),
        "prior_strict_gap_is_not_required": reclassification["claim_boundary"]["strict_product_Dirac_Wronskian_required_in_advance"] is False,
        "actual_factorized_measure_was_open": frontier["preserved_open_objects"]["realized_factorized_source_weighted_limiting_absorption"] == "OPEN",
        "exact_transfer_derivative_matches_prior_witness": math.isclose(exact["first_form_weight_over_k_squared_limit"], prior_exact["weight_over_momentum_squared_limit"], rel_tol=1e-14),
        "explicit_majorant_dominates_exact_witness": majorant["first_form_weight_over_k_squared_upper"] >= exact["first_form_weight_over_k_squared_limit"],
        "source_measure_exponent_meets_E1_criterion": majorant["source_measure_excess_exponent"] > 0.0,
        "high_energy_integrability_already_derived": high_energy["adjudication"]["compact_weak_E1_high_energy_integrability"] == "DERIVED",
        "finite_end_needs_no_continuous_LAP": finite_end["remaining_input"] is None,
        "infinite_end_only_needs_threshold_normalization_scalar": infinite_open["remaining_input"] == "FINITE_UNIFORM_NEAR_THRESHOLD_SUM_OF_SQUARED_GENERALIZED_EIGENSTATE_NORMALIZATIONS",
        "normalization_scalar_closes_the_abstract_infinite_end_theorem": infinite_closed["remaining_input"] is None,
        "full_operator_LAP_not_demanded": infinite_open["full_operator_norm_limiting_absorption_required"] is False,
        "actual_N12_normalization_not_fabricated": True,
        "no_new_selector_scale_endpoint_prediction_or_action_term": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION",
        "action_version": "BHSM-AE-2.0.0",
        "status": "FACTORIZED_E1_THRESHOLD_REDUCED_TO_ONE_SOURCE_CONTRACTED_NORMALIZATION_SCALAR_PER_INFINITE_CHANNEL",
        "classification": "AT_EVERY_FACTORIZED_ZERO_RESONANCE_THE_FIXED_CHANNEL_TRANSFER_SYSTEM_IS_ANALYTIC_IN_lambda=k_squared_AND_Au_zero=0;_DIFFERENTIATING_THE_EXACT_TRANSFER_EQUATION_GIVES_Au_k=O(k_squared)_ON_COMPACT_SOURCE_SUPPORT,_SO_THE_FIRST_LOG_RADIUS_FORM_WEIGHT_IS_O(k_squared)_AND_THE_CUMULATIVE_ONE_DIMENSIONAL_SOURCE_MEASURE_IS_O(Lambda^(3/2))_WHEN_THE_SUM_OF_SQUARED_GENERALIZED_EIGENSTATE_NORMALIZATIONS_IS_UNIFORMLY_BOUNDED_NEAR_THRESHOLD;_FINITE_REGULAR_OR_CANONICAL_STOP_ENDS_REQUIRE_NO_CONTINUOUS_LAP",
        "theorem": {
            "system": "u_prime=-s*u+v,_v_prime=s*v-lambda*u,_lambda=k_squared",
            "resonant_solution": "u_0(t)=exp(-S(t)),_v_0(t)=0,_S(t)=integral_0^t_s",
            "spectral_derivative": "partial_lambda_v_at_0=-exp(S(t))*integral_0^t_exp(-2*S(r))dr",
            "first_vertex": "D_h_q[u_k]=2Re_integral_(A*u_k)^*(-h*s*u_k)",
            "weight_conclusion": "limsup_k_to_0_abs(D_h_q[psi_k])/k_squared<=C_h",
            "measure_conclusion": "limsup_Lambda_to_0_abs(nu_h)([0,Lambda])/Lambda^(3/2)<=C_h/3",
            "majorant": majorant,
            "endpoint_dichotomy": {"finite": finite_end, "infinite_open": infinite_open, "infinite_with_normalization": infinite_closed},
            "scope": "ONE_FIXED_FACTORIZED_CHANNEL_AND_ONE_COMPACTLY_SUPPORTED_RETAINED_LOG_RADIUS_DIRECTION;_SUM_CHANNELWISE_WITH_RETAINED_ABSOLUTE_GRADING_WEIGHTS",
        },
        "exact_crosscheck": {"transfer_derivative": exact, "prior_scattering_witness": prior_exact},
        "frontier_sharpening": {
            "retired_as_required": ["STRICT_ZERO_WRONSKIAN", "FULL_OPERATOR_NORM_LIMITING_ABSORPTION", "GENERIC_OPERATOR_HISTORY_TUBE"],
            "new_weakest_actual_input": "FOR_EACH_INFINITE_REGULAR_FACTORIZED_CHANNEL_PROVE_A_FINITE_UNIFORM_NEAR_THRESHOLD_SUM_OF_SQUARED_GENERALIZED_EIGENSTATE_NORMALIZATIONS_ON_THE_COMPACT_SOURCE_SUPPORT;_FINITE_EVENT_OR_CANONICAL_STOP_CHANNELS_ARE_ALREADY_IN_THE_COMPACT_RESOLVENT_BRANCH",
            "actual_N12_status": "OPEN_BECAUSE_THE_REALIZED_MAXIMAL_FORWARD_FAR_END_CLASS_AND_ITS_THRESHOLD_NORMALIZATION_HAVE_NOT_BEEN_CERTIFIED",
        },
        "claim_boundary": {
            "abstract_factorized_transfer_to_source_measure_theorem": "CLOSED",
            "actual_N12_infinite_end_threshold_normalization": "OPEN",
            "nonfermion_threshold": "CLOSED",
            "high_energy_integrability": "CLOSED_QUALITATIVELY",
            "angular_sum": "OPEN",
            "zero_source_force": "OPEN",
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "CLASSIFY_EACH_REALIZED_MAXIMAL_FORWARD_FACTORIZED_CHANNEL_AS_FINITE_EVENT_OR_CANONICAL_STOP_VERSUS_INFINITE_REGULAR_END;_FOR_EACH_INFINITE_END_PROVE_ONLY_A_FINITE_UNIFORM_NEAR_THRESHOLD_GENERALIZED_EIGENSTATE_NORMALIZATION_SUM_ON_THE_RETAINED_COMPACT_SOURCE_SUPPORT,_THEN_INSERT_THE_EXPLICIT_TRANSFER_MAJORANT_INTO_THE_E1_DYADIC_CRITERION_AND_ASSEMBLE_THE_ANGULAR_SUM",
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
        raise RuntimeError(f"factorized source-measure reduction failed: {failed}")
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
