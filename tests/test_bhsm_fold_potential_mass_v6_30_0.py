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

from bhsm.interface import fold_potential_mass as potential


def test_exact_v629_merge_baseline():
    assert potential.SOURCE_MAIN_SHA == (
        "6e123ec1864044a3949b13e26c205acbe26ad898"
    )
    assert potential.V629_SCIENTIFIC_SHA == (
        "0c65bd9bf6480eee705fc6ee7769ecb4521b3abf"
    )
    assert potential.V629_REPRODUCIBILITY_SHA == (
        "4f7ca8791c74bc86397e0f8275de25cea4a71c73"
    )


def test_formal_einstein_value():
    assert potential.einstein_value() == potential.V0


def test_formal_einstein_gradient():
    assert potential.einstein_gradient() == (
        potential.V1
        - 2 * potential.F1 * potential.V0 / potential.F0
    )


def test_formal_einstein_hessian():
    expected = (
        potential.V2
        - 4 * potential.F1 * potential.V1 / potential.F0
        + (
            6 * potential.F1**2 / potential.F0**2
            - 2 * potential.F2 / potential.F0
        )
        * potential.V0
    )
    assert sp.simplify(potential.einstein_hessian() - expected) == 0


def test_stationary_relation_sets_gradient_to_zero():
    residual = potential.einstein_gradient().subs(
        potential.V1, potential.stationary_jordan_gradient()
    )
    assert sp.simplify(residual) == 0


def test_stationary_hessian_keeps_V2_and_F2():
    hessian = potential.stationary_einstein_hessian()
    assert hessian.has(potential.V2)
    assert hessian.has(potential.F2)


def test_null_hessian_relation_closes_only_combination():
    relation = potential.null_hessian_jordan_relation()
    assert sp.simplify(
        potential.stationary_einstein_hessian().subs(
            potential.V2, relation
        )
    ) == 0
    assert relation.has(potential.F2)
    assert relation.has(potential.V0)


def test_frame_F0_matches_inherited_exact_result():
    assert potential.frame_coefficients(1)["F0"] == sp.pi / 2


def test_frame_F1_is_sheet_odd():
    plus = potential.frame_coefficients(1)["F1"]
    minus = potential.frame_coefficients(-1)["F1"]
    assert sp.simplify(plus + minus) == 0


def test_frame_F2_contains_unstored_second_profiles():
    formula = sp.sstr(potential.frame_coefficients(1)["F2_functional"])
    assert "a_2(t)" in formula
    assert "N_2(t)" in formula


def test_invalid_sheet_rejected():
    try:
        potential.frame_coefficients(0)
    except ValueError as error:
        assert "tau" in str(error)
    else:
        raise AssertionError("invalid sheet was silently accepted")


def test_affine_metric_schur_cancels_exactly():
    assert potential.affine_zero_derivative_schur() == 0


def test_scalar_jacobi_quadratic_form_is_null():
    assert potential.scalar_critical_quadratic_form() == 0


def test_complete_critical_Jordan_hessian_is_null():
    assert potential.critical_jordan_reduced_hessian() == 0


def test_regular_frame_preserves_null_hessian():
    assert potential.critical_einstein_hessian() == 0


def test_dimensionless_mass_is_exactly_null():
    assert potential.dimensionless_mass_squared() == 0


def test_fixed_control_normal_form():
    expected = (
        potential.DELTA_MU * potential.Q**2 / 4
        - potential.TAU * potential.NU_1 * potential.Q**3 / 6
    )
    assert potential.reduced_normal_form() == expected


def test_branch_substitution_reproduces_cusp():
    assert potential.on_shell_cusp() == (
        potential.TAU * potential.NU_1 * potential.Q**3 / 12
    )


def test_fixed_control_hessian_at_critical_fold_is_null():
    assert potential.fixed_control_hessian_at_fold() == 0


def test_hessian_is_sensitive_to_V2():
    assert potential.v2_sensitivity_after_stationarity() == 1


def test_hessian_is_sensitive_to_F2_when_V0_nonzero():
    assert potential.f2_sensitivity_after_stationarity() == (
        -2 * potential.V0 / potential.F0
    )


def test_action_uses_two_caps_and_one_common_B1():
    ledger = potential.action_ledger()
    assert ledger["cap_multiplicity"] == 2
    assert ledger["common_B1_multiplicity"] == 1
    assert ledger["matcher_eliminated"] is True


