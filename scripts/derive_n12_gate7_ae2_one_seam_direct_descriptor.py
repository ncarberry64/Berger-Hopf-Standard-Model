"""Derive and audit the direct AE2 one-seam finite-core descriptor."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_ae2_one_seam_descriptor import (  # noqa: E402
    assemble_ae2_one_seam_descriptor,
    scalar_seam_schur_value,
)


BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR.json"
SOURCE_ROLE = BASE / "BHSM_N12_GATE7_EXTERNAL_BIRTH_SOURCE_ROLE_SUPERSESSION.json"
ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
COMPACT = BASE / "BHSM_N12_COMPACT_FINITE_HISTORY_OPERATOR.json"
CHILD = BASE / "BHSM_N12_C2_1222_SEGMENT_FINITE_CORE_DESCRIPTOR.json"
MODULE = ROOT / "src" / "bhsm" / "interface" / "aether_ae2_one_seam_descriptor.py"
THEORY = ROOT / "theory" / "n12_gate7_ae2_one_seam_direct_descriptor.md"
INPUTS = (SOURCE_ROLE, ONTOLOGY, COMPACT, CHILD, MODULE, THEORY)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _scalar_endpoint_diagonal(
    x_left: float,
    x_right: float,
    duration: float,
    unit_value: float,
    shifted_mass: float,
) -> float:
    potential = unit_value * math.exp(-(x_left + x_right))
    return 1.0 / duration + (potential + shifted_mass) * duration / 3.0


def _witness() -> dict[str, Any]:
    xf = np.asarray((0.02, 0.01, 0.0))
    hf = np.asarray((0.21, 0.17))
    xc = np.asarray((0.0, -0.01, 0.015, 0.02))
    hc = np.asarray((0.13, 0.19, 0.23))
    unit_value = 3.0
    contact = 0.4
    shift = 0.7
    descriptor = assemble_ae2_one_seam_descriptor(
        formation_log_radii=xf,
        formation_proper_durations=hf,
        child_log_radii=xc,
        child_proper_durations=hc,
        channel="scalar",
        unit_channel_value=unit_value,
        seam_contact=contact,
    )
    P = descriptor["K"] + shift * descriptor["M"]
    seam = descriptor["seam_reduced_index"]
    formation_interior = list(range(seam))
    child_interior = list(range(seam + 1, P.shape[0]))

    formation_diagonal = _scalar_endpoint_diagonal(
        xf[-2], xf[-1], hf[-1], unit_value, shift
    )
    child_diagonal = _scalar_endpoint_diagonal(
        xc[0], xc[1], hc[0], unit_value, shift
    )

    def arm_value(indices: list[int], seam_diagonal: float) -> float:
        if not indices:
            return seam_diagonal
        block = P[np.ix_(indices, indices)]
        coupling = P[np.ix_(indices, [seam])].reshape(-1)
        return seam_diagonal - float(coupling @ np.linalg.solve(block, coupling))

    M_f = arm_value(formation_interior, formation_diagonal)
    M_c = arm_value(child_interior, child_diagonal)
    schur_sum = M_f + M_c + contact
    direct_schur = scalar_seam_schur_value(P, seam)

    sign, direct_logdet = np.linalg.slogdet(P)
    formation_logdet = (
        float(np.linalg.slogdet(P[np.ix_(formation_interior, formation_interior)])[1])
        if formation_interior
        else 0.0
    )
    child_logdet = (
        float(np.linalg.slogdet(P[np.ix_(child_interior, child_interior)])[1])
        if child_interior
        else 0.0
    )
    factorized_logdet = formation_logdet + child_logdet + math.log(schur_sum)

    epsilon = 1.0e-6
    plus = assemble_ae2_one_seam_descriptor(
        formation_log_radii=xf,
        formation_proper_durations=hf,
        child_log_radii=xc,
        child_proper_durations=hc,
        channel="scalar",
        unit_channel_value=unit_value,
        seam_contact=contact + epsilon,
    )
    minus = assemble_ae2_one_seam_descriptor(
        formation_log_radii=xf,
        formation_proper_durations=hf,
        child_log_radii=xc,
        child_proper_durations=hc,
        channel="scalar",
        unit_channel_value=unit_value,
        seam_contact=contact - epsilon,
    )
    plus_logdet = float(np.linalg.slogdet(plus["K"] + shift * plus["M"])[1])
    minus_logdet = float(np.linalg.slogdet(minus["K"] + shift * minus["M"])[1])
    centered_contact_derivative = (plus_logdet - minus_logdet) / (2.0 * epsilon)
    analytic_contact_derivative = 1.0 / schur_sum
    return {
        "formation_segments": int(hf.size),
        "child_segments": int(hc.size),
        "direct_dimension": int(P.shape[0]),
        "expected_dimension": int(hf.size + hc.size - 1),
        "internal_seam_trace_count": descriptor["internal_seam_trace_count"],
        "matrix_positive": bool(sign > 0 and np.linalg.eigvalsh(P)[0] > 0.0),
        "M_f": M_f,
        "transported_M_C2": M_c,
        "W_phys": contact,
        "direct_seam_schur": direct_schur,
        "factorized_seam_sum": schur_sum,
        "seam_sum_absolute_residual": abs(direct_schur - schur_sum),
        "direct_logdet": direct_logdet,
        "factorized_logdet": factorized_logdet,
        "logdet_absolute_residual": abs(direct_logdet - factorized_logdet),
        "analytic_contact_logdet_derivative": analytic_contact_derivative,
        "centered_contact_logdet_derivative": centered_contact_derivative,
        "contact_derivative_absolute_residual": abs(
            analytic_contact_derivative - centered_contact_derivative
        ),
        "explicit_matrix_inverse_formed": descriptor["explicit_matrix_inverse_formed"],
    }


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing one-seam inputs: " + ", ".join(missing))
    source_role, ontology, compact, child = map(_load, INPUTS[:4])
    if not all(record.get("validation_passed") is True for record in (
        source_role, ontology, compact, child
    )):
        raise RuntimeError("validated one-seam parents required")
    witness = _witness()
    validation = {
        "only_external_birth_trace_is_zero": (
            source_role["source_ordering"]["zero_source_restriction"]
            == "j_birth=0_EQUIVALENT_TO_Gamma0_birth(U)=0"
        ),
        "M_f_remains_internal_M11": (
            source_role["adjudication"]["M_f_equals_M11_at_zero_external_birth_trace"]
            == "REAFFIRMED"
        ),
        "one_internal_E1_C2_seam": (
            source_role["adjudication"]["complete_internal_seam_topology"]
            == "CLOSED_ONE_E1_C2_SEAM"
        ),
        "no_pre_E0_arm": source_role["adjudication"]["M_E0_required"] is False,
        "compact_action_operator_available": (
            compact["claim_boundary"]["K_and_D_xi_K"] == "DERIVED"
        ),
        "C2_finite_core_coefficients_available": (
            child["adjudication"]["finite_core_force_net"] == "EXTENDED_TO_1222"
        ),
        "direct_dimension_counts_seam_once": (
            witness["direct_dimension"] == witness["expected_dimension"]
            and witness["internal_seam_trace_count"] == 1
        ),
        "direct_shifted_form_is_positive": witness["matrix_positive"],
        "direct_and_Schur_seam_values_agree": (
            witness["seam_sum_absolute_residual"] < 1.0e-12
        ),
        "direct_and_factorized_determinants_agree": (
            witness["logdet_absolute_residual"] < 1.0e-12
        ),
        "contact_is_differentiated_once": (
            witness["contact_derivative_absolute_residual"] < 1.0e-8
        ),
        "no_explicit_matrix_inverse": witness["explicit_matrix_inverse_formed"] is False,
        "no_selector_source_scale_recurrence_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_AE2_ONE_SEAM_DIRECT_DESCRIPTOR",
        "status": (
            "ONE_SEAM_DIRECT_DESCRIPTOR_AND_SCHUR_EQUIVALENCE_DERIVED"
            if passed else "ONE_SEAM_DIRECT_DESCRIPTOR_VALIDATION_FAILED"
        ),
        "classification": (
            "THE_EXTERNAL_E0_DIRICHLET_TRACE_AND_FAR_C2_FRIEDRICHS_CORE_TRACE_"
            "LEAVE_ONE_INTERNAL_E1_C2_NODE;_DIRECT_ACTION_FORM_ASSEMBLY_IS_"
            "EXACTLY_EQUIVALENT_TO_M_f_PLUS_U_R_DAGGER_M_C2_U_R_PLUS_W_phys_"
            "AND_EXPOSES_THE_COEFFICIENT_JETS_WITHOUT_A_KINETIC_OR_DIRAC_INVERSE"
        ),
        "action_version": "BHSM-AE-2.0.0",
        "operator": {
            "external_birth": "E0_DIRICHLET_Gamma0_birth=0",
            "internal_seam": "ONE_COMMON_E1_C2_TRACE",
            "far_core": "C2_FRIEDRICHS_FORM_CORE_DIRICHLET_NOT_A_PHYSICAL_ENDPOINT",
            "direct_form": "P_joint=P_formation_GLUED_AT_E1_P_C2+W_phys|E1",
            "Schur_equivalent": "S_AE2=M_f+U_R^dagger*M_C2*U_R+W_phys",
            "route_exclusivity": "USE_DIRECT_OR_SCHUR_REPRESENTATION_NOT_BOTH",
            "per_level_generation": (
                "INSERT_THE_RETAINED_SCALAR_OR_FACTORIZED_DIRAC_UNIT_S3_"
                "EIGENVALUE_BEFORE_APPLYING_THE_FIXED_GRADING_WEIGHT"
            ),
            "first_jet": "ELEMENTWISE_D_x_mid_K_D_h_K_D_h_M_PLUS_ONE_D_W_phys",
        },
        "matching_audit": {
            "external_birth_trace": "VALID_MATCH_DIRICHLET_REFERENCE",
            "incoming_M_f": "VALID_INTERNAL_SCHUR_BLOCK_M11_NOT_ZEROED",
            "transported_M_C2": "VALID_INTERNAL_CHILD_SCHUR_BLOCK",
            "W_phys_and_contacts": "VALID_INTERNAL_SEAM_FORM_COUNTED_ONCE",
            "M_E0": "NOT_A_CURRENT_GATE7_SLOT",
            "B_birth": "NOT_A_CURRENT_GATE7_SLOT",
            "finite_core_joint_operator_type": "CLOSED_DIRECTLY",
            "finite_core_joint_first_jet_type": "CLOSED_DIRECTLY",
            "actual_incoming_parameter_member": "OPEN_NO_MEMBER_SELECTED",
            "maximal_C2_tail": "OPEN",
            "actual_graded_cotangent_value": "OPEN",
        },
        "witness": witness,
        "exact_next_dependency": (
            "INTERVAL_ASSEMBLE_THE_DIRECT_ONE_SEAM_DESCRIPTOR_ON_THE_RETAINED_"
            "INCOMING_AMPLITUDE_FAMILY_AND_C2_PARAMETRIC_FAMILY,_APPLY_THE_"
            "GRADED_HEAT_MINUS_ZETA_COTANGENT_ONCE,_AND_PROVE_THE_PROJECTED_"
            "MAXIMAL_CAUCHY_TAIL_OR_CERTIFY_A_LATER_EVENT_OR_CANONICAL_STOP"
        ),
        "claim_boundary": {
            "finite_core_joint_operator_type": "DERIVED_EXECUTABLE",
            "finite_core_joint_first_jet_type": "DERIVED_EXECUTABLE",
            "actual_joint_graded_value": "OPEN",
            "maximal_projected_tail": "OPEN",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": passed,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not payload["validation_passed"]:
        raise RuntimeError("one-seam descriptor validation failed")
    print(RESULT)


if __name__ == "__main__":
    main()
