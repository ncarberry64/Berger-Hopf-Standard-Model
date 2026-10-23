import numpy as np
import pytest

from bhsm.interface.muon_profile_preserving_phase_sample import (
    load_profile_preserving_phase,profile_preserving_raw_sample,profile_preserving_lepton_sample,
)
from bhsm.interface.muon_inherited_lepton_temporal_weak_action import inherited_cell_raw_at_time


@pytest.fixture(scope='module')
def phase():
    return load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1')


def test_same_cell_interpolation_matches_independent_temporal_weak_owner(phase):
    t=3.25e-6
    a=profile_preserving_raw_sample(phase,t)
    b=inherited_cell_raw_at_time(phase['arrays']['stage_independent_raw'][0],5e-6,t,phase['representation'])
    np.testing.assert_array_equal(a['raw_fields'],b)
    assert not a['interpolation_is_continuous_Euler_solution']
    with pytest.raises(ValueError,match='signed numerical phase'):
        profile_preserving_raw_sample(phase,-1e-7)


def test_analytic_total_time_jet_includes_parent_reference_clock(phase):
    time=5e-6;a=profile_preserving_lepton_sample(phase,time)
    for key in ('W','Omega_tau','H_can'):
        errors=[]
        for eps in (1e-6,5e-7):
            plus=profile_preserving_lepton_sample(phase,time+eps)['operator'][key]
            minus=profile_preserving_lepton_sample(phase,time-eps)['operator'][key]
            errors.append(np.linalg.norm((plus-minus)/(2*eps)-a['time_derivatives'][key]['coordinate_time']))
        assert errors[-1]<2e-8
        assert errors[-1]<max(0.6*errors[0],3e-9)
    assert abs(a['explicit_inherited_profile_coordinate_rate'])>0.
    assert np.linalg.norm(a['time_derivatives']['W']['explicit_inherited_clock'])>0.
    assert a['inherited_connection_count']==1


def test_proper_clock_and_haar_density_contact_come_from_same_sample(phase):
    a=profile_preserving_lepton_sample(phase,4e-6);d=a['time_derivatives']['W'];N=a['operator']['N']
    np.testing.assert_allclose(d['proper_time']*N,d['coordinate_time'],rtol=3e-16,atol=1e-30)
    assert not a['physical_history_or_formation_or_Pauli_selected']
    assert a['algebraic_At_time_derivative_not_claimed']
