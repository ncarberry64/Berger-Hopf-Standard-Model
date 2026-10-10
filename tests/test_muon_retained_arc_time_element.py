"""Readonly checks of the new retained-node integral and trace assembly."""
import json
from pathlib import Path
import numpy as np
import pytest


REF=Path(__file__).resolve().parents[1]/'artifacts/muon_prefix_time_element_20261004'


def load(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


@pytest.fixture(scope='module')
def saved():return load(REF/'future_run_2/retained_arc_time_element.npz'),load(REF/'assembly_run_1/partial_coupled_temporal_KM.npz')


def test_actual_state_clock_and_source_tangents(saved):
    a,_=saved;h=load(REF/'future_run_2/retained_future_points.npz')
    for i in range(2):
        nb=np.exp(h['states'][i,74:86]@((-1.)**np.arange(1,13)))
        np.testing.assert_allclose(a['action_Y_tau'][i,:37],h['states'][i,37:74]/nb,rtol=5e-15)
        np.testing.assert_array_equal(a['actual_states'][i],h['states'][i])
        p=json.loads((REF/f'future_run_2/point_{i+1}.json').read_text())
        assert p['first_action']['branch']==24
        assert p['first_action']['clock_identity_relative']<1e-14
    assert abs(a['action_Y_tau'][0,74]-a['action_Y_tau'][1,74])>100
    assert np.linalg.norm(a['a0'][0]-a['a0'][1])>100


def test_linear_density_integral_by_independent_Gauss(saved):
    a,_=saved;scale=float(a['temporal_basis_scale']);size=len(a['element_K'])//2
    K=np.zeros_like(a['element_K']);M=K.copy()
    gx,gw=np.polynomial.legendre.leggauss(3)
    for y,w in zip(gx,gw/2):
        A,B,C,m=(a['Legendre_density_'+k][0]+y*a['Legendre_density_'+k][1] for k in ('A','B','C','M'))
        phi=[1,scale*y/2];dt=[0,scale]
        for i in range(2):
            for j in range(2):
                sl=np.s_[i*size:(i+1)*size,j*size:(j+1)*size]
                K[sl]+=w*(phi[i]*phi[j]*A+phi[i]*dt[j]*B+dt[i]*phi[j]*B.conj().T+dt[i]*dt[j]*C)
                M[sl]+=w*phi[i]*phi[j]*m
    assert np.linalg.norm(K-a['element_K'])/np.linalg.norm(K)<5e-15
    assert np.linalg.norm(M-a['element_M'])/np.linalg.norm(M)<5e-15


def test_source_full_output_contraction_and_pairings(saved):
    a,_=saved
    direct=0
    for i in range(2):
        spatial=sum(float((a['radial_weights']*a['point_volume_density'][i])@
            np.sum(abs(a[f'actual_source_Dp_n{n}'][i].reshape(len(a['radial_weights']),-1))**2,axis=1)) for n in (1,3))
        direct+=.5*a['clock_tau_x'][i]*spatial
    source=a['source_constant_coefficients']
    assert abs(direct-np.vdot(source,a['source_form_cotangent']).real)/direct<1e-14
    assert np.linalg.norm(a['point_volume_density']-a['point_Cauchy_density'])>0


def test_coupled_trace_matching_preserves_original_source(saved):
    _,a=saved;x=a['source_coefficients'];C=a['trace_continuity']
    np.testing.assert_array_equal(C@x,np.zeros(C.shape[0]))
    np.testing.assert_array_equal(a['left_total_source_trace'],a['right_total_source_trace'])
    for i,rel in enumerate(['run_1/prefix_time_element.npz','assembly_run_1/cut_to_future1_element.npz','future_run_2/retained_arc_time_element.npz']):
        p=load(REF/rel);sl=slice(i*48,(i+1)*48)
        np.testing.assert_array_equal(a['K'][sl,sl],p['element_K'])
        np.testing.assert_array_equal(a['M'][sl,sl],p['element_M'])
        np.testing.assert_array_equal(a['source_weak_rhs'][sl],p['source_weak_rhs'])
        np.testing.assert_array_equal(a['source_form_cotangent'][sl],p['source_form_cotangent'])


def test_interpolation_scope_and_unsolved_owner(saved):
    r=json.loads((REF/'future_run_2/result.json').read_text());j=json.loads((REF/'assembly_run_1/result.json').read_text())
    assert r['temporal_integral']['temporal_interpolation_bound'] is None
    assert r['physical_a_mu'] is None and r['physical_g_mu'] is None
    assert j['solution'] is None and j['stationary_residual'] is None
    assert j['other_owner_terms']['wall_Higgs_interface'] is None
    assert j['remaining_required_action']['physical_boundary_selection_missing'] is False
