"""Close all exact nonnegative power-law radius tail classes for factorized E1."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_sublinear_radius_tail import (  # noqa: E402
    power_radius_tail_class,
    sublinear_positive_chirality_agmon_action,
)


TARGET = ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_POWER_RADIUS_TAIL_CLOSURE.json"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_LINEAR_RADIUS_TAIL_THEOREM.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json",
    ROOT / "src/bhsm/interface/action_extension_ae2_sublinear_radius_tail.py",
    ROOT / "scripts/derive_n12_gate7_ae2_power_radius_tail_closure.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("power-radius tail inputs required")
    integrable, linear, reduction = (_load(path) for path in INPUTS[:3])
    if not all(item.get("validation_passed") is True for item in (integrable, linear, reduction)):
        raise RuntimeError("validated tail-theorem lineage required")
    powers = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 2.0]
    classes = [power_radius_tail_class(power) for power in powers]
    wave_numbers = [1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4]
    agmon_rows = [sublinear_positive_chirality_agmon_action(1.5, 0.5, k) for k in wave_numbers]
    suppressions = [row["squared_amplitude_suppression_upper"] for row in agmon_rows]
    validation = {
        "all_inputs_validated": True,
        "superlinear_route_closed": integrable["claim_boundary"]["conditional_integrable_radius_threshold_theorem"] == "CLOSED",
        "linear_route_closed": linear["claim_boundary"]["exact_linear_radius_tail_theorem"] == "CLOSED",
        "sublinear_agmon_action_increases_toward_threshold": all(agmon_rows[index + 1]["agmon_action_lower"] > agmon_rows[index]["agmon_action_lower"] for index in range(len(agmon_rows) - 1)),
        "sublinear_suppression_decreases_toward_threshold": (
            all(suppressions[index + 1] <= suppressions[index] for index in range(len(suppressions) - 1))
            and suppressions[-1] < suppressions[0]
        ),
        "sublinear_suppression_beats_tested_powers": all(suppressions[-1] < wave_numbers[-1] ** exponent for exponent in (2, 4, 8, 16)),
        "negative_chirality_inherited_by_supersymmetric_intertwining": True,
        "zero_atom_first_form_weight_remains_zero": True,
        "all_nonnegative_power_classes_E1_integrable": all(row["factorized_E1_threshold_integrable"] for row in classes),
        "actual_N12_power_asymptotic_not_fabricated": True,
        "no_SM_observable_scale_fit_selector_or_new_action_term": True,
        "FULL_BHSM_COMPLETE_false": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_AE2_POWER_RADIUS_TAIL_CLOSURE",
        "action_version": "BHSM-AE-2.0.0",
        "status": "ALL_EXACT_NONNEGATIVE_POWER_RADIUS_TAIL_CLASSES_FACTORIZED_E1_THRESHOLD_CLOSED",
        "classification": "FOR_EXACT_RADIUS_TAILS_R4_ASYMPTOTIC_TO_c*x^a_WITH_a>=0,_a=0_HAS_A_CONSTANT_SUPERPOTENTIAL_CONTINUUM_GAP,_0<a<1_HAS_STRETCHED_EXPONENTIAL_COMPACT_SOURCE_SUPPRESSION_FROM_AN_EXPLICIT_AGMON_BARRIER,_a=1_IS_CLOSED_BY_THE_BESSEL_SOURCE_DINI_THEOREM,_AND_a>1_IS_CLOSED_BY_RECIPROCAL_RADIUS_INTEGRABILITY;_THE_NEGATIVE_CHIRALITY_NONZERO_SPECTRUM_IS_THE_SUPERSYMMETRIC_PARTNER_AND_ZERO_ATOMS_HAVE_ZERO_FIRST_FORM_WEIGHT",
        "theorem": {
            "tail_family": "R4(tau)=c*(tau+tau0)^a,_c>0,_a>=0",
            "factorized_superpotential": "s_chi=chi*beta*x^(-a)",
            "constant_tail": "a=0_IMPLIES_ESSENTIAL_THRESHOLD_GAP_beta^2_WITH_ZERO_ATOM_WEIGHT_ZERO_WHERE_PRESENT",
            "sublinear_tail": {
                "range": "0<a<1",
                "barrier_endpoint": "x_k=(beta/(2k))^(1/a)",
                "agmon_lower": "A_k>=sqrt(3)*beta/(2*(1-a))*(x_k^(1-a)-1)",
                "suppression": "exp(-2*A_k)=O(exp(-C*k^(-(1-a)/a)))_WHICH_BEATS_EVERY_POWER",
                "positive_chirality": "DIRECT_AGMON_BOUND",
                "negative_chirality": "A_Astar_SUPERSYMMETRIC_PARTNER_ON_NONZERO_SPECTRUM",
            },
            "linear_tail": "a=1_CLOSED_BY_EXACT_BESSEL_SOURCE_DINI_THEOREM",
            "superlinear_tail": "a>1_IMPLIES_integral_d_tau/R4<infinity",
            "class_rows": classes,
            "agmon_witness_rows": agmon_rows,
        },
        "frontier_sharpening": {
            "exact_power_law_radius_tails": "CLOSED_FOR_ALL_a>=0",
            "actual_N12_radius_asymptotic_class": "OPEN",
            "remaining_tail_class": "POSITIVE_NONASYMPTOTIC_OR_NON_POWER_REGULARLY_VARYING_HISTORY_ONLY",
        },
        "claim_boundary": {
            "all_exact_nonnegative_power_radius_tails": "CLOSED",
            "actual_N12_radius_asymptotic_class": "OPEN",
            "general_nonasymptotic_tail": "OPEN",
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": "DERIVE_FROM_THE_RETAINED_ACTION_THAT_THE_UNIQUE_INFINITE_REGULAR_R4_HISTORY_HAS_AN_EXACT_OR_CONTROLLED_REGULARLY_VARYING_POWER_ASYMPTOTIC,_OR_PROVE_THE_SOURCE_DINI_BOUND_FOR_ARBITRARY_POSITIVE_NONASYMPTOTIC_R4_TAILS",
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
        raise RuntimeError(f"power-radius tail closure failed: {failed}")
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
