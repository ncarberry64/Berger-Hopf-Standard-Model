import numpy as np
from bhsm.interface.muon_birth_external_trace_chart import birth_external_trace_chart


def test_actual_half_density_and_opposite_clock_origins_cancel_in_physical_trace():
    U=np.array([[0,1j],[1j,0]]);a=birth_external_trace_chart(.9,1.1,.03,0.,raw_reset=U,energy=.7+.2j)
    T=(1.1/.9)**1.5*U
    np.testing.assert_allclose(a['physical_value_reset_from_envelopes'],T,atol=4e-16)
    np.testing.assert_allclose(a['analytic_trace_pairing_residual'],0.,atol=4e-16)
    h=1e-5
    plus=birth_external_trace_chart(.9,1.1,.03,0.,raw_reset=U,energy=.7+.2j+h)
    minus=birth_external_trace_chart(.9,1.1,.03,0.,raw_reset=U,energy=.7+.2j-h)
    np.testing.assert_allclose((plus['envelope_value_reset']-minus['envelope_value_reset'])/(2*h),a['envelope_value_reset_energy_first'],atol=8e-12)
    assert np.linalg.norm(a['envelope_value_reset_energy_first'])>0
