import hashlib

import pytest

from bhsm.interface.ae3_c2_maxwell_common_shift_no_go import (
    claim_boundary,
    common_covariant_shift_witness,
    exact_common_shift_no_go,
    muon_chain_boundary,
    required_noncommon_correction,
)
from scripts.materialize_ae3_c2_maxwell_common_shift_no_go import (
    TARGET,
    build_payload,
    main,
)


def test_any_finite_common_shift_preserves_parent_difference():
    for shift in (0.0, 0.5, 10.0, 1.0e6):
        result = common_covariant_shift_witness(shift)
        assert result["relative_difference_invariance_residual"] < 1.0e-12
        assert not result["one_Maxwell_residue_after_finite_common_shift"]
        assert result["ratio_after_shift"] < 1.0
    with pytest.raises(ValueError):
        common_covariant_shift_witness(float("inf"))


def test_common_f_squared_repair_is_excluded_but_not_all_repairs():
    result = exact_common_shift_no_go()
    assert result["parent_difference_Zs_minus_Zt"] > 0.0
    assert not result["finite_local_covariant_F_squared_shift_repairs_mismatch"]
    assert not result["renormalization_scale_choice_repairs_mismatch"]
    assert not result["all_quantum_or_boundary_corrections_excluded"]


def test_required_noncommon_difference_is_exact_and_unfitted():
    result = required_noncommon_correction()
    theorem = exact_common_shift_no_go()
    assert result["required_delta_Zt_minus_delta_Zs"] == pytest.approx(
        theorem["parent_difference_Zs_minus_Zt"]
    )
    assert not result["one_candidate_selected_by_current_action"]
    assert not result["coefficient_fitted_to_required_difference"]


def test_photon_muon_boundary_and_materialization_are_conservative():
    boundary = claim_boundary()
    chain = muon_chain_boundary()
    assert boundary["CURRENT_C2_COMMON_COVARIANT_F2_SHIFT_NO_GO_DERIVED"]
    assert not boundary["CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED"]
    assert not boundary["CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED"]
    assert not chain["common_matter_wavefunction_renormalization_can_unlock_photon"]
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
