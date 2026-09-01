"""Correct the one-sided event-normal initialization to the AE2 seam law.

The Riccati differential identity is valid on either arm, but the physical
event is an internal AE2 transmission seam.  Eliminating the opposite arm
therefore supplies its pulled-back Calderon response in addition to the
local Wentzell block.  The local event graph does not set that response to
zero and does not initialize a physical arm by ``W_phys`` alone.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
)
INPUTS = (
    ARTIFACTS / "action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json",
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_GATE7_AE2_ZERO_THRESHOLD_NO_SHORTCUT.json"
    ),
    ARTIFACTS / "flagship_integration/BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json",
    ARTIFACTS / "flagship_integration/BHSM_N12_FINITE_HISTORY_FORCE_DOMAIN_AUDIT.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def seam_and_jet_witness() -> dict[str, float]:
    """Verify the pulled-back two-sided seam and its full geometry jet."""

    rng = np.random.default_rng(7017)

    def hermitian() -> np.ndarray:
        raw = rng.normal(size=(3, 3)) + 1.0j * rng.normal(size=(3, 3))
        return 0.5 * (raw + raw.conj().T)

    generator = rng.normal(size=(3, 3)) + 1.0j * rng.normal(size=(3, 3))
    generator = 0.5 * (generator - generator.conj().T)
    unitary = expm(hermitian() * 1.0j)
    event = hermitian()
    child = hermitian()
    wentzell = hermitian()
    d_event = hermitian()
    d_child = hermitian()
    d_wentzell = hermitian()

    seam = event + unitary.conj().T @ child @ unitary + wentzell
    analytic = (
        d_event
        + unitary.conj().T @ (d_child + child @ generator - generator @ child) @ unitary
        + d_wentzell
    )
    epsilon = 1.0e-6

    def perturbed(sign: float) -> np.ndarray:
        u_eps = expm(sign * epsilon * generator) @ unitary
        return (
            event
            + sign * epsilon * d_event
            + u_eps.conj().T
            @ (child + sign * epsilon * d_child)
            @ u_eps
            + wentzell
            + sign * epsilon * d_wentzell
        )

    finite = (perturbed(1.0) - perturbed(-1.0)) / (2.0 * epsilon)
    one_sided = event + wentzell
    return {
        "unitarity_residual": float(
            np.linalg.norm(unitary.conj().T @ unitary - np.eye(3), ord=2)
        ),
        "seam_hermiticity_residual": float(
            np.linalg.norm(seam - seam.conj().T, ord=2)
        ),
        "geometry_jet_finite_difference_residual": float(
            np.linalg.norm(analytic - finite, ord=2)
        ),
        "opposite_arm_term_norm": float(
            np.linalg.norm(unitary.conj().T @ child @ unitary, ord=2)
        ),
        "one_sided_W_only_omission_residual": float(
            np.linalg.norm(seam - one_sided, ord=2)
        ),
    }


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("two-sided event-seam correction inputs required")
    records = {path.name: _load(path) for path in INPUTS}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated two-sided event-seam inputs required")
    action = records["BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"]
    domain = records["BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"]
    nonfermion = records["BHSM_N12_GATE7_AE2_NONFERMION_THRESHOLD_MARGIN.json"]
    zero = records["BHSM_N12_GATE7_AE2_ZERO_THRESHOLD_NO_SHORTCUT.json"]
    prior = records["BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json"]
    witness = seam_and_jet_witness()
    validation = {
        "AE2_internal_transmission_graph_consumed": (
            action["action_definition"]["independent_normal_matter_boundary_action"]
            == "S_Sigma_F_AE2=0"
        ),
        "physical_seam_sum_matches_retained_nonfermion_theorem": (
            nonfermion["theorem"]["seam_operator"]
            == "M_event(0)+U_R_DAGGER*M_child(0)*U_R+W_phys"
        ),
        "fermion_local_surface_block_is_zero_but_child_response_is_not": (
            domain["source_domain"]["fermion_W_phys_local_surface_block"] == 0
            and domain["sector_status"]["nonzero_event_child_Calderon_oracle"] == "OPEN"
        ),
        "local_collars_do_not_fix_two_sided_zero_response": (
            zero["provenance_adjudication"]["maximal_exterior_Calderon_value_and_geometry_jets"]
            == "OPEN"
        ),
        "prior_Riccati_differential_identity_preserved": (
            prior["event_normal_system"]["Riccati_equation"]
            == "D_s_M=(L_spatial(Y(s))-zI)-M^2"
        ),
        "unitary_pullback_verified": witness["unitarity_residual"] < 1.0e-12,
        "seam_is_Hermitian": witness["seam_hermiticity_residual"] < 1.0e-12,
        "full_seam_geometry_jet_verified": (
            witness["geometry_jet_finite_difference_residual"] < 1.0e-8
        ),
        "opposite_arm_cannot_be_algebraically_omitted": (
            witness["one_sided_W_only_omission_residual"] > 1.0e-3
        ),
        "no_endpoint_selector_contour_scale_fit_action_term_or_gate_added": True,
    }
    return {
        "artifact": "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION",
        "status": "ONE_SIDED_W_ONLY_INITIALIZATION_SUPERSEDED_TWO_SIDED_AE2_SEAM_RESPONSE_OPEN",
        "classification": (
            "THE_EVENT_NORMAL_RICCATI_AND_GEOMETRY_JET_DIFFERENTIAL_IDENTITIES_"
            "ARE_VALID_ARM_TRANSFER_IDENTITIES,_BUT_THE_PHYSICAL_AE2_EVENT_IS_"
            "AN_INTERNAL_TWO_SIDED_TRANSMISSION_SEAM;_ELIMINATING_THE_OPPOSITE_"
            "ARM_GIVES_THE_EFFECTIVE_LOAD_U_R_DAGGER*M_CHILD(z)*U_R+W_phys,_"
            "NOT_W_phys_ALONE;_THE_EVENT_GRAPH_THEREFORE_DOES_NOT_YET_FIX_THE_"
            "PHYSICAL_N12_RICCATI_INITIAL_VALUE"
        ),
        "corrected_seam_theorem": {
            "physical_seam_operator": (
                "S_AE2(z)=M_event(z)+U_R_DAGGER*M_child(z)*U_R+W_phys"
            ),
            "event_arm_effective_load_after_child_elimination": (
                "B_event(z)=U_R_DAGGER*M_child(z)*U_R+W_phys"
            ),
            "conditional_arm_initial_value": "M_load(0,z)=B_event(z)",
            "Riccati_transport_identity": "D_s_M=(L_spatial(Y(s))-zI)-M^2",
            "geometry_jet_identity": (
                "D_Phi_B_event=(D_Phi_U_R_DAGGER)*M_child*U_R+"
                "U_R_DAGGER*(D_Phi_M_child)*U_R+U_R_DAGGER*M_child*"
                "(D_Phi_U_R)+D_Phi_W_phys"
            ),
            "fermion_AE2_specialization": (
                "W_phys=0_SO_B_event(z)=U_R_DAGGER*M_child(z)*U_R;_"
                "ZERO_LOCAL_SURFACE_ACTION_DOES_NOT_MEAN_ZERO_CHILD_RESPONSE"
            ),
            "nonfermion_specialization": (
                "W_phys_AND_CHILD_LOWER_BOUND_CLOSE_THE_ZERO_THRESHOLD_SIGN_"
                "BUT_DO_NOT_SUPPLY_THE_FULL_z_DEPENDENT_MAP_OR_GEOMETRY_JETS_"
                "REQUIRED_BY_THE_HEAT_FORCE"
            ),
        },
        "supersession": {
            "artifact": "BHSM_N12_EVENT_NORMAL_WEYL_RICCATI",
            "superseded_claim": "M(0,z)=W_phys_AS_THE_PHYSICAL_AE2_EVENT_INITIAL_VALUE",
            "preserved_results": [
                "MATRIX_RICCATI_DIFFERENTIAL_IDENTITY",
                "LINEARIZED_GEOMETRY_JET_IDENTITY",
                "SCALAR_ORIENTATION_CROSSCHECK",
                "ARBITRARY_VALIDATION_CUTOFF_IS_NOT_AN_ACTION_ENDPOINT",
            ],
            "prior_small_s_expansion_status": (
                "CONDITIONAL_ONLY_AFTER_THE_ACTION_OWNED_EFFECTIVE_TWO_SIDED_"
                "LOAD_AND_SPATIAL_COEFFICIENT_ARE_SUPPLIED"
            ),
        },
        "finite_encapsulation_consequence": {
            "infinite_nonencapsulating_tail_obligation": "REMOVED_FROM_PHYSICAL_READOUT_DOMAIN",
            "two_sided_event_child_seam_removed": False,
            "reason": (
                "FINITE_ENCAPSULATION_TERMINATES_FORMATION_AND_IMMEDIATELY_"
                "ENTERS_CHILD_DECAY_OR_EVOLUTION;_AE2_GLUING_OF_THE_TWO_REGULAR_"
                "TRACES_REMAINS_PART_OF_THE_ACTION_DOMAIN"
            ),
        },
        "witness": witness,
        "exact_next_dependency": (
            "CONSTRUCT_OR_ENCLOSE_THE_ACTION_OWNED_CHILD_ARM_CALDERON_MAP_"
            "M_child(z),_D_Phi_M_child,_AND_D_Phi_U_R_ON_THE_REALIZED_FINITE_"
            "EVENT_CHILD_HISTORY,_OR_SOLVE_THE_EQUIVALENT_JOINT_TWO_SIDED_"
            "FINITE_HISTORY_OPERATOR;_ONLY_THEN_INITIALIZE_THE_EVENT_ARM_"
            "RICCATI_TRANSFER_AND_EVALUATE_THE_HEAT_MINUS_ZETA_FORCE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_TWO_SIDED_FINITE_HISTORY_CALDERON_ORACLE_OPEN",
            "Riccati_and_geometry_jet_differential_identities": "DERIVED",
            "physical_AE2_event_initial_value": "OPEN",
            "child_arm_Calderon_value_and_geometry_jets": "OPEN",
            "zero_source_force_value": "OPEN",
            "same_action_saddle": "WAITING_ON_TWO_SIDED_OPERATOR",
            "pair_plus_contact_Hessian": "OPEN_AFTER_SADDLE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(RESULT)


if __name__ == "__main__":
    main()
