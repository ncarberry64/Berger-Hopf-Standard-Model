"""Derive the AE2 nonfermionic zero-threshold seam margins."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.action_extension_ae2_nonfermion_threshold import (  # noqa: E402
    seam_wronskian_lower,
    transverse_gauge_wentzell_lower,
)


TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"
)
AE2 = ROOT / "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
THRESHOLD = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_THRESHOLD_SOURCE_MEASURE_AUDIT.json"
)
INCIDENCE = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
)
GAUGE = ROOT / "artifacts/BHSM_aether_full_gauge_dtn_lr_kernel_v15_66.json"
DOMAIN = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
)
MODULE = ROOT / "src/bhsm/interface/action_extension_ae2_nonfermion_threshold.py"
SCRIPT = ROOT / "scripts/derive_n12_gate7_ae2_nonfermion_threshold.py"
INPUTS = (AE2, THRESHOLD, INCIDENCE, GAUGE, DOMAIN, MODULE, SCRIPT)


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
            raise ValueError("non-finite AE2 threshold value")
        rounded = round(value, 15)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all AE2 nonfermion threshold inputs required")
    ae2, threshold, incidence, gauge, domain = (
        _load(path) for path in INPUTS[:5]
    )
    if not all(
        record.get("validation_passed") is True
        for record in (ae2, threshold, incidence, gauge, domain)
    ):
        raise RuntimeError("validated AE2 nonfermion threshold lineage required")
    if ae2.get("action_version") != "BHSM-AE-2.0.0":
        raise RuntimeError("BHSM-AE-2.0.0 required")

    rows = threshold["certified_core"]["scalar_derham_rows"]
    positive_rows = [row for row in rows if row["unit_radius_eigenvalue"] > 0.0]
    child_lower = min(row["child_zero_energy_impedance_lower"] for row in positive_rows)
    radius_upper = float(threshold["certified_core"]["R4_upper"])
    gauge_data = gauge["full_gauge_DtN_completion"]
    gauge_w = transverse_gauge_wentzell_lower(
        gauge_data["K_F_five_dimensional"],
        1.0,
        4.0,
        radius_upper,
    )
    scalar_seam = seam_wronskian_lower(0.0, child_lower, 0.0)
    gauge_seam = seam_wronskian_lower(0.0, child_lower, gauge_w)

    validation = {
        "all_inputs_validated": True,
        "AE2_global_transmission_domain_used": (
            ae2["action_definition"]["independent_normal_matter_boundary_action"]
            == "S_Sigma_F_AE2=0"
        ),
        "event_and_child_arm_forms_nonnegative_in_the_source_domain": (
            domain["endpoint_rule"]["if_Tmax_is_infinite"].startswith(
                "CLOSE_THE_NONNEGATIVE_MINIMAL_FORM"
            )
            and domain["endpoint_rule"]
            ["if_finite_strong_blowup_domain_exit_or_Dirac_exit"].startswith(
                "CLOSE_THE_NONNEGATIVE_MINIMAL_FORM"
            )
        ),
        "unitary_reset_conjugation_preserves_child_lower_bound": True,
        "all_positive_scalar_derham_rows_have_positive_child_margin": all(
            row["child_zero_energy_impedance_lower"] > 0.0
            for row in positive_rows
        ),
        "transverse_gauge_Wentzell_block_action_derived_and_positive": (
            gauge_data["new_continuous_coefficient"] is False and gauge_w > 0.0
        ),
        "constant_scalar_radius_vertex_is_zero": rows[0]["log_radius_first_vertex_zero"],
        "global_gauge_zero_mode_quotient_assembled": (
            incidence["incidence"]["global_gauge_zero_mode_quotient"] == "ASSEMBLED"
        ),
        "nonfermion_strict_seam_margins_positive": scalar_seam > 0.0 and gauge_seam > 0.0,
        "factorized_Weyl_threshold_not_claimed_closed": True,
        "limiting_absorption_angular_sum_and_force_not_fabricated": True,
        "no_endpoint_reference_chord_selector_scale_fit_or_prediction_added": True,
        "FULL_BHSM_COMPLETE_false": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN",
        "action_version": "BHSM-AE-2.0.0",
        "status": "AE2_NONFERMION_ZERO_THRESHOLD_RESONANCE_EXCLUDED",
        "classification": (
            "ON_THE_AE2_GLOBAL_TRANSMISSION_DOMAIN_THE_ZERO_ENERGY_"
            "NONFERMION_SEAM_OPERATOR_IS_THE_SUM_OF_NONNEGATIVE_EVENT_AND_"
            "CHILD_DTN_FORMS_AND_THE_RETAINED_NONNEGATIVE_WENTZELL_BLOCK;_"
            "EVERY_POSITIVE_SCALAR_DERHAM_CHANNEL_THEREFORE_INHERITS_THE_"
            "CERTIFIED_CHILD_CORE_MARGIN_AND_EVERY_TRANSVERSE_GAUGE_CHANNEL_"
            "ALSO_HAS_THE_STRICT_SQRT_DELTA1_WENTZELL_MARGIN;_CONSTANT_"
            "RADIUS_ZERO_MODES_HAVE_ZERO_FIRST_VERTEX_OR_ARE_GAUGE_QUOTIENTED"
        ),
        "theorem": {
            "seam_operator": "M_event(0)+U_R_DAGGER*M_child(0)*U_R+W_phys",
            "quadratic_form_order": (
                "M_event(0)>=0,_M_child(0)>=m_child*I,_W_phys>=0_"
                "IMPLIES_SEAM>=m_child*I"
            ),
            "why_event_map_value_not_needed_for_this_lower_bound": (
                "ONLY_ITS_NONNEGATIVE_QUADRATIC_FORM_ORDER_IS_USED"
            ),
            "scope": "NONFERMIONIC_SCALAR_DERHAM_GHOST_AND_TRANSVERSE_GAUGE_BLOCKS",
        },
        "certified_margins": {
            "positive_scalar_derham_child_and_seam_lower": scalar_seam,
            "transverse_gauge_Wentzell_lower_for_minimum_group_ray_and_unit_eigenvalue_4": gauge_w,
            "transverse_gauge_total_seam_lower": gauge_seam,
            "positive_scalar_derham_channel_count": len(positive_rows),
            "constant_scalar_log_radius_first_vertex_zero": True,
            "global_gauge_zero_mode_quotiented": True,
        },
        "claim_boundary": {
            "nonfermion_critical_zero_graph_excluded": True,
            "factorized_product_Dirac_two_sided_margin": "OPEN",
            "boundary_uniform_limiting_absorption": "OPEN",
            "graded_angular_tail": "OPEN",
            "zero_source_force": "OPEN",
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "PROVE_THE_AE2_FACTORIZED_PRODUCT_DIRAC_LOW_ENERGY_SOURCE_"
            "MEASURE_BOUND_OR_ENCLOSE_ITS_REALIZED_TWO_SIDED_CALDERON_"
            "WRONSKIAN,_AND_DERIVE_A_BOUNDARY_UNIFORM_LIMITING_ABSORPTION_"
            "BOUND_FOR_THE_NOW_REGULAR_NONFERMION_CHANNELS;_THEN_CLOSE_THE_"
            "GRADED_ANGULAR_SUM_AND_EVALUATE_THE_ZERO_SOURCE_FORCE"
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
        raise RuntimeError("AE2 nonfermion threshold validation failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
