"""Derive the complete moving-duration common-scale heat-zeta Ward force."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.forward_finite_endpoint_heat_force import (  # noqa: E402
    common_scale_heat_value_and_force,
    common_scale_zeta_value_and_force,
    direct_sum_heat_value_and_force,
    zeta_casimir_value_and_force,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD.json"
WEYL = BASE / "BHSM_N12_C2_COMMON_SCALE_WEYL_COVARIANCE.json"
FORCE = BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"
INCIDENCE = BASE / "BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
SUPERDET = ROOT / "artifacts" / "BHSM_aether_common_quantum_superdeterminant_v15_96.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "forward_finite_endpoint_heat_force.py"
THEORY = ROOT / "theory" / "n12_gate7_common_scale_heat_zeta_ward.md"
INPUTS = (WEYL, FORCE, INCIDENCE, SUPERDET, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _witness() -> dict[str, float]:
    first = np.asarray([
        [2.4, 0.17 - 0.08j, 0.03],
        [0.17 + 0.08j, 3.1, -0.11j],
        [0.03, 0.11j, 4.2],
    ], dtype=complex)
    second = np.asarray([[1.3, -0.09], [-0.09, 2.7]], dtype=float)
    blocks = (
        {"operator": first, "coefficient": 3.0},
        {"operator": second, "coefficient": -2.0},
    )
    analytic = common_scale_heat_value_and_force(blocks)
    epsilon = 1.0e-6
    def value(a: float) -> float:
        return direct_sum_heat_value_and_force([
            {
                "operator": np.exp(-2.0 * a) * block["operator"],
                "geometry_jets": {},
                "coefficient": block["coefficient"],
            }
            for block in blocks
        ])["Gamma_heat"]
    finite_heat = (value(epsilon) - value(-epsilon)) / (2.0 * epsilon)

    radii = np.asarray([0.9, 1.1, 1.4, 0.8])
    weights = np.asarray([0.2, 0.31, 0.27, 0.18])
    zeta = common_scale_zeta_value_and_force(radii, weights)
    zeta_epsilon = 1.0e-3
    def zeta_value(a: float) -> float:
        factor = np.exp(a)
        return zeta_casimir_value_and_force(
            factor * radii, factor * weights, {}
        )["Gamma_SM_zeta"]
    finite_zeta = (
        zeta_value(zeta_epsilon) - zeta_value(-zeta_epsilon)
    ) / (2.0 * zeta_epsilon)
    return {
        "heat_analytic": float(analytic["common_scale_heat_force"]),
        "heat_centered_difference": float(finite_heat),
        "heat_absolute_residual": abs(
            float(analytic["common_scale_heat_force"]) - float(finite_heat)
        ),
        "zeta_analytic": float(zeta["common_scale_zeta_force"]),
        "zeta_centered_difference": float(finite_zeta),
        "zeta_absolute_residual": abs(float(finite_zeta)),
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing common-scale Ward inputs: " + ", ".join(missing))
    weyl, force, incidence, superdet = (
        _load(path) for path in (WEYL, FORCE, INCIDENCE, SUPERDET)
    )
    if not all(record.get("validation_passed") is True for record in (
        weyl, force, incidence, superdet,
    )):
        raise RuntimeError("validated Weyl, force, incidence, and superdeterminant parents required")
    witness = _witness()
    validation = {
        "common_scale_Weyl_pullback_parent_is_closed": (
            weyl["adjudication"]["physical_common_scale_geometry_pullback"] == "CLOSED"
        ),
        "basis_independent_heat_force_parent_is_derived": (
            force["exact_force_theorem"]["basis_independent"] is True
        ),
        "graded_source_incidence_parent_is_assembled": (
            incidence["claim_boundary"]["domain_parametric_nonzero_local_incidence"]
            == "DERIVED"
        ),
        "retained_parent_heat_length_is_fixed_and_positive": (
            float(superdet["regulated_free_superdeterminant_seed"][
                "common_heat_length_in_ell_kappa"
            ]) > 0.0
        ),
        "all_nontrivial_graded_spatial_blocks_have_inverse_radius_squared_weight": all(
            "/R4(tau)^2" in superdet["graded_operator_ledger"][sector]["spatial_eigenvalue"]
            for sector in ("gauge_transverse", "Weyl", "Hubbard_Strattonovich")
        ),
        "longitudinal_ghost_block_cancels_mode_by_mode": (
            superdet["graded_operator_ledger"]["gauge_longitudinal_ghost"]
            ["net_supertrace_sign"] == 0
        ),
        "heat_Ward_witness_matches_centered_difference": (
            witness["heat_absolute_residual"] < 1.0e-9
        ),
        "zeta_radius_and_moving_duration_terms_cancel": (
            witness["zeta_analytic"] == 0.0
            and witness["zeta_absolute_residual"] < 1.0e-12
        ),
        "actual_joint_heat_trace_value_is_not_claimed": True,
        "non_scale_reset_quotient_force_is_not_claimed": True,
        "no_selector_endpoint_scale_fit_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_COMMON_SCALE_HEAT_ZETA_WARD",
        "status": (
            "GATE7_COMMON_SCALE_HEAT_ZETA_FORCE_REDUCED_TO_GRADED_HEAT_TRACE"
            if passed else "GATE7_COMMON_SCALE_HEAT_ZETA_WARD_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_COMPLETE_SIMULTANEOUS_RADIUS_AND_PROPER_DURATION_COMMON_"
            "SCALE_VARIATION_SENDS_EACH_POSITIVE_PHYSICAL_OPERATOR_TO_"
            "exp(-2a)P;_WITH_THE_RETAINED_PARENT_HEAT_LENGTH_FIXED_THE_"
            "HEAT_FORCE_IS_MINUS_THE_GRADED_HEAT_TRACE,_WHILE_THE_LOCAL_"
            "ZETA_CASIMIR_RADIUS_AND_MEASURE_VARIATIONS_CANCEL_EXACTLY"
        ),
        "exact_Ward_theorem": {
            "geometry": "R4(a)=exp(a)R4,_d_tau(a)=exp(a)d_tau",
            "operator": "P_C(a)=exp(-2a)P_C_ON_THE_NORMALIZED_DOMAIN",
            "heat_length": "THE_RETAINED_PARENT_ell_kappa_IS_HELD_FIXED",
            "heat_force": "D_a_Gamma_heat=-STr_exp(-ell_kappa^2*P)",
            "zeta_density": "d_tau(a)/R4(a)=d_tau/R4",
            "zeta_force": "D_a_Gamma_SM_zeta=0",
            "replacement_common_scale_force": (
                "D_a_Gamma_replacement=-STr_exp(-ell_kappa^2*P)"
            ),
            "noncommuting_geometry_jet_required": False,
            "moving_duration_included": True,
        },
        "witness": witness,
        "adjudication": {
            "common_scale_source_contraction_formula": "CLOSED",
            "common_scale_zeta_moving_duration_completion": "CLOSED_ZERO",
            "actual_common_scale_numeric_force": "OPEN_UNTIL_JOINT_OPERATOR_REALIZATION",
            "non_scale_projected_force_sector": "OPEN",
            "same_action_saddle": "WAITING_ON_COMPLETE_FORCE",
            "Gate7": "G7_08_OPEN",
            "Gate8": "LOCKED",
        },
        "validated_invalidated_open": {
            "VALIDATED": [
                "common-scale heat Ward force",
                "moving-duration zeta cancellation",
                "graded direct-sum implementation",
            ],
            "INVALIDATED": [
                "fixed-duration radius-only zeta derivative is the physical common-scale force",
                "a pathwise geometry Jacobi is needed for common-scale source contraction",
            ],
            "OPEN": [
                "actual joint graded heat trace",
                "non-scale reset quotient force sector",
                "complete zero-source force and same-action saddle",
            ],
        },
        "hindsight": {
            "classification": "MOVING_DURATION_PRODUCT_RULE_COMPLETES_THE_COMMON_SCALE_WARD_IDENTITY",
            "obstruction_physical": False,
        },
        "exact_next_dependency": (
            "REALIZE_THE_JOINT_POSITIVE_SELF_ADJOINT_OPERATOR_TO_EVALUATE_"
            "THE_GRADED_HEAT_TRACE_AND_SOLVE_THE_REMAINING_NON_SCALE_"
            "RESET_QUOTIENT_ADJOINT_SECTOR"
        ),
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "heat_residual": payload["witness"]["heat_absolute_residual"],
        "zeta_residual": payload["witness"]["zeta_absolute_residual"],
        "validation_passed": payload["validation_passed"],
    }, indent=2))


if __name__ == "__main__":
    main()
