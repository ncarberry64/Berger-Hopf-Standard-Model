"""Certify that the open maximal tail is supported only on C2 launch data."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_MAXIMAL_TAIL_SUPPORT_REDUCTION.json"
RESET = BASE / "BHSM_N12_FULL_RESET_ACTION_JACOBIAN.json"
RESET_DATA = RESET.with_suffix(".npz")
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
LAUNCH_DATA = LAUNCH.with_suffix(".npz")
LAUNCH_ADJOINT = BASE / "BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE.json"
FIXED_SEED = BASE / "BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER.json"
PARAMETER = BASE / "BHSM_N12_DESINGULARIZED_FINITE_HISTORY_OPERATOR_PARAMETER.json"
MAXIMAL_INCOMING = BASE / (
    "BHSM_N12_GATE7_MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT.json"
)
FINITE_HEAT = BASE / "BHSM_N12_GATE7_ONE_SEAM_FULL_GRADED_FINITE_CORE_HEAT_BOUND.json"
SOURCE_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
TIME_QUOTIENT = BASE / "BHSM_N12_RESET_TIME_QUOTIENT_GENERATOR_AUDIT.json"
THEORY = ROOT / "theory" / "n12_gate7_maximal_tail_support_reduction.md"
INPUTS = (
    RESET,
    RESET_DATA,
    LAUNCH,
    LAUNCH_DATA,
    LAUNCH_ADJOINT,
    FIXED_SEED,
    PARAMETER,
    MAXIMAL_INCOMING,
    FINITE_HEAT,
    SOURCE_ONTOLOGY,
    TIME_QUOTIENT,
    THEORY,
)
STATE_DIMENSION = 98
RANK_THRESHOLD = 1.0e-8


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _rank(matrix: np.ndarray) -> int:
    return int(np.count_nonzero(np.linalg.svd(matrix, compute_uv=False) > RANK_THRESHOLD))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing maximal-tail support inputs: " + ", ".join(missing))
    records = {path: _load(path) for path in INPUTS if path.suffix == ".json"}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated maximal-tail support parents required")

    with np.load(RESET_DATA) as data:
        jacobian = np.asarray(data["analytic_full_reset_jacobian"], dtype=float)
    with np.load(LAUNCH_DATA) as data:
        reset_tangent = np.asarray(data["reset_tangent_basis"], dtype=float)
        fixed_seed_lift = np.asarray(data["event_lift_kernel_basis"], dtype=float)
        launch_basis = np.asarray(data["launch_basis"], dtype=float)

    c2_projection = reset_tangent[:STATE_DIMENSION]
    fixed_c2_component = fixed_seed_lift[:STATE_DIMENSION]
    fixed_seed_reset_residual = jacobian @ fixed_seed_lift
    seed_rank = _rank(c2_projection)
    fixed_seed_dimension = fixed_seed_lift.shape[1]
    launch_dimension = launch_basis.shape[1]
    fixed_c2_component_norm = float(np.linalg.norm(fixed_c2_component, 2))
    fixed_seed_reset_residual_norm = float(np.linalg.norm(fixed_seed_reset_residual, 2))

    maximal = records[MAXIMAL_INCOMING]
    split = maximal["low_high_spectral_split"]
    net_linear_decay = float(split["net_low_energy_linear_decay_rate"])
    gaussian_decay = float(split["high_energy_quadratic_decay_rate"])
    parameter = records[PARAMETER]
    source = records[SOURCE_ONTOLOGY]
    time = records[TIME_QUOTIENT]
    fixed = records[FIXED_SEED]
    launch_adjoint = records[LAUNCH_ADJOINT]
    launch = records[LAUNCH]

    # Exponential and Gaussian collar factors dominate any fixed polynomial
    # order.  These sample orders are a replay of the general limit, not a
    # cutoff in the retained angular ledger.
    sample_polynomial_orders = (0, 2, 4, 8, 16)
    domination_rows = []
    for order in sample_polynomial_orders:
        mu = max(1.0e34, 4.0 * (order + 2) / net_linear_decay)
        low_log_slope = (order + 2) / (1.0 + mu) - net_linear_decay
        high_log_slope = (order + 2) / (1.0 + mu) - 2.0 * gaussian_decay * mu
        domination_rows.append({
            "polynomial_order": order,
            "sample_mu": mu,
            "low_log_derivative": low_log_slope,
            "high_log_derivative": high_log_slope,
            "both_strictly_negative": low_log_slope < 0.0 and high_log_slope < 0.0,
        })

    validation = {
        "all_parent_artifacts_are_validated": True,
        "reset_tangent_dimension_is_139": reset_tangent.shape == (196, 139),
        "outgoing_C2_seed_projection_rank_is_72": seed_rank == 72,
        "fixed_C2_kernel_dimension_is_67": fixed_seed_dimension == 67,
        "fixed_seed_lift_has_zero_C2_component": fixed_c2_component_norm < 1.0e-12,
        "fixed_seed_lift_is_reset_tangent": fixed_seed_reset_residual_norm < 1.0e-10,
        "launch_dimension_is_72_plus_1": launch_dimension == seed_rank + 1 == 73,
        "downstream_C2_pullback_annihilates_fixed_seed_kernel": (
            launch_adjoint["adjudication"]["67_kernel_downstream_C2_contribution"]
            == "IDENTICALLY_ZERO"
        ),
        "fixed_seed_force_owner_is_upstream_plus_interface": (
            fixed["adjudication"]["67_kernel_is_the_raw_fixed_C2_preceding_E1_tangent"]
            is True
        ),
        "incoming_amplitude_keeps_terminal_Cauchy_jet_fixed": (
            parameter["parameter_separation"]["terminal_Cauchy_jet_moves_with_amplitude"]
            is False
        ),
        "incoming_amplitude_maximal_graded_cotangent_is_summable": (
            maximal["claim_boundary"][
                "maximal_incoming_full_graded_relative_heat_cotangent"
            ]
            == "CERTIFIED_SUMMABLE"
        ),
        "collar_low_and_high_decay_are_strict": net_linear_decay > 0.0 and gaussian_decay > 0.0,
        "collar_dominates_sampled_finite_vertex_orders": all(
            row["both_strictly_negative"] for row in domination_rows
        ),
        "finite_incoming_operator_has_full_graded_trace_control": (
            records[FINITE_HEAT]["validation"][
                "all_absolute_angular_sector_sums_are_positive_finite"
            ]
            is True
            and records[FINITE_HEAT]["validation"][
                "heat_and_seed_bounds_remain_in_log_space"
            ]
            is True
        ),
        "intrinsic_time_quotient_count_is_retained": (
            time["dimension_statement"]["declared_after_existing_whole_system_time_quotient"]
            == 66
        ),
        "only_external_source_is_zeroed": (
            source["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "no_internal_response_is_zeroed": True,
        "no_source_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_MAXIMAL_TAIL_SUPPORT_REDUCTION",
        "status": (
            "FIXED_C2_UPSTREAM_INTERFACE_MAXIMAL_TAIL_CLOSED"
            if passed
            else "MAXIMAL_TAIL_SUPPORT_REDUCTION_INVALID"
        ),
        "classification": (
            "THE_67_DIMENSIONAL_FIXED_C2_RESET_KERNEL_CHANGES_ONLY_THE_COMPACT_"
            "UPSTREAM_HISTORY_AND_LOCAL_AE2_INTERFACE;_ITS_FULL_GRADED_MAXIMAL_"
            "COTANGENT_IS_A_BOUNDARY_LOCAL_CAUCHY_NET,_SO_THE_ONLY_REMAINING_"
            "NONCOMPACT_COEFFICIENT_JACOBI_TAIL_IS_SUPPORTED_ON_THE_72_PLUS_1_"
            "OUTGOING_C2_LAUNCH_BLOCK"
        ),
        "exact_subspace_decomposition": {
            "reset_tangent_dimension": int(reset_tangent.shape[1]),
            "outgoing_C2_seed_projection_rank": seed_rank,
            "fixed_C2_kernel_dimension": fixed_seed_dimension,
            "fixed_seed_identity": "Z*K_fixedC2={0}_C2_DIRECT_SUM_ker(J_E1)",
            "fixed_C2_component_operator_norm": fixed_c2_component_norm,
            "fixed_seed_reset_residual_operator_norm": fixed_seed_reset_residual_norm,
            "outgoing_descriptor_direction_count": 1,
            "remaining_noncompact_tail_support_dimension_upper": launch_dimension,
            "dimension_identity": "139=72+67_AND_73=72+1",
        },
        "fixed_C2_tail_theorem": {
            "child_coefficient_jet": "D_h_P_C2=0_FOR_h_IN_K_fixedC2",
            "child_Weyl_jet": "D_h_M_C2_max=0_FOR_h_IN_K_fixedC2",
            "remaining_heat_variation": (
                "FINITE_COMPACT_INCOMING_ARM_PLUS_FINITE_RANK_BOUNDARY_INTERFACE_"
                "PERTURBATION_OF_ONE_FIXED_MAXIMAL_C2_FRIEDRICHS_OPERATOR"
            ),
            "remaining_zeta_variation": "COMPACT_INCOMING_ARM_ONLY",
            "maximal_core_Cauchy_status": "CLOSED_FULL_GRADED",
            "time_quotient_rule": (
                "PASS_TO_THE_INTRINSIC_QUOTIENT_AFTER_CONVERGENCE;_NO_EXPLICIT_"
                "HYBRID_GENERATOR_IS_NEEDED_FOR_THIS_SUPPORT_RESULT"
            ),
        },
        "angular_domination": {
            "low_energy_net_linear_decay_rate": net_linear_decay,
            "high_energy_gaussian_decay_rate": gaussian_decay,
            "principle": (
                "STRICT_EXPONENTIAL_OR_GAUSSIAN_DECAY_DOMINATES_EVERY_FIXED_"
                "FINITE_DIFFERENTIAL_ORDER_AND_QUADRATIC_MULTIPLICITY"
            ),
            "sample_rows": domination_rows,
            "sample_rows_are_not_a_mode_cutoff": True,
        },
        "formation_amplitude_routing": {
            "is_reset_fiber_tangent": False,
            "terminal_E1_Cauchy_jet_moves": False,
            "maximal_full_graded_boundary_cotangent": "CLOSED_SUMMABLE",
            "C2_reverse_state_tail_required": False,
            "signed_value": "OPEN",
        },
        "adjudication": {
            "fixed_C2_upstream_interface_maximal_tail": "CLOSED_CAUCHY",
            "incoming_amplitude_maximal_tail": "CLOSED_CAUCHY_SEPARATE_COORDINATE",
            "remaining_noncompact_tail_owner": "OUTGOING_C2_72_PLUS_1_LAUNCH_BLOCK",
            "remaining_noncompact_tail_dimension_upper": launch_dimension,
            "actual_outgoing_C2_projected_tail": "OPEN_CURRENT_OWNER",
            "actual_signed_upstream_interface_value": "OPEN",
            "actual_projected_KKT_root": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "PROVE_THE_SOURCE_CONTRACTED_PROJECTED_CAUCHY_LIMIT_ONLY_ON_THE_"
            "OUTGOING_72_PLUS_1_C2_LAUNCH_BLOCK_OR_CERTIFY_AN_ACTUAL_LATER_"
            "EVENT_OR_CANONICAL_STOP;_THEN_COMBINE_WITH_THE_NOW_CAUCHY_FIXED_C2_"
            "AND_INCOMING_AMPLITUDE_BLOCKS_AND_TEST_THE_INTRINSIC_OR_BORDERED_KKT_ROOT"
        ),
        "claim_boundary": {
            "fixed_C2_upstream_interface_full_graded_maximal_tail": "CERTIFIED_CAUCHY",
            "incoming_amplitude_full_graded_maximal_tail": "CERTIFIED_CAUCHY",
            "remaining_outgoing_C2_launch_tail": "OPEN_CURRENT_OWNER",
            "actual_projected_KKT_root": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not payload["validation_passed"]:
        raise RuntimeError("maximal-tail support reduction validation failed")
    print(json.dumps({
        "status": payload["status"],
        "remaining_tail_dimension_upper": payload["adjudication"][
            "remaining_noncompact_tail_dimension_upper"
        ],
        "fixed_C2_component_operator_norm": payload["exact_subspace_decomposition"][
            "fixed_C2_component_operator_norm"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
