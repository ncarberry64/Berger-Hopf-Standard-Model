"""Materialize the FSC encapsulation constitutive adjudication artifact."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.fsc_encapsulation_constitutive_adjudication import (  # noqa: E402
    EFFECTIVE_MAP_CLASS,
    EM_CLASS,
    EXACT_NEXT_OBJECT,
    GEOMETRIC_CLASS,
    INTERFACE_CLASS,
    LOOP_CLASS,
    PREGEOMETRIC_CLASS,
    PRIMITIVE_CLASS,
    RSP_CLASS,
    SCALE_CLASS,
    VERSION,
    adjudication_payload,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_FSC_ENCAPSULATION_CONSTITUTIVE_ADJUDICATION.json"
)
INPUTS = (
    ROOT / "src/bhsm/interface/fsc_encapsulation_constitutive_adjudication.py",
    ROOT / "scripts/materialize_fsc_encapsulation_constitutive_adjudication.py",
    ROOT / "scripts/audit_fsc_encapsulation_constitutive_adjudication.py",
    ROOT / "tests/test_fsc_encapsulation_constitutive_adjudication.py",
    ROOT / "theory/bhsm_fsc_encapsulation_constitutive_adjudication.md",
    ROOT / "src/bhsm/interface/owner_authorized_encapsulation_interface_action.py",
    ROOT / "src/bhsm/interface/current_semantic_normalization.py",
    ROOT / "src/bhsm/interface/gauge_coupling_spectral_residue.py",
    ROOT / "src/bhsm/interface/gauge_coupling_quantum/action_attachment.py",
    ROOT / "src/bhsm/interface/gauge_coupling_quantum/sector_weight_source.py",
    ROOT / "src/bhsm/interface/gauge_coupling_quantum/registry_pattern.py",
    ROOT / "src/bhsm/interface/completion/v14_9_28_lineage_recovery_v14_29.py",
    ROOT / "src/bhsm/interface/completion/alpha_dynamic_band_p8_bridge_v14_79.py",
    ROOT / "src/bhsm/interface/triality_generation_scale_architecture.py",
    ROOT / "src/gauge_couplings.py",
    ROOT / "src/rg_matching.py",
    ROOT / "src/constants.py",
    ROOT / "theory/bhsm_full_recall_hindsight_recon_foresight.md",
)


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    result = adjudication_payload()
    lineage = result["lineage"]
    weights = {row["channel"]: row for row in result["channel_weights"]}
    variation = result["variation_rank_cycle"]
    closure = result["closure"]
    frozen = result["frozen_cross_check"]
    firewall = result["claim_firewall"]

    validation = {
        "owner_FSC_is_symbolic_P1_not_empirical_decimal": (
            result["primitive"]["classification"] == PRIMITIVE_CLASS == "FSC-P1"
            and not result["primitive"]["exact_numeric_value_selected"]
            and result["primitive"]["observed_value_role"] == "downstream comparison only"
        ),
        "all_lineage_authority_classes_are_explicit": (
            len(lineage) >= 12
            and all(row["classification"] in {"FSC-P3", "FSC-P2", "FSC-P1", "FSC-P0", "SUPERSEDED"} for row in lineage)
        ),
        "historical_Xi_conflict_and_fit_are_superseded": (
            next(row for row in lineage if row["id"] == "HISTORICAL_XI_COUPLING_MAP")["classification"] == "SUPERSEDED"
            and next(row for row in lineage if row["id"] == "HISTORICAL_LOW_ENERGY_DRESSING_FIT")["classification"] == "SUPERSEDED"
        ),
        "6pi2_identity_not_promoted_to_coupling": (
            "MATHEMATICAL_DENSITY_IDENTITY_ONLY" in next(row for row in lineage if row["id"] == "WEYL_3D_DENSITY")["disposition"]
            and "SUPERSEDES" in next(row for row in lineage if row["id"] == "GAUGE_INVARIANCE_6PI2_NO_GO")["disposition"]
        ),
        "minimum_channel_ledger_is_complete": (
            set(weights) == {
                "electromagnetic/U1-like", "weak", "strong/color", "scalar/topographic",
                "geometric/gravitational", "pregeometric/emergent",
            }
            and weights["scalar/topographic"]["classification"] == "W4"
            and weights["geometric/gravitational"]["classification"] == "W4"
            and weights["pregeometric/emergent"]["classification"] == "W4"
        ),
        "127_weights_not_promoted": (
            not result["weak_strong"]["weak"]["historical_127_promoted"]
            and not result["weak_strong"]["strong"]["historical_127_promoted"]
        ),
        "GEFF5_and_SCALE4_are_fail_closed": (
            result["effective_map"]["classification"] == EFFECTIVE_MAP_CLASS == "GEFF5"
            and not result["effective_map"]["linear_candidate_justified"]
            and result["scale_running"]["classification"] == SCALE_CLASS == "SCALE4"
            and not result["scale_running"]["interface_running_law_owned"]
        ),
        "all_twelve_density_families_audited_without_selection": (
            len(result["invariant_coefficients"]) == 12
            and all(not row["coefficient_selected"] for row in result["invariant_coefficients"])
        ),
        "FSC_IF5_factorization_does_not_fake_closure": (
            result["constitutive_closure"]["classification"] == INTERFACE_CLASS == "FSC-IF5"
            and not result["constitutive_closure"]["factorization_has_decision_power"]
        ),
        "EM_and_geometry_claims_are_bounded": (
            result["electromagnetic"]["classification"] == EM_CLASS == "EM-FSC3"
            and result["geometric_pregeometric"]["geometric_classification"] == GEOMETRIC_CLASS == "GEO-FSC3"
            and result["geometric_pregeometric"]["pregeometric_classification"] == PREGEOMETRIC_CLASS == "GEO-FSC4"
        ),
        "rho_and_perturbative_shortcuts_rejected": (
            not result["energy_spacetime_ratio"]["multiplication_derived"]
            and not result["energy_spacetime_ratio"]["rho_E/ST_defined_by_FSC"]
            and not result["perturbative_hierarchy"]["global_expansion_valid"]
            and result["perturbative_hierarchy"]["first_nonzero_allowed_order"] is None
        ),
        "rank_loop_and_RSP_are_unchanged": (
            variation["N12_rank_added"] == 0
            and variation["N12_residual_before_time_quotient"] == 67
            and variation["N12_residual_after_time_quotient"] == 66
            and variation["loop"] == LOOP_CLASS == "LOOP3"
            and variation["RSP"] == RSP_CLASS == "RSP5"
            and not variation["cycle_rerun"]
        ),
        "no_interface_object_fabricated": all(
            closure[key] is None
            for key in ("selected_S_enc", "selected_carrier", "selected_F_B", "selected_L_s", "selected_Delta_enc")
        ),
        "exact_next_object_and_no_owner_question": (
            closure["exact_next_object"] == EXACT_NEXT_OBJECT and closure["owner_question"] is None
        ),
        "frozen_and_claim_firewalls_hold": (
            not any(frozen.values()) and not any(firewall.values())
        ),
    }

    return {
        "artifact": "BHSM_FSC_ENCAPSULATION_CONSTITUTIVE_ADJUDICATION",
        "version": VERSION,
        "classification": {
            "primitive": PRIMITIVE_CLASS,
            "effective_map": EFFECTIVE_MAP_CLASS,
            "scale": SCALE_CLASS,
            "interface": INTERFACE_CLASS,
            "electromagnetic": EM_CLASS,
            "geometric": GEOMETRIC_CLASS,
            "pregeometric": PREGEOMETRIC_CLASS,
            "loop": LOOP_CLASS,
            "RSP": RSP_CLASS,
        },
        "scientific_result": result["primary_verdict"],
        "adjudication": result,
        "VALIDATED": [
            "alpha_FSC is an owner-authorized symbolic common reference unit",
            "canonical gauge normalization permits different FSC powers for kinetic and vertex objects",
            "v14.19 supplies a conditional relative trace weight while v14.20 blocks the 1:2:7 universal-coupling promotion",
            "FSC factorization alone leaves the ORD1 constitutive function class unchanged",
            "GEFF5, SCALE4, FSC-IF5, LOOP3, RSP5, and zero added N12 rank",
        ],
        "INVALIDATED": [
            "1/137 is an exact scale-independent BHSM action constant",
            "1/(6*pi^2), 1/(12*pi^2), or 1/(13*pi^2) is the current universal interface coupling",
            "alpha_FSC*W_r is uniquely justified for every channel",
            "FSC normalizes rho_E/ST or selects a geometric/pregeometric coupling",
            "factoring alpha_FSC from S_enc collapses IF5",
        ],
        "REDUNDANT": [
            "absorbing alpha_FSC into an otherwise arbitrary W_s",
            "recounting the owned GHY/Hayward coefficient as FSC interface strength",
            "using observed low-energy alpha to refit a historical dressing or interface coefficient",
        ],
        "OPEN": [
            EXACT_NEXT_OBJECT,
            "physical U1 projection and reference scale/scheme",
            "FSC powers and action-attached weights per interface invariant",
            "event-scale map and interface RG/dressing law",
            "physical carrier, F_B, L_s, S_enc, and Delta_enc",
        ],
        "validation": validation,
        "validation_passed": all(validation.values()),
        "source_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in INPUTS
        },
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        failed = [name for name, passed in payload["validation"].items() if not passed]
        raise RuntimeError("FSC adjudication validation failed: " + ", ".join(failed))
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(payload), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
