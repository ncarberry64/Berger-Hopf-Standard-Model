"""Exact common-cutoff identity and actual same-background Jacobi checks."""
import numpy as np
import pytest
from scipy.integrate import quad
from bhsm.interface.muon_intrinsic_higgs_positive_green import (
    common_heat_two_green_kernel,intrinsic_higgs_cell_jacobi,
    intrinsic_higgs_mixed_green_application,
)


def actual_inputs():
    from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
    from bhsm.interface.muon_magnetic_open_lepton_vertex import magnetic_open_fields_at_node
    from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
    from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    b=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/incoming_run_1',repository=ROOT)
    fields=magnetic_open_fields_at_node(b,b['source']['times'][2])
    rep=dict(b['representation'],native_positive_nu_squared_action=b['receipt']['action_parameters']['nu_squared_action'])
    return fields['raw_fields'],rep,retained_full_q_angular_space(ROOT),b['receipt']['chronological_response_span']


def test_common_cutoff_is_total_schwinger_time_not_separate_cutoffs():
    # CONTROL_ONLY positive scalar spectra, including exact repeated poles.
    p=np.array([2.,3.]);q=np.array([2.,4.]);c=.7
    a=common_heat_two_green_kernel(p,q,c,order=32)
    expected=np.array([[quad(lambda u:np.exp(-u*x)*np.exp(-max(c-u,0)*y)/y,0,c,epsabs=1e-13)[0]+np.exp(-c*x)/(x*y) for y in q] for x in p])
    np.testing.assert_allclose(a,expected,rtol=3e-15)
    assert a[0,0]==pytest.approx(np.exp(-2*c)*(c/2+1/4),rel=2e-15)
    assert np.max(abs(a-np.exp(-c*p[:,None]-c*q[None,:])/(p[:,None]*q[None,:])))>.01
    np.testing.assert_array_equal(common_heat_two_green_kernel(p,q,0),1/(p[:,None]*q[None,:]))


def test_actual_jacobi_keeps_temporal_connection_and_cap_pairing():
    raw,rep,angular,L=actual_inputs();r=intrinsic_higgs_cell_jacobi(raw,rep,angular,length=L)
    np.testing.assert_allclose(r['operator'],sum(r[k] for k in ('temporal','time_connection','spatial','potential')),rtol=1e-15)
    assert np.linalg.norm(r['action_Hessian']@r['Green']-np.eye(80))<1e-13
    assert np.linalg.norm(r['time_connection'])>0
    assert np.linalg.eigvalsh(r['potential'])[0]<0 # actual potential not discarded/positivity-assumed.
    assert r['eigenvalues'][0]>0
    assert not r['intrinsic_H_identified_with_EC_HS_auxiliary']
    broken=dict(rep);broken.pop('native_positive_nu_squared_action')
    with pytest.raises(ValueError,match='nu_squared'):intrinsic_higgs_cell_jacobi(raw,broken,angular,length=L)


def test_actual_open_mixed_unregulated_limit_agrees_with_two_inverse_contraction():
    raw,rep,angular,L=actual_inputs()
    r=intrinsic_higgs_mixed_green_application(raw,rep,angular,length=L,cutoff=0)
    np.testing.assert_allclose(r['mixed_Green_contraction'],r['unregulated_mixed_Green_contraction'],rtol=2e-12,atol=1e-27)
    assert np.linalg.norm(r['mixed_Green_contraction'])>0
    assert r['mixed_vertices'].shape==(80,360,18)
    assert not r['EC_HS_and_gauge_ghost_blocks_included']
    assert not r['graded_quantum_self_energy_completed']
    assert r['physical_a_mu'] is None


def test_missing_or_negative_operator_inputs_cannot_default_zero():
    with pytest.raises(ValueError):common_heat_two_green_kernel([0],[2],1)
    with pytest.raises(ValueError):common_heat_two_green_kernel([2],[3],-1)
