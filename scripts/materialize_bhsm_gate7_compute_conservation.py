"""Materialize the Gate-7 compute audit and budget ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "artifacts/flagship_integration"
C = ROOT / "artifacts/current_semantics"
MANIFEST = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_CHECKPOINT_MANIFEST.json"
COMPUTE_BENCHMARK = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_COMPUTE_BENCHMARK.json"
BILINEAR_AUDIT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_EQUIVALENCE_AUDIT.json"
BILINEAR_DATA = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_EQUIVALENCE_AUDIT.npz"
ALL_ENDPOINTS = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS.json"
ALL_ENDPOINTS_DATA = ALL_ENDPOINTS.with_suffix(".npz")
OUTWARD_AUDIT = C / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_OUTWARD_COMPUTE_JUSTIFICATION.json"
OUTWARD = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_OUTWARD_RECONCILIATION.json"
OUTWARD_DATA = OUTWARD.with_suffix(".npz")
MIXED_HS_AUDIT = C / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_COMPUTE_JUSTIFICATION.json"
THEORY = ROOT / "theory/n12_gate7_compute_justification_audit.md"
THIS_SCRIPT = Path(__file__).resolve()
AUDIT = C / "BHSM_COMPUTE_JUSTIFICATION_AUDIT.json"
LEDGER = C / "BHSM_COMPUTE_BUDGET_LEDGER.json"
AUDIT_INPUTS = (MANIFEST, COMPUTE_BENCHMARK, THEORY, THIS_SCRIPT)
LEDGER_INPUTS = (
    MANIFEST,
    COMPUTE_BENCHMARK,
    ALL_ENDPOINTS,
    ALL_ENDPOINTS_DATA,
    OUTWARD_AUDIT,
    OUTWARD,
    OUTWARD_DATA,
    MIXED_HS_AUDIT,
    THEORY,
    THIS_SCRIPT,
)
INPUTS = LEDGER_INPUTS


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payloads() -> tuple[dict[str, object], dict[str, object]]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("validation_passed") is not True:
        raise ValueError("checkpoint manifest is not valid")
    benchmark = json.loads(COMPUTE_BENCHMARK.read_text(encoding="utf-8"))
    if benchmark.get("validation_passed") is not True:
        raise ValueError("compute benchmark is not valid")
    all_endpoints = json.loads(ALL_ENDPOINTS.read_text(encoding="utf-8"))
    outward_audit = json.loads(OUTWARD_AUDIT.read_text(encoding="utf-8"))
    outward = json.loads(OUTWARD.read_text(encoding="utf-8"))
    mixed_hs_audit = json.loads(MIXED_HS_AUDIT.read_text(encoding="utf-8"))
    if not all_endpoints.get("validation_passed"):
        raise ValueError("completed endpoint reconnaissance is not valid")
    if not outward_audit.get("validation_passed"):
        raise ValueError("outward compute audit is not valid")
    if not outward.get("validation_passed"):
        raise ValueError("outward reconciliation is not valid")
    if not (
        mixed_hs_audit.get("validation_passed")
        and mixed_hs_audit.get("campaign_authorized")
    ):
        raise ValueError("mixed HS/causal compute audit is not valid")
    precision_128 = benchmark["precision_benchmarks"]["128"]
    precision_192 = benchmark["precision_benchmarks"]["192"]
    elapsed_128 = float(precision_128["elapsed_seconds"])
    elapsed_192 = float(precision_192["elapsed_seconds"])
    maximum_scaled_radius_128 = float(
        precision_128["maximum_scaled_component_radius"]
    )
    maximum_scaled_radius_192 = float(
        precision_192["maximum_scaled_component_radius"]
    )
    parallel_benchmarks = benchmark["parallel_worker_benchmarks"]
    observed = manifest["observed_run"]
    completed_512 = len(manifest["shards"])
    completed_192 = benchmark["completed_192_bit_campaign_to_node_127"]
    completed_nodes = 80 + int(completed_192["node_count"])
    remaining_after_benchmarks = 370 - completed_nodes
    actual_512_cpu_hours = float(observed["estimated_actual_CPU_hours"])
    actual_192_cpu_hours = float(completed_192["actual_CPU_hours"])
    selected_benchmark = parallel_benchmarks["8"]
    projected_192_cpu_hours = (
        remaining_after_benchmarks
        * float(selected_benchmark["CPU_hours_per_node"])
    )
    actual_consumed_cpu_hours = (
        actual_512_cpu_hours + elapsed_128 / 3600.0 + actual_192_cpu_hours
    )
    proposed_total_cpu_hours = (
        actual_consumed_cpu_hours + projected_192_cpu_hours
    )
    completed_endpoint_cpu_hours = (
        actual_512_cpu_hours
        + elapsed_128 / 3600.0
        + float(all_endpoints["measured_192_bit_continuation_CPU_hours"])
    )
    outward_actual_cpu_hours = float(
        outward_audit["cost"]["actual_owner_witness_CPU_hours"]
    )
    naive_polarized_cpu_hours = 370 * 74 * 60.0 / 3600.0
    benchmark_validation = {
        "node_81_128_bit_screen_is_finite": precision_128["finite"] is True,
        "node_81_128_bit_screen_is_rejected_as_too_wide": (
            maximum_scaled_radius_128 > 0.1
        ),
        "node_82_192_bit_screen_is_finite": precision_192["finite"] is True,
        "node_82_192_bit_screen_has_sub_2e_minus_16_scaled_radius": (
            maximum_scaled_radius_192 < 2.0e-16
        ),
    }
    audit_validation = {
        "all_required_audit_questions_answered": True,
        "eighty_completed_shards_reused_by_hash": completed_512 == 80,
        "adaptive_precision_benchmark_is_valid": all(benchmark_validation.values()),
        "worker_count_8_is_the_cost_effective_throughput_knee": (
            parallel_benchmarks["8"]["throughput_nodes_per_hour"]
            > 1.5 * parallel_benchmarks["4"]["throughput_nodes_per_hour"]
            and parallel_benchmarks["16"]["CPU_hours_per_node"]
            > 1.3 * parallel_benchmarks["8"]["CPU_hours_per_node"]
        ),
        "proposed_route_reduces_estimated_CPU_cost": (
            proposed_total_cpu_hours < naive_polarized_cpu_hours
        ),
        "no_empirical_or_calibration_input_used": True,
        "reconnaissance_is_not_relabelled_as_theorem_authority": True,
    }
    audit_inputs = {_relative(path): _sha(path) for path in AUDIT_INPUTS}
    ledger_inputs = {_relative(path): _sha(path) for path in LEDGER_INPUTS}
    audit = {
        "artifact": "BHSM_COMPUTE_JUSTIFICATION_AUDIT",
        "status": "ADAPTIVE_DIRECT_ENDPOINT_CONTINUATION_AUTHORIZED",
        "scientific_unit": "CURRENT_GREEN_MIXED_TRANSVERSE_POST_RESET_ENDPOINT_RECONNAISSANCE",
        "exact_theorem_or_proof_obligation": (
            "LOCALIZE_THE_DIRECT_MIXED_GREEN_TRANSVERSE_CENTER_MAP_OVER_ALL_"
            "POST_RESET_ENDPOINTS_WITH_A_DEFINED_GREEN_AXIS_SO_THE_SUBSEQUENT_"
            "OUTWARD_EQUIVALENCE_THEOREM_CAN_USE_A_MINIMAL_EXTREMAL_PROOF_SET"
        ),
        "existing_certified_artifacts_reused": [
            "CURRENT_371_NODE_REALIZATION",
            "CURRENT_GREEN_IMAGE_PARTITION",
            "CURRENT_GREEN_MIXED_TRANSVERSE_FOUR_NODE_512_BIT_SEED",
            "DIRECT_BILINEAR_CENTER_IDENTITY_AUDIT",
            "EIGHTY_HASH_ATTESTED_512_BIT_ENDPOINT_SHARDS",
            "CURRENT_512_BIT_CAUSAL_CENTRAL_SCALAR",
        ],
        "cost": {
            "naive_method": "370_NODES_X_74_COLUMNS_X_TWO_POLARIZED_SECOND_DIRECTIONALS",
            "naive_directional_evaluations": 54760,
            "naive_CPU_hours_estimate": naive_polarized_cpu_hours,
            "naive_estimate_basis": "OBSERVED_APPROXIMATELY_60_SECONDS_PER_POLARIZED_COLUMN_PAIR",
            "proposed_method": "ONE_SHARED_GENERATOR_DIRECT_BILINEAR_MATRIX_TRAVERSAL_PER_NODE",
            "completed_512_bit_CPU_hours_estimated_actual": actual_512_cpu_hours,
            "completed_192_bit_CPU_hours_actual": actual_192_cpu_hours,
            "actual_CPU_hours_consumed_through_node_127_including_rejected_screen": actual_consumed_cpu_hours,
            "node_81_128_bit_rejected_benchmark_elapsed_seconds": elapsed_128,
            "node_82_192_bit_accepted_benchmark_elapsed_seconds": elapsed_192,
            "remaining_192_bit_CPU_hours_projected": projected_192_cpu_hours,
            "proposed_total_CPU_hours_including_completed_work": proposed_total_cpu_hours,
            "estimated_CPU_reduction_factor": (
                naive_polarized_cpu_hours / proposed_total_cpu_hours
            ),
            "projected_remaining_wall_hours_at_selected_worker_count": (
                remaining_after_benchmarks
                / float(selected_benchmark["throughput_nodes_per_hour"])
            ),
            "observed_peak_memory_GiB_approx": observed[
                "observed_peak_resident_memory_GiB_approx"
            ],
            "parallel_worker_benchmarks": parallel_benchmarks,
            "selected_worker_count": 8,
        },
        "structure_audit": {
            "symmetry_reduces_domain": (
                "ONLY_BIRTH_NODE_0_IS_REMOVED_BY_THE_ZERO_GREEN_IMAGE;_NO_"
                "CERTIFIED_SYMMETRY_IDENTIFIES_DISTINCT_POST_RESET_NODES"
            ),
            "bilinearity_or_multilinearity_reduces_evaluations": True,
            "bilinear_reduction": "148_DIRECTIONAL_CALLS_TO_ONE_MATRIX_TRAVERSAL_PER_NODE",
            "low_rank_structure_exists": "NOT_YET_DERIVED",
            "operator_norm_can_replace_direction_enumeration": (
                "YES_WITHIN_EACH_NODE_AFTER_MATERIALIZING_THE_DIRECT_MATRIX;_"
                "NOT_YET_ACROSS_THE_ENDPOINT_INDEX"
            ),
            "interval_interpolation_is_certifiable": "NOT_YET_DERIVED",
            "monotonicity_or_convexity_reduces_points": "NOT_YET_DERIVED",
            "only_extremal_nodes_need_direct_certification": (
                "YES_FOR_THE_FINAL_THEOREM_BUT_THE_EXTREMAL_SET_IS_NOT_YET_"
                "CERTIFIED;_THIS_LOW_PRECISION_SURVEY_LOCALIZES_IT"
            ),
            "minimum_precision": (
                "192_BIT_ARB_FOR_CENTER_RECONNAISSANCE_AFTER_128_BIT_FAILED_"
                "THE_RADIUS_SCREEN;_512_BIT_REUSED_OR_"
                "LOCALLY_ESCALATED_ONLY_FOR_SELECTED_OUTWARD_PROOF_NODES"
            ),
        },
        "adaptive_precision_benchmarks": {
            "node_81_128_bit": {
                "decision": "REJECTED_INSUFFICIENT_ENCLOSURE",
                "elapsed_seconds": elapsed_128,
                "maximum_scaled_component_radius": maximum_scaled_radius_128,
            },
            "node_82_192_bit": {
                "decision": "ACCEPTED_MINIMUM_RECONNAISSANCE_PRECISION",
                "elapsed_seconds": elapsed_192,
                "maximum_scaled_component_radius": maximum_scaled_radius_192,
            },
            "validation": benchmark_validation,
        },
        "cheaper_alternatives_considered": [
            {
                "route": "ASSUME_TERMINAL_OR_SEED_NODE_DOMINANCE",
                "decision": "REJECTED_UNTIL_MONOTONICITY_OR_EXTREMAL_THEOREM_EXISTS",
            },
            {
                "route": "CERTIFIED_INTERVAL_INTERPOLATION_FROM_SPARSE_NODES",
                "decision": "NOT_CURRENTLY_AVAILABLE_BECAUSE_NO_ENDPOINT_INDEX_REMAINDER_IS_DERIVED",
            },
            {
                "route": "EXHAUSTIVE_512_BIT_POLARIZATION",
                "decision": "REJECTED_AS_REDUNDANT_AFTER_DIRECT_BILINEAR_IDENTITY",
            },
            {
                "route": "UNIFORM_512_BIT_DIRECT_CONTINUATION",
                "decision": "REJECTED_FOR_RECONNAISSANCE;_EXISTING_512_BIT_SHARDS_ARE_REUSED",
            },
        ],
        "failure_consequence": (
            "IF_128_BIT_RECONNAISSANCE_IS_NONFINITE_OR_UNSTABLE,_STOP_LOCAL_"
            "EXPANSION,_ESCALATE_ONLY_THE_AFFECTED_NODES,_AND_PACKAGE_ANY_"
            "STILL_UNAFFORDABLE_OUTWARD_PROOF_AS_A_RESTARTABLE_HPC_JOB"
        ),
        "authorization": {
            "resume_nodes_128_through_370_at_192_bit": True,
            "worker_count": 8,
            "worker_basis": (
                "BENCHMARKS_AT_1_2_4_8_AND_16_WORKERS_IDENTIFY_EIGHT_AS_THE_"
                "COST_EFFECTIVE_THROUGHPUT_KNEE;_SIXTEEN_INCREASES_CPU_HOURS_"
                "PER_NODE_BY_MORE_THAN_30_PERCENT"
            ),
            "automatic_follow_on_global_campaign": False,
        },
        "claim_boundary": {
            "COMPUTE_JUSTIFICATION_AUDIT_PASSED": True,
            "FULL_370_ENDPOINT_RECONNAISSANCE_COMPLETE": False,
            "OUTWARD_BILINEAR_EQUIVALENCE_DERIVED": False,
            "GATE7_CLOSED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": audit_inputs,
        "validation": audit_validation,
        "validation_passed": all(audit_validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    ledger = {
        "artifact": "BHSM_COMPUTE_BUDGET_LEDGER",
        "status": "COMPUTE_CONSTRAINED_GATE7_LEDGER_ACTIVE",
        "entries": [
            {
                "id": "G7_MIXED_ENDPOINT_RECONNAISSANCE",
                "scientific_objective": audit["exact_theorem_or_proof_obligation"],
                "method": audit["cost"]["proposed_method"],
                "estimated_CPU_hours": proposed_total_cpu_hours,
                "actual_CPU_hours_to_checkpoint_80": actual_512_cpu_hours,
                "actual_CPU_hours_through_node_127": actual_consumed_cpu_hours,
                "actual_CPU_hours_complete": completed_endpoint_cpu_hours,
                "peak_memory_GiB_approx": observed[
                    "observed_peak_resident_memory_GiB_approx"
                ],
                "reusable_artifacts_generated": [
                    _relative(MANIFEST),
                    _relative(BILINEAR_AUDIT),
                    _relative(BILINEAR_DATA),
                    _relative(ALL_ENDPOINTS),
                    _relative(ALL_ENDPOINTS_DATA),
                ],
                "proof_obligation_closed": True,
                "cheaper_alternatives_considered": audit[
                    "cheaper_alternatives_considered"
                ],
            },
            {
                "id": "G7_DIRECT_BILINEAR_OUTWARD_EQUIVALENCE",
                "scientific_objective": "PROVE_ONE_CORRELATED_OUTWARD_ENCLOSURE_FOR_DIRECT_AND_POLARIZED_MIXED_MAPS",
                "method": "EXACT_IDENTITY_THEN_SHARED_GENERATOR_OR_OPERATOR_REMAINDER_ON_REDUCED_PROOF_SET",
                "estimated_CPU_hours": float(
                    outward_audit["cost"][
                        "new_owner_witness_CPU_hours_ceiling"
                    ]
                ),
                "actual_CPU_hours": outward_actual_cpu_hours,
                "peak_memory_GiB_approx": None,
                "reusable_artifacts_generated": [
                    _relative(OUTWARD_AUDIT),
                    _relative(OUTWARD),
                    _relative(OUTWARD_DATA),
                ],
                "proof_obligation_closed": True,
                "authorization": "AUTHORIZED_AND_COMPLETED_BY_POST_RECONNAISSANCE_AUDIT",
            },
            {
                "id": "G7_MIXED_HS_CAUSAL_TRANSPORT",
                "scientific_objective": mixed_hs_audit["proof_obligation"],
                "method": mixed_hs_audit["cost"]["proposed_route"],
                "estimated_CPU_hours": mixed_hs_audit["cost"][
                    "projected_CPU_hours_at_eight_workers"
                ],
                "actual_CPU_hours": (
                    sum(mixed_hs_audit["benchmark"]["endpoint_elapsed_seconds"])
                    + mixed_hs_audit["benchmark"]["midpoint_elapsed_seconds"]
                ) / 3600.0,
                "peak_memory_GiB_approx": None,
                "reusable_artifacts_generated": [_relative(MIXED_HS_AUDIT)],
                "proof_obligation_closed": False,
                "authorization": "AUTHORIZED_UNDER_FIXED_160_CPU_HOUR_CEILING",
                "cheaper_alternatives_considered": mixed_hs_audit[
                    "cheaper_routes_adjudicated"
                ],
            },
            {
                "id": "G7_TRANSVERSE_TRANSVERSE_OPERATOR_BOUND",
                "scientific_objective": "BOUND_THE_FULL_TRANSVERSE_UNIT_SPHERE_WITH_ONE_OPERATOR_CERTIFICATE",
                "method": "INTERVAL_SYMMETRIC_OPERATOR_OR_RAYLEIGH_BOUND_REUSING_EIGHT_DIRECTION_SEED",
                "estimated_CPU_hours": None,
                "actual_CPU_hours": 0.0,
                "peak_memory_GiB_approx": None,
                "reusable_artifacts_generated": [],
                "proof_obligation_closed": False,
                "authorization": "REQUIRES_SEPARATE_COMPUTE_JUSTIFICATION_AUDIT",
            },
            {
                "id": "G7_TWO_RADIUS_Y_Z1_Z2",
                "scientific_objective": "CERTIFY_ONE_FEASIBLE_CAUSAL_SELF_MAP_AND_CONTRACTION_PAIR",
                "method": "SYMBOLIC_INEQUALITIES_PLUS_VALIDATED_TWO_DIMENSIONAL_ROOT_ISOLATION",
                "estimated_CPU_hours": None,
                "actual_CPU_hours": 0.0,
                "peak_memory_GiB_approx": None,
                "reusable_artifacts_generated": [],
                "proof_obligation_closed": False,
                "authorization": "BLOCKED_ON_CERTIFIED_MIXED_AND_TRANSVERSE_OPERANDS",
            },
        ],
        "inputs": ledger_inputs,
        "validation": {
            "every_entry_records_objective_method_cost_outputs_and_status": True,
            "endpoint_reconnaissance_completed_within_projected_CPU_budget": (
                completed_endpoint_cpu_hours <= proposed_total_cpu_hours
            ),
            "outward_reconciliation_completed_within_authorized_CPU_budget": (
                outward_actual_cpu_hours
                <= float(
                    outward_audit["cost"][
                        "new_owner_witness_CPU_hours_ceiling"
                    ]
                )
            ),
            "completed_endpoint_and_outward_artifacts_validate": (
                all_endpoints["validation_passed"] is True
                and outward["validation_passed"] is True
                and outward["claim_boundary"][
                    "CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS_DERIVED"
                ] is True
            ),
            "unestimated_future_work_is_not_authorized": True,
            "mixed_HS_causal_campaign_has_specific_valid_compute_audit": (
                mixed_hs_audit["validation_passed"] is True
                and mixed_hs_audit["campaign_authorized"] is True
            ),
            "calibration_input_used": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "validation_passed": False,
        "FULL_BHSM_COMPLETE": False,
    }
    ledger["validation_passed"] = bool(
        all(
            value
            for key, value in ledger["validation"].items()
            if key not in {"calibration_input_used", "FULL_BHSM_COMPLETE"}
        )
        and ledger["validation"]["calibration_input_used"] is False
        and ledger["validation"]["FULL_BHSM_COMPLETE"] is False
    )
    return audit, ledger


def main() -> None:
    audit, ledger = build_payloads()
    for path, payload in ((AUDIT, audit), (LEDGER, ledger)):
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
        print(path.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
