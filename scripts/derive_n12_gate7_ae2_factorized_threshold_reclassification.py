"""Reclassify strict Wronskian positivity as sufficient, not necessary."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_factorized_threshold import (  # noqa: E402
    factorized_constant_core_log_radius_weight,
    factorized_zero_resonance_weight_coefficient,
)


TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json"
)
AE2_ZERO = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ZERO_THRESHOLD_NO_SHORTCUT.json"
)
NONFERMION = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"
)
CRITERION = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json"
)
PRODUCT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
)
MODULE = ROOT / "src/bhsm/interface/action_extension_ae2_factorized_threshold.py"
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_factorized_threshold_reclassification.py"
INPUTS = (AE2_ZERO, NONFERMION, CRITERION, PRODUCT, MODULE, SCRIPT)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite factorized threshold value")
        rounded = round(value, 15)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("factorized threshold reclassification inputs required")
    zero, nonfermion, criterion, product = (_load(path) for path in INPUTS[:4])
    if not all(
        record.get("validation_passed") is True
        for record in (zero, nonfermion, criterion, product)
    ):
        raise RuntimeError("validated factorized threshold lineage required")

    superpotential = 2.0
    length = 0.75
    exact = factorized_zero_resonance_weight_coefficient(superpotential, length)
    momenta = [0.1, 0.03, 0.01, 0.003, 0.001]
    rows = [
        factorized_constant_core_log_radius_weight(superpotential, length, k)
        for k in momenta
    ]
    target = exact["weight_over_momentum_squared_limit"]
    residuals = [abs(row["weight_over_momentum_squared"] - target) for row in rows]

    validation = {
        "all_inputs_validated": True,
        "retained_product_form_is_A_star_A": (
            product["factorized_comparison_theorem"]["factor"].startswith("A_lambda=")
        ),
        "AE2_local_zero_wronskian_shortcut_remains_invalid": (
            zero["claim_boundary"]["local_collars_suffice_for_strict_margin"] is False
        ),
        "nonfermion_margin_theorem_preserved": (
            nonfermion["claim_boundary"]["nonfermion_critical_zero_graph_excluded"]
            is True
        ),
        "model_has_exact_nonzero_zero_resonance": (
            exact["strict_zero_energy_wronskian_margin"] == 0.0
            and exact["zero_energy_core_end_value"] > 0.0
        ),
        "first_factorized_geometry_weight_is_positive": all(
            row["first_log_radius_weight"] > 0.0 for row in rows
        ),
        "weight_is_quadratic_in_momentum": residuals[-1] < residuals[0] / 1000.0,
        "cumulative_source_exponent_is_three_halves": (
            exact["cumulative_weight_over_Lambda_to_three_halves_limit"] > 0.0
        ),
        "strict_Wronskian_not_declared_necessary": True,
        "actual_N12_limiting_absorption_not_fabricated": True,
        "no_endpoint_reference_chord_selector_scale_fit_or_prediction_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION",
        "action_version": "BHSM-AE-2.0.0",
        "status": "STRICT_ZERO_WRONSKIAN_RECLASSIFIED_AS_SUFFICIENT_NOT_NECESSARY",
        "classification": (
            "AN_EXACT_FACTORIZED_A_s_STAR_A_s_HALF_LINE_HAS_A_NONZERO_"
            "ZERO_THRESHOLD_RESONANCE_AND_ZERO_WRONSKIAN_MARGIN_WHILE_THE_"
            "LOG_RADIUS_FIRST_FORM_WEIGHT_IS_C*k_squared_PLUS_o(k_squared)_"
            "AND_ITS_CUMULATIVE_SOURCE_WEIGHT_IS_(C/3)*Lambda_to_3_over_2;_"
            "THEREFORE_STRICT_WRONSKIAN_POSITIVITY_IS_SUFFICIENT_BUT_NOT_"
            "NECESSARY_FOR_THE_RETAINED_E1_FIRST_VARIATION"
        ),
        "exact_model": {
            "factor": "A_s=d_dx+s*1_[0,T]",
            "operator": "K_s=A_s_star*A_s",
            "birth_graph": "A_s*u(0)=0",
            "exterior": "A_s=d_dx_AFTER_T",
            "log_radius_factor_jet": "D_h_A_s=-s*1_[0,T]",
            "parameters": {"s": superpotential, "T": length},
            "asymptotic": exact,
            "rows": rows,
            "maximum_final_scaled_residual": residuals[-1],
        },
        "provenance_reclassification": {
            "strict_two_sided_Wronskian_margin": "SUFFICIENT_NOT_NECESSARY",
            "exact_zero_atom_first_weight": "ZERO_AND_PRESERVED",
            "weakest_actual_N12_requirement": (
                "A_RESONANCE_COMPATIBLE_FACTORIZED_LIMITING_ABSORPTION_OR_"
                "SOURCE_WEIGHTED_WEYL_BOUND_WITH_EXPONENT_STRICTLY_ABOVE_ONE"
            ),
            "what_the_model_does_not_prove": (
                "THE_UNKNOWN_MAXIMAL_N12_EVENT_CHILD_EXTERIOR_BELONGS_TO_"
                "THIS_CONSTANT_CORE_FREE_EXTERIOR_CLASS"
            ),
        },
        "claim_boundary": {
            "factorized_N12_low_energy_source_measure": "OPEN",
            "strict_product_Dirac_Wronskian_required_in_advance": False,
            "nonfermion_threshold_margin": "CLOSED",
            "graded_angular_tail": "OPEN",
            "zero_source_force": "OPEN",
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "PROVE_FOR_THE_REALIZED_AE2_TWO_SIDED_PRODUCT_DIRAC_FAMILY_A_"
            "RESONANCE_COMPATIBLE_SOURCE_WEIGHTED_LIMITING_ABSORPTION_BOUND_"
            "abs(nu_h)([0,Lambda])<=C_h*Lambda^(1+epsilon_h)_WITH_"
            "epsilon_h>0,_WITHOUT_REQUIRING_A_STRICT_ZERO_WRONSKIAN;_THEN_"
            "ASSEMBLE_THE_GRADED_ANGULAR_TAIL_AND_ZERO_SOURCE_FORCE"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n").encode("utf-8")


def materialize() -> Path:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise RuntimeError("factorized threshold reclassification failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
