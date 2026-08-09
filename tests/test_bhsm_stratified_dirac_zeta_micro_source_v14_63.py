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

from bhsm.interface.completion.stratified_dirac_zeta_micro_source_v14_63 import (
    VERSION,
    PRIMARY_VERDICT,
    EXACT_NEXT_OBJECT,
    REQUIRED_MOMENT_ORDERS,
    exponential_cutoff_moment,
    mixture_moment,
    moment_matrix,
    matrix_rank_with_tol,
    nullspace,
    cutoff_moment_rank_witness,
    zeta_logdet_rescaling_shift,
    zeta_renormalization_payload,
    local_zeta_coverage_payload,
    cutoff_spectral_expansion_payload,
    finite_dirac_data_payload,
    global_spectral_triple_requirement_payload,
    candidate_statuses,
    micro_source_exhaustion_payload,
    next_branch_gate_payload,
    completion_gate_payload,
    artifact_payloads,
    materialize,
)


def test_version_and_fail_closed_verdict():
    assert VERSION == "v14.63"
    assert "DOES_NOT_YET_CLOSE_ZERO_INPUT_BHSM" in PRIMARY_VERDICT
    assert "GLOBAL_STRATIFIED_SPECTRAL_TRIPLE" in EXACT_NEXT_OBJECT


def test_exponential_cutoff_moments_exact():
    assert exponential_cutoff_moment(0, 3.0) == 1.0
    assert exponential_cutoff_moment(2, 4.0) == 0.25
    assert exponential_cutoff_moment(4, 2.0) == 0.25
    assert abs(exponential_cutoff_moment(8, 2.0) - 0.0625) < 1e-15


