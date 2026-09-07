"""Materialize the retained GFHS boundary-variation adjudication."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from bhsm.interface.nonfermion_relative_boundary_variation import (
    ACTION_VERSION,
    CLASSIFICATION,
    EXACT_MISSING_DATUM,
    STATUS,
    ae4_reset_gluing_status,
    brst_graph_compatibility_witness,
    canonical_boundary_variables,
    claim_boundary,
    event_balance_decomposition,
    full_field_child_inheritance_status,
    higher_graph_jet_dependency,
    hs_boundary_variation_witness,
    moving_domain_hessian_witness,
    radial_maxwell_green_identity_witness,
    two_background_boundary_witness,
    variational_selection_witness,
)


TARGET = ROOT / (
    "artifacts/action_extension/"
    "BHSM_NONFERMION_RELATIVE_BOUNDARY_VARIATION.json"
)
SCRIPT = Path(__file__).resolve()
MODULE = ROOT / "src/bhsm/interface/nonfermion_relative_boundary_variation.py"
THEORY = ROOT / "theory/bhsm_nonfermion_relative_boundary_variation.md"
TEST = ROOT / "tests/test_nonfermion_relative_boundary_variation.py"


def _sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json", ".toml", ".yaml", ".yml"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.ndarray):
        return _canonical(value.tolist())
    if isinstance(value, np.complexfloating):
        value = complex(value)
    if isinstance(value, complex):
        if not (math.isfinite(value.real) and math.isfinite(value.imag)):
            raise ValueError("non-finite artifact value")
        return {
            "real": _canonical(value.real),
            "imag": _canonical(value.imag),
        }
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite artifact value")
        rounded = round(value, 12)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, Mapping):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"


def build_payload() -> dict[str, Any]:
    variables = canonical_boundary_variables()
    green = radial_maxwell_green_identity_witness()
    selection = variational_selection_witness()
    brst = brst_graph_compatibility_witness()
    hs = hs_boundary_variation_witness()
    hessian = moving_domain_hessian_witness()
    backgrounds = two_background_boundary_witness()
    higher = higher_graph_jet_dependency()
    gluing = ae4_reset_gluing_status()
    inheritance = full_field_child_inheritance_status()
    balance = event_balance_decomposition()
    claims = claim_boundary()
    sources = (
        "src/bhsm/interface/ae3_c2_lorentzian_gauge_ghost_hessian.py",
        "src/bhsm/interface/ae31_c2_gauge_composite_hs_action.py",
        "src/bhsm/interface/ae32_c2_einstein_cartan_lr_action.py",
        "src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py",
        "src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py",
        "src/bhsm/interface/background_covariant_gfhs_operator_family.py",
        str(MODULE.relative_to(ROOT)).replace("\\", "/"),
        str(SCRIPT.relative_to(ROOT)).replace("\\", "/"),
        str(THEORY.relative_to(ROOT)).replace("\\", "/"),
        str(TEST.relative_to(ROOT)).replace("\\", "/"),
    )
    hashes = {
        source: _sha256(ROOT / source)
        for source in sorted(sources)
        if (ROOT / source).is_file()
    }
    validation = {
        "Maxwell_boundary_Green_identity_exact": green[
            "green_identity_residual"
        ]
        < 1.0e-12,
        "stored_response_tables_not_used": not green["stored_response_table_used"],
        "zero_field_graph_shared_but_first_jets_distinct": (
            selection["same_zero_field_graph"]
            and selection["different_first_field_jets"]
        ),
        "both_candidates_pass_retained_vertical_variation": selection[
            "all_fixed_field_vertical_variations_cancel"
        ],
        "bulk_variation_does_not_fake_uniqueness": (
            not selection["retained_bulk_variation_selects_unique_jet"]
            and not selection["competing_nonuniqueness_witness_rejected"]
        ),
        "BRST_relates_but_does_not_select_jets": (
            brst["both_nonuniqueness_witnesses_BRST_compatible"]
            and not brst["BRST_selects_common_jet_value"]
        ),
        "antighost_jet_not_independent": not brst[
            "independent_antighost_jet_required"
        ],
        "HS_normal_Legendre_map_rank_zero": (
            hs["normal_Legendre_rank"] == 0
            and hs["all_HS_graph_jets_invisible_to_retained_bulk_boundary_variation"]
        ),
        "moving_domain_Hessian_nonuniqueness_exact": (
            hessian["both_moving_domain_Hessians_internally_consistent"]
            and hessian["Hessians_distinct"]
            and not hessian["second_variation_selects_unique_jet"]
        ),
        "two_background_dependence_does_not_select_graph": (
            backgrounds["bulk_background_dependence_nontrivial"]
            and not backgrounds["background_dependence_selects_graph_jet"]
        ),
        "higher_graph_jet_dependency_derived": (
            not higher["first_jet_alone_completes_global_S1_through_S4"]
            and not higher["S2_global"]["available"]
            and not higher["S3_global"]["available"]
            and not higher["S4_global"]["available"]
        ),
        "AE4_and_child_inheritance_fail_closed": (
            not gluing["nonfermion_first_order_reset_gluing"]
            and not inheritance["nonzero_first_order_nonfermion_inheritance_unique"]
        ),
        "physical_event_balance_not_fabricated": (
            balance["total"] is None
            and not balance["physical_event_balance_evaluable"]
            and not balance["empirical_counterterm_inserted"]
        ),
        "one_exact_missing_variational_datum": (
            claims["exact_missing_variational_datum"] == EXACT_MISSING_DATUM
        ),
        "Gate7_and_physical_flags_preserved": (
            not claims["physical_background_bound"]
            and not claims["physical_HS_direction_derived"]
            and not claims["physical_yukawas_derived"]
            and not claims["physical_spectrum_derived"]
            and not claims["FULL_BHSM_COMPLETE"]
        ),
    }
    return {
        "artifact": "BHSM_NONFERMION_RELATIVE_BOUNDARY_VARIATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        "Theta_GFHS_zero_field": {
            "status": "AUTHORIZED_KINEMATIC_ZERO_BACKGROUND_MATCH_ONLY",
            "trace_relation": "Gamma0_child=U_0*Gamma0_event",
            "relative_conormal_graph_coordinate": "Theta_GFHS[B;0]=0",
            "variation_relation": "Gamma0_child(deltaPhi)=U_0*Gamma0_event(deltaPhi)",
            "source": "BHSM_AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN",
        },
        "D_Phi_Theta_GFHS_at_zero": {
            "D_A_Theta": None,
            "D_c_Theta": None,
            "D_cbar_Theta": None,
            "D_H_Theta": None,
            "derived_relations_only": {
                "ghost": brst["relation"],
                "antighost": brst["antighost_relation"],
            },
            "uniquely_determined": False,
        },
        "jet_source": {
            "retained_bulk_variation": "INSUFFICIENT",
            "missing_owner": (
                "BRST_COMPATIBLE_NONFERMION_RESET_BOUNDARY_GENERATING_"
                "FUNCTIONAL_S_RESET_GFHS"
            ),
            "first_missing_variational_datum": EXACT_MISSING_DATUM,
            "why_this_derivative": (
                "D_PhiSM_D_Gamma0_SQUARED_S_RESET_IS_D_PhiSM_THETA_AND_"
                "DISTINGUISHES_THETA_0_FROM_THETA_1"
            ),
        },
        "boundary_green_form": {
            "canonical_variables": variables,
            "Maxwell_discrete_identity": green,
            "HS_variation": hs,
        },
        "variational_selection": selection,
        "brst_compatibility": brst,
        "moving_domain_Hessian": hessian,
        "two_background_geometry_dependence": backgrounds,
        "ae4_reset_gluing": gluing,
        "child_inheritance": inheritance,
        "event_balance": balance,
        "higher_graph_jets_required": higher,
        "S1_global": "REFERENCE_ZERO_FIELD_SLICE_ONLY",
        "S2_global": "BLOCKED_BY_D_PhiSM_Theta",
        "S3_global": "ALSO_REQUIRES_D_PhiSM_SQUARED_Theta",
        "S4_global": "ALSO_REQUIRES_D_PhiSM_CUBED_Theta",
        "empirical_inputs": [],
        "validated": [
            "MAXWELL_AND_FP_GREEN_FORMS_FROM_RETAINED_BULK_ACTION",
            "HS_BARE_BOUNDARY_GREEN_FORM_IDENTICALLY_ZERO",
            "ZERO_FIELD_NONFERMION_RESET_MATCH",
            "BRST_RELATION_BETWEEN_GAUGE_GHOST_AND_ANTIGHOST_GRAPH_JETS",
            "THETA_0_THETA_1_REMAIN_VARIATIONALLY_UNDISTINGUISHED",
            "MOVING_DOMAIN_S3_S4_REQUIRE_HIGHER_GRAPH_JETS",
        ],
        "invalidated": [
            "RETAINED_BULK_GREEN_FORM_UNIQUELY_SELECTS_D_PhiSM_THETA",
            "HERMITICITY_GAUGE_CENTRALITY_OR_PROJECTORS_SELECT_THE_JET",
            "BRST_COMPATIBILITY_SELECTS_THE_COMMON_GAUGE_GHOST_JET_VALUE",
            "ALGEBRAIC_EC_HS_KERNEL_SUPPLIES_AN_HS_NORMAL_MOMENTUM",
            "FIRST_GRAPH_JET_ALONE_COMPLETES_GLOBAL_S1_THROUGH_S4",
            "AE4_RESPONSE_BLOCKS_MAY_BE_PROMOTED_TO_BOUNDARY_ACTION",
        ],
        "open": [EXACT_MISSING_DATUM],
        "exact_next_calculation": (
            "DERIVE_THE_BRST_COMPATIBLE_NONFERMION_RESET_BOUNDARY_"
            "GENERATING_FUNCTIONAL_S_RESET_GFHS_FROM_AN_ACTION_OWNED_"
            "RESET_ATTACHMENT_OR_TRACE_INCIDENCE_AND_EVALUATE_"
            "D_PhiSM_D_Gamma0_SQUARED_S_RESET_AT_THE_REFERENCE;_THEN_"
            "REPEAT_TO_D_PhiSM_SQUARED_AND_CUBED_THETA_FOR_GLOBAL_S3_S4"
        ),
        "physical_background_bound": False,
        "physical_HS_direction_derived": False,
        "physical_yukawas_derived": False,
        "physical_spectrum_derived": False,
        "FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND": False,
        "FULL_BHSM_COMPLETE": False,
        "claims": claims,
        "source_sha256": hashes,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def main() -> Path:
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(deterministic_json(build_payload()), encoding="utf-8", newline="\n")
    return TARGET


if __name__ == "__main__":
    print(main())
