import numpy as np

from bhsm.interface.master_action import common_parent_charged_current_attachment as v88


def test_proxy_kernel_is_full_rank():
    audit = v88.kernel_domain_audit()
    assert audit["full_rank"]
    assert audit["proxy_smallest_singular_value"] > 1.0e-6


def test_polar_isometry_is_unitary():
    U = v88.polar_isometry(v88.proxy_parent_kernel())
    assert np.allclose(U.conj().T @ U, np.eye(3), atol=1.0e-11)


def test_twisted_weak_generators_close_su2():
    audit = v88.su2_closure_audit()
    assert audit["SU2_algebra_closed"]
    assert audit["tree_level_neutral_FCNC_generated"] is False


def test_polar_map_is_family_basis_covariant():
    audit = v88.basis_covariance_audit()
    assert audit["basis_covariant"]
    assert audit["covariance_residual"] < 1.0e-11


def test_action_term_has_no_new_coupling_or_field():
    term = v88.action_term()
    assert not term["new_charged_coupling"]
    assert not term["new_continuous_parameter"]
    assert not term["new_fundamental_field"]
    assert term["Hermitian"]


def test_payload_passes_without_ckm_promotion():
    payload = v88.payload()
    assert payload["validation_passed"]
    assert not payload["physical_CKM_promoted"]
    assert not payload["frozen_predictions_changed"]
    assert not payload["repository_master_action_modified"]

