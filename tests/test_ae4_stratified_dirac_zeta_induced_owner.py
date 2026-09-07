import hashlib
import math

import pytest

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import (
    claim_boundary,
    enclosure_holding_threshold_hypothesis,
    forward_time_domain_contract,
    historical_reconciliation,
    induced_local_weight_ledger,
    microscopic_owner_contract,
    native_spectral_length_contract,
    proper_time_moment,
    proper_time_moment_ratio,
)
from scripts.materialize_ae4_stratified_dirac_zeta_induced_owner import (
    TARGET,
    build_payload,
    main,
)


def test_integrated_heat_moments_have_exact_inverse_order_weights():
    expected = {8: -1 / 8, 6: -1 / 6, 5: -1 / 5, 4: -1 / 4, 3: -1 / 3, 2: -1 / 2}
    for order, value in expected.items():
        assert proper_time_moment(order) == value
    assert proper_time_moment_ratio(8, 4) == 0.5
    assert math.isclose(proper_time_moment_ratio(5, 3, 2.0), (3 / 5) * 2.0 ** -2)


def test_moments_scale_covariantly_with_one_common_length():
    for order in (8, 6, 5, 4, 3, 2):
        base = proper_time_moment(order, 0.73)
        scaled = proper_time_moment(order, 1.9 * 0.73)
        assert math.isclose(scaled / base, 1.9 ** -order, rel_tol=2e-15)
    with pytest.raises(ValueError):
        proper_time_moment(0)
    with pytest.raises(ValueError):
        proper_time_moment(4, 0.0)


def test_owner_retires_independent_wilson_sectors_without_claiming_domain():
    owner = microscopic_owner_contract()
    boundary = claim_boundary()
    assert not owner["independent_M8_M5_M4_Wilson_owners_retained"]
    assert boundary["AE4_STRATIFIED_DIRAC_ZETA_MICROSCOPIC_OWNER_SELECTED"]
    assert boundary["AE4_POSITIVE_ORDER_M8_M5_M4_MOMENT_RATIOS_DERIVED"]
    assert not boundary["AE4_GLOBAL_SELF_ADJOINT_STRATIFIED_DIRAC_DOMAIN_DERIVED"]
    assert not boundary["AE4_COMMON_SPECTRAL_LENGTH_PHYSICAL_ORIGIN_DERIVED"]


def test_spectral_length_is_native_first_future_surface_not_free_cutoff():
    native = native_spectral_length_contract()
    time = forward_time_domain_contract()
    stability = enclosure_holding_threshold_hypothesis()
    assert native["ell_star_is_BHSM_native_geometry_functional"]
    assert not native["ell_star_is_free_universal_cutoff"]
    assert native["first_crossing_not_singular_endpoint_evaluation"]
    assert not native["numerical_ell_star_evaluated_on_current_C2"]
    assert time["physical_time_orientation"] == "FUTURE_DIRECTED_ONLY"
    assert time["retarded_domain_required"]
    assert not time["periodic_cycle_surrogate_for_physical_frequency_allowed"]
    assert stability["atomic_decay_is_surface_holding_failure"] == "HYPOTHESIS_TO_DERIVE"
    assert not stability["physical_decay_law_derived"]


def test_integrated_determinant_is_not_misidentified_as_raw_heat_trace():
    reconciliation = historical_reconciliation()
    weights = induced_local_weight_ledger()
    assert not reconciliation["raw_heat_trace_confused_with_integrated_determinant"]
    assert weights["derived_positive_order_moments"]["F8"] == -1 / 8
    assert weights["derived_positive_order_moments"]["F4"] == -1 / 4
    assert weights["independent_profile_moments_remaining"] == 0


def test_materialized_AE4_owner_is_valid_and_deterministic():
    assert build_payload()["validation_passed"]
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
