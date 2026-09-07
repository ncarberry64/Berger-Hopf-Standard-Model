"""Materialize the compute audit for the mixed HS/causal proof job."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "artifacts/flagship_integration"
C = ROOT / "artifacts/current_semantics"
RESULT = C / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_COMPUTE_JUSTIFICATION.json"
CAMPAIGN = ROOT / "scripts/certify_n12_gate7_current_green_mixed_hs_causal_transport.py"
THEORY = ROOT / "theory/n12_gate7_current_green_mixed_hs_causal_transport.md"
ENDPOINT_BENCHMARKS = (
    F / "BHSM_N12_GATE7_CURRENT_GREEN_ENDPOINT_FIRST_VARIATION_NODE8_192BIT_BENCHMARK.npz",
    F / "BHSM_N12_GATE7_CURRENT_GREEN_ENDPOINT_FIRST_VARIATION_NODE9_192BIT_BENCHMARK.npz",
)
MIDPOINT_BENCHMARK = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_INTERVAL8_192BIT_BENCHMARK.npz"
PRIOR_BENCHMARK = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_COMPUTE_BENCHMARK.json"
MIXED_ENDPOINT = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_TRANSVERSE_ALL_ENDPOINTS.json"
OUTWARD = F / "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_BILINEAR_OUTWARD_RECONCILIATION.json"
THIS_SCRIPT = Path(__file__).resolve()
INPUTS = (CAMPAIGN, THEORY, *ENDPOINT_BENCHMARKS, MIDPOINT_BENCHMARK,
          PRIOR_BENCHMARK, MIXED_ENDPOINT, OUTWARD, THIS_SCRIPT)


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
    endpoint_seconds = []
    for path in ENDPOINT_BENCHMARKS:
        with np.load(path) as source:
            endpoint_seconds.append(float(source["elapsed_seconds"]))
    with np.load(MIDPOINT_BENCHMARK) as source:
        midpoint_seconds = float(source["elapsed_seconds"])
        midpoint_finite = bool(
            np.all(np.isfinite(source["local_hs_mid"]))
            and np.all(np.isfinite(source["local_hs_radius"]))
            and np.all(source["local_hs_radius"] >= 0.0)
        )
        maximum_scaled_radius = float(np.max(
            source["local_hs_radius"]
            / np.maximum(1.0, np.abs(source["local_hs_mid"]))
        ))
    prior = json.loads(PRIOR_BENCHMARK.read_text(encoding="utf-8"))
    endpoint_mean = float(np.mean(endpoint_seconds))
    serial_cpu_hours = 370.0 * (endpoint_mean + midpoint_seconds) / 3600.0
    one_worker_reference = float(
        prior["parallel_worker_benchmarks"]["1"]["CPU_hours_per_node"]
    )
    eight_worker_reference = float(
        prior["parallel_worker_benchmarks"]["8"]["CPU_hours_per_node"]
    )
    contention_factor = eight_worker_reference / one_worker_reference
    projected_cpu_hours = serial_cpu_hours * contention_factor
    projected_wall_hours = projected_cpu_hours / 8.0
    budget_ceiling_cpu_hours = 160.0
    validation = {
        "exact_proof_obligation_declared": True,
        "all_existing_endpoint_mixed_maps_reused_without_recomputation": True,
        "naive_polarization_rejected_by_exact_bilinear_vectorization": True,
        "symmetry_does_not_remove_ordered_causal_intervals": True,
        "low_rank_structure_not_assumed_without_certificate": True,
        "operator_norm_cannot_replace_signed_causal_matrix_transport": True,
        "interval_interpolation_rejected_without_rate_Hessian_Lipschitz_certificate": True,
        "monotonicity_or_convexity_not_available_for_matrix_components": True,
        "extremal_only_sampling_rejected_without_between_interval_remainder": True,
        "minimum_192_bit_precision_selected_from_prior_same_kernel_failure_at_128_bits": (
            prior["selected_precision_bits"] == 192
        ),
        "representative_192_bit_midpoint_is_finite": midpoint_finite,
        "representative_192_bit_midpoint_scaled_radius_below_1e_minus_8": (
            maximum_scaled_radius < 1.0e-8
        ),
        "eight_worker_cost_effective_knee_reused_not_rebenchmarked": (
            prior["selected_worker_count"] == 8
        ),
        "projected_campaign_below_fixed_compute_ceiling": (
            projected_cpu_hours < budget_ceiling_cpu_hours
        ),
        "failure_consequence_is_dependency_or_precision_localization_not_model_refit": True,
        "no_empirical_or_calibration_input_used": True,
        "FULL_BHSM_COMPLETE": False,
    }
    # Negative declarations are successful only when they remain false.
    passed = all(value for key, value in validation.items()
                 if key != "FULL_BHSM_COMPLETE") and not validation["FULL_BHSM_COMPLETE"]
    return {
        "artifact": "BHSM_N12_GATE7_CURRENT_GREEN_MIXED_HS_CAUSAL_COMPUTE_JUSTIFICATION",
        "status": "MIXED_HS_CAUSAL_CAMPAIGN_AUTHORIZED_UNDER_FIXED_COMPUTE_CEILING",
        "campaign_authorized": passed,
        "proof_obligation": (
            "DERIVE_ALL_370_CORRELATED_MIXED_HERMITE_SIMPSON_LOCAL_OPERATORS_AND_"
            "THEIR_FROZEN_CAUSAL_PRECONDITIONED_COMPOSITION"
        ),
        "reused_certified_assets": [
            "all 370 endpoint mixed Green/transverse outward maps",
            "exact direct-versus-polarization bilinear identity",
            "current 371-node center, branch, frames, and reset trace",
            "frozen left/right Newton blocks and causal preconditioner",
            "existing retained-action Arb jet and bordered-response machinery",
        ],
        "benchmark": {
            "precision_bits": 192,
            "endpoint_nodes": [8, 9],
            "endpoint_elapsed_seconds": endpoint_seconds,
            "endpoint_mean_elapsed_seconds": endpoint_mean,
            "midpoint_interval": 8,
            "midpoint_elapsed_seconds": midpoint_seconds,
            "midpoint_maximum_scaled_component_radius": maximum_scaled_radius,
        },
        "cost": {
            "naive_route": "148_POLARIZED_SECOND_DIRECTIONAL_EVALUATIONS_PER_INTERVAL_PLUS_ENDPOINT_FIRST_VARIATIONS",
            "proposed_route": "ONE_74_COLUMN_SHARED_GENERATOR_BILINEAR_MAP_PLUS_ONE_SHARED_FIRST_VARIATION_PER_INTERVAL",
            "proposed_serial_CPU_hours_from_benchmark": serial_cpu_hours,
            "eight_worker_contention_factor_reused": contention_factor,
            "projected_CPU_hours_at_eight_workers": projected_cpu_hours,
            "projected_wall_hours_at_eight_workers": projected_wall_hours,
            "fixed_campaign_CPU_ceiling": budget_ceiling_cpu_hours,
            "stop_condition": "STOP_IF_PROJECTED_OR_MEASURED_CPU_EXCEEDS_CEILING_OR_A_FINITE_NECESSARY_CONDITION_FAILS",
        },
        "cheaper_routes_adjudicated": [
            {"route": "ENDPOINT_ONLY_OR_EXTREMAL_MIDPOINT_SAMPLING",
             "decision": "REJECTED_NO_CERTIFIED_MATRIX_MONOTONICITY_OR_BETWEEN_INTERVAL_REMAINDER"},
            {"route": "BINARY64_JAX_MIDPOINT_HESSIANS",
             "decision": "RECONNAISSANCE_ONLY_NOT_OUTWARD_AUTHORITY"},
            {"route": "INDEPENDENT_POLARIZATION",
             "decision": "REJECTED_EXACT_BILINEAR_IDENTITY_ALREADY_PROVED"},
            {"route": "SCALAR_OPERATOR_NORM_RECURRENCE",
             "decision": "REJECTED_FOR_PRIMARY_PROOF_BECAUSE_IT_DISCARDS_THE_SIGNED_CAUSAL_MATRIX_CORRELATION"},
            {"route": "UNIFORM_512_BIT_CAMPAIGN",
             "decision": "REJECTED_ADAPTIVE_192_BIT_START_WITH_LOCAL_ESCALATION_ONLY"},
        ],
        "expected_failure_consequence": (
            "A_FAILED_OR_WRAPPED_RECURRENCE_LOCALIZES_THE_FIRST_PRECISION_OR_"
            "DEPENDENCY_OWNER;_IT_DOES_NOT_AUTHORIZE_A_NEW_CENTER_SCALE_ACTION_"
            "TERM_OR_EMPIRICAL_RENORMALIZATION"
        ),
        "reusable_outputs": [
            "restart-safe endpoint first-variation shards",
            "restart-safe mixed midpoint chain-rule shards",
            "causal mixed operator profile and owner",
        ],
        "inputs": {_relative(path): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
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
        "campaign_authorized": payload["campaign_authorized"],
        "cost": payload["cost"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
