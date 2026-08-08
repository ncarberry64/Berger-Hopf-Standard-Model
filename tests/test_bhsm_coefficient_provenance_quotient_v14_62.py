from __future__ import annotations
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.coefficient_provenance_quotient_v14_62 import (
    VERSION, PRIMARY_VERDICT, EXACT_NEXT_OBJECT,
    ghy_required_coefficient, ghy_boundary_derivative_residual,
    determinant_prefactor_ledger, provenance_quotient_ledger,
    coefficient_quotient_payload, toy_stationary_point,
    common_normalization_invariance_payload, ghy_payload,
    dynamic_vs_wilson_payload, spectral_candidate_payload,
    zero_input_no_go_payload, finite_input_branch_payload,
    microscopic_choice_gate_payload, completion_gate_payload,
    artifact_payloads, materialize,
)


def test_version_and_primary_verdict_fail_closed():
    assert VERSION == "v14.62"
    assert "ZERO_INPUT" in PRIMARY_VERDICT
    assert "MICROSCOPIC" in EXACT_NEXT_OBJECT


def test_ghy_relative_coefficient_exact():
    for c in (0.125, 1.0, 3.75, -2.0):
        assert ghy_required_coefficient(c) == 2.0*c
        assert ghy_boundary_derivative_residual(c, 2.0*c) == 0.0


def test_ghy_wrong_ratio_does_not_cancel():
    assert abs(ghy_boundary_derivative_residual(1.0, 1.0)) > 0.5
    assert abs(ghy_boundary_derivative_residual(1.0, 3.0)) > 0.5


def test_determinant_statistics_prefactors():
    rows = {r["field"]: r for r in determinant_prefactor_ledger()["rows"]}
    assert rows["real_boson"]["positive_operator_prefactor"] == 0.5
    assert rows["complex_boson"]["positive_operator_prefactor"] == 1.0
    assert rows["dirac_fermion"]["positive_operator_prefactor"] == -0.5
    assert rows["complex_FP_ghost"]["positive_operator_prefactor"] == -1.0
    assert determinant_prefactor_ledger()["prefactors_are_tunable_Wilson_coefficients"] is False


def test_provenance_ledger_has_true_wilson_families():
    entries = provenance_quotient_ledger()
    true_inputs = [e for e in entries if e.true_wilson_input]
    assert len(true_inputs) == 4
    assert {e.name for e in true_inputs} == {
        "M8_volume_and_parent_potential_data",
        "M8_two_derivative_geometry_eta",
        "M5_cap_Einstein_scalar_data",
        "M4_intrinsic_local_action",
    }


def test_shape_and_RH_are_not_misclassified_as_wilson_coefficients():
    by_name = {e.name: e for e in provenance_quotient_ledger()}
    assert by_name["three_transverse_shape_channels"].true_wilson_input is False
    assert "DYNAMICAL" in by_name["three_transverse_shape_channels"].v14_62_class
    assert by_name["cosmological_parent_anchor"].true_wilson_input is False


def test_common_positive_action_scaling_leaves_stationary_point():
    base = toy_stationary_point(1.3, 0.8, 2.1)
    scaled = toy_stationary_point(13.0, 8.0, 21.0)
    assert abs(base-scaled) < 1e-15


def test_independent_ratio_changes_global_stationary_point():
    base = toy_stationary_point(1.3, 0.8, 2.1)
    changed = toy_stationary_point(1.3, 1.7, 2.1)
    assert abs(base-changed) > 1e-2


def test_common_normalization_payload_exposes_ratio_obstruction():
    p = common_normalization_invariance_payload()
    assert p["common_rescaling_difference"] < 1e-14
    assert p["ratio_change_effect"] > 1e-2
    assert p["physical_BHSM_solution"] is False


def test_coefficient_quotient_removes_false_blockers_without_claiming_completion():
    p = coefficient_quotient_payload()
    assert len(p["true_independent_Wilson_families"]) == 4
    assert "relative_nonlocal_spectral" in p["reclassified_non_Wilson_open_objects"]
    assert "three_transverse_shape_channels" in p["reclassified_non_Wilson_open_objects"]
    assert "cosmological_parent_anchor" in p["reclassified_non_Wilson_open_objects"]
    assert p["measured_particle_data_used"] is False


def test_spectral_candidate_keeps_historical_127_invalidated():
    p = spectral_candidate_payload()
    assert p["canonical_gauge_trace_ratio"] == "K_Y:K_2:K_3=5/3:1:1"
    assert p["historical_1_2_7_derived"] is False
    assert p["zero_input_completion_from_this_branch"] is False
    assert p["adopted_into_authoritative_stratified_action"] is False


def test_zero_input_no_go_is_about_current_axioms_only():
    p = zero_input_no_go_payload()
    assert p["zero_input_completion_derivable_from_current_axioms"] is False
    assert p["global_envelopment_cap_selection_invalidated"] is False
    assert len(p["remaining_true_Wilson_families"]) == 4


def test_finite_input_branch_enforces_precomparison_freeze():
    p = finite_input_branch_payload()
    assert p["can_run_global_BVP_after_inputs_and_operators_are_frozen"] is True
    assert p["zero_input_prediction_of_Standard_Model_parameters"] is False
    assert any("hash-freeze" in step for step in p["allowed_workflow"])


def test_microscopic_choice_gate_does_not_automatically_add_new_theory():
    p = microscopic_choice_gate_payload()
    assert p["gate"] == "MICROSCOPIC_SOURCE_CHOICE_REQUIRED"
    assert p["automatic_choice_made_by_v14_62"] is False
    assert p["option_B"]["must_be_declared_before_physical_comparison"] is True


def test_completion_gate_remains_false_and_usb_untouched():
    p = completion_gate_payload()
    assert p["full_BHSM_complete"] is False
    assert p["mark_III"] == "NOT_REACHED"
    assert p["usb_touched"] is False
    assert p["frozen_predictions_changed"] is False
    assert p["official_prediction_logic_changed"] is False
    assert p["physical_prediction_emitted"] is False


def test_artifact_payloads_are_canonical_json_serializable():
    for payload in artifact_payloads().values():
        s = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        assert s.startswith("{")


def test_materialization_is_byte_deterministic(tmp_path):
    a = tmp_path/"a"; b = tmp_path/"b"
    materialize(str(a)); materialize(str(b))
    names = sorted(p.name for p in a.iterdir())
    assert names == sorted(p.name for p in b.iterdir())
    assert len(names) == 9
    for n in names:
        assert (a/n).read_bytes() == (b/n).read_bytes()


def test_ghy_payload_does_not_claim_cap_EH_coefficient_derived():
    p = ghy_payload()
    assert p["GHY_is_independent_Wilson_input"] is False
    assert p["cap_Einstein_coefficient_is_derived"] is False


def test_dynamic_vs_wilson_prevents_postcomparison_fits():
    p = dynamic_vs_wilson_payload()
    assert set(p["not_allowed_as_post_comparison_fit_parameters"]) == {"R_H", "x", "q_Lr(tau)", "seam_X"}


def test_no_nonfinite_numbers_in_artifacts():
    def walk(x):
        if isinstance(x, float): assert math.isfinite(x)
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x: walk(v)
    for p in artifact_payloads().values(): walk(p)
