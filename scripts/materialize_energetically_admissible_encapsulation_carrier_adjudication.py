"""Materialize the energetic encapsulation-carrier adjudication."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae3_reciprocal_join_localization import regular_carrier_certificate
from bhsm.interface.energetically_admissible_encapsulation_carrier_adjudication import (
    ACTION_VERSION,
    CLASSIFICATION,
    adjudication_payload,
)


TARGET = (
    ROOT
    / "artifacts/action_extension"
    / "BHSM_ENERGETICALLY_ADMISSIBLE_ENCAPSULATION_CARRIER_ADJUDICATION.json"
)
INPUTS = (
    ROOT / "src/bhsm/interface/energetically_admissible_encapsulation_carrier_adjudication.py",
    ROOT / "scripts/materialize_energetically_admissible_encapsulation_carrier_adjudication.py",
    ROOT / "tests/test_energetically_admissible_encapsulation_carrier_adjudication.py",
    ROOT / "theory/bhsm_energetically_admissible_encapsulation_carrier_adjudication.md",
    ROOT / "src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py",
    ROOT / "src/bhsm/interface/envelopment/global_conservation.py",
    ROOT / "src/bhsm/interface/completion/local_environment_finite_time_encapsulation_gate_v14_94.py",
    ROOT / "src/bhsm/interface/energy_geometry_confinement_invariant.py",
    ROOT / "src/bhsm/interface/envelopment/proper_volume_depth_v10_4.py",
    ROOT / "src/bhsm/interface/envelopment/spacetime_removal_depth_v10_3.py",
    ROOT / "src/bhsm/interface/envelopment/depth_constraint_reduction_v10_4.py",
    ROOT / "src/bhsm/interface/envelopment/spacetime_support_order_parameter_v10_4.py",
    ROOT / "src/bhsm/interface/envelopment/canonical_crystallization_v11_0.py",
    ROOT / "src/bhsm/interface/ae3_reciprocal_join_localization.py",
    ROOT / "src/bhsm/interface/ae4_current_c2_physical_enclosure_state_integration.py",
    ROOT / "src/bhsm/interface/environment_conditioned_reset_selector_recovery.py",
    ROOT / "src/bhsm/interface/universal_decay_collision.py",
    ROOT / "src/bhsm/interface/universal_channel_ledger.py",
    ROOT / "theory/n12_constraint_reduced_energy_identity.md",
    ROOT / "artifacts/action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",
    ROOT / "artifacts/action_extension/BHSM_AE4_CURRENT_C2_PHYSICAL_ENCLOSURE_STATE_INTEGRATION.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json",
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    """Build a deterministic, source-hashed fail-closed certificate."""

    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    result = adjudication_payload()
    local = regular_carrier_certificate()
    boundary = result["claim_boundary"]
    validation = {
        "recovered_candidate_audit_has_nine_or_more_rows": len(result["recovered_candidates"]) >= 9,
        "available_energy_fails_closed": not result["available_event_energy"]["defined"],
        "envelopment_requirement_fails_closed": not result["envelopment_requirement"]["defined"],
        "no_ex_nihilo_firewall_is_explicit": (
            not result["conservation"]["reset_may_supply_missing_energy"]
        ),
        "rho5_is_preserved": result["rho"]["classification"] == "RHO5",
        "no_manual_Planck_threshold": not result["scale"]["manual_Planck_threshold_inserted"],
        "AE3_local_carrier_is_analytically_regular": (
            local["regular_level_set"] and abs(local["zero_coordinate"] - 0.7853981633974483) < 1.0e-15
        ),
        "AE3_local_carrier_scope_is_not_promoted": (
            not result["carrier_family"]["local_AE3_subsystem_carrier"]["terminal_reset_boundary"]
            and not boundary["FULL_EVENT_TO_CHILD_ENCAPSULATION_CARRIER_SELECTED"]
        ),
        "full_carrier_remains_CARR5": result["carrier_selection"]["full_classification"] == "CARR5",
        "saturation_is_not_assumed": not result["carrier_selection"]["saturation_derived"],
        "multiple_child_semantics_do_not_invent_dynamics": (
            not result["multiple_children"]["action_owned_branching_dynamics"]
        ),
        "boundary_operator_package_fails_closed": (
            result["boundary_operator_package"]["physical_Calderon_or_DtN_operators"]
            == "NOT_INSTANTIATED"
        ),
        "actual_stabilizer_and_projectors_fail_closed": (
            result["stabilizer_spectral_incidence"]["spectral_projectors"] == "OPEN"
        ),
        "RSP5_is_preserved": (
            result["response_and_active_differential"]["response_classification"] == "RSP5"
        ),
        "N12_new_rank_is_zero": result["n12_rank"]["actual_new_rank"] == 0,
        "N12_time_quotient_residual_is_66": result["n12_rank"]["residual_after_time_quotient"] == 66,
        "response_function_not_selected": not boundary["ENCAPSULATION_RESPONSE_FUNCTION_SELECTED"],
        "frozen_predictions_untouched": not boundary["FROZEN_PREDICTIONS_MODIFIED"],
        "Gate7_not_promoted": not boundary["GATE7_PROMOTED"],
        "full_BHSM_not_claimed": not boundary["FULL_BHSM_COMPLETE"],
    }
    return {
        "artifact": "BHSM_ENERGETICALLY_ADMISSIBLE_ENCAPSULATION_CARRIER_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "scientific_result": (
            "AE3_SIGMA_ZERO_IS_A_UNIQUE_ACTION_OWNED_LOCAL_MATERIAL_CARRIER,_"
            "BUT_THE_FULL_EVENT_TO_CHILD_ENERGETIC_CARRIER_REMAINS_CARR5_BECAUSE_"
            "THE_BOUNDARY_IMPROVED_AVAILABLE_AND_ENVELOPMENT_CHARGES_AND_FULL_FIELD_"
            "DOMAINS_ARE_NOT_INSTANTIATED"
        ),
        "adjudication": result,
        "AE3_local_regular_carrier_certificate": local,
        "validation": validation,
        "validation_passed": all(validation.values()),
        "provenance": {
            "RECOVERED_PRIOR_BHSM": [
                "Noether/stress and boundary-flux conservation",
                "conditional Brown-York/Hamiltonian charges",
                "support/depth and scale candidates",
                "AE3 sigma-zero local material carrier",
                "AE4 first-future impedance/core crossing architecture",
                "generic decay-channel readout machinery",
            ],
            "OWNER_CLARIFICATION": (
                "event mode geometry/amplitude plus local support and scale, subject "
                "to no ex-nihilo energy and separate ledgers for independent children"
            ),
            "NEWLY_DERIVED": (
                "scoped CARR1-local/CARR5-full reconciliation, RHO5 persistence, "
                "typed charge obstruction, conservation firewall, and rank-zero result"
            ),
        },
        "source_hashes_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
    }


def main() -> None:
    payload = build_payload()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
