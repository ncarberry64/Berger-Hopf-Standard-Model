import sympy as sp

from bhsm.interface.envelopment import local_radion_v10_3 as radion


def test_einstein_frame_local_breathing_mode_is_metric_derived_and_healthy():
    row = radion.pure_einstein_reduction()
    assert row["kinetic_coefficient_C_beta"] == 6
    assert row["internal_curvature_exponent"] == -4
    assert row["kinetic_sign"] == "HEALTHY_IF_KAPPA5_POSITIVE"
    assert row["new_scalar_appended"] is False


def test_general_breathing_coefficient_formula():
    assert radion.einstein_frame_breathing_coefficient(5, 3) == 6
    assert radion.internal_curvature_exponent(5, 3) == -4
    assert radion.einstein_frame_breathing_coefficient(4, 1) == sp.Rational(3, 2)


def test_homogeneous_limit_reproduces_v102_and_source_fails_closed():
    payload = radion.radion_payload()
    assert payload["validation_passed"] is True
    assert payload["homogeneous_limit"]["strictly_negative"] is True
    assert payload["localized_source"]["M4_intrinsic_source"] is None
    assert payload["localized_source"]["new_stabilizing_term_added"] is False
