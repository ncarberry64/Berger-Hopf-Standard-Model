from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface import fixed_action_nonlinear_fold_potential as fold


def test_v6302_merge_and_scientific_ancestry_are_pinned():
    assert fold.SOURCE_MAIN_SHA == (
        "c049d4d6833c7c9b2c98682cdd81a9368693a0d3"
    )
    assert fold.V6302_SCIENTIFIC_SHA == (
        "0d72d9ab14d203cb7a5dd7c12733824d56d563c7"
    )


def test_fixed_h_first_vector_is_pure_scalar():
    assert fold.fixed_action_phi1() == ("0", "0", "u1", "0")


def test_common_frame_functional_has_zero_fixed_action_derivative():
    assert fold.fixed_action_frame_F1() == 0


def test_historical_frame_derivative_is_nonzero_on_both_sheets():
    assert sp.simplify(fold.inherited_curvature_varying_frame_F1(1)) != 0
    assert sp.simplify(fold.inherited_curvature_varying_frame_F1(-1)) != 0


def test_historical_tangent_varies_curvature_probe():
    assert fold.inherited_curvature_tangent(1) == fold.CHI_1
    assert fold.inherited_curvature_tangent(-1) == -fold.CHI_1


def test_first_tangent_mismatch_is_exact_and_sheet_odd():
    plus = fold.first_tangent_contradiction(1)
    minus = fold.first_tangent_contradiction(-1)
    assert plus != 0
    assert sp.simplify(plus + minus) == 0


def test_frozen_lapse_action_obeys_radial_noether_identity():
    assert fold.radial_noether_identity_residual() == 0


def test_failed_equation_and_smallest_missing_object_are_explicit():
    ledger = fold.family_ledger()
    assert "mathbb L_D Phi1=0" in ledger["failed_equation"]
    assert "simultaneously" in ledger["smallest_missing_object"]
    assert ledger["missing_object_location"].startswith("none:")


def test_no_higher_response_is_promoted_after_order_one_contradiction():
    ledger = fold.family_ledger()
    assert ledger["highest_consistent_order"] == 1
    assert ledger["Phi2"] is None
    assert ledger["result"] == fold.PRIMARY_RESULT


def test_surface_is_non_degenerate_and_matcher_rank_does_not_change():
    surface = fold.surface_ledger()
    assert surface["induced_metric_determinant_ratio"] == 1
    assert surface["induced_volume_measure_ratio"] == 1
    assert surface["induced_metric_rank"] == 4
    assert surface["matcher_trace_rank_pre_gauge"] == 2
    assert surface["rank_change_at_q0"] is False


def test_surface_distance_and_curvatures_are_finite():
    surface = fold.surface_ledger()
    assert surface["k_E_0"] > 0
    assert surface["normal_H_at_B1"] == 1
    assert surface["extrinsic_curvature_finite"] is True
    assert "finite" in surface["canonical_distance"]


def test_unique_terminal_diagnostic_verdict_is_regular_spacetime():
    assert fold.surface_ledger()["result"] == (
        "BHSM_CRITICAL_FOLD_IS_REGULAR_SPACETIME_CONFIGURATION"
    )


def test_tau_is_not_scalar_amplitude_sign():
    surface = fold.surface_ledger()
    assert surface["scalar_Z2"] == "(q,tau)->(-q,tau)"
    assert "not the sign" in surface["tau_relation"]


def test_jordan_linear_coefficient_domain_comparison():
    jordan = fold.jordan_ledger()
    assert jordan["fixed_action_F1"] == "0"
    assert jordan["required_probe_condition"] == "dr/dq=0"
    assert "dX/dq=tau chi_1" in jordan["historical_source"]
    assert jordan["F2"] is None


def test_einstein_interaction_and_scale_are_not_promoted():
    einstein = fold.einstein_ledger()
    permission = fold.permission_ledger()
    assert einstein["first_nonzero_interaction"] is None
    assert einstein["local_stability"] == fold.STABILITY_RESULT
    assert permission["scale_phase_permitted"] is False
    assert permission["scale_permission"] == fold.SCALE_RESULT


def test_integrity_guards():
    for key, value in fold.GUARDS.items():
        assert value is False, key


def test_empirical_inverse_is_quarantined():
    text = json.dumps(fold.artifact_payloads())
    for forbidden in ('"m_tau"', '"m_mu"', '"m_e"', '"CKM"', '"PMNS"'):
        assert forbidden not in text


def test_artifact_count_and_names():
    assert len(fold.ARTIFACT_FILES) == 5
    assert set(fold.artifact_payloads()) == set(fold.ARTIFACT_FILES)


def test_deterministic_artifact_bytes():
    first = fold.artifact_bytes()
    second = fold.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }


def test_checked_in_artifacts_are_current():
    for name, content in fold.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == content


def test_materializer_is_idempotent():
    script = (
        ROOT
        / "scripts"
        / "materialize_fixed_action_nonlinear_fold_potential_v6_30_3.py"
    )
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in fold.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in fold.ARTIFACT_FILES.values()
    }
    assert first == second == fold.artifact_bytes()
