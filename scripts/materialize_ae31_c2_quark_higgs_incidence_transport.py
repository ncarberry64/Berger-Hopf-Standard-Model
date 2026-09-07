"""Materialize the current-C2 quark--Higgs incidence support transport."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_higgs_incidence_transport import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    current_c2_domain_tensor_theorem,
    exact_remaining_owner,
    finite_sector_projectors,
    quark_higgs_support_pencil,
    two_to_four_component_transport,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT.json"
INPUTS = (
    ROOT / "theory/theorem_discharge_yukawa_operator_results.json",
    ROOT / "theory/theorem_discharge_higgs_scalar_results.json",
    ROOT / "docs/bhsm_sector_projector_ledger_theorem.md",
    A / "BHSM_AE31_C2_QUARK_VERTEX_CONTACT_PROJECTION.json",
    A / "BHSM_AE3_C2_QUARK_RESPONSE_SUM_RULES.json",
    A / "BHSM_AE31_C2_QUARK_PARENT_THIRD_VARIATION.json",
    ROOT / "src/bhsm/interface/ae31_c2_quark_higgs_incidence_transport.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    yukawa, scalar, _, projection, response, parent = (
        _load(INPUTS[0]),
        _load(INPUTS[1]),
        INPUTS[2].read_text(encoding="utf-8"),
        _load(INPUTS[3]),
        _load(INPUTS[4]),
        _load(INPUTS[5]),
    )
    convention = two_to_four_component_transport()
    projectors = finite_sector_projectors()
    support = quark_higgs_support_pencil()
    domain = current_c2_domain_tensor_theorem()
    remaining = exact_remaining_owner()
    boundary = claim_boundary()
    historical = yukawa["allowed_operator_classes"]
    validation = {
        "historical_quark_operator_classes_reused": (
            historical["cyclic_upper_closure"]["fields"]
            == ["A_cyc", "H", "S_cyc_upper"]
            and historical["cyclic_lower_closure"]["fields"]
            == ["A_cyc", "H_tilde", "S_cyc_lower"]
            and yukawa["summary"]["exactly_four_renormalizable_yukawa_classes"]
        ),
        "historical_scalar_and_conjugate_reused": (
            scalar["summary"]["active_orientation_fundamental"]
            and scalar["summary"]["Y"] == "1"
            and scalar["scalar_representation"]["conjugate"]["Y"] == "-1"
        ),
        "two_to_four_component_bridge_closes_both_charges": (
            convention["both_quark_classes_transport_uniquely"]
            and not convention["standard_model_operator_table_used_as_premise"]
        ),
        "existing_projectors_select_disjoint_complete_support": (
            projectors["quark_projector_orthogonality_residual"] == 0.0
            and projectors["all_sector_orthogonality_residual"] == 0.0
            and projectors["sector_completeness_residual"] == 0.0
            and projectors["up_down_support_selected"]
            and not projectors["up_down_residue_selected"]
        ),
        "binary_incidence_supports_independent": (
            support["supports_linearly_independent"]
            and support["support_inner_product"] == 0.0
            and support["up_support_rank"] == support["down_support_rank"] == 2
        ),
        "finite_incidence_preserves_current_C2_domain": (
            domain["sample_commutator_residual"] == 0.0
            and domain["finite_internal_support_is_bounded"]
            and domain["reset_generated_C2_radial_operator_unchanged"]
            and domain["retained_birth_trace_unchanged"]
            and not domain["maximal_or_friedrichs_radial_domain_reselected"]
        ),
        "family_shapes_reused_not_rebuilt": (
            response["claim_boundary"]["CURRENT_C2_UP_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED"]
            and response["claim_boundary"]["CURRENT_C2_DOWN_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED"]
            and not boundary["particle_spectrum_rebuilt"]
        ),
        "prior_missing_map_narrowed_to_coefficients_and_contacts": (
            projection["exact_missing_incidence_map"]["required_map"].startswith(
                "rho_qH_current_C2"
            )
            and remaining["transported_object"].startswith("rho_qH_support")
            and parent["claim_boundary"]["CURRENT_C2_UP_DOWN_YUKAWA_OPERATORS_ACTION_OWNED"]
            is False
        ),
        "no_coefficient_pole_CKM_or_completion_overclaim": (
            not boundary["CURRENT_C2_UP_DOWN_YUKAWA_COEFFICIENTS_ACTION_DERIVED"]
            and not boundary["CURRENT_C2_QUARK_CONTACT_JET_ACTION_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["CKM_MATRIX_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "two_to_four_component_transport": convention,
        "finite_sector_projectors": projectors,
        "quark_higgs_support_pencil": support,
        "current_C2_domain_tensor_theorem": domain,
        "exact_remaining_owner": remaining,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 quark--Higgs incidence transport failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
