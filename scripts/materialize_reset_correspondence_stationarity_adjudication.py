"""Materialize the reset-correspondence stationarity adjudication."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.reset_correspondence_stationarity_adjudication import (  # noqa: E402
    ACTION_VERSION,
    CHARGE_CLASS,
    CLASSIFICATION,
    D_CLASS,
    DIFFERENTIABILITY_CLASS,
    EXACT_NEXT_OBJECT,
    F_CLASS,
    L_CLASS,
    NEW_PHYSICS_DEFICIT,
    OUTCOME,
    STATUS,
    base_map_stationarity_adjudication,
    boundary_restriction_witness,
    claim_boundary,
    corner_and_endpoint_result,
    existing_action_reset_term_inventory,
    formal_F_B_variation,
    formal_L_s_variation,
    generator_charge_and_downstream_status,
    hindsight_ledger,
    hopf_rotor_stationarity_result,
    interface_functional_deficit,
    lagrangian_relation_stationarity_adjudication,
    restricted_action_family,
    seam_transversality_equations,
    stationary_child_set_verdict,
)


TARGET = ROOT / "artifacts/action_extension/BHSM_RESET_CORRESPONDENCE_STATIONARITY_ADJUDICATION.json"
MODULE = ROOT / "src/bhsm/interface/reset_correspondence_stationarity_adjudication.py"
SCRIPT = Path(__file__).resolve()
THEORY = ROOT / "theory/bhsm_reset_correspondence_stationarity_adjudication.md"
TEST = ROOT / "tests/test_reset_correspondence_stationarity_adjudication.py"


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".py", ".md", ".json"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


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
            raise ValueError("non-finite complex value")
        return {"real": _canonical(value.real), "imag": _canonical(value.imag)}
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float value")
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
    terms = existing_action_reset_term_inventory()
    restricted = restricted_action_family()
    boundary = boundary_restriction_witness()
    f_variation = formal_F_B_variation()
    f_verdict = base_map_stationarity_adjudication()
    l_variation = formal_L_s_variation()
    l_verdict = lagrangian_relation_stationarity_adjudication()
    seam = seam_transversality_equations()
    corner = corner_and_endpoint_result()
    hopf = hopf_rotor_stationarity_result()
    child = stationary_child_set_verdict()
    deficit = interface_functional_deficit()
    downstream = generator_charge_and_downstream_status()
    hindsight = hindsight_ledger()
    claims = claim_boundary()

    source_paths = (
        "src/bhsm/interface/master_action/terms.py",
        "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
        "src/bhsm/interface/nonfermion_relative_boundary_variation.py",
        "src/bhsm/interface/ae3_reciprocal_join_localization.py",
        "src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py",
        "src/bhsm/interface/aether_moving_interface_transfer_v15_12.py",
        "src/bhsm/interface/full_field_moving_reset_graph_decision.py",
        "artifacts/action_extension/BHSM_FULL_FIELD_MOVING_RESET_GRAPH_DECISION.json",
        MODULE.relative_to(ROOT).as_posix(),
        SCRIPT.relative_to(ROOT).as_posix(),
        THEORY.relative_to(ROOT).as_posix(),
        TEST.relative_to(ROOT).as_posix(),
    )
    hashes = {
        source: _sha256(ROOT / source)
        for source in sorted(source_paths)
        if (ROOT / source).is_file()
    }
    validation = {
        "all_master_action_terms_classified": terms["all_registered_master_terms_covered"],
        "no_explicit_F_B_term_found": not terms["any_term_explicitly_contains_F_B"],
        "no_nonfermion_seam_action_fabricated": terms["genuine_reset_seam_terms"]["nonfermion"] is None,
        "AE2_zero_fermion_seam_action_preserved": (
            terms["genuine_reset_seam_terms"]["fermion"] == "S_Sigma_F_AE2=0"
        ),
        "restricted_action_constructed_memberwise": restricted["same_bulk_density_for_every_member"],
        "domain_union_not_promoted_to_action": not restricted["single_functional_on_union_of_domains_exists"],
        "F_and_L_partial_derivatives_fail_closed": (
            not restricted["partial_derivative_delta_F_S_is_action_defined"]
            and not restricted["partial_derivative_delta_L_S_is_action_defined"]
        ),
        "conditional_momentum_transversality_verified": boundary["momentum_matching_residual"] < 1.0e-12,
        "boundary_one_form_decomposition_verified": boundary["decomposition_residual"] < 1.0e-12,
        "domain_variation_does_not_select_graph": (
            boundary["formal_domain_gradient_nonzero"] and not boundary["that_condition_selects_C"]
        ),
        "formal_F_variation_not_promoted": (
            not f_variation["existing_action_allows_delta_F_as_configuration_variation"]
            and not f_variation["attachment_equation_action_owned"]
        ),
        "F4_selected_exclusively": (
            not f_verdict["F1_unique_modulo_redundancy"]
            and not f_verdict["F2_structured_residual"]
            and not f_verdict["F3_equation_with_uncontrolled_freedom"]
            and f_verdict["F4_action_blind_to_required_choice"]
        ),
        "all_base_routes_remain_unselected": all(
            value == "NOT_SELECTED_OR_ELIMINATED" for value in f_verdict["base_map_routes"].values()
        ),
        "formal_L_variation_not_promoted": not l_variation["lambda_s_is_an_action_configuration_variable"],
        "inequivalent_fixed_graphs_survive_field_stationarity": (
            l_variation["two_fixed_graphs_cancel_field_variations"]
            and l_variation["two_fixed_graphs_maximal_isotropic"]
            and l_variation["graph_jets_and_boundary_potentials_differ"]
            and l_variation["self_adjoint_transfer_spectra_differ"]
        ),
        "L4_selected_exclusively": (
            not l_verdict["L1_unique_modulo_redundancy"]
            and not l_verdict["L2_structured_residual"]
            and not l_verdict["L3_uncontrolled_family_selected_by_an_equation"]
            and l_verdict["L4_no_selection_by_existing_action"]
        ),
        "momentum_half_not_confused_with_full_graph": (
            seam["natural_boundary_equations_exist_after_L_is_selected"]
            if "natural_boundary_equations_exist_after_L_is_selected" in seam
            else not seam["sectors_combine_into_action_selected_full_field_relation"]
        ),
        "corner_does_not_select_matter_domain": not corner["Hayward_selects_matter_or_core_domain"],
        "no_zero_parameter_completion_forced": not corner["standard_zero_parameter_completion_forces_reset_selection"],
        "Hopf_minimum_energy_not_smuggled_in": (
            hopf["positive_relative_energy"] and not hopf["minimum_energy_selection_invoked"]
            and not hopf["stationarity_fixes_relative_Hopf_orientation"]
        ),
        "D4_selected_exclusively": (
            not child["D1_singleton_physical_child"]
            and not child["D2_unique_modulo_proved_redundancy"]
            and not child["D3_structured_residual"]
            and child["D4_genuinely_underdetermined"]
        ),
        "new_physics_deficit_quantified": (
            deficit["minimum_independent_choice_count"] == 1
            and deficit["minimum_choice_type"] == NEW_PHYSICS_DEFICIT
            and not deficit["unique_zero_new_parameter_term_forced"]
        ),
        "new_interface_law_not_implemented": not deficit["implemented_or_tuned"],
        "G4_U_D_retained": (
            downstream["differentiability_class"] == "G4"
            and downstream["charge_class"] == "U"
            and downstream["outcome"] == "D"
        ),
        "frozen_predictions_unchanged": not claims["frozen_predictions_changed"],
        "full_BHSM_not_claimed": not claims["FULL_BHSM_COMPLETE"],
    }
    return {
        "artifact": "BHSM_RESET_CORRESPONDENCE_STATIONARITY_ADJUDICATION",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "status": STATUS,
        "F_class": F_CLASS,
        "L_class": L_CLASS,
        "stationary_child_class": D_CLASS,
        "differentiability_class": DIFFERENTIABILITY_CLASS,
        "charge_class": CHARGE_CLASS,
        "outcome": OUTCOME,
        "existing_action_reset_terms": terms,
        "restricted_action_family": restricted,
        "boundary_restriction_witness": boundary,
        "formal_F_B_variation": f_variation,
        "base_map_stationarity": f_verdict,
        "formal_L_s_variation": l_variation,
        "L_s_stationarity": l_verdict,
        "seam_transversality": seam,
        "corner_and_endpoint": corner,
        "Hopf_rotor_stationarity": hopf,
        "stationary_child_set": child,
        "interface_functional_deficit": deficit,
        "generator_charge_and_downstream": downstream,
        "VALIDATED": hindsight["VALIDATED"],
        "INVALIDATED": hindsight["INVALIDATED"],
        "REDUNDANT": hindsight["REDUNDANT"],
        "OPEN": hindsight["OPEN"],
        "DECISION_POWER": hindsight["DECISION_POWER"],
        "NEW_PHYSICS_DEFICIT": NEW_PHYSICS_DEFICIT,
        "EXACT_NEXT_OBJECT": EXACT_NEXT_OBJECT,
        "claim_boundary": claims,
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
