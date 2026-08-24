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
    "artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    "artifacts/flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json",
    "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json",
    "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json",
    "artifacts/flagship_integration/BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json",
    "artifacts/flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json",
    "artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json",
    "artifacts/intrinsic_state_selection/BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json",
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
    finite_domain = loaded["artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"]
    finite_force = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json"]
    force_domain = loaded["artifacts/flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json"]
    event_weyl = loaded["artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json"]
    seam_correction = loaded["artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"]
    seam_enclosure = loaded["artifacts/flagship_integration/BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json"]
    seam_family = loaded["artifacts/flagship_integration/BHSM_N12_AE2_NEGATIVE_AXIS_SEAM_FAMILY.json"]
    projected_saddle = loaded["artifacts/flagship_integration/BHSM_N12_CONSTRAINT_PROJECTED_REPLACEMENT_SADDLE.json"]
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
    if angular_dini["retained_action_uniform_scale_ownership_audit"]["status"] != "EXACT_SCALE_WEIGHTS_DERIVED_NO_OSGOOD_DECAY_THEOREM":
        raise RuntimeError("uniform-scale Osgood ownership audit is not current")
    if finite_domain["claim_boundary"]["finite_encapsulation_existence"] != "CLOSED_LOCAL_ACTION_THEOREM":
        raise RuntimeError("finite-encapsulation existence is not closed locally")
    if finite_domain["claim_boundary"]["zero_source_force"] != "NEXT_CURRENT_OWNER":
        raise RuntimeError("zero-source force is not the current Gate7 owner")
    if not (
        finite_force["claim_boundary"]["zero_source_force_functional"] == "DERIVED"
        and finite_force["claim_boundary"]["zero_source_force_value"] == "OPEN"
    ):
        raise RuntimeError("finite-endpoint force frontier is not current")
    if force_domain["domain_adjudication"]["arbitrary_regular_free_cutoff_allowed"] is not False:
        raise RuntimeError("an arbitrary force-domain cutoff was restored")
    if not (
        event_weyl["claim_boundary"]["event_normal_Weyl_initial_condition"] == "DERIVED"
        and seam_correction["supersession"]["superseded_claim"]
        == "M(0,z)=W_phys_AS_THE_PHYSICAL_AE2_EVENT_INITIAL_VALUE"
        and seam_correction["claim_boundary"]["physical_AE2_event_initial_value"]
        == "OPEN"
        and seam_correction["claim_boundary"][
            "child_arm_Calderon_value_and_geometry_jets"
        ]
        == "OPEN"
        and seam_enclosure["claim_boundary"]["two_sided_child_load_at_z_minus_1"]
        == "ENCLOSED_BROADLY"
        and seam_enclosure["claim_boundary"]["complete_heat_spectral_family"]
        == "OPEN"
        and seam_family["claim_boundary"][
            "complete_spectral_parameter_coverage"
        ]
        == "CLOSED_ON_NEGATIVE_REAL_AXIS"
        and seam_family["claim_boundary"]["actual_spectral_trace_value"]
        == "OPEN"
    ):
        raise RuntimeError("two-sided AE2 force value frontier is not current")
    if not (
        projected_saddle["claim_boundary"][
            "constraint_tangent_force_criterion"
        ] == "DERIVED"
        and projected_saddle["claim_boundary"][
            "ambient_force_zero_required"
        ] is False
        and projected_saddle["claim_boundary"][
            "actual_projected_force_value"
        ] == "OPEN"
        and projected_saddle["claim_boundary"][
            "same_action_saddle"
        ] == "OPEN_COUPLED_TO_FORCE"
    ):
        raise RuntimeError("constraint-projected replacement saddle frontier is not current")


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
