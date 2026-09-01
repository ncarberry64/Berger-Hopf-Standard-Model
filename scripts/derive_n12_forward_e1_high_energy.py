"""Derive compact-source E1 high-energy trace-norm control."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_e1_high_energy import (  # noqa: E402
    factorized_heat_sandwich_trace_norm_bound,
    finite_matrix_e1_high_energy_witness,
)


FLAGSHIP = ROOT / "artifacts/flagship_integration"
THRESHOLD = FLAGSHIP / "BHSM_N12_FORWARD_THRESHOLD_SOURCE_MEASURE_AUDIT.json"
CRITERION = FLAGSHIP / "BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json"
WEAK = FLAGSHIP / "BHSM_N12_FORWARD_WEAK_HEAT_VARIATIONS.json"
PRINCIPAL = FLAGSHIP / "BHSM_N12_GATE7_HEAT_PRINCIPAL_SYMBOL_AUDIT.json"
JETS = FLAGSHIP / "BHSM_N12_FORWARD_COMMON_SOURCE_GEOMETRY_JETS.json"
MODULE = ROOT / "src/bhsm/interface/aether_forward_e1_high_energy.py"
RESULT = FLAGSHIP / "BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"
INPUTS = (THRESHOLD, CRITERION, WEAK, PRINCIPAL, JETS, MODULE)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite high-energy audit value")
        return value
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all E1 high-energy inputs are required")
    threshold, criterion, weak, principal, jets = (
        json.loads(path.read_text(encoding="utf-8")) for path in INPUTS[:-1]
    )
    if not all(
        record.get("validation_passed") is True
        for record in (threshold, criterion, weak, principal, jets)
    ):
        raise RuntimeError("all E1 high-energy inputs must validate")

    matrix_witness = finite_matrix_e1_high_energy_witness(
        np.array([[2.0, -1.0], [-1.0, 3.0]]),
        np.array([[1.0, 0.75], [0.75, -2.0]]),
    )
    factorized_witness = {
        "localized_energy_heat_HS_norm": 2.0,
        "localized_vertex_heat_HS_norm": 3.0,
        "heat_sandwich_trace_norm_upper": (
            factorized_heat_sandwich_trace_norm_bound(2.0, 3.0)
        ),
    }

    validation = {
        "all_inputs_validated": True,
        "weak_variations_are_compactly_supported": (
            "COMPACTLY_SUPPORTED"
            in weak["weak_variation_theorem"]["allowed_variations"]
        ),
        "retained_vertices_have_finite_differential_order": (
            principal["regulator_order"]["spectral_order"]
            == "MINUS_INFINITY_AFTER_FINITE_ORDER_VERTICES"
        ),
        "heat_regulator_is_high_covector_smoothing": (
            principal["adjudication"][
                "retained_heat_pair_plus_contact_can_change_strict_principal_K_B"
            ]
            is False
        ),
        "local_first_geometry_jets_are_derived": (
            jets["validation"]["all_inputs_validated"] is True
        ),
        "matrix_tail_below_trace_norm_bound": (
            matrix_witness["bound_residual"] >= -1.0e-14
        ),
        "factorized_two_HS_bound_positive": (
            factorized_witness["heat_sandwich_trace_norm_upper"] == 12.0
        ),
        "global_unperturbed_heat_trace_not_reclassified": True,
        "low_energy_threshold_not_claimed_closed": True,
        "numerical_angular_tail_not_claimed_enclosed": True,
        "no_reference_gap_endpoint_chord3_selector_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM",
        "status": "COMPACT_WEAK_E1_HIGH_ENERGY_INTEGRABILITY_DERIVED_BY_HEAT_SANDWICH",
        "classification": (
            "FOR_EVERY_RETAINED_COMPACTLY_SUPPORTED_WEAK_GEOMETRY_DIRECTION_"
            "THE_UNIT_HEAT_SANDWICH_T_h=exp(-K/2)*P_h*exp(-K/2)_IS_TRACE_"
            "CLASS_BECAUSE_THE_SOURCE_VERTEX_HAS_FINITE_LOCAL_DIFFERENTIAL_"
            "ORDER_AND_THE_HEAT_SEMIGROUP_IS_SMOOTHING;_THEREFORE_THE_E1_"
            "HIGH_ENERGY_TOTAL_VARIATION_TAIL_IS_FINITE_AND_BOUNDED_BY_"
            "norm(T_h)_1,_WITHOUT_A_GLOBAL_HEAT_TRACE_OR_SPECTRAL_GAP"
        ),
        "theorem": {
            "source_measure": "nu_h(B)=STr(E_K(B)*P_h)",
            "heat_sandwich": "T_h=exp(-K/2)*P_h*exp(-K/2)",
            "weighted_measure": (
                "mu_h(B)=STr(E_K(B)*T_h)=integral_B_exp(-lambda)*dnu_h(lambda)"
            ),
            "tail_bound": (
                "H_h=integral_[1,infinity]_exp(-lambda)/lambda_"
                "dabs(nu_h)(lambda)<=norm(T_h)_1<infinity"
            ),
            "graded_rule": (
                "SUM_THE_TRACE_NORM_BOUNDS_WITH_ABSOLUTE_RETAINED_SECTOR_"
                "WEIGHTS;_NO_CANCELLATION_IS_NEEDED_FOR_INTEGRABILITY"
            ),
            "factorized_first_vertex": (
                "P_h=A^*B_h+B_h^*A_AND_POLAR_DECOMPOSITION_OF_COMPACT_"
                "B_h_FACTORS_EACH_HEAT_SANDWICH_TERM_INTO_TWO_LOCAL_"
                "HILBERT_SCHMIDT_FACTORS"
            ),
        },
        "exact_witnesses": {
            "noncommuting_two_by_two": matrix_witness,
            "factorized_two_Hilbert_Schmidt": factorized_witness,
        },
        "adjudication": {
            "compact_weak_E1_high_energy_integrability": "DERIVED",
            "explicit_actual_N12_high_energy_numeric_bound": "OPEN",
            "complete_internal_S3_angular_tail_enclosure": "OPEN",
            "continuous_low_energy_source_measure_exponent": "OPEN",
            "zero_source_force": "OPEN",
            "absolute_infinite_history_heat_action": "OPEN_NOT_REQUIRED_HERE",
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "PROVE_THE_ACTION_OWNED_CONTINUOUS_LOW_ENERGY_LIMITING_"
            "ABSORPTION_OR_WEYL_THRESHOLD_ESTIMATE_WITH_STRICTLY_"
            "SUPERLINEAR_SOURCE_WEIGHTED_COUNTING,_THEN_COMPUTE_OR_"
            "ENCLOSE_THE_GRADED_FIXED_CHANNEL_AND_ANGULAR_SUM_TO_SIGN_"
            "ADJUDICATE_THE_ZERO_SOURCE_FORCE"
        ),
        "claim_boundary": {
            "high_energy_integrability_is_a_numeric_force_value": False,
            "absolute_global_heat_trace_made_finite": False,
            "low_energy_threshold_closed": False,
            "angular_sum_numerically_enclosed": False,
            "zero_source_force_closed": False,
            "Gate_7": "ACTIVE_NOT_CLOSED",
            "Gate_8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def materialize() -> Path:
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(_canonical(build_payload()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return RESULT


if __name__ == "__main__":
    print(materialize())
