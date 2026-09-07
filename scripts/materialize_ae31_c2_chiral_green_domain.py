"""Materialize the AE3.1 current-C2 chiral Green-domain theorem."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae31_c2_chiral_green_domain import (
    ACTION_VERSION,
    CLASSIFICATION,
    chiral_operator_assembly,
    claim_boundary,
    domain_provenance_reconciliation,
    family_reset_intertwiner_certificate,
    green_operator_feasibility,
)


A = ROOT / "artifacts"
AE2 = A / "action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
AE3 = A / "action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json"
AE31 = A / "action_extension/BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json"
DOMAIN = A / "flagship_integration/BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
READINESS = A / "BHSM_M4_first_order_fermionic_action_readiness_v6_1_3.json"
M4_GEOMETRY = A / "BHSM_round_equatorial_M4_geometry_v6_1_1.json"
C2_FAMILY = A / "flagship_integration/BHSM_N12_C2_1222_PARAMETRIC_BASE_FAMILY.json"
TARGET = A / "action_extension/BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN.json"
INPUTS = (
    AE2,
    AE3,
    AE31,
    DOMAIN,
    READINESS,
    M4_GEOMETRY,
    C2_FAMILY,
    ROOT / "src/bhsm/interface/ae31_c2_chiral_green_domain.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    ae2, ae3, ae31, domain, readiness, m4_geometry, c2_family = map(
        _load, INPUTS[:7]
    )
    reconciliation = domain_provenance_reconciliation()
    operator = chiral_operator_assembly()
    intertwiner = family_reset_intertwiner_certificate()
    feasibility = green_operator_feasibility()
    boundary = claim_boundary()
    validation = {
        "AE2_selected_one_global_reset_domain": (
            ae2["variation_theorem"]["self_adjointness"].startswith("THE_GRAPH")
            and ae2["action_definition"]["independent_Cayley_phase"] is None
        ),
        "prior_domain_no_go_explicitly_reconciled": (
            domain["prior_no_go_reconciliation"]["superseded_only_for_action_version"]
            == "BHSM-AE-2.0.0"
            and domain["validation"]["old_U1_times_U1_family_removed_from_AE2_domain"]
        ),
        "AE3_enclosure_is_smooth_internal_interface": (
            ae3["euler_lagrange_and_interface_variation"]["interpretation"]
            == "resolved_internal_material_level_set_not_a_terminal_boundary_or_reset_locus"
        ),
        "AE31_local_mass_operator_precedes_this_join": ae31["claim_boundary"][
            "conditional_tree_level_charged_lepton_mass_operator_derived"
        ],
        "historical_global_hyperbolicity_requirement_was_explicit": (
            readiness["self_adjoint_domain"] == "architecture available but not selected"
            and "globally hyperbolic" in readiness["conserved_inner_product"]
        ),
        "current_M4_is_closed_FLRW_with_positive_finite_core_radius": (
            m4_geometry["metric"] == "ds4^2=-dt^2+a(t)^2 ds^2_S3"
            and c2_family["finite_cover_witness"]["minimum_certified_R4"] > 0.0
            and c2_family["finite_cover_witness"]["proper_duration_interval"][0]
            > 0.0
        ),
        "first_order_chiral_block_assembled_on_preserved_domain": (
            operator["same_current_C2_first_order_LR_block_assembled"]
            and operator["domain_preserved_by_zero_order_mass_term"]
            and operator["Hermitian_zero_order_perturbation"]
        ),
        "family_mass_intertwines_reset_exactly": (
            intertwiner["mass_block_intertwines_AE2_reset"]
            and not intertwiner["new_Cayley_phase_introduced"]
        ),
        "causal_theorem_not_overpromoted": (
            feasibility["finite_core_global_hyperbolicity_derived_familywise"]
            and feasibility["advanced_retarded_Green_operator_existence_derived"]
            and not feasibility["physical_C2_history_member_selected"]
            and not feasibility["maximal_C2_Lorentzian_continuation_certified"]
            and not feasibility["retarded_Green_operator_constructed"]
            and not feasibility["Feynman_two_point_function_constructed"]
        ),
        "native_resolvent_type_preserved": (
            feasibility["proper_history_product_Dirac_resolvent_variable"] == "z"
            and not feasibility["proper_history_z_identified_with_p_squared"]
        ),
        "claim_boundary_is_fail_closed": (
            boundary["current_C2_first_order_charged_lepton_LR_operator_assembled"]
            and not boundary["global_current_C2_charged_lepton_Green_operator_derived"]
            and not boundary["muon_magnetic_moment_derived"]
        ),
    }
    return {
        "artifact": "BHSM_AE31_C2_CHIRAL_GREEN_DOMAIN",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "domain_provenance_reconciliation": reconciliation,
        "chiral_operator_assembly": operator,
        "family_reset_intertwiner_certificate": intertwiner,
        "green_operator_feasibility": feasibility,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE3.1 chiral Green-domain theorem failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
