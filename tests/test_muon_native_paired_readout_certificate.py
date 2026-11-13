"""CONTROL_ONLY exact finite readout checks; no numerical action solve."""
import numpy as np
import pytest
from flint import arb_mat,arb,ctx

from bhsm.interface.muon_native_paired_readout_certificate import (
    interpolate_phase_interval,pair_target_phase_intervals,critical_phase_compatibility,
    unbounded_export_mesh_diagnostics,
)


def fixture():
    grid=np.array([0.,.125,.25,.375]);columns=np.arange(1,65,dtype=float)
    phase=np.zeros((4,2,64));phase[:,0]=grid[:,None]*columns;phase[:,1]=phase[:,0]
    midpoint=np.zeros((3,2,64));midpoint[:,0]=columns;midpoint[:,1]=columns/2
    return grid,phase,midpoint,columns


def test_interval_interpolation_uses_x_and_full_midpoint_not_p():
    grid,phase,midpoint,col=fixture();previous=ctx.prec
    try:
        ctx.prec=192;value,k,theta=interpolate_phase_interval(grid,phase,0.,midpoint,0.,.1875)
        assert k==1 and theta.contains(.5)
        for j in range(64):
            assert value[0,j].contains(.1875*col[j])
            assert value[1,j].contains(col[j])
            assert value[2,j].contains(col[j]/2)
    finally:ctx.prec=previous


def test_outward_phase_and_target_pairing_preserves_all64_source_positions():
    grid,phase,midpoint,col=fixture();times=np.array([.0625,.3125])
    target=np.array([[.125,.25,.5],[.5,.125,-.25]])
    result=pair_target_phase_intervals(target,target,np.zeros((2,3)),np.zeros((2,3)),
        times,grid,phase,0.,midpoint,0.,np.eye(3))
    expected=(.125*.0625+.25+.5/2+.5*.3125+.125-.25/2)*col.reshape(8,8)
    assert np.all(result['reference_lower']<=expected)
    assert np.all(result['reference_upper']>=expected)
    assert np.array_equal(result['FE_reference_allowance_upper'],np.zeros((8,8)))
    assert not result['sample_density_reapplied']
    assert not result['complete_native_or_Pauli_evaluated']


def test_FE_and_Y4_errors_are_separate_and_signed_center_uses_absolute_states():
    grid,phase,midpoint,col=fixture();phase[...,::2]*=-1;midpoint[...,::2]*=-1
    target=np.array([[.125,.25,.5]]);fe=np.full((1,3),.01);tail=np.full((1,3),.002)
    result=pair_target_phase_intervals(target,target,fe,tail,[.0625],grid,phase,0.,midpoint,0.,np.eye(3))
    expected_fe=.01*(.0625+1+.5)*col.reshape(8,8)
    assert np.all(result['FE_reference_allowance_upper']>=expected_fe)
    assert np.all(result['Y4_allowance_upper']>=expected_fe/5)
    assert np.all(result['total_lower']<result['reference_lower'])
    assert np.all(result['total_upper']>result['reference_upper'])


def test_export_errors_widen_the_actual_pairing_without_default_zero():
    grid,phase,midpoint,_=fixture();target=np.array([[.125,.25,.5]])
    result=pair_target_phase_intervals(target,target,np.zeros((1,3)),np.zeros((1,3)),
        [.0625],grid,phase,.01,midpoint,.02,np.eye(3))
    assert np.min(result['reference_upper']-result['reference_lower'])>.02
    with pytest.raises(ValueError,match='phase export error'):
        pair_target_phase_intervals(target,target,np.zeros((1,3)),np.zeros((1,3)),
            [.0625],grid,phase,None,midpoint,.02,np.eye(3))


def test_Arb_coordinate_lift_encloses_its_own_nonexact_coefficient():
    grid,phase,midpoint,_=fixture();target=np.array([[1.]])
    lift=arb_mat([[arb(1,'1e-6'),arb(0),arb(0)]])
    result=pair_target_phase_intervals(target,target,np.zeros((1,1)),np.zeros((1,1)),
        [.0625],grid,phase,0.,midpoint,0.,lift)
    assert result['reference_lower'][0,0]<.0625<result['reference_upper'][0,0]


