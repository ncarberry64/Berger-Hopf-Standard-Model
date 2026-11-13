"""Actual corrected profile binding plus exact source-interpolation checks."""
import numpy as np
import pytest
from bhsm.interface.muon_corrected_profile_magnetic_response import (
    corrected_magnetic_source_sample,corrected_profile_reached_sample,
    corrected_magnetic_sampled_form,corrected_wall_reference,
)


@pytest.fixture(scope='module')
def actual():
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    folders=('artifacts/muon_finite_normal_phase_20261011/incoming_run_1',
        'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
    phases=[load_profile_preserving_phase(p,repository=ROOT) for p in folders]
    angular=retained_full_q_angular_space(ROOT)
    app=corrected_magnetic_source_sample(phases[1],5e-6,angular,electric_charge=.3028)
    return phases,angular,app


def test_actual_outgoing_full_inherited_value_time_radial_and_material_wall(actual):
    phases,angular,app=actual;phase=phases[1];a=app['action'];s=phase['arrays']
    np.testing.assert_allclose(a['inherited_profile_value_time_radial'],s['stage_profile_increment'][0],rtol=0,atol=5e-16)
    from bhsm.interface.muon_inherited_intrinsic_lepton_operator import inherited_intrinsic_lepton_operator
    raw=app['raw_sample']['raw_fields'];op=inherited_intrinsic_lepton_operator(raw,5e-6,s['initial_pair'],s['reference_pair'],phase['representation'])
    np.testing.assert_allclose(a['wall_background_values'],op['total_wall_connection'],rtol=0,atol=8e-16)
    assert np.linalg.norm(a['inherited_profile_value_time_radial'])>.1
    assert a['inherited_connection_count']==1 and a['extra_connection_Ar_advection_count']==0
    assert a['raw_forms'][0].shape==(488,488)
    assert a['gauge_weak_rows'].shape==(4,80,488)
    assert a['scalar_Maxwell_relative_normalization']==8.
    assert not a['physical_Pauli_value']


def test_actual_local_magnetic_jet_and_all_gauss_rows_remain(actual):
    _,_,app=actual;s=app['source'];a=app['action']
    assert s['active_source_indices']==[0,1,2]
    assert np.count_nonzero(s['connection_source'][:,3:])==0
    assert s['local_point_jet']['magnetic_curvature_defect']<2e-13
    assert s['local_point_jet']['potential_zero_defect']<2e-14
    r=a['reduced'];rng=np.random.default_rng(908) # CONTROL_ONLY action column, no physical state.
    z=rng.normal(size=408);v=rng.normal(size=408)
    y=r['At_value_map']@z+r['At_velocity_map']@v
    residual=r['Gauss_matrix']@y+r['Gauss_value_row']@z+r['Gauss_velocity_row']@v
    scale=1+np.linalg.norm(r['Gauss_matrix']@y)+np.linalg.norm(r['Gauss_value_row']@z)+np.linalg.norm(r['Gauss_velocity_row']@v)
    assert np.linalg.norm(residual)/scale<2e-14
    assert y.shape==(80,)


def test_hermite_source_rate_is_same_interpolated_polynomial(actual):
    # CONTROL_ONLY interpolation polynomial; no response/state selected.
    _,_,app=actual;base=app['action'];times=np.linspace(0,1,5);samples=[]
    for t in times:
        s=dict(base);Q=np.zeros((400,8));Qt=Q.copy()
        Q[180,0]=1+2*t+3*t*t+t**3;Qt[180,0]=2+6*t+3*t*t
        s['source']=Q;s['source_rate']=Qt;samples.append(s)
    f=corrected_magnetic_sampled_form(times,samples,duration=.25)
    for t in np.linspace(0,1,19):
        assert f['source_map'](t)[180,0]==pytest.approx(1+2*t+3*t*t+t**3,abs=3e-15)
        assert f['source_rate_map'](t)[180,0]==pytest.approx(2+6*t+3*t*t,abs=5e-15)
    assert f['source_rate_is_derivative_of_supplied_source_interpolation']


def test_missing_inherited_pair_and_wrong_source_domain_reject(actual):
    phases,angular,app=actual;raw=app['raw_sample']['raw_fields'];rep=phases[1]['representation']
    with pytest.raises(ValueError,match='both initial and reference'):
        corrected_wall_reference(raw,rep,coordinate_time=5e-6,initial_pair=phases[1]['arrays']['initial_pair'])
    Q=app['source']['connection_source'].copy();Q[0,0]=1
    with pytest.raises(ValueError,match='spatial400'):
        corrected_profile_reached_sample(raw,rep,angular,Q,app['source']['connection_source_rate'],coordinate_time=5e-6,nu_squared_action=4)
