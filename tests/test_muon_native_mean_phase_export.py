"""Phase-export intervals enclose the same exact stored implicit solution."""
import numpy as np
from bhsm.interface.muon_parent_mean_causal_descriptor import _descriptor_from_samples,implicit_mean_source_target_application
from bhsm.interface.muon_native_mean_phase_export import implicit_mean_phase_export


def test_export_error_includes_conversion_and_shared_complete_step():
    times=np.linspace(0,1,5);H=np.zeros((5,3,3));H[:,0,0]=.3;H[:,1,1]=2;H[:,2,2]=-1
    H[:,0,1]=H[:,1,0]=.2;H[:,1,2]=H[:,2,1]=.5;H[:,0,2]=H[:,2,0]=.1
    J=np.zeros((5,3,8,8))
    for k,t in enumerate(times):J[k]=np.array([t,t*t,.4+t])[:,None,None]*np.eye(8)
    d=_descriptor_from_samples(dict(times=times,hessian_samples=H,source_samples=J,x_count=1,v_count=1,y_count=1))
    kw=dict(time_steps=4,target_times=np.array([.2,.8]),target_loads=np.ones((2,3,1)),precision_bits=128)
    old=implicit_mean_source_target_application(d,**kw);new=implicit_mean_phase_export(d,**kw)
    np.testing.assert_array_equal(old['phase_values'],new['phase_values'])
    np.testing.assert_array_equal(old['midpoint_value_rate_algebraic'],new['midpoint_value_rate_algebraic'])
    np.testing.assert_array_equal(old['adjoint_target'],new['adjoint_target'])
    assert new['phase_export_entry_error_bounds'].shape==new['phase_values'].shape
    assert new['midpoint_export_entry_error_bounds'].shape==new['midpoint_value_rate_algebraic'].shape
    assert new['exact_stored_phase_export_entry_error_upper']>0
    assert new['exact_stored_phase_export_entry_error_upper']<1e-14
    assert new['exact_stored_midpoint_export_entry_error_upper']<1e-14
    assert new['exact_stored_forward_adjoint_intervals_overlap']
