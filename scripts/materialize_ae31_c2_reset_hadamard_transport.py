"""Materialize the AE3.1 reset transport of fermion Hadamard states."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_reset_hadamard_transport import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    finite_reset_transport_witness,
    reset_hadamard_transport_theorem,
)


A = ROOT / "artifacts/action_extension"
STATE = A / "BHSM_AE31_C2_FERMION_HADAMARD_STATE_CLASS.json"
RESET = A / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
GREEN = A / "BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN.json"
HOPF = A / "BHSM_AE3_C2_HOPF_SEMIGROUP_TRANSPORT.json"
TARGET = A / "BHSM_AE31_C2_RESET_HADAMARD_TRANSPORT.json"
INPUTS = (
    STATE,
    RESET,
    GREEN,
    HOPF,
    ROOT / "src/bhsm/interface/ae31_c2_reset_hadamard_transport.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    state, reset, green, hopf = map(_load, INPUTS[:4])
    theorem = reset_hadamard_transport_theorem()
    witness = finite_reset_transport_witness()
    boundary = claim_boundary()
    validation = {
        "same_AE31_state_class": (
            state["action_version"] == theorem["action_version"] == ACTION_VERSION
            and state["claim_boundary"][
                "FINITE_CORE_CURRENT_C2_HADAMARD_STATE_CLASS_NONEMPTY_FAMILYWISE"
            ]
        ),
        "AE2_reset_lift_unitary_and_maximal_isotropic": (
            reset["finite_certificate"]["transmission_graph"]["maximal_isotropic"]
            and reset["finite_certificate"]["unitarity_residual"] < 1.0e-12
            and theorem["reset_lift_unitary"]
        ),
        "same_reset_glued_chiral_domain": (
            green["claim_boundary"][
                "AE2_reset_glued_fermion_domain_current_and_unique_modulo_frame"
            ]
            and green["chiral_operator_assembly"][
                "maximal_isotropic_Green_trace_form_unchanged"
            ]
        ),
        "frozen_family_operator_already_attached": hopf["claim_boundary"][
            "frozen_internal_Hopf_response_operator_attached_to_current_C2"
        ],
        "finite_covariance_transport_passes": all(
            witness[key]
            for key in (
                "positivity_and_order_preserved",
                "self_dual_CAR_constraint_preserved",
                "purity_preserved",
                "transport_is_bijective",
            )
        ),
        "Hadamard_and_family_identity_transport_derived": (
            theorem["future_null_covectors_map_to_future_null_covectors"]
            and theorem["Hadamard_wavefront_and_polarization_preserved"]
            and theorem["commutes_with_frozen_family_projectors"]
            and boundary[
                "UPSTREAM_HADAMARD_PARTICLE_STATE_CARRIED_INTO_CURRENT_C2_ENCLOSURE"
            ]
        ),
        "transport_not_misreported_as_state_selection": (
            theorem["statement_is_conditional_on_an_upstream_state"]
            and not theorem["one_upstream_or_child_state_selected"]
            and not boundary["CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED"]
        ),
        "no_pole_particle_production_or_g_minus_2_overclaim": (
            not boundary["CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED"]
            and not boundary["BOGOLIUBOV_PARTICLE_PRODUCTION_DERIVED"]
            and not boundary["MUON_MAGNETIC_MOMENT_DERIVED"]
        ),
        "no_new_parameter_or_spectrum_rebuild": (
            not theorem["new_state_parameter_inserted"]
            and not boundary["particle_spectrum_rebuilt"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_RESET_HADAMARD_TRANSPORT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "reset_hadamard_transport_theorem": theorem,
        "finite_reset_transport_witness": witness,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 reset Hadamard transport failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
