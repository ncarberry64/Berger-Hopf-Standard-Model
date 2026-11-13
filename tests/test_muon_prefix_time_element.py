"""Read-only checks of the new non-cut time element, no old producers."""
import json
from pathlib import Path
import numpy as np
import pytest


REF=Path(__file__).resolve().parents[1]/'artifacts/muon_prefix_time_element_20261004'


@pytest.fixture(scope='module')
def saved():
    def load(p):
        with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}
    return (load(REF/'run_1/prefix_time_element.npz'),
            load(REF/'run_3/point_volume_and_Cauchy.npz'),
            json.loads((REF/'run_1/temporal_point_receipts.json').read_text()),
            json.loads((REF/'run_3/result.json').read_text()))


def test_time_integral_matches_analytic_Legendre_moments(saved):
    a,_,_,_=saved;s=float(a['temporal_basis_scale'])
    A,B,C,M=(a['Legendre_density_'+k] for k in ('A','B','C','M'))
    # Orthogonality on0..1 gives integralP_l=delta_l0,
    # integral y P_l=delta_l1/3, integral y^2 P_l=delta_l0/3+2delta_l2/15.
    K=np.block([[A[0],s*(A[1]/6+B[0])],
        [s*(A[1]/6+B[0].conj().T),s*s*(A[0]/12+A[2]/30+(B[1]+B[1].conj().T)/6+C[0])]])
    mass=np.block([[M[0],s*M[1]/6],[s*M[1]/6,s*s*(M[0]/12+M[2]/30)]])
    assert np.linalg.norm(K-a['element_K'])/np.linalg.norm(K)<5e-15
    assert np.linalg.norm(mass-a['element_M'])/np.linalg.norm(mass)<5e-15


def test_original_chart_controls_non_cut_states_and_clock(saved):
    a,_,points,_=saved
    assert (a['temporal_x']>0).all() and (a['temporal_x']<1).all()
    assert not np.array_equal(a['source_history_states'][0],a['source_history_states'][-1])
    for p in points.values():
        f=p['field']
        assert f['branch']==24
        assert f['joint_chart_use']['interval'][1]<f['chart_radius']['interval'][0]
        assert f['Delta_box']['interval'][0]>0
        assert f['clock_tau_x']['interval'][0]>0
    # New interior values actually vary; they are not frozen endpoint data.
    assert np.ptp(a['action_multiplier_tau'][:,0])>1e9


def test_original_source_is_applied_before_timejet_cancellation(saved):
    a,measure,_,r=saved
    source=a['source_constant_coefficients'];d=len(source)//4
    np.testing.assert_array_equal(source[:d],0)
    np.testing.assert_array_equal(source[2*d:],0)
    w=measure['radial_weights'];energies=[]
    for i in range(len(a['temporal_x'])):
        energy=sum(float((w*measure['point_volume_density'][i])@
            np.sum(abs(a[f'actual_source_Dp_n{n}'][i].reshape(len(w),-1))**2,axis=1)) for n in (1,3))
        energies.append(energy)
    direct=float(a['temporal_weights']@(a['clock_tau_x']*energies))
    via_form=float(np.vdot(source,a['element_K']@source).real)
    assert abs(direct-via_form)/direct<1e-14
    assert r['assembly']['full_exterior_solved'] is False


def test_scaling_transforms_source_traces_and_duals_consistently(saved):
    a,_,_,_=saved;T=a['hierarchical_to_endpoint_coefficients'];x=a['source_constant_coefficients']
    ends=T@x;dim=len(x)//2
    np.testing.assert_array_equal(ends[:dim],a['left_source_trace'])
    np.testing.assert_array_equal(ends[dim:],a['right_source_trace'])
    np.testing.assert_allclose(a['element_M']@x,a['source_weak_rhs'],rtol=2e-15,atol=0)


def test_pairings_and_unsolved_conormal_are_distinct(saved):
    a,measure,_,r=saved
    assert np.linalg.norm(measure['point_volume_density']-measure['point_Cauchy_density'])>0
    assert np.linalg.norm(a['left_trial_outward_conormal_dual'])>0
    assert np.linalg.norm(a['right_trial_outward_conormal_dual'])>0
    assert r['assembly']['stationary_conormal'] is None
    assert r['physical_a_mu'] is None and r['physical_g_mu'] is None