def test_control_varying_curve_is_rejected_as_potential():
    ledger = potential.jordan_provenance_ledger()
    assert ledger["control_varying_curve_is_fixed_action"] is False
    assert ledger["on_shell_cusp_is_off_shell_potential"] is False
    assert "changes mu=-A5/Z5" in ledger["candidate_rejected"]


def test_full_Jordan_potential_is_not_claimed():
    assert potential.jordan_provenance_ledger()[
        "full_Jordan_potential_derived"
    ] is False


def test_local_potential_is_derived_only_through_quadratic_order():
    ledger = potential.critical_hessian_ledger()
    assert ledger["stationary"] is True
    assert ledger["Einstein_reduced_hessian"] == "0"
    assert ledger["result"] == potential.LOCAL_POTENTIAL_RESULT


def test_required_full_potential_verdict_is_not_emitted():
    text = json.dumps(potential.artifact_payloads())
    assert potential.REQUIRED_FULL_POTENTIAL_RESULT not in text
    assert potential.PRIMARY_RESULT in text


def test_required_mass_curvature_verdict_is_emitted():
    assert potential.mass_ledger()["result"] == potential.MASS_RESULT
    assert potential.mass_ledger()["mu_q_squared"] == "0"


def test_null_mass_is_not_called_tachyon_or_positive_mass():
    ledger = potential.mass_ledger()
    assert ledger["ghost"] is False
    assert ledger["tachyon"] is False
    assert ledger["positive_mass"] is False


def test_no_physical_mass_or_stability_claim():
    ledger = potential.mass_ledger()
    assert ledger["physical_mass"] is None
    assert ledger["potential_stability_away_from_q0"] == "not derived"
    assert potential.GUARDS["physical_mass_claimed"] is False
    assert potential.GUARDS["potential_stability_claimed"] is False


def test_blocker_is_class_B_not_fatal():
    blocker = potential.blocker_ledger()
    assert blocker["obstruction_class"].startswith("B:")
    assert blocker["fatal_inconsistency"] is False
    assert blocker["repair_path_uses_existing_action"] is True
    assert blocker["new_action_required"] is False


def test_v631_is_not_permitted():
    blocker = potential.blocker_ledger()
    assert blocker["v6_31_permitted"] is False
    assert blocker["next_result"] == potential.NEXT_RESULT
    assert potential.GUARDS["v6_31_permitted"] is False


def test_smallest_missing_object_is_fixed_action_and_fixed_regulator():
    missing = potential.blocker_ledger()["smallest_missing_object"]
    assert "fixed-action" in missing
    assert "fixed-regulator" in missing
    assert "A5" in missing
    assert "G5" in missing


def test_no_measurement_fit_new_primitive_or_scale():
    for name in (
        "measured_input_used",
        "fitted_parameter_used",
        "chat_only_value_imported",
        "new_action_introduced",
        "new_primitive_introduced",
        "new_scale_introduced",
    ):
        assert potential.GUARDS[name] is False


def test_no_vacuum_subtraction_or_hidden_coefficients():
    for name in (
        "vacuum_constant_subtracted",
        "F2_assumed",
        "V2_assumed",
        "on_shell_cusp_used_as_off_shell_potential",
    ):
        assert potential.GUARDS[name] is False


def test_frozen_and_official_prediction_logic_unchanged():
    assert potential.GUARDS["frozen_predictions_changed"] is False
    assert potential.GUARDS["official_prediction_logic_changed"] is False


def test_artifact_count_and_names():
    assert len(potential.ARTIFACT_FILES) == 5
    assert set(potential.artifact_payloads()) == set(
        potential.ARTIFACT_FILES
    )


def test_deterministic_artifact_bytes():
    first = potential.artifact_bytes()
    second = potential.artifact_bytes()
    assert first == second
    assert {
        name: hashlib.sha256(content).hexdigest()
        for name, content in first.items()
    } == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in second.items()
    }


def test_materializer_matches_generated_bytes(tmp_path):
    paths = potential.materialize_artifacts(tmp_path)
    assert len(paths) == 5
    expected = potential.artifact_bytes()
    for path in paths:
        assert path.read_bytes() == expected[path.name]


def test_checked_in_artifacts_are_current():
    for name, content in potential.artifact_bytes().items():
        assert (ROOT / "artifacts" / name).read_bytes() == content


def test_materializer_is_idempotent():
    script = ROOT / "scripts" / "materialize_fold_potential_mass_v6_30_0.py"
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    first = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in potential.ARTIFACT_FILES.values()
    }
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
    second = {
        name: (ROOT / "artifacts" / name).read_bytes()
        for name in potential.ARTIFACT_FILES.values()
    }
    assert first == second == potential.artifact_bytes()
