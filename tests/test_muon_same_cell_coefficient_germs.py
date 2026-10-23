import numpy as np
import pytest
from bhsm.interface.muon_profile_preserving_phase_sample import (
    load_profile_preserving_phase,profile_preserving_lepton_sample,
)
from bhsm.interface.muon_same_cell_coefficient_germs import (
    same_cell_coefficient_germs,divided_coefficient_germs,
)
from bhsm.interface.muon_parent_maxwell_full_weak import M


@pytest.fixture(scope='module',params=('incoming','outgoing'))
def bound(request):
    side=request.param
    folder=('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'
        else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    phase=load_profile_preserving_phase(folder)
    stage=phase['arrays'][phase['stage_key']][0];time=phase['receipt']['span']/2
    kwargs={}if side=='incoming'else dict(initial_pair=phase['arrays']['initial_pair'],
        reference_pair=phase['arrays']['reference_pair'])
    def evaluate(t):return same_cell_coefficient_germs(stage,time,t,phase['representation'],**kwargs)
    return phase,time,evaluate


def test_values_bind_full_intrinsic_owner_and_clock_once(bound):
    phase,t,evaluate=bound;a=evaluate(t);full=profile_preserving_lepton_sample(phase,t)
    assert a['germs']['R4'][0]==full['operator']['R4']
    assert a['germs']['N'][0]==full['operator']['N']
    if phase['receipt']['side']=='outgoing':
        op=full['operator'];independent=op['wall_independent_plus_inherited_image'][2:]-M*op['inherited_wall_profile'][0]
        np.testing.assert_allclose(op['total_wall_connection'][2:]-independent,
            M*a['germs']['kappa_wall'][0],rtol=3e-15,atol=1e-15)
        assert abs(a['explicit_inherited_clock'][1])>0
        assert a['explicit_inherited_clock'][1]==full['explicit_inherited_profile_coordinate_rate']
    assert a['inherited_connection_count']==1


def test_first_and_second_germs_are_derivatives_of_full_cell_values(bound):
    _,t,evaluate=bound;a=evaluate(t)
    plus=evaluate(t+1e-6);minus=evaluate(t-1e-6)
    clock_second=(plus['explicit_inherited_clock'][1]-minus['explicit_inherited_clock'][1])/2e-6
    np.testing.assert_allclose(a['explicit_inherited_clock'][2],clock_second,rtol=4e-7,atol=2e-9)
    for name,jet in a['germs'].items():
        first=(plus['germs'][name][0]-minus['germs'][name][0])/2e-6
        second=(plus['germs'][name][1]-minus['germs'][name][1])/2e-6
        np.testing.assert_allclose(jet[1],first,rtol=4e-7,atol=2e-9)
        np.testing.assert_allclose(jet[2],second,rtol=4e-7,atol=2e-9)
        assert a['proper_time_first'][name]==jet[1]/a['germs']['N'][0]


def test_divided_germ_avoids_subtraction_at_coincident_times(bound):
    _,t,evaluate=bound
    coincident=divided_coefficient_germs(evaluate,t,t)
    for name,jet in evaluate(t)['germs'].items():assert coincident[name]==jet[1]
    eps=2e-6;divided=divided_coefficient_germs(evaluate,t+eps,t,quadrature_order=4)
    for name in divided:
        direct=(evaluate(t+eps)['germs'][name][0]-evaluate(t)['germs'][name][0])/eps
        np.testing.assert_allclose(divided[name],direct,rtol=4e-7,atol=2e-9)
