import numpy as np
import pytest
from bhsm.interface.muon_charge_source_clock_contract import validated_source_clock_higgs_first
from bhsm.interface.muon_common_domain_charge_source_clock import corrected_source_clock_higgs_first


def test_differently_scaled_ordinary_clock_is_rejected_instead_of_relabeling_the_source_ode():
    h = np.array([.2+.1j, .03j, -.04, .1])
    for clock in (2, 1+.01j):
        with pytest.raises(ValueError, match='unit proper-clock'):
            validated_source_clock_higgs_first(h, np.zeros(4), 0, 0, clock, 1.2+.03j)
    value = validated_source_clock_higgs_first(h, np.zeros(4), 0, 0, 1, 1.2+.03j)
    np.testing.assert_allclose(value['H_source_clock_first'], -1j*h/(1.2+.03j), atol=3e-17)


def test_connector_clocks_are_not_forced_to_the_unrelated_ordinary_source_normalization():
    h = np.array([.2+.1j, .03j, -.04, .1]); b = .02j*np.arange(4)
    for part in (1, 2):
        value = validated_source_clock_higgs_first(h, b, part, .02+.03j, .1+.4j, 1.2+.03j)
        expected = corrected_source_clock_higgs_first(h, b, part, .02+.03j, .1+.4j, 1.2+.03j)
        np.testing.assert_array_equal(value['H_source_clock_first'], expected['H_source_clock_first'])
