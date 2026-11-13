import numpy as np
import pytest
from bhsm.interface.muon_d5_saved_response_diagnostics import (
    original_term_arrays,term_report,saved_nodal_partitions,time_polynomial_diagnostics,boundary_data_diagnostics,
)
from bhsm.interface.muon_d5_complement_bulk_response import nodal_derivative


def test_all_source_placements_are_retained_without_conjugating_source():
    I=np.eye(2);shape=(3,3,2,2);c={k:np.broadcast_to((j+1)*I,shape) for j,k in enumerate(
        ('time','radial','body','time_source','radial_source','body_source'))}
    f={k:np.full((3,3,2,1),1j*(j+1)) for j,k in enumerate(
        ('value','time','radial','source','time_source','radial_source'))}
    p=original_term_arrays(f,c)
    np.testing.assert_array_equal(p['original_D5'],p['T_dt']+p['R_dr']+p['K_value'])
    np.testing.assert_array_equal(p['original_D5_source'],sum(p[k] for k in
        ('dT_dt','dR_dr','dK_value','T_dt_source','R_dr_source','K_source')))
    report=term_report(f,c,p);assert report['physical_current_or_Cauchy_norm'] is None
    assert report['physical_admission'] is False
    f['source']=None
    with pytest.raises(ValueError,match='every consumed source'):original_term_arrays(f,c)


def test_nodal_partition_and_data_germ_do_not_turn_held_rows_into_passes():
    t=np.linspace(0,1,6);r=np.linspace(.2,.6,3);Dt=nodal_derivative(t);Dr=nodal_derivative(r)
    V=np.zeros((6,3,2,1),complex);V[:,:,0,0]=t[:,None]-r[None,:];V[:,:,1,0]=t[:,None]+r[None,:]
    X=1j*V;shape=(6,3,2,2);zero=np.zeros(shape,complex)
    c=dict(time=np.broadcast_to(np.eye(2),shape),radial=np.broadcast_to(np.diag([1.,-1.]),shape),body=zero,
        time_source=zero,radial_source=zero,body_source=zero)
    inner=np.array([[1.],[0.]]);outer=np.array([[0.],[1.]])
    arrays,report,_,_=saved_nodal_partitions(V,X,c,Dt,Dr,inner,outer)
    for value in arrays.values():assert np.max(abs(value))<1e-13
    birth=V[0];bx=X[0];incoming=np.stack((V[1:,0,0,0],V[1:,-1,1,0]),axis=1)[:,:,None]
    incx=1j*incoming
    _,germ=boundary_data_diagnostics(birth,bx,incoming,incx,c,Dt,Dr,inner,outer)
    assert germ['original_C1_value']['max_abs']<1e-13
    assert germ['physical_future_incoming_data_selected'] is False
    assert report['physical_admission'] is False


def test_time_scaling_is_explicit_conditioning_only():
    width=2e-9;t=width*(1-np.cos(np.pi*np.arange(6)/5))/2;z=2*t/width-1
    values=np.polynomial.chebyshev.chebval(z,[0,0,0,0,0,1])[:,None]
    report=time_polynomial_diagnostics(values,t,nodal_derivative(t))
    assert abs(report['coefficient_max_by_mode'][5]-1)<2e-15
    assert report['coordinate_time_first']['max_abs']>1e10
    assert abs(report['conditioning_only']['width_times_time_first']-50)<1e-12
