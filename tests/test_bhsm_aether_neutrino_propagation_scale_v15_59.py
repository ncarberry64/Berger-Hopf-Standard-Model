import math

import pytest

from bhsm.interface import aether_neutrino_propagation_scale_v15_59 as neutrino


def test_weyl_spectrum_and_projective_null_return():
    radius = neutrino.RADIUS0 / 2
    assert math.isclose(neutrino.weyl_frequency(0, radius), 1.5 / radius)
    for level in range(12):
        cycle = neutrino.propagation_cycle(level, radius)
        assert cycle["projective_return"]
        assert abs(cycle["phase_real"] + 1.0) < 2e-13
    with pytest.raises(ValueError):
        neutrino.weyl_frequency(-1, radius)


def test_three_family_massless_neutrino_sector_has_no_oscillation_splitting():
    result = neutrino.neutrino_family_propagation_contract()
    assert result["family_factor"] == "I3"
    assert result["mass_squared_splittings"] == [0.0, 0.0]
    assert result["PMNS_observable"] is False
    assert result["all_modes_return_on_the_odd_projective_ray"]


def test_all_absolute_units_reduce_to_single_kappa1_length():
    result = neutrino.geometric_scale_map()
    assert result["fundamental_length"] == "ell_kappa=kappa1^(-1/6)"
    assert result["M4_radius"] == "R4=R_F/2"
    assert result["absolute_numeric_eV_or_GeV_value"] is None
    assert result["external_calibration_used"] is False


def test_payload_json_is_deterministic_and_valid():
    payload = neutrino.completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["massless_neutrino_projective_propagation_cycle_derived"]
    assert neutrino.deterministic_json(payload) == neutrino.deterministic_json(
        neutrino.completion_payload()
    )
