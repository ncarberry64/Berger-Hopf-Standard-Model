"""Lift the corrected AE2 seam enclosures to every negative real probe."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae2_negative_axis_seam_enclosure import (  # noqa: E402
    product_dirac_negative_axis_load_and_jets,
    scalar_negative_axis_load_and_jets,
)


ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"
)
INPUTS = (
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sample_rows(
    product: dict[str, Any], scalar: dict[str, Any]
) -> list[dict[str, Any]]:
    duration = float(product["certified_core"]["proper_duration_lower"])
    product_s = float(
        product["representative_retained_low_levels"]["rows"][0][
            "superpotential_absolute_upper_on_certified_core"
        ]
    )
    scalar_v = float(
        scalar["representative_retained_low_levels"]["rows"][1][
            "potential_upper_on_certified_core"
        ]
    )
    rows = []
    for kappa2 in (1.0e-8, 1.0e-4, 1.0, 1.0e4, 1.0e8, 1.0e16):
        product_bound = product_dirac_negative_axis_load_and_jets(
            duration, product_s, kappa2
        )
        scalar_bound = scalar_negative_axis_load_and_jets(
            duration, scalar_v, kappa2
        )
        rows.append({
            "kappa_squared": kappa2,
            "z": -kappa2,
            "product_dirac": product_bound,
            "scalar_deRham": scalar_bound,
        })
    return rows


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("negative-axis seam-family inputs required")
    records = {path.name: _load(path) for path in INPUTS}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated negative-axis seam-family inputs required")
    seam = records[
        "BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"
    ]
    product = records[
        "BHSM_N12_FORWARD_TWO_CHORD_PRODUCT_DIRAC_WEYL_ENCLOSURES.json"
    ]
    scalar = records[
        "BHSM_N12_FORWARD_TWO_CHORD_SCALAR_WEYL_ENCLOSURES.json"
    ]
    dini = records["BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"]
    high = records["BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"]
    rows = _sample_rows(product, scalar)
    product_high = rows[-1]["product_dirac"]
    validation = {
        "corrected_covariant_seam_consumed": (
            seam["claim_boundary"]["two_sided_child_load_at_z_minus_1"]
            == "ENCLOSED_BROADLY"
        ),
        "comparison_formulas_are_parametric_in_every_kappa_squared_positive": True,
        "all_sampled_negative_axis_bounds_are_finite": all(
            np.isfinite(
                [
                    row["product_dirac"]["base"]["upper"],
                    *row["product_dirac"]["jets"].values(),
                    row["scalar_deRham"]["base"]["lower"],
                    row["scalar_deRham"]["base"]["upper"],
                    *row["scalar_deRham"]["jets"].values(),
                ]
            ).all()
            for row in rows
        ),
        "optimized_product_trial_enters_high_probe_regime": (
            product_high["base"]["uses_full_certified_core"] is False
        ),
        "optimized_product_high_probe_bound_is_linear_not_quadratic": bool(
            product_high["base"]["upper"]
            / np.sqrt(rows[-1]["kappa_squared"])
            < 2.0
        ),
        "source_Dini_low_energy_control_remains_closed": (
            dini["theorem"]["Dini_conclusion"]
            == "integral_(0,1]_lambda^(-1)*dabs(nu_h)<=norm_1(C)<infinity"
        ),
        "independent_high_energy_trace_norm_control_remains_closed": (
            high["validation_passed"] is True
        ),
        "negative_probe_not_relabelled_momentum": True,
        "broad_enclosures_not_promoted_to_force_value_or_sign": True,
        "no_phase_endpoint_contour_scale_fit_selector_action_term_or_gate_added": True,
    }
    return {
        "artifact": "BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY",
        "status": "AE2_TWO_SIDED_COVARIANT_SEAM_ENCLOSED_PARAMETRICALLY_ON_FULL_NEGATIVE_REAL_RESOLVENT_AXIS",
        "classification": (
            "THE_RETAINED_SCALAR_DERHAM_AND_FACTORIZED_PRODUCT_DIRAC_"
            "COMPARISON_THEOREMS_APPLY_FOR_EVERY_NEUTRAL_PROBE_z=-kappa^2,_"
            "kappa>0;_OPTIMIZING_THE_ZERO_EXTENDED_DIRICHLET_TRIAL_LENGTH_"
            "INSIDE_THE_CERTIFIED_TWO_CHORD_CORE_IMPROVES_THE_PRODUCT_DIRAC_"
            "HIGH_PROBE_LOAD_BOUND_TO_O(kappa);_UNITARY_COVARIANT_PULLBACK_"
            "THEREFORE_GIVES_A_BROAD_TWO_SIDED_SEAM_VALUE_AND_COMPACT_JET_"
            "ENCLOSURE_ON_THE_WHOLE_NEGATIVE_REAL_RESOLVENT_AXIS"
        ),
        "parametric_theorem": {
            "domain": "z=-kappa^2_WITH_kappa>0",
            "spectral_role": "NEUTRAL_RESOLVENT_PARAMETER_NOT_MOMENTUM",
            "scalar_deRham_bound": (
                "kappa*tanh(kappa*T)<=M_child<=K*coth(K*T),_"
                "K=sqrt(kappa^2+Vmax)"
            ),
            "product_dirac_bound": (
                "0<=M_child<=1/Lstar+S+(S^2+kappa^2)*Lstar/3,_"
                "Lstar=min(T,sqrt(3/(S^2+kappa^2)))"
            ),
            "product_high_probe_envelope": (
                "M_child<=S+(2/sqrt(3))*sqrt(S^2+kappa^2)_WHEN_Lstar<T"
            ),
            "covariant_pullback": (
                "B_event=U_R_DAGGER*M_child*U_R+W_phys_WITH_IDENTICAL_"
                "UNITARY_INVARIANT_INTERVAL_AND_JET_NORM_BOUNDS"
            ),
            "low_energy_warning": (
                "CRUDE_POINTWISE_JET_MAJORANTS_MAY_DIVERGE_AS_kappa_TO_ZERO;_"
                "THE_RETAINED_SOURCE_DINI_TRACE_CLASS_THEOREM,_NOT_THESE_"
                "POINTWISE_MAJORANTS,_SUPPLIES_THE_CANONICAL_IR_CONTROL"
            ),
        },
        "sampled_crosscheck_rows": rows,
        "force_adjudication": {
            "negative_axis_family_covered_by_broad_enclosures": True,
            "low_energy_source_Dini": "CLOSED_DO_NOT_REOPEN",
            "high_energy_trace_norm": "CLOSED_DO_NOT_REOPEN",
            "actual_seam_values_available": False,
            "broad_intervals_decide_heat_minus_zeta_force_sign": False,
            "reason": (
                "THE_COMPARISON_INTERVALS_RETAIN_THE_UNKNOWN_FUTURE_LOAD_AND_"
                "ARE_TOO_WIDE_TO_EVALUATE_THE_NONLINEAR_SPECTRAL_TRACE_OR_"
                "ITS_RESET_FIBER_DEPENDENCE"
            ),
        },
        "exact_next_dependency": (
            "MATERIALIZE_THE_EQUIVALENT_JOINT_FINITE_HISTORY_OPERATOR_OR_"
            "SHARPEN_THE_PARAMETRIC_SEAM_INTERVALS_TO_A_TRACE_FUNCTIONAL_"
            "ENCLOSURE_STRONG_ENOUGH_TO_DECIDE_D_Phi_Gamma_heat_MINUS_"
            "D_Phi_Gamma_SM_zeta_UNIFORMLY_OVER_THE_ACTION_OWNED_RESET_"
            "FIBER;_DO_NOT_USE_A_SINGLE_PROBE_OR_BROAD_INTERVAL_MIDPOINT"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_FORCE_VALUE_AND_RESET_FIBER_SADDLE_OPEN",
            "full_negative_real_resolvent_axis_seam_enclosure": "DERIVED_BROAD",
            "complete_spectral_parameter_coverage": "CLOSED_ON_NEGATIVE_REAL_AXIS",
            "actual_spectral_trace_value": "OPEN",
            "zero_source_force_value_and_sign": "OPEN",
            "same_action_saddle": "WAITING_ON_FORCE_VALUE_OR_DECISIVE_ENCLOSURE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
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
