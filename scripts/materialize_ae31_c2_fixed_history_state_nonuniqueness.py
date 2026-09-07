"""Materialize the fixed-history current-C2 fermion-state no-selector theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_fixed_history_state_nonuniqueness import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    finite_rank_hadamard_nonuniqueness_theorem,
    pure_self_dual_covariance,
    retained_selector_status,
)


A = ROOT / "artifacts/action_extension"
STATE = A / "BHSM_AE31_C2_FERMION_HADAMARD_STATE_CLASS.json"
RESET = A / "BHSM_AE31_C2_RESET_HADAMARD_TRANSPORT.json"
BOUNDARY = (
    ROOT
    / "artifacts/intrinsic_state_selection"
    / "BHSM_N12_CHILD_BOUNDARY_HAMILTONIAN_OWNERSHIP_GATE.json"
)
GATE7 = (
    ROOT
    / "artifacts/flagship_integration"
    / "BHSM_N12_GATE7_WITHIN_SEAM_CONSTRAINT_CENTER_OBSTRUCTION.json"
)
ASYMPTOTIC = (
    ROOT
    / "artifacts/flagship_integration"
    / "BHSM_N12_FULL_RETAINED_ASYMPTOTIC_BRANCH.json"
)
TARGET = A / "BHSM_AE31_C2_FIXED_HISTORY_STATE_NONUNIQUENESS.json"
INPUTS = (
    STATE,
    RESET,
    BOUNDARY,
    GATE7,
    ASYMPTOTIC,
    ROOT / "src/bhsm/interface/ae31_c2_fixed_history_state_nonuniqueness.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest().upper()


def _jsonable_witness(theta: float) -> dict[str, Any]:
    witness = pure_self_dual_covariance(theta)
    result: dict[str, Any] = {}
    for key, value in witness.items():
        if hasattr(value, "dtype") and value.dtype.kind == "c":
            result[f"{key}_real"] = value.real.tolist()
            result[f"{key}_imag"] = value.imag.tolist()
        else:
            result[key] = value.tolist() if hasattr(value, "tolist") else value
    return result


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    state, reset, boundary, gate7, asymptotic = map(_load, INPUTS[:5])
    theorem = finite_rank_hadamard_nonuniqueness_theorem()
    selector = retained_selector_status()
    witness = _jsonable_witness(0.37)
    boundary_claim = claim_boundary()
    tolerance = 1.0e-12
    validation = {
        "same_AE31_Hadamard_class_and_reset_transport": (
            state["action_version"] == reset["action_version"] == ACTION_VERSION
            and state["claim_boundary"][
                "FINITE_CORE_CURRENT_C2_HADAMARD_STATE_CLASS_NONEMPTY_FAMILYWISE"
            ]
            and reset["claim_boundary"][
                "AE2_RESET_HADAMARD_STATE_CLASS_TRANSPORT_DERIVED"
            ]
        ),
        "finite_pure_self_dual_witness_passes": (
            witness["frame_orthonormality_residual"] < tolerance
            and witness["Hermitian_residual"] < tolerance
            and witness["purity_residual"] < tolerance
            and witness["self_dual_CAR_residual"] < tolerance
            and witness["charge_commutator_residual"] < tolerance
            and witness["minimum_eigenvalue"] > -tolerance
            and witness["maximum_eigenvalue"] < 1.0 + tolerance
            and witness["distance_from_zero_covariance"] > 0.1
        ),
        "finite_rank_change_preserves_Hadamard_class": (
            theorem["P_theta_minus_P_is_finite_rank_smoothing"]
            and theorem["Hadamard_wavefront_and_polarization_unchanged"]
            and theorem["continuum_of_distinct_pure_Hadamard_covariances"]
        ),
        "family_and_reset_data_do_not_remove_freedom": (
            theorem["gauge_charge_grading_unchanged"]
            and
            theorem["family_projectors_unchanged"]
            and theorem["reset_transport_preserves_the_continuum"]
            and reset["reset_hadamard_transport_theorem"][
                "quasifree_state_class_transport_bijective"
            ]
        ),
        "current_Gate7_center_not_promoted": (
            gate7["claim_boundary"]["continuous_action_constrained_center"]
            == "OPEN"
            and not gate7["claim_boundary"][
                "nonlinear_72D_history_first_jet"
            ]
            == "CLOSED"
            and selector["stored_quarter_DOP853_center_is_physical_history"]
            is False
        ),
        "nonrealized_expanding_branch_not_used_as_vacuum": (
            asymptotic["adjudication"]["physical_status"]
            == "NONREALIZED_FORMATION_HISTORY_OWNER_AUTHORIZED"
            and asymptotic["adjudication"]["mathematical_infinite_branch_outcome"]
            == "H4_TO_H0_POSITIVE"
            and not selector["asymptotic_stationary_vacuum_condition_derived"]
        ),
        "boundary_Hamiltonian_not_fabricated": (
            not boundary["action_owned_inventory"]["complete_Q_xi_assembler"]
            and not boundary["action_owned_inventory"][
                "selected_child_boundary_ensemble"
            ]
            and boundary["reduced_action_consequence"][
                "canonical_Legendre_energy_on_child_constraint_set"
            ]
            == 0.0
            and not selector["complete_child_boundary_H_xi_executable"]
        ),
        "history_and_state_selection_separated": (
            not theorem["history_selection_alone_selects_a_state"]
            and not boundary_claim[
                "CURRENT_C2_HISTORY_SELECTION_ALONE_SUFFICIENT_FOR_STATE_SELECTION"
            ]
            and not boundary_claim["CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"]
        ),
        "no_parameter_spectrum_pole_or_g_minus_2_overclaim": (
            not boundary_claim["new_state_parameter_inserted"]
            and not boundary_claim["particle_spectrum_rebuilt"]
            and not boundary_claim["CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED"]
            and not boundary_claim["CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED"]
            and not boundary_claim["MUON_MAGNETIC_MOMENT_DERIVED"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_FIXED_HISTORY_STATE_NONUNIQUENESS",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "finite_rank_hadamard_nonuniqueness_theorem": theorem,
        "retained_selector_status": selector,
        "finite_pure_covariance_witness": witness,
        "claim_boundary": boundary_claim,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 fixed-history state nonuniqueness failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
