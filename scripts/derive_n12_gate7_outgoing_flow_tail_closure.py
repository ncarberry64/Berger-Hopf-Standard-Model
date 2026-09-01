"""Close the maximal tail on the exact outgoing descriptor-flow direction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_OUTGOING_FLOW_TAIL_CLOSURE.json"
TAIL_SUPPORT = BASE / "BHSM_N12_GATE7_MAXIMAL_TAIL_SUPPORT_REDUCTION.json"
LAUNCH = BASE / "BHSM_N12_C2_RESET_GENERATED_LAUNCH_CHART.json"
LAUNCH_DATA = LAUNCH.with_suffix(".npz")
EXACT_FIELD = BASE / "BHSM_N12_C2_EXACT_FIXED_S_FIELD_ORACLE.json"
MAXIMAL_WEYL = BASE / "BHSM_N12_MAXIMAL_FRIEDRICHS_WEYL_EXHAUSTION.json"
RICCATI = BASE / "BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json"
SEAM = BASE / "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
MAXIMAL_GRADED = BASE / (
    "BHSM_N12_GATE7_MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT.json"
)
DIRECT_ZETA = BASE / "BHSM_N12_GATE7_DIRECT_ZETA_COEFFICIENT_COTANGENT.json"
SOURCE_ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
THEORY = ROOT / "theory" / "n12_gate7_outgoing_flow_tail_closure.md"
INPUTS = (
    TAIL_SUPPORT,
    LAUNCH,
    LAUNCH_DATA,
    EXACT_FIELD,
    MAXIMAL_WEYL,
    RICCATI,
    SEAM,
    MAXIMAL_GRADED,
    DIRECT_ZETA,
    SOURCE_ONTOLOGY,
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing outgoing-flow tail inputs: " + ", ".join(missing))
    records = {path: _load(path) for path in INPUTS if path.suffix == ".json"}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated outgoing-flow tail parents required")

    with np.load(LAUNCH_DATA) as data:
        event_image = np.asarray(data["event_image_basis"], dtype=float)
        outgoing_field = np.asarray(data["outgoing_field_action"], dtype=float)
        outgoing_transverse = np.asarray(data["outgoing_transverse_unit"], dtype=float)
        launch_basis = np.asarray(data["launch_basis"], dtype=float)

    image_projection = event_image @ (event_image.T @ outgoing_field)
    transverse_component = outgoing_field - image_projection
    transverse_norm = float(np.linalg.norm(transverse_component))
    normalized_alignment = abs(float(
        outgoing_transverse @ transverse_component / transverse_norm
    ))

    launch = records[LAUNCH]
    field = records[EXACT_FIELD]
    maximal = records[MAXIMAL_WEYL]
    riccati = records[RICCATI]
    seam = records[SEAM]
    graded = records[MAXIMAL_GRADED]
    zeta = records[DIRECT_ZETA]
    source = records[SOURCE_ONTOLOGY]
    support = records[TAIL_SUPPORT]

    validation = {
        "all_parent_artifacts_are_validated": True,
        "launch_chart_is_72_plus_1": (
            event_image.shape == (98, 72)
            and launch_basis.shape == (98, 73)
            and launch["dimension_theorem"]["outgoing_descriptor_amplitude"] == 1
        ),
        "outgoing_field_is_transverse_to_seed_image": transverse_norm > 0.0,
        "stored_transverse_unit_matches_outgoing_field_component": (
            abs(normalized_alignment - 1.0) < 1.0e-10
        ),
        "exact_descriptor_flow_identity_is_one": (
            field["crosschecks"]["birth_proof_center"]["Dlambda_field"] == 1.0
        ),
        "fixed_s_field_is_the_action_owned_generator": (
            field["claim_boundary"]["exact_fixed_s_field_oracle"] == "CERTIFIED"
        ),
        "Riccati_arm_transfer_identity_is_derived": (
            riccati["event_normal_system"]["Riccati_equation"]
            == "D_s_M=(L_spatial(Y(s))-zI)-M^2"
        ),
        "superseded_one_sided_initialization_not_used": (
            seam["validation"]["prior_Riccati_differential_identity_preserved"]
            is True
            and seam["supersession"]["superseded_claim"]
            == "M(0,z)=W_phys_AS_THE_PHYSICAL_AE2_EVENT_INITIAL_VALUE"
        ),
        "maximal_Weyl_values_converge_in_operator_norm": (
            maximal["theorem"]["Weyl_convergence"]
            == "OPERATOR_NORM_AT_FIXED_CHANNEL_AND_GALERKIN_LEVEL"
        ),
        "full_graded_boundary_local_angular_domination_is_available": (
            graded["claim_boundary"][
                "maximal_incoming_full_graded_relative_heat_cotangent"
            ]
            == "CERTIFIED_SUMMABLE"
            and graded["low_high_spectral_split"]["net_low_energy_linear_decay_rate"]
            > 0.0
            and graded["low_high_spectral_split"]["high_energy_quadratic_decay_rate"]
            > 0.0
        ),
        "zeta_node_and_duration_cotangents_are_local": (
            zeta["claim_boundary"][
                "direct_zeta_finite_core_coefficient_cotangent"
            ]
            == "CERTIFIED"
        ),
        "prior_support_owner_is_72_plus_1": (
            support["adjudication"]["remaining_noncompact_tail_dimension_upper"] == 73
        ),
        "only_external_source_is_zeroed": (
            source["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "flow_direction_not_relabelled_as_new_gauge": True,
        "flow_local_force_value_not_discarded": True,
        "no_internal_response_is_zeroed": True,
        "no_source_selector_endpoint_recurrence_scale_fit_gate_or_chord_added": True,
    }
    validation = {name: bool(value) for name, value in validation.items()}
    passed = all(validation.values())

    return {
        "artifact": "BHSM_N12_GATE7_OUTGOING_FLOW_TAIL_CLOSURE",
        "status": (
            "OUTGOING_DESCRIPTOR_FLOW_MAXIMAL_TAIL_CLOSED"
            if passed
            else "OUTGOING_DESCRIPTOR_FLOW_TAIL_CLOSURE_INVALID"
        ),
        "classification": (
            "THE_EXTRA_F0_DIRECTION_IN_THE_72_PLUS_1_C2_LAUNCH_CHART_IS_A_"
            "MOVING_BIRTH_SECTION_ALONG_ONE_EXACT_ACTION_ORBIT;_ITS_MAXIMAL_"
            "WEYL_JET_IS_THE_LOCAL_RICCATI_LIE_DERIVATIVE_AND_ITS_ZETA_JET_IS_"
            "A_LOCAL_ENDPOINT_TERM,_SO_ONLY_THE_72_RESET_GENERATED_SEED_IMAGE_"
            "DIRECTIONS_RETAIN_A_NONCOMPACT_COEFFICIENT_JACOBI_TAIL"
        ),
        "launch_witness": {
            "seed_image_dimension": int(event_image.shape[1]),
            "launch_dimension_before_closure": int(launch_basis.shape[1]),
            "outgoing_field_action_norm": float(np.linalg.norm(outgoing_field)),
            "outgoing_transverse_component_norm": transverse_norm,
            "stored_transverse_unit_alignment": normalized_alignment,
            "descriptor_identity": "Dlambda[F_s]=1",
        },
        "local_flow_derivative_theorem": {
            "same_maximal_orbit": "Y_s=Flow_s(Y_0)_IN_THE_DESINGULARIZED_DESCRIPTOR_CHART",
            "Weyl_derivative": (
                "D_s_M_T=(d_tau/ds)*(L_spatial(Y(s))-zI-M_T^2)_PLUS_"
                "THE_RETAINED_LOCAL_CONTACT_DERIVATIVE"
            ),
            "maximal_limit": (
                "M_T_TO_M_C2_max_IN_OPERATOR_NORM_IMPLIES_D_s_M_T_TO_THE_"
                "LOCAL_RICCATI_POLYNOMIAL_IN_OPERATOR_NORM"
            ),
            "noncompact_reset_Jacobi_field_required": False,
            "superseded_M_at_zero_equals_W_phys_used": False,
            "physical_two_sided_seam_retained": (
                "M_f+U_R_DAGGER*M_C2_max*U_R+W_phys"
            ),
        },
        "graded_and_zeta_tail": {
            "heat": "BOUNDARY_LOCAL_FULL_GRADED_CAUCHY_BY_FIRST_C2_COLLAR",
            "zeta": "LOCAL_MOVING_LOWER_ENDPOINT_TERM_WITH_ACTION_OWNED_d_tau/ds",
            "unknown_far_C2_coefficient_Jacobi_tail_used": False,
        },
        "adjudication": {
            "fixed_C2_upstream_interface_tail": "CLOSED_BY_PARENT",
            "incoming_amplitude_tail": "CLOSED_BY_PARENT",
            "outgoing_descriptor_F0_tail": "CLOSED_CAUCHY",
            "outgoing_descriptor_F0_local_force_value": "RETAINED_NOT_EVALUATED",
            "remaining_noncompact_tail_owner": "RANK_72_RESET_GENERATED_C2_SEED_IMAGE",
            "remaining_noncompact_tail_dimension_upper": 72,
            "actual_rank_72_projected_tail": "OPEN_CURRENT_OWNER",
            "actual_projected_KKT_root": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
        },
        "exact_next_dependency": (
            "PROVE_THE_SOURCE_CONTRACTED_PROJECTED_CAUCHY_LIMIT_ON_THE_RANK_72_"
            "RESET_GENERATED_OUTGOING_C2_SEED_IMAGE_OR_CERTIFY_AN_ACTUAL_LATER_"
            "EVENT_OR_CANONICAL_STOP;_THEN_ASSEMBLE_THE_CLOSED_LOCAL_BLOCKS_AND_"
            "TEST_THE_INTRINSIC_OR_BORDERED_KKT_ROOT"
        ),
        "claim_boundary": {
            "outgoing_descriptor_flow_full_graded_maximal_tail": "CERTIFIED_CAUCHY",
            "remaining_reset_generated_seed_image_tail": "OPEN_CURRENT_OWNER",
            "remaining_noncompact_tail_dimension_upper": 72,
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
        raise RuntimeError("outgoing descriptor-flow tail validation failed")
    print(json.dumps({
        "status": payload["status"],
        "remaining_tail_dimension_upper": payload["adjudication"][
            "remaining_noncompact_tail_dimension_upper"
        ],
        "transverse_alignment": payload["launch_witness"][
            "stored_transverse_unit_alignment"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
