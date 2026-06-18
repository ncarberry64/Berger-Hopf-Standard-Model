from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_primitive_cyclic_monodromy import (  # noqa: E402
    DIM_H_EQUALS_ABS_OMEGA_PARTIAL,
    LEPTON_8_9_CHANNEL_RULE_CONDITIONAL_STRENGTHENED,
    PRIMITIVE_CYCLIC_MONODROMY_PARTIAL,
    S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION,
    audit_payload,
    charged_lepton_omega_values,
    cyclic_orbit_states,
    down_omega_values,
    export_primitive_cyclic_monodromy_outputs,
    is_primitive_order,
    monodromy_order_from_omega,
    omega_from_Arep,
    orbit_dimension,
    primitive_closure_check,
    q_from_kj,
    sector_monodromy,
    sector_monodromy_order,
    sector_orbit_dimension,
    up_omega_values,
    U_power_identity_condition,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_exact_monodromy_orders_and_orbits() -> None:
    assert monodromy_order_from_omega(3) == 3
    assert monodromy_order_from_omega(6) == 6
    assert monodromy_order_from_omega(12) == 12

    assert cyclic_orbit_states(3) == [0, 1, 2]
    assert orbit_dimension(3) == 3
    assert orbit_dimension(6) == 6
    assert orbit_dimension(12) == 12

    assert U_power_identity_condition(3, 3) is True
    assert U_power_identity_condition(3, 1) is False
    assert is_primitive_order(3, 3) is True
    assert primitive_closure_check(3) is True
    assert primitive_closure_check(6) is True
    assert primitive_closure_check(12) is True


def test_sector_omega_values_orders_and_dimensions() -> None:
    assert q_from_kj(5, 2) == 1
    assert q_from_kj(9, 3) == 3
    assert q_from_kj(6, 0) == 6
    assert q_from_kj(10, 1) == 8
    assert q_from_kj(6, 3) == 0
    assert q_from_kj(8, 2) == 4

    assert charged_lepton_omega_values() == (Fraction(3), Fraction(3))
    assert up_omega_values() == (Fraction(6), Fraction(6))
    assert down_omega_values() == (Fraction(12), Fraction(12))

    assert sector_monodromy_order("charged_lepton") == 3
    assert sector_monodromy_order("up") == 6
    assert sector_monodromy_order("down") == 12
    assert sector_orbit_dimension("charged_lepton") == 3
    assert sector_orbit_dimension("up") == 6
    assert sector_orbit_dimension("down") == 12


def test_omega_from_Arep_matches_sector_projectors() -> None:
    assert omega_from_Arep(q_from_kj(5, 2), 2, 0, 1, Fraction(-1, 2)) == 3
    assert omega_from_Arep(q_from_kj(9, 3), 3, 0, 1, Fraction(-1, 2)) == 3
    assert omega_from_Arep(q_from_kj(6, 0), 0, Fraction(1, 3), 0, Fraction(1, 2)) == 6
    assert omega_from_Arep(q_from_kj(10, 1), 1, Fraction(1, 3), 0, Fraction(1, 2)) == 6
    assert omega_from_Arep(q_from_kj(6, 3), 3, Fraction(1, 3), 0, Fraction(-1, 2)) == 12
    assert omega_from_Arep(q_from_kj(8, 2), 2, Fraction(1, 3), 0, Fraction(-1, 2)) == 12


def test_sector_monodromy_reports_expected_mode_rows() -> None:
    lepton = sector_monodromy("charged_lepton")
    up = sector_monodromy("up")
    down = sector_monodromy("down")

    assert lepton.omega == 3
    assert lepton.dimension == 3
    assert lepton.orbit_states == (0, 1, 2)
    assert lepton.primitive is True

    assert up.omega == 6
    assert up.dimension == 6
    assert up.primitive is True

    assert down.omega == 12
    assert down.dimension == 12
    assert down.primitive is True


def test_payload_is_partial_not_overpromoted() -> None:
    payload = audit_payload()

    assert payload["primitive_cyclic_monodromy_status"] == PRIMITIVE_CYCLIC_MONODROMY_PARTIAL
    assert payload["dim_H_equals_abs_Omega_status"] == DIM_H_EQUALS_ABS_OMEGA_PARTIAL
    assert payload["lepton_8_9_consequence_status"] == LEPTON_8_9_CHANNEL_RULE_CONDITIONAL_STRENGTHENED
    assert payload["does_boundary_action_define_U_f"] is True
    assert payload["does_variation_force_parallel_transport"] is True
    assert payload["does_finite_action_force_primitive_closure"] is False
    assert payload["does_U_f_have_order_abs_Omega"] is True
    assert payload["does_cyclic_orbit_define_channel_space"] is True
    assert payload["does_dim_H_equal_abs_Omega_become_derived"] is False
    assert payload["does_this_promote_full_lepton_8_9"] is False
    assert payload["does_this_change_official_predictions"] is False
    assert payload["safe_to_merge_as_candidate_only"] is True


def test_s2_geometric_quantization_is_hazard_not_dimension_route() -> None:
    payload = audit_payload()

    assert payload["preferred_dimension_route"] == "cyclic_boundary_monodromy"
    assert payload["geometric_quantization_plus_one_hazard"] is True
    assert payload["S2_geometric_quantization_used_for_channel_dimension"] is False
    assert payload["rejected_or_limited_route_note"] == S2_GEOMETRIC_QUANTIZATION_NOT_USED_FOR_CHANNEL_DIMENSION


def test_frozen_sanity_and_official_branches_remain_unchanged() -> None:
    payload = audit_payload()
    sanity = payload["frozen_sanity"]

    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    assert sanity["a_unchanged"] is True
    assert sanity["S_unchanged"] is True


def test_export_writes_reports_without_touching_frozen_predictions() -> None:
    frozen_paths = [
        ROOT / "docs" / "frozen_predictions.md",
        ROOT / "docs" / "frozen_predictions.json",
    ]
    before = {path: _sha(path) for path in frozen_paths}

    export_primitive_cyclic_monodromy_outputs(ROOT)

    after = {path: _sha(path) for path in frozen_paths}
    assert before == after

    expected_paths = [
        ROOT / "theory" / "primitive_cyclic_monodromy_from_boundary_action.md",
        ROOT / "theory" / "wilson_loop_boundary_monodromy_candidate.md",
        ROOT / "theory" / "boundary_phase_matching_condition.md",
        ROOT / "theory" / "self_adjoint_boundary_monodromy_candidate.md",
        ROOT / "theory" / "hopf_fiber_primitive_orbit_candidate.md",
        ROOT / "theory" / "topological_boundary_term_monodromy_candidate.md",
        ROOT / "theory" / "lepton_8_9_monodromy_status_update.md",
        ROOT / "theory" / "action_monodromy_remaining_assumptions.md",
        ROOT / "audits" / "primitive_cyclic_monodromy_boundary_action_audit.md",
        ROOT / "audits" / "primitive_cyclic_monodromy_boundary_action_audit.json",
    ]
    for path in expected_paths:
        assert path.exists()

    parsed = json.loads((ROOT / "audits" / "primitive_cyclic_monodromy_boundary_action_audit.json").read_text())
    assert parsed["official_outputs_modified"] is False
    assert parsed["frozen_predictions_modified"] is False
    assert parsed["preferred_dimension_route"] == "cyclic_boundary_monodromy"
    assert parsed["S2_geometric_quantization_used_for_channel_dimension"] is False


def test_reports_do_not_contain_forbidden_overclaims() -> None:
    export_primitive_cyclic_monodromy_outputs(ROOT)
    forbidden = [
        "bhsm is proven",
        "bhsm is confirmed",
        "replaces the standard model",
        "ordinary faster-than-light neutrino",
        "ordinary environmental mass-drift",
        "ordinary environmental mass drift",
        "full standard model derivation",
        "official lepton dressing update",
        "official quark dressing update",
    ]
    paths = [
        ROOT / "theory" / "primitive_cyclic_monodromy_from_boundary_action.md",
        ROOT / "theory" / "wilson_loop_boundary_monodromy_candidate.md",
        ROOT / "audits" / "primitive_cyclic_monodromy_boundary_action_audit.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    for phrase in forbidden:
        assert phrase not in text