def test_critical_covector_is_evaluated_on_reached_phase_and_has_no_failure_promotion():
    grid,phase,_,_=fixture();critical=dict(phase_row=[1.,-1.],source_row=np.zeros((8,8)).tolist(),numerical_root_time=.1875)
    result=critical_phase_compatibility(grid,phase,0.,critical)
    assert np.all(result['residual_lower']<=0) and np.all(result['residual_upper']>=0)
    assert result['source_row_alone_is_not_a_failure_verdict']
    assert not result['continuous_constitutive_compatibility_proved']
    critical['source_row']=np.ones((8,8)).tolist()
    result=critical_phase_compatibility(grid,phase,0.,critical)
    assert np.all(result['residual_lower']<=1) and np.all(result['residual_upper']>=1)


@pytest.mark.parametrize('time',[-.01,.5])
def test_extrapolation_is_rejected(time):
    grid,phase,midpoint,_=fixture()
    with pytest.raises(ValueError,match='extrapolation'):
        interpolate_phase_interval(grid,phase,0.,midpoint,0.,time)


def test_negative_allowance_and_reversed_target_endpoints_rejected():
    grid,phase,midpoint,_=fixture();target=np.ones((1,3))
    with pytest.raises(ValueError):pair_target_phase_intervals(target,target,-target,np.zeros((1,3)),[.1],grid,phase,0.,midpoint,0.,np.eye(3))
    with pytest.raises(ValueError):pair_target_phase_intervals(target,target/2,np.zeros((1,3)),np.zeros((1,3)),[.1],grid,phase,0.,midpoint,0.,np.eye(3))


def test_unbounded_legacy_mesh_diagnostic_does_not_fill_unknown_phase_errors():
    grid,phase,midpoint,col=fixture();target=np.array([[.125,.25,.5]])
    critical=dict(phase_row=[1.,-1.],source_row=np.zeros((8,8)),numerical_root_time=.1875)
    fine_grid=np.linspace(0.,.375,7);fine_phase=np.zeros((7,2,64))
    fine_phase[:,0]=fine_grid[:,None]*col;fine_phase[:,1]=fine_phase[:,0]
    fine_midpoint=np.tile(midpoint[0],(6,1,1))
    meshes=[dict(time_grid=grid,phase_values=phase,midpoint_value_rate_algebraic=midpoint),
        dict(time_grid=fine_grid,phase_values=fine_phase,midpoint_value_rate_algebraic=fine_midpoint)]
    result=unbounded_export_mesh_diagnostics(meshes,target,target,[.0625],np.eye(3),critical)
    assert np.array_equal(result['mesh_differences'][0]['reference_center_difference'],np.zeros((8,8)))
    assert result['finite_applications'][0]['phase_export_error_upper'] is None
    assert not result['finite_applications'][0]['finite_readout_interval_certified']
    assert not result['missing_phase_export_errors_replaced_with_zero']
    assert not result['mesh_differences'][0]['continuous_mesh_error_bound_inferred']
    assert result['finite_applications'][0]['critical_residual_absolute_max']==0


def test_legacy_mesh_difference_keeps64_source_positions_and_no_convergence_inference():
    grid,phase,midpoint,col=fixture();changed=phase.copy();changed[:,0]*=2
    critical=dict(phase_row=[1.,-1.],source_row=np.ones((8,8)),numerical_root_time=.1875)
    fine_grid=np.linspace(0.,.375,7);fine_phase=np.zeros((7,2,64))
    fine_phase[:,0]=2*fine_grid[:,None]*col;fine_phase[:,1]=fine_grid[:,None]*col
    fine_midpoint=np.tile(midpoint[0],(6,1,1))
    result=unbounded_export_mesh_diagnostics([
        dict(time_grid=grid,phase_values=phase,midpoint_value_rate_algebraic=midpoint),
        dict(time_grid=fine_grid,phase_values=fine_phase,midpoint_value_rate_algebraic=fine_midpoint)],
        np.array([[1.,0.,0.]]),np.array([[1.,0.,0.]]),[.0625],np.eye(3),critical)
    assert np.array_equal(result['mesh_differences'][0]['reference_center_difference'],.0625*col.reshape(8,8))
    assert np.array_equal(result['finite_applications'][1]['critical_residual_center'],(.1875*col+1).reshape(8,8))
    assert not result['continuous_temporal_error_enclosed']
