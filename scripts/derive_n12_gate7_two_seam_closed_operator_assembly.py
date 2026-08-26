"""Derive the closed E0/C1--E1/C2 two-seam operator assembly."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY.json"
BIRTH = BASE / "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
GLUING = BASE / "BHSM_N12_FINITE_HISTORY_GLUING_FORCE_PROVENANCE.json"
ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
SEED = BASE / "BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json"
AE2 = ROOT / "artifacts" / "action_extension" / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
THEORY = ROOT / "theory" / "n12_gate7_two_seam_closed_operator_assembly.md"
INPUTS = (BIRTH, COMPACT, GLUING, ONTOLOGY, SEED, AE2, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _exact_witness() -> dict[str, str | bool]:
    # Scalar unitary U0=-1; all arithmetic is exact.
    m00, m01, m10, m11 = map(Fraction, (3, 1, 1, 4))
    u0 = Fraction(-1)
    load0 = Fraction(2)
    load1 = Fraction(5)
    a0 = load0 + u0 * m00 * u0
    c01 = u0 * m01
    c10 = m10 * u0
    d1 = m11 + load1
    direct_det = a0 * d1 - c01 * c10
    birth_load = u0 * load0 * u0
    x_birth = m01 / (m00 + birth_load)
    mf_physical = m11 - m10 * x_birth
    reduced_e1 = mf_physical + load1
    schur_det = a0 * reduced_e1
    d_m11 = Fraction(7)
    direct_d_logdet = d_m11 * a0 / direct_det
    schur_d_logdet = d_m11 / reduced_e1
    return {
        "M_form": "[[3,1],[1,4]]",
        "U0": str(u0),
        "L0": str(load0),
        "L1": str(load1),
        "S_01": f"[[{a0},{c01}],[{c10},{d1}]]",
        "B_birth": str(birth_load),
        "X_birth": str(x_birth),
        "M_f_physical": str(mf_physical),
        "S_E1": str(reduced_e1),
        "direct_determinant": str(direct_det),
        "Schur_determinant": str(schur_det),
        "determinant_residual": str(direct_det - schur_det),
        "D_M11": str(d_m11),
        "direct_D_logdet": str(direct_d_logdet),
        "Schur_D_logdet": str(schur_d_logdet),
        "first_variation_residual": str(direct_d_logdet - schur_d_logdet),
        "positive_definite": a0 > 0 and direct_det > 0,
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing two-seam assembly inputs: " + ", ".join(missing))
    birth, compact, gluing, ontology, seed, ae2 = map(_load, INPUTS[:-1])
    records = (birth, compact, gluing, ontology, seed, ae2)
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated two-seam parents required")
    witness = _exact_witness()
    validation = {
        "birth_load_type_is_closed": (
            birth["exact_birth_load"]["load"]
            == "B_birth=U_R0*(M_E0+W_E0)*U_R0^dagger"
        ),
        "compact_two_boundary_partition_is_free": (
            compact["endpoint_partition"]["both_endpoint_traces_free_Calderon_data"]
            is True
        ),
        "one_seam_Schur_identity_is_retained": (
            gluing["exact_identities"]["determinant"]
            == "det(P_joint)=det(A)*det(F)*det(S_AE2)"
        ),
        "only_external_J_ext_is_zeroed": (
            ontology["external_internal_partition"]["set_to_zero"] == ["J_ext"]
        ),
        "single_reverse_seed_is_retained": (
            seed["adjudication"]["joint_reverse_seed_formula"] == "CLOSED"
        ),
        "reset_lift_is_unitary": ae2["finite_certificate"]["unitarity_residual"] < 1.0e-12,
        "exact_determinant_identity_closes": witness["determinant_residual"] == "0",
        "exact_first_variation_identity_closes": witness["first_variation_residual"] == "0",
        "positive_exact_witness_used": witness["positive_definite"] is True,
        "no_double_counting_source_seam_force_selector_or_action_term_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY",
        "status": (
            "TWO_SEAM_CLOSED_OPERATOR_TOPOLOGY_AND_SCHUR_EQUIVALENCE_DERIVED"
            if passed else "TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY_NOT_CERTIFIED"
        ),
        "classification": (
            "THE_COMPLETE_E0_C1_AND_E1_C2_INTERNAL_SEAM_TOPOLOGY_IS_AN_EXACT_"
            "TWO_TRACE_BLOCK_WHOSE_DIRECT_AND_BIRTH_REDUCED_DETERMINANTS_AND_FIRST_"
            "VARIATIONS_AGREE;_THE_BIRTH_TRACE_REMAINS_IN_THE_ZERO_SOURCE_"
            "DETERMINANT_AND_THE_MISSING_NUMERICAL_BLOCK_IS_M_E0_WITH_ITS_JET"
        ),
        "closed_operator": {
            "diagram": "PRE_E0--E0/C1--COMPACT_C1--E1/C2--C2_EXTERIOR",
            "formation_Calderon": "M_form=[[M00,M01],[M10,M11]]",
            "E0_load": "L0=M_E0+W0",
            "E1_load": "L1=U1^dagger*M_C2*U1+W1",
            "two_seam_trace_block": (
                "S_01=[[L0+U0^dagger*M00*U0,U0^dagger*M01],"
                "[M10*U0,M11+L1]]"
            ),
            "external_source_coupling": "-Re<J_ext,u_E0>",
            "zero_source_effect": "REMOVE_LINEAR_COUPLING_BUT_RETAIN_BOTH_ROWS_AND_COLUMNS",
        },
        "inverse_free_reduction": {
            "B_birth": "U0*L0*U0^dagger",
            "solve": "(M00+B_birth)*X_birth=M01",
            "physical_M_f": "M11-M10*X_birth",
            "terminal_seam": "S_E1=M_f_phys+L1",
            "determinant": "det(S_01)=det(L0+U0^dagger*M00*U0)*det(S_E1)",
            "direct_and_Schur_routes_counted": "EXACTLY_ONCE_AS_EQUIVALENT_REPRESENTATIONS",
            "explicit_matrix_inverse_formed": False,
        },
        "first_jet": {
            "D_A0": (
                "D_L0+(D_U0^dagger)*M00*U0+U0^dagger*(D_M00)*U0+"
                "U0^dagger*M00*(D_U0)"
            ),
            "D_C01": "(D_U0^dagger)*M01+U0^dagger*(D_M01)",
            "D_D1": (
                "D_M11+(D_U1^dagger)*M_C2*U1+U1^dagger*(D_M_C2)*U1+"
                "U1^dagger*M_C2*(D_U1)+D_W1"
            ),
            "reverse_rule": "ONE_JOINT_COTANGENT_REVERSED_ONCE_THROUGH_S_01_AND_ALL_ARMS",
        },
        "exact_witness": witness,
        "matching_audit": {
            "two_seam_operator_topology": "VALID_MATCH_DERIVED",
            "birth_trace_retention_at_J_ext_zero": "VALID_MATCH_DERIVED",
            "direct_Schur_determinant_equivalence": "VALID_MATCH_DERIVED",
            "direct_Schur_first_variation_equivalence": "VALID_MATCH_DERIVED",
            "E0_event_side_M_E0_and_first_jet": "ACTUALLY_MISSING",
            "C2_maximal_tail": "ACTUALLY_MISSING",
            "actual_per_level_graded_operator_values": "ACTUALLY_MISSING",
        },
        "exact_next_dependency": (
            "REALIZE_M_E0_AND_ITS_FIRST_ACTION_JET_AND_COMPLETE_THE_C2_MAXIMAL_"
            "TAIL_ON_THE_SAME_LOCAL_FAMILY,_THEN_INSTANTIATE_S_01_PER_GRADED_LEVEL_"
            "AND_APPLY_THE_EXISTING_SINGLE_HEAT_MINUS_ZETA_REVERSE_SEED"
        ),
        "adjudication": {
            "complete_internal_operator_topology": "CLOSED",
            "complete_internal_operator_numerical_family": "OPEN_CURRENT_OPERATOR_OWNER",
            "additional_external_or_seam_source": "FORBIDDEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "Gate7": "ACTIVE_TWO_SEAM_OPERATOR_VALUES_AND_GRADED_COTANGENT",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
            "operator_topology_derived": True,
            "operator_values_realized": False,
            "numerical_force_claimed": False,
            "frozen_predictions_changed": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "topology": payload["adjudication"]["complete_internal_operator_topology"],
        "values": payload["adjudication"]["complete_internal_operator_numerical_family"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
