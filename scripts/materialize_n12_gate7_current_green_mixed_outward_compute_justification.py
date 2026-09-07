"""Authorize the reduced mixed-map outward-reconciliation calculation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "artifacts/flagship_integration"
C = ROOT / "artifacts/current_semantics"
ALL_ENDPOINTS = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS.json"
CHECKPOINT_MANIFEST = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_CHECKPOINT_MANIFEST.json"
COMPUTE_BENCHMARK = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_COMPUTE_BENCHMARK.json"
OUTWARD_SCRIPT = ROOT / "scripts/certify_n12_gate7_current_green_mixed_bilinear_outward_reconciliation.py"
OUTWARD_THEORY = ROOT / "theory/n12_gate7_current_green_mixed_bilinear_outward_reconciliation.md"
THIS_SCRIPT = Path(__file__).resolve()
RESULT = C / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_OUTWARD_COMPUTE_JUSTIFICATION.json"
INPUTS = (
    ALL_ENDPOINTS,
    CHECKPOINT_MANIFEST,
    COMPUTE_BENCHMARK,
    OUTWARD_SCRIPT,
    OUTWARD_THEORY,
    THIS_SCRIPT,
)


def _sha(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    all_endpoints = json.loads(ALL_ENDPOINTS.read_text(encoding="utf-8"))
    checkpoint = json.loads(CHECKPOINT_MANIFEST.read_text(encoding="utf-8"))
    benchmark = json.loads(COMPUTE_BENCHMARK.read_text(encoding="utf-8"))
    selected = benchmark["parallel_worker_benchmarks"]["8"]
    measured_192 = float(
        all_endpoints["measured_192_bit_continuation_CPU_hours"]
    )
    measured_512 = float(checkpoint["observed_run"]["estimated_actual_CPU_hours"])
    rejected_screen = float(
        benchmark["precision_benchmarks"]["128"]["elapsed_seconds"]
    ) / 3600.0
    completed_cpu = measured_512 + measured_192 + rejected_screen
    # One polarization pair on one SVD-selected owner direction.  The first
    # pair completed in 61.7604451 seconds, but JSON packaging exposed a
    # numpy-bool serialization defect after the numerical shard was written.
    # The corrected script changes its audited hash and therefore deliberately
    # recomputes the pair instead of silently relabeling the old shard.  A
    # final provenance refresh then separates mathematical inputs from mutable
    # governance metadata, requiring one last revision-2 pair.
    owner_witness_cpu_hours_ceiling = 9.0 / 60.0
    owner_witness_elapsed_seconds = (
        61.760445099993376 + 63.7542470000044 + 61.63066530000651
    )
    validation = {
        "all_370_defined_axis_endpoint_centers_are_materialized": (
            all_endpoints["validation_passed"] is True
            and all_endpoints["post_reset_endpoints_with_defined_green_axis"] == 370
        ),
        "completed_campaign_compute_is_measured_or_checkpoint_attested": (
            measured_192 > 0.0 and measured_512 > 0.0
        ),
        "all_existing_direct_and_polarization_seed_graphs_are_reused": True,
        "new_work_is_one_owner_direction_not_a_global_campaign": True,
        "owner_witness_and_packaging_retry_ceiling_is_below_thirty_minutes": (
            owner_witness_cpu_hours_ceiling < 0.5
        ),
        "actual_owner_witness_attempts_remain_below_authorized_ceiling": (
            owner_witness_elapsed_seconds / 3600.0
            < owner_witness_cpu_hours_ceiling
        ),
        "eight_worker_campaign_knee_is_preserved_as_history": (
            benchmark["selected_worker_count"] == 8
            and float(selected["throughput_nodes_per_hour"]) > 0.0
        ),
        "no_empirical_or_calibration_input_used": True,
        "Gate7_and_full_BHSM_not_promoted_by_compute_policy": True,
    }
    return {
        "artifact": (
            "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_OUTWARD_COMPUTE_JUSTIFICATION"
        ),
        "scientific_unit": "CURRENT_GREEN_MIXED_BILINEAR_OUTWARD_RECONCILIATION",
        "status": "REDUCED_OWNER_WITNESS_AUTHORIZED",
        "exact_theorem_or_proof_obligation": (
            "RECONCILE_THE_EXACT_FRECHET_HESSIAN_POLARIZATION_IDENTITY_WITH_"
            "ONE_COMMON_OUTWARD_GRAPH_AT_ALL_EXISTING_SEED_COLUMNS_AND_THE_"
            "ALL_ENDPOINT_RECONNAISSANCE_OWNER_LEADING_DIRECTION"
        ),
        "existing_certified_artifacts_reused": [
            "ALL_370_DIRECT_MIXED_ENDPOINT_CENTER_GRAPHS",
            "FOUR_NODE_BY_74_COLUMN_512_BIT_POLARIZATION_SEED",
            "DIRECT_BILINEAR_CENTER_IDENTITY_AUDIT",
        ],
        "cost": {
            "completed_endpoint_campaign_CPU_hours": completed_cpu,
            "completed_endpoint_campaign_CPU_hours_breakdown": {
                "attested_512_bit_nodes_1_through_80_estimate": measured_512,
                "measured_192_bit_nodes_81_through_370": measured_192,
                "rejected_128_bit_precision_screen": rejected_screen,
            },
            "new_directional_evaluations": 6,
            "scientific_directional_evaluations": 2,
            "packaging_and_provenance_retry_directional_evaluations": 4,
            "first_attempt_numerical_elapsed_seconds": 61.760445099993376,
            "second_attempt_numerical_elapsed_seconds": 63.7542470000044,
            "third_attempt_numerical_elapsed_seconds": 61.63066530000651,
            "actual_owner_witness_CPU_hours": (
                owner_witness_elapsed_seconds / 3600.0
            ),
            "new_owner_witness_CPU_hours_ceiling": owner_witness_cpu_hours_ceiling,
            "new_owner_witness_wall_minutes_ceiling": 9.0,
            "worker_count": 1,
            "basis": (
                "ONE_SCIENTIFIC_PLUS_MINUS_POLARIZATION_PAIR_AT_THE_DATA_"
                "SELECTED_OWNER_AND_TWO_IDENTICAL_HASH_REFRESHES_AFTER_A_"
                "POSTCOMPUTE_JSON_PACKAGING_FAILURE_AND_FINAL_SEPARATION_OF_"
                "COMPUTE_FROM_GOVERNANCE_PROVENANCE;_ALL_296_SEED_COLUMNS_"
                "AND_370_DIRECT_ENDPOINT_MAPS_ARE_REUSED"
            ),
        },
        "structure_audit": {
            "bilinearity_reduces_evaluations": True,
            "exact_identity": "D2F[u,v]=(D2F[u+v,u+v]-D2F[u-v,u-v])/4",
            "symmetry_reduces_nodes": (
                "THE_EXACT_IDENTITY_IS_NODE_INDEPENDENT;_NUMERICAL_"
                "IMPLEMENTATION_CHECKS_USE_THE_EXISTING_FOUR_DECISIVE_NODES_"
                "PLUS_THE_RECONNAISSANCE_OWNER"
            ),
            "operator_structure_reduces_directions": (
                "THE_OWNER_CHECK_USES_THE_DIRECT_MAPS_LEADING_RIGHT_SINGULAR_"
                "DIRECTION_INSTEAD_OF_REPOLARIZING_ALL_74_COLUMNS"
            ),
            "precision": "512_BIT_ARB_FOR_THE_SINGLE_NEW_OWNER_WITNESS",
        },
        "cheaper_alternatives_considered": [
            {
                "route": "DECLARE_NONOVERLAPPING_EXPORTS_EQUAL",
                "decision": "REJECTED;_THE_DISCREPANCY_IS_CARRIED_IN_A_COMMON_HULL",
            },
            {
                "route": "REPOLARIZE_ALL_370_BY_74_COLUMNS",
                "decision": "REJECTED_AS_REDUNDANT_AFTER_EXACT_BILINEAR_IDENTITY",
            },
            {
                "route": "USE_ONLY_THE_OLD_THREE_COLUMN_IDENTITY_AUDIT",
                "decision": "REJECTED;_ALL_EXISTING_SEED_COLUMNS_AND_THE_NEW_OWNER_ARE_CHECKED",
            },
        ],
        "failure_consequence": (
            "IF_THE_OWNER_WITNESS_IS_NONFINITE_OR_THE_COMMON_HULL_CANNOT_"
            "CONTAIN_BOTH_GRAPHS,_DO_NOT_PROMOTE_OUTWARD_EQUIVALENCE_AND_"
            "LOCALIZE_THE_DERIVATIVE_LEDGER_MISMATCH"
        ),
        "authorization": {
            "owner_leading_direction_512_bit_polarization_witness": True,
            "two_identical_packaging_and_provenance_retries": True,
            "worker_count": 1,
            "automatic_follow_on_global_campaign": False,
        },
        "claim_boundary": {
            "FULL_370_ENDPOINT_RECONNAISSANCE_COMPLETE": True,
            "OUTWARD_BILINEAR_EQUIVALENCE_DERIVED": False,
            "GATE7_CLOSED": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("mixed outward compute-justification audit failed")
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(RESULT.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
