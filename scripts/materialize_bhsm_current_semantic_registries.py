"""Materialize the nine authoritative AE2/Gate-7 normalization registries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.current_semantic_normalization import build_registries  # noqa: E402


TARGET = ROOT / "artifacts/current_semantics"
SOURCES = (
    "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_FIXED_CHANNEL_TRANSFER.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_GAUGE_WEYL_READOUT_FAMILY.json",
    "artifacts/flagship_integration/BHSM_N12_FORWARD_E1_SOURCE_MEASURE_CRITERION.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_LINEAR_RADIUS_TAIL_THEOREM.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_POWER_RADIUS_TAIL_CLOSURE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json",
    "artifacts/BHSM_alpha_i_update_v4_2.json",
    "theory/bhsm_prediction_ledger.json",
    "artifacts/frozen_constants_v2.json",
    "artifacts/BHSM_rho_ch_action_audit_v1_9.json",
    "artifacts/intrinsic_state_selection/BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json",
    "theory/norman_owner_ontology_recovered.md",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def verify_current_lineage() -> None:
    """Verify the rebuilt DAG statuses against the newest stored theorems."""

    loaded = {
        item: json.loads((ROOT / item).read_text(encoding="utf-8"))
        for item in SOURCES
        if item.endswith(".json")
    }
    theorem_sources = [item for item in SOURCES if item.startswith("artifacts/flagship_integration/")]
    if not all(loaded[item].get("validation_passed") is True for item in theorem_sources):
        raise RuntimeError("every current Gate7 theorem input must be validated")
    ae2 = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"]
    nonfermion = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"]
    factorized = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_THRESHOLD_RECLASSIFICATION.json"]
    reduction = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json"]
    radius_route = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_INTEGRABLE_RADIUS_THRESHOLD_ROUTE.json"]
    linear_tail = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_LINEAR_RADIUS_TAIL_THEOREM.json"]
    power_tail = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_POWER_RADIUS_TAIL_CLOSURE.json"]
    compact_dini = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"]
    angular_dini = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"]
    frontier = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_AE2_THRESHOLD_SUPERSESSION.json"]
    if ae2.get("action_version") != "BHSM-AE-2.0.0":
        raise RuntimeError("AE2 action version mismatch")
    if nonfermion["claim_boundary"]["nonfermion_critical_zero_graph_excluded"] is not True:
        raise RuntimeError("disk does not close the nonfermion threshold obstruction")
    if factorized["claim_boundary"]["factorized_N12_low_energy_source_measure"] != "OPEN":
        raise RuntimeError("disk no longer identifies factorized source measure as open")
    if factorized["claim_boundary"]["strict_product_Dirac_Wronskian_required_in_advance"] is not False:
        raise RuntimeError("disk still requires the superseded strict Wronskian premise")
    if frontier["preserved_open_objects"]["realized_factorized_source_weighted_limiting_absorption"] != "OPEN":
        raise RuntimeError("disk frontier does not identify the current live owner")
    if reduction["claim_boundary"]["abstract_factorized_transfer_to_source_measure_theorem"] != "CLOSED":
        raise RuntimeError("factorized source-measure reduction is not closed")
    if reduction["claim_boundary"]["actual_N12_infinite_end_threshold_normalization"] != "OPEN":
        raise RuntimeError("realized infinite-end normalization is not the current live owner")
    if radius_route["claim_boundary"]["conditional_integrable_radius_threshold_theorem"] != "CLOSED":
        raise RuntimeError("integrable reciprocal-radius threshold route is not closed")
    if not (
        radius_route["claim_boundary"]["actual_N12_reciprocal_radius_integrability"] == "OPEN"
        and radius_route["claim_boundary"]["direct_nonintegrable_tail_theorem"] == "OPEN"
    ):
        raise RuntimeError("realized infinite-tail dichotomy is not the current live owner")
    if linear_tail["claim_boundary"]["exact_linear_radius_tail_theorem"] != "CLOSED":
        raise RuntimeError("exact linear-radius tail theorem is not closed")
    if not (
        linear_tail["claim_boundary"]["actual_N12_radius_asymptotic_class"] == "OPEN"
        and linear_tail["claim_boundary"]["general_sublinear_or_nonasymptotic_tail"] == "OPEN"
    ):
        raise RuntimeError("remaining radius-tail class is not the current live owner")
    if power_tail["claim_boundary"]["all_exact_nonnegative_power_radius_tails"] != "CLOSED":
        raise RuntimeError("exact power-radius tail family is not closed")
    if not (
        power_tail["claim_boundary"]["actual_N12_radius_asymptotic_class"] == "OPEN"
        and power_tail["claim_boundary"]["general_nonasymptotic_tail"] == "OPEN"
    ):
        raise RuntimeError("power-tail predecessor does not preserve its pre-closure frontier")
    if compact_dini["factorization_only_test"]["answer"] != "YES_WITHIN_THE_RETAINED_ADMISSIBLE_CLASS":
        raise RuntimeError("compact-source factorization theorem is not closed")
    if compact_dini["claim_boundary"]["angular_sum"] != "OPEN_CURRENT_OWNER":
        raise RuntimeError("angular channel sum is not the current live owner")
    if angular_dini["adjudication"]["fixed_channel_source_Dini"] != "CLOSED_DO_NOT_REOPEN":
        raise RuntimeError("angular audit reopened the fixed-channel theorem")
    if angular_dini["adjudication"]["arbitrary_positive_tail_angular_sum"] != "FALSE":
        raise RuntimeError("angular audit did not retain its exact counterexample")
    if angular_dini["conditional_at_most_linear_sufficient_class"]["status"] != "CLOSED_CONDITIONAL_THEOREM":
        raise RuntimeError("at-most-linear angular barrier theorem is not closed conditionally")
    if not (
        angular_dini["adjudication"]["eventual_two_sided_Lipschitz_radius_sufficient"] is True
        and angular_dini["adjudication"]["eventual_logarithmic_speed_Osgood_radius_sufficient"] is True
        and angular_dini["adjudication"]["radius_monotonicity_required"] is False
        and angular_dini["adjudication"]["eventual_two_sided_Lipschitz_radius_proved_by_action"] is False
        and angular_dini["adjudication"]["eventual_logarithmic_speed_Osgood_radius_proved_by_action"] is False
    ):
        raise RuntimeError("current angular owner is not the action-to-radius bound")


def materialize() -> list[Path]:
    source_paths = [ROOT / item for item in SOURCES]
    missing = [path for path in source_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"normalization inputs missing: {missing}")
    verify_current_lineage()
    hashes = {item: sha256(ROOT / item) for item in SOURCES}
    registries = build_registries(hashes)
    TARGET.mkdir(parents=True, exist_ok=True)
    output = []
    for name, payload in sorted(registries.items()):
        path = TARGET / name
        path.write_bytes(deterministic_bytes(payload))
        output.append(path)
    return output


if __name__ == "__main__":
    for result in materialize():
        print(result)