def test_exponential_cutoff_rejects_invalid_inputs():
    for rate in (0.0, -1.0, float("inf")):
        try:
            exponential_cutoff_moment(2, rate)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid rate accepted")
    try:
        exponential_cutoff_moment(-1, 1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("negative moment order accepted")


def test_mixture_moment_is_linear():
    rates = [1.0, 4.0]
    weights = [2.0, 3.0]
    expected = 2.0 * 1.0 + 3.0 * 0.25
    assert abs(mixture_moment(2, rates, weights) - expected) < 1e-15


def test_required_moment_matrix_is_full_rank():
    rates = [0.55, 0.8, 1.1, 1.6, 2.3, 3.4, 5.2]
    m = moment_matrix(REQUIRED_MOMENT_ORDERS, rates)
    assert m.shape == (7, 7)
    assert matrix_rank_with_tol(m) == 7


def test_nullspace_preserves_selected_constraints():
    rates = [0.55, 0.8, 1.1, 1.6, 2.3, 3.4, 5.2]
    c = moment_matrix((0, 4), rates)
    ns = nullspace(c)
    assert ns.shape[0] == 7
    assert ns.shape[1] == 5
    assert np.linalg.norm(c @ ns) < 1e-11


def test_cutoff_witness_preserves_F0_F4_but_changes_F8():
    p = cutoff_moment_rank_witness()
    assert p["moment_matrix_rank"] == 7
    assert p["all_perturbed_weights_positive"] is True
    assert p["F0_preservation_residual"] < 1e-11
    assert p["F4_preservation_residual"] < 1e-11
    assert abs(p["F8_change"]) > 1e-5
    assert p["physical_BHSM_prediction"] is False


def test_zeta_rescaling_law():
    assert abs(zeta_logdet_rescaling_shift(1.5, 4.0) - 1.5 * math.log(4.0)) < 1e-15
    assert zeta_logdet_rescaling_shift(0.0, 9.0) == 0.0


def test_zeta_payload_keeps_local_counterterms_open():
    p = zeta_renormalization_payload()
    assert p["nonlocal_finite_spectral_part_fixed_by_operator"] is True
    assert p["local_relevant_counterterms_required_in_renormalized_EFT"] is True
    assert p["finite_local_counterterm_parts_fixed_by_determinant_alone"] is False
    assert p["zero_input_all_Wilson_coefficients_derived"] is False


def test_local_zeta_does_not_generate_M8_M5_relevant_terms():
    p = local_zeta_coverage_payload()
    assert p["local_zeta_can_compress_dimension_four_M4_coefficients"] is True
    assert p["local_zeta_generates_M8_M5_relevant_volume_EH_terms"] is False
    assert p["absolute_scale_generated"] is False


def test_cutoff_spectral_action_needs_profile_and_cross_stratum_trace():
    p = cutoff_spectral_expansion_payload()
    assert p["specific_profile_would_relate_moments"] is True
    assert p["profile_selected_by_current_BHSM_axioms"] is False
    assert p["global_cross_stratum_trace_defined_by_current_archive"] is False
    assert p["therefore_zero_input_completion"] is False


def test_finite_dirac_gate_retains_canonical_trace_but_not_yukawa_derivation():
    p = finite_dirac_data_payload()
    assert p["canonical_dimension_four_trace_result_retained"]["gauge_trace_ratio"] == "K_Y:K_2:K_3=5/3:1:1"
    assert p["canonical_dimension_four_trace_result_retained"]["historical_1_2_7_derived"] is False
    assert p["spectral_action_dependence"]["Yukawa_values_derived_by_spectral_trace_alone"] is False
    assert p["zero_input_flavor_closed"] is False


def test_global_spectral_triple_requirement_is_new_foundational_object():
    p = global_spectral_triple_requirement_payload()
    assert p["is_already_derived_in_current_archive"] is False
    assert p["may_be_new_theory_definition"] is True
    assert p["cannot_be_selected_using_neutrino_mass_CKM_PMNS_or_coupling_targets"] is True
    assert len(p["must_fix_before_physical_comparison"]) >= 6


def test_all_three_candidate_statuses_fail_zero_input_completion():
    rows = candidate_statuses()
    assert {r.name for r in rows} == {
        "PURE_ZETA_INDUCED_DETERMINANT",
        "LOCAL_ZETA_A_D",
        "CUTOFF_SPECTRAL_ACTION",
    }
    assert all(r.zero_input_complete_from_current_archive is False for r in rows)


def test_micro_source_exhaustion_retains_cap_and_v1462_progress():
    p = micro_source_exhaustion_payload()
    assert p["v14_59_global_cap_bypass_retained"] is True
    assert p["v14_62_GHY_and_common_normalization_quotient_retained"] is True
    assert p["single_microscopic_functional_derived_in_current_archive"] is False
    assert p["measured_particle_data_used"] is False


def test_next_branch_gate_does_not_auto_choose_new_theory():
    p = next_branch_gate_payload()
    assert p["branch_A"]["status"] == "AVAILABLE"
    assert p["branch_B"]["status"] == "OPEN_FOUNDATIONAL_OBJECT_REQUIRED"
    assert p["automatic_foundational_choice_made_by_v14_63"] is False
    assert p["branch_B"]["postcomparison_selection_forbidden"] is True


def test_completion_gate_is_fail_closed_and_usb_untouched():
    p = completion_gate_payload()
    assert p["full_BHSM_complete"] is False
    assert p["mark_III"] == "NOT_REACHED"
    assert p["usb_touched"] is False
    assert p["frozen_predictions_changed"] is False
    assert p["official_prediction_logic_changed"] is False
    assert p["physical_prediction_emitted"] is False
    assert len(p["missing_checks"]) >= 7


def test_artifact_payloads_are_json_serializable_and_finite():
    def walk(x):
        if isinstance(x, float):
            assert math.isfinite(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    for payload in artifact_payloads().values():
        s = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        assert s.startswith("{")
        walk(payload)


def test_materialization_is_byte_deterministic(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    materialize(a)
    materialize(b)
    names = sorted(p.name for p in a.iterdir())
    assert names == sorted(p.name for p in b.iterdir())
    assert len(names) == 9
    for name in names:
        assert (a / name).read_bytes() == (b / name).read_bytes()
