import numpy as np

from bhsm.interface.envelopment import global_zero_mode_v10_3 as zero_mode


def test_fredholm_projection_detects_kernel_obstruction():
    u0 = np.array([1.0, 1.0])
    assert np.isclose(zero_mode.fredholm_projection(np.array([1.0, -1.0]), u0), 0.0)
    assert not np.isclose(zero_mode.fredholm_projection(np.array([1.0, 0.0]), u0), 0.0)


def test_prior_fold_schur_response_is_imported_but_not_radion_closure():
    row = zero_mode.prior_fold_zero_mode()
    assert row["M_z_positive"] is True
    assert row["constraint_response_derived"] is True
    assert row["same_as_Hopf_radion_zero_mode"] is False
    assert row["fixes_dimensional_scale"] is False


def test_global_constraint_has_no_external_target_or_scale_fixing():
    payload = zero_mode.global_payload()
    assert payload["validation_passed"] is True
    assert payload["global_constraint"]["external_targets_adopted"] == []
    assert payload["global_constraint"]["beta0_fixed"] is False
    assert payload["global_constraint"]["remaining_dimensional_moduli"] == 1
