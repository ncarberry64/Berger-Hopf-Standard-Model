"""Materialize the current-C2 quark--Higgs contact closure."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_quark_higgs_contact_closure import (
    ACTION_VERSION,
    CLASSIFICATION,
    affine_first_order_contact_theorem,
    claim_boundary,
    determinant_hessian_reduction,
    exact_remaining_owner,
    squared_pencil_contact_closure,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE31_C2_QUARK_HIGGS_CONTACT_CLOSURE.json"
INPUTS = (
    A / "BHSM_AE31_C2_QUARK_HIGGS_INCIDENCE_TRANSPORT.json",
    A / "BHSM_AE31_C2_QUARK_VERTEX_CONTACT_PROJECTION.json",
    A / "BHSM_AE31_C2_QUARK_CHANNEL_SELECTOR_DOMAIN.json",
    A / "BHSM_AE3_C2_QUARK_RESPONSE_SUM_RULES.json",
    A / "BHSM_AE3_C2_FULL_FIELD_PUZZLE_ASSEMBLY.json",
    ROOT / "src/bhsm/interface/ae31_c2_quark_higgs_contact_closure.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    incidence, projection, selector, response, puzzle = map(_load, INPUTS[:5])
    shapes = response["attached_frozen_internal_operator_witness"]["comparison"]
    first_order = affine_first_order_contact_theorem()
    squared = squared_pencil_contact_closure(
        up_shape=shapes["up"]["attached_ratios_to_heavy"],
        down_shape=shapes["down"]["attached_ratios_to_heavy"],
        c_up=1.7,
        c_down=0.6,
    )
    determinant = determinant_hessian_reduction()
    remaining = exact_remaining_owner()
    boundary = claim_boundary()
    validation = {
        "incidence_support_and_affine_operator_reused": (
            incidence["claim_boundary"][
                "CURRENT_C2_QUARK_HIGGS_INCIDENCE_SUPPORT_TRANSPORTED_CONDITIONAL"
            ]
            and incidence["quark_higgs_support_pencil"][
                "coefficients_in_support_pencil"
            ]
            == "BINARY_INCIDENCE_ONLY"
            and first_order["first_order_contact_jet_zero"]
        ),
        "first_order_contact_zero_without_higher_dimension_term": (
            all(value == "0" for value in first_order["second_variations"].values())
            and not first_order["higher_dimension_scalar_fermion_contact_inserted"]
        ),
        "squared_contact_fixed_by_vertices": (
            squared["Q_up_up_residual"] == 0.0
            and squared["Q_down_down_residual"] == 0.0
            and squared["mixed_contact_zero_by_disjoint_support"]
            and squared["diagonal_contacts_positive_semidefinite"]
            and squared["contact_jet_fixed_once_vertices_are_fixed"]
            and squared["independent_contact_coefficient_count"] == 0
        ),
        "retained_product_Dirac_contact_scaling_reconciled": (
            projection["unit_probe_scaling_theorem"]["contact_scaling"]
            == "Q(q)=q^2*Q(1)"
            and puzzle["operator_piece"]["second_contact_derivative"]
            == "Q_e=2*p_e^2*M_e"
            and squared["diagonal_contact_identity"] == "Q_ff=2*V_f^dagger*V_f"
        ),
        "selector_formula_keeps_state_dependence": (
            selector["quantum_selector_contract"]["G_C"]
            == "STATE_DEPENDENT_CURRENT_C2_FEYNMAN_INVERSE"
            and not selector["quantum_selector_contract"][
                "current_C2_action_selected_Feynman_inverse_present"
            ]
            and determinant["state_covariance_or_Feynman_inverse_still_required"]
        ),
        "family_shapes_reused_without_spectrum_rebuild": (
            response["claim_boundary"]["CURRENT_C2_QUARK_RESPONSE_IDENTITIES_HOLD_FOR_ALL_POSITIVE_SQUASHING"]
            and not boundary["particle_spectrum_rebuilt"]
        ),
        "remaining_owner_reduced_to_first_vertex_residues": (
            remaining["independent_missing_vertex_residues"] == ["c_u", "c_d"]
            and remaining["independent_missing_contact_coefficients"] == []
            and not remaining["independent_yukawa_contact_or_mass_fit_allowed"]
        ),
        "no_vertex_quantum_pole_CKM_or_completion_overclaim": (
            not boundary["CURRENT_C2_UP_DOWN_YUKAWA_VERTEX_RESIDUES_ACTION_DERIVED"]
            and not boundary["CURRENT_C2_QUARK_QUANTUM_HESSIAN_DERIVED"]
            and not boundary["CURRENT_C2_PHYSICAL_QUARK_POLES_DERIVED"]
            and not boundary["CKM_MATRIX_DERIVED"]
            and not boundary["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_QUARK_HIGGS_CONTACT_CLOSURE",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "affine_first_order_contact_theorem": first_order,
        "squared_pencil_contact_closure": squared,
        "determinant_hessian_reduction": determinant,
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
        raise SystemExit("AE3.1 quark--Higgs contact closure failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
