"""Materialize the owner-authorized encapsulation interface-action class."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.owner_authorized_encapsulation_interface_action import (  # noqa: E402
    ACTION_VERSION,
    CLASSIFICATION,
    DERIVATIVE_CLASS,
    EXACT_NEXT_OBJECT,
    INTERFACE_FREEDOM_CLASS,
    LOOP_CLASS,
    UNIQUE_ACTUALIZATION_CLASS,
    interface_action_payload,
    passive_mismatch_active_differential,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_OWNER_AUTHORIZED_ENCAPSULATION_INTERFACE_ACTION_CLASSIFICATION.json"
)
INPUTS = (
    ROOT / "src/bhsm/interface/owner_authorized_encapsulation_interface_action.py",
    ROOT / "scripts/materialize_owner_authorized_encapsulation_interface_action.py",
    ROOT / "tests/test_owner_authorized_encapsulation_interface_action.py",
    ROOT / "theory/bhsm_owner_authorized_encapsulation_interface_action.md",
    ROOT / "src/bhsm/interface/reset_charge_carrier_dependency_cycle_adjudication.py",
    ROOT / "artifacts/action_extension/BHSM_RESET_CHARGE_CARRIER_DEPENDENCY_CYCLE_ADJUDICATION.json",
    ROOT / "src/bhsm/interface/encapsulation_response_representation_theorem.py",
    ROOT / "src/bhsm/interface/active_encapsulation_boundary_generator_adjudication.py",
    ROOT / "src/bhsm/interface/environmental_child_compatibility_selection.py",
    ROOT / "src/bhsm/interface/energetically_admissible_encapsulation_carrier_adjudication.py",
    ROOT / "src/bhsm/interface/full_field_moving_reset_graph_decision.py",
    ROOT / "src/bhsm/interface/reset_correspondence_stationarity_adjudication.py",
    ROOT / "src/bhsm/interface/nonfermion_relative_boundary_variation.py",
    ROOT / "src/bhsm/interface/master_action/terms.py",
    ROOT / "src/bhsm/interface/master_action/variations.py",
    ROOT / "src/bhsm/interface/completion/global_envelopment_cap_selection_v14_60.py",
    ROOT / "src/bhsm/interface/completion/full_global_envelopment_v14_61.py",
    ROOT / "src/bhsm/interface/completion/global_attachment_incidence_curvature_v14_68.py",
    ROOT / "src/bhsm/interface/completion/tensor_differential_incidence_v14_69.py",
    ROOT / "src/bhsm/interface/aether_master_closure_v15_5.py",
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    result = interface_action_payload()
    authority = result["authority"]
    variables = result["variables"]
    density = result["invariant_densities"]
    order = result["derivative_order"]
    equations = result["Euler_Lagrange_system"]
    active = result["active_differential"]
    canonical = result["canonical_Lagrangian"]
    freedom = result["parameter_freedom"]
    closure = result["closure_and_rank"]
    claims = result["claim_boundary"]
    passive_residual = passive_mismatch_active_differential(
        [0.5, -0.2, 0.7],
        [0.1, 0.4],
        [[1.0, 0.2], [0.0, 1.0], [0.3, -0.1]],
    )
    validation = {
        "owner_authority_separated_from_old_action": (
            authority["new_primitive"] == "P-A*"
            and not authority["part_of_previous_13_term_action"]
            and not authority["mathematical_density_selected_by_authorization"]
        ),
        "all_required_interface_variables_are_dynamical": (
            variables["carrier"]["varied"]
            and variables["attachment"]["not_external_input"]
            and variables["boundary_relation"]["not_external_input"]
            and variables["fields"]["varied"]
        ),
        "carrier_is_stratified_and_pregeometry_guarded": (
            len(variables["carrier"]["active_strata"]) == 3
            and "dim M^(s)-1" in variables["carrier"]["dimension"]
            and "no ordinary embedded carrier" in variables["carrier"]["pregeometry_guardrail"]
        ),
        "density_families_classified": (
            len(density) == 12
            and any(row["family"] == "attachment_first_jet" and row["status"] == "REQUIRED_CLASS" for row in density)
            and any(row["family"] == "owned_GHY_Hayward" and row["status"].startswith("REDUNDANT") for row in density)
        ),
        "ORD1_is_minimal": order["classification"] == DERIVATIVE_CLASS == "ORD1" and order["minimum"] == 1,
        "full_variation_and_five_equation_classes_recorded": (
            all(key in equations for key in ("carrier", "attachment", "boundary_relation", "event_field_seam", "child_field_seam"))
            and "E_iota" in result["first_variation"]["variation"]
            and "E_F" in result["first_variation"]["variation"]
            and "E_L" in result["first_variation"]["variation"]
        ),
        "Delta_enc_derived_from_action_variation_but_value_withheld": (
            "E_qc(S_enc)+C(F_B)^*E_qe(S_enc)" in active["definition_from_total_seam_equations"]
            and active["amplitude"] is None
            and not active["value_derived"]
        ),
        "passive_mismatch_no_go_verified": float((passive_residual @ passive_residual) ** 0.5) < 1.0e-14,
        "canonical_class_not_member_promoted": (
            canonical["conditional_status"] == "CANONICAL_GENERATING_FAMILY_CLASS_DERIVED"
            and not canonical["actual_isotropy_verified"]
            and not canonical["actual_Lagrangian_verified"]
        ),
        "IF5_no_coefficients_or_functions_selected": (
            freedom["classification"] == INTERFACE_FREEDOM_CLASS == "IF5"
            and freedom["functions_selected"] == 0
            and freedom["coefficients_fitted"] == 0
        ),
        "all_adversarial_convenience_actions_rejected": all(
            not row["admissible_class_member"] for row in result["adversarial_candidates"]
        ),
        "historical_candidates_not_promoted": all(
            not row["selected"] for row in result["historical_candidates"]
        ),
        "LOOP3_UA5_and_rank_firewall_preserved": (
            closure["loop"] == LOOP_CLASS == "LOOP3"
            and closure["unique_actualization"] == UNIQUE_ACTUALIZATION_CLASS == "UA5"
            and closure["N12_rank_added"] == 0
            and closure["N12_residual_before_time_quotient"] == 67
            and closure["N12_residual_after_time_quotient"] == 66
        ),
        "no_reset_or_downstream_attachment_fabricated": (
            closure["selected_carrier"] is None
            and closure["selected_F_B"] is None
            and closure["selected_L_s"] is None
            and closure["physical_reset_domain"] is None
            and closure["S1"] is None
            and closure["S2"] is None
            and closure["S3"] is None
            and closure["S4"] is None
        ),
        "no_arbitrary_owner_question": result["owner_question"] is None and "IF5" in result["why_no_owner_question"],
        "exact_next_object_recorded": result["exact_next_object"] == EXACT_NEXT_OBJECT,
        "claim_firewall_preserved": (
            claims["OWNER_AUTHORIZED_PRIMITIVE_RECORDED"]
            and not any(value for key, value in claims.items() if key != "OWNER_AUTHORIZED_PRIMITIVE_RECORDED")
        ),
    }
    source_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
        for path in INPUTS
    }
    return {
        "artifact": "BHSM_OWNER_AUTHORIZED_ENCAPSULATION_INTERFACE_ACTION_CLASSIFICATION",
        "action_version": ACTION_VERSION,
        "classification": {
            "authority": CLASSIFICATION,
            "derivative_order": DERIVATIVE_CLASS,
            "interface_freedom": INTERFACE_FREEDOM_CLASS,
            "unique_actualization": UNIQUE_ACTUALIZATION_CLASS,
            "dependency_loop": LOOP_CLASS,
        },
        "scientific_result": (
            "OWNER_AUTHORIZATION_FIXES_THE_PHYSICAL_ROLE_AND_MAXIMAL_ORD1_"
            "COVARIANT_GENERATING_FUNCTIONAL_CLASS_BUT_NOT_ITS_CONSTITUTIVE_"
            "DENSITY;_IF5_FUNCTIONAL_FREEDOM_REMAINS_AND_THE_LOOP_IS_NOT_EXECUTABLY_BROKEN"
        ),
        "interface_action": result,
        "VALIDATED": [
            "P-A* is an owner-authorized new primitive and not a derivation from the old 13-term action",
            "one abstract stratified carrier, dynamical F_B, and Lagrangian-relation-valued L_s",
            "ORD1 is the minimal local derivative class",
            "Delta_enc is the action-derived active seam source for any selected member",
            "no-ex-nihilo is a Ward/Noether identity with explicit environment work",
            "the generating-family class is canonically meaningful",
            "IF5, UA5, and executable LOOP3",
        ],
        "INVALIDATED": [
            "owner semantic authorization uniquely specifies a zero-parameter density",
            "a passive trace-mismatch penalty produces active encapsulation work",
            "rho_hold is an available input before the common charge domain exists",
            "v14 synthetic envelopment coefficients are the physical interface law",
            "a fixed external environment can absorb unrecorded energy while preserving closed-system conservation",
        ],
        "REDUNDANT": [
            "recounting the existing GHY/Hayward completion as new interface strength",
            "new second-derivative curvature terms without an independent extension",
            "independent child-mode controls when the initiating event must determine the response",
        ],
        "OPEN": [
            EXACT_NEXT_OBJECT,
            "physical carrier, attachment, nonfermion relation, and active differential values",
            "physical reduced symplectic domain, actual stabilizer, and projectors",
            "all downstream charges, rho_hold, beta, graph jets, S1-S4, and full attachment",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
        "source_sha256": source_hashes,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [key for key, value in payload["validation"].items() if not value]
        raise RuntimeError("interface-action classification validation failed: " + ", ".join(failed))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
