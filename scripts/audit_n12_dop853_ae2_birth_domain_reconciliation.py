"""Reconcile the DOP853 descriptor response with the canonical birth-domain no-go.

The adaptive DOP853 certificates concern a finite-dimensional bordered Hessian
response on the C2 state tangent.  They are not, by themselves, a temporal
matter operator or a choice of its self-adjoint birth-interface domain.  This
audit records the exact action-version split: the v6.7 no-go survives, while
the already owner-selected BHSM-AE-2.0.0 global-spin transmission domain
supersedes it only for that explicitly versioned action.
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
OLD_NO_GO = BASE / "BHSM_N12_FORWARD_MATTER_DOMAIN_NO_GO.json"
RETAINED_COMPLETION_NO_GO = BASE / "BHSM_RETAINED_ACTION_COMPLETION_NO_GO.json"
AE2_ACTION = ROOT / "artifacts" / "action_extension" / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
AE2_DOMAIN = BASE / "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
PROJECTOR_SCRIPT = ROOT / "scripts" / "certify_n12_c2_stop_dop853_adaptive_selected_projector_graph.py"
INVERSE_SCRIPT = ROOT / "scripts" / "certify_n12_c2_stop_dop853_adaptive_bordered_hard_inverse.py"
RESPONSE_SCRIPT = ROOT / "scripts" / "certify_n12_c2_stop_dop853_adaptive_bordered_rhs_response.py"
LOCAL_ACTION = ROOT / "src" / "bhsm" / "interface" / "aether_n3_exact_full_local_action_jet_v17_60.py"
RESULT = BASE / "BHSM_N12_DOP853_AE2_BIRTH_DOMAIN_RECONCILIATION.json"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _called_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            names.add(function.id)
        elif isinstance(function, ast.Attribute):
            parts = [function.attr]
            value = function.value
            while isinstance(value, ast.Attribute):
                parts.append(value.attr)
                value = value.value
            if isinstance(value, ast.Name):
                parts.append(value.id)
            names.add(".".join(reversed(parts)))
    return names


def build_payload() -> dict[str, Any]:
    old = _load(OLD_NO_GO)
    retained = _load(RETAINED_COMPLETION_NO_GO)
    ae2 = _load(AE2_ACTION)
    ae2_domain = _load(AE2_DOMAIN)

    response_text = RESPONSE_SCRIPT.read_text(encoding="utf-8")
    projector_text = PROJECTOR_SCRIPT.read_text(encoding="utf-8")
    calls = _called_names(RESPONSE_SCRIPT) | _called_names(PROJECTOR_SCRIPT)
    forbidden_domain_tokens = {
        "Gamma0", "Gamma1", "Cayley", "Robin", "U_R", "W_phys",
        "M_event", "M_child", "D_AE2",
    }
    absent_tokens = sorted(
        token for token in forbidden_domain_tokens
        if token not in response_text and token not in projector_text
    )

    checks = {
        "unchanged_retained_action_no_go_is_validated": (
            old["validation_passed"] is True
            and retained["status"] == "TERMINAL_CANONICAL_NO_GO_FOR_UNCHANGED_RETAINED_ACTION"
        ),
        "ae2_is_an_explicitly_versioned_owner_selected_action": (
            ae2["action_version"] == "BHSM-AE-2.0.0"
            and ae2["action_version_status"] == "OWNER_SELECTED_NEW_ACTION_DOMAIN_VERSION"
            and ae2["validation"]["owner_selected_A"] is True
            and ae2["validation"]["old_action_no_go_preserved"] is True
        ),
        "ae2_domain_is_validated_and_unique_modulo_gauge_and_spin_sign": (
            ae2_domain["validation_passed"] is True
            and ae2_domain["validation"]["spinor_birth_graph_unique_modulo_gauge_and_global_sign"] is True
            and ae2_domain["source_domain"]["Cayley_phase_family"] is None
        ),
        "dop853_uses_local_action_jet": (
            "dense.cluster.local.exact_full_action_jet_at_state" in calls
            and "np.linalg.eigh" in calls
            and "np.linalg.solve" in calls
        ),
        "dop853_contains_no_temporal_birth_domain_symbol": len(absent_tokens) == len(forbidden_domain_tokens),
        "dop853_bordered_dimension_is_literal_62": '"bordered_dimension": 62' in INVERSE_SCRIPT.read_text(encoding="utf-8"),
        "dop853_does_not_import_the_ae2_action_module": (
            "action_extension_global_spin_reset_ae2" not in response_text
            and "action_extension_global_spin_reset_ae2" not in projector_text
        ),
    }
    passed = all(checks.values())

    return {
        "artifact": "BHSM_N12_DOP853_AE2_BIRTH_DOMAIN_RECONCILIATION",
        "status": (
            "B1_AE2_SUPERSEDES_THE_UNCHANGED_ACTION_DOMAIN_NO_GO;_DOP853_IS_AUXILIARY_GEOMETRY_ONLY"
            if passed else "BIRTH_DOMAIN_RECONCILIATION_OPEN"
        ),
        "phase_B_outcome": "B1_NO_GO_SUPERSEDED_FOR_BHSM_AE_2_0_0_ONLY" if passed else "OPEN",
        "exact_answers": {
            "1_domain_used_by_current_DOP853_K": (
                "FINITE_DIMENSIONAL_REAL_EUCLIDEAN_REDUCED_C2_TANGENT:_"
                "K_border=[[H_red-lambda_24*I,psi_24],[psi_24^T,0]]_ON_R62;_"
                "THIS_IS_NOT_A_TEMPORAL_MATTER_SELF_ADJOINT_BIRTH_DOMAIN"
            ),
            "2_is_that_birth_domain_derived_from_the_unchanged_action": (
                "NOT_APPLICABLE_TO_THE_DOP853_MATRIX;_THE_UNCHANGED_V6_7_ACTION_"
                "STILL_DOES_NOT_DERIVE_A_UNIQUE_NORMAL_MATTER_BIRTH_DOMAIN"
            ),
            "3_implicit_Cayley_Robin_or_transmission_phase": (
                "NONE_IN_THE_DOP853_CONSTRUCTION;_OMISSION_IS_NOT_SELECTION_AND_"
                "DOES_NOT_TURN_THE_MATRIX_INTO_THE_GATE7_SEAM_OPERATOR"
            ),
            "4_new_DOP853_theorem_removes_phase_family": False,
            "5_existing_transmission_theorem_supersedes_old_no_go": (
                "YES_ONLY_FOR_THE_EXPLICIT_OWNER_SELECTED_ACTION_VERSION_BHSM_AE_2_0_0"
            ),
            "6_exact_supersession_equations": {
                "trace": ae2["action_definition"]["trace_graph"],
                "variation": ae2["action_definition"]["variation_graph"],
                "conormal": ae2["action_definition"]["squared_operator_flux_graph"],
                "squared_domain": ae2["action_definition"]["squared_operator_domain"],
                "why_old_resolvent_witness_no_longer_applies": (
                    "THE_WITNESS_STILL_PROVES_THAT_ALTERNATE_PHASE_DOMAINS_ARE_"
                    "INEQUIVALENT,_BUT_THOSE_DOMAINS_ARE_NOT_MEMBERS_OF_THE_SINGLE_"
                    "AE2_GLOBAL_SECTION_CONFIGURATION_SPACE"
                ),
            },
            "7_DOP853_canonical_classification": (
                "VALID_ACTION_GEOMETRY_AUXILIARY_UNDER_BOTH_LINEAGES;_NOT_A_"
                "CANONICAL_GATE7_OPERATOR_UNTIL_COMPOSED_WITH_THE_AE2_JOINT_SEAM_DOMAIN"
            ),
        },
        "action_version_split": {
            "unchanged_retained_v6_7": {
                "result": "B2_NO_GO_SURVIVES",
                "FULL_BHSM_COMPLETE": False,
                "smallest_blocker": (
                    "UNCHANGED_RETAINED_ACTION_DOES_NOT_SELECT_A_UNIQUE_"
                    "NORMAL_MATTER_BIRTH_DOMAIN_REQUIRED_BY_GATE_7"
                ),
            },
            "owner_selected_BHSM_AE_2_0_0": {
                "result": "B1_DOMAIN_NO_GO_SUPERSEDED",
                "Gate7": "ACTIVE",
                "remaining_requirement": (
                    "COMPOSE_THE_CERTIFIED_DOP853_GEOMETRY_RESPONSE_WITH_THE_"
                    "AE2_TWO_SIDED_CALDERON_SEAM_AND_EVALUATE_THE_PHYSICAL_"
                    "HEAT_MINUS_ZETA_QUOTIENT_COVECTOR"
                ),
            },
        },
        "dop853_type_audit": {
            "state_dimension": 98,
            "configuration_dimension_removed_from_reduced_hessian": 37,
            "reduced_hessian_dimension": 61,
            "selected_line_dimension": 1,
            "hard_complement_dimension": 60,
            "bordered_dimension": 62,
            "operator_source": "exact_full_action_jet_at_state(...).hessian[QDIM:,QDIM:]",
            "rhs_source": "retained_local_action_gradient_minus_mixed_Hessian_times_configuration",
            "temporal_boundary_trace_space_present": False,
            "normal_matter_domain_parameter_present": False,
            "absent_domain_tokens": absent_tokens,
        },
        "validation": checks,
        "validation_passed": passed,
        "claim_boundary": {
            "DOP853_closes_canonical_Gate7_by_itself": False,
            "unchanged_action_no_go_retracted": False,
            "AE2_silently_adopted": False,
            "AE2_domain_ownership_closed": passed,
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                OLD_NO_GO, RETAINED_COMPLETION_NO_GO, AE2_ACTION, AE2_DOMAIN,
                PROJECTOR_SCRIPT, INVERSE_SCRIPT, RESPONSE_SCRIPT, LOCAL_ACTION,
            )
        },
        "exact_next_dependency": (
            "FINISH_THE_IN_FLIGHT_RESPONSE_REFINEMENT,_THEN_ASSEMBLE_THE_FIRST_"
            "RIGOROUS_SECOND_VARIATION_TUBE_AS_A_GEOMETRY_INPUT;_DO_NOT_PROMOTE_"
            "IT_UNTIL_THE_AE2_JOINT_SEAM_OPERATOR_COMPOSITION_IS_EXPLICIT"
        ),
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
        "phase_B_outcome": payload["phase_B_outcome"],
        "validation_passed": payload["validation_passed"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
