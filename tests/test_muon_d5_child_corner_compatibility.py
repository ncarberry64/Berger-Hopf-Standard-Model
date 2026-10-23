import numpy as np
from bhsm.interface.muon_d5_child_characteristic_field import solve_child_characteristic_cell
from bhsm.interface.muon_d5_child_corner_compatibility import (
    build_child_corner_compatibility,apply_child_corner_to_data,
    prepare_child_data_response,apply_child_data_source,evaluate_child_data_response,
)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def control():
    t=np.linspace(0,.2,6);r=np.array([.1,.3,.5]);f=full_d5_localized_lepton_trace();c={}
    for side,eps in (('plus',1),('minus',-1)):
      for branch in ('particle','conjugate'):
        g=f['gamma5D_'+branch];T=1j*np.kron(g[0],np.eye(16));R=1j*eps*np.kron(g[4],np.eye(16))
        shape=(6,3,64,64);z=np.zeros(shape,complex)
        c[side+'_'+branch]=dict(time=np.broadcast_to(T,shape),radial=np.broadcast_to(R,shape),body=z,
            time_source=z[None],radial_source=z[None],body_source=np.broadcast_to(T,(1,*shape)))
    app,_=solve_child_characteristic_cell(c,t,r)
    for label,row in c.items():
      for bi in range(int(app[label+'_block_count'])):
        p=label+'_block'+str(bi)+'_';idx=app[p+'indices']
        for key,a in row.items():app[p+'original_coefficient_'+key]=a[...,idx,:][...,idx]
    return app


def test_corner_eliminates_only_named_incoming_germ_not_initial_or_outer_state():
    app=control();corner,report=build_child_corner_compatibility(app)
    assert report['remaining_data_per_collar']==2688
    for entry in report['blocks'].values():
        assert entry['pivot_rank']==entry['rows'] and abs(entry['pivot_condition2']-1)<1e-14
        assert entry['pivot_identity_max']==0
    rng=np.random.default_rng(912);z=rng.normal(size=(8,384,2))+1j*rng.normal(size=(8,384,2))
    zx=rng.normal(size=z.shape)+1j*rng.normal(size=z.shape)
    for side in ('plus','minus'):
        actual,source,receipt=apply_child_corner_to_data(app,corner,side,z,zx)
        np.testing.assert_array_equal(actual[[0,1,2,4,5,6,7]],z[[0,1,2,4,5,6,7]])
        np.testing.assert_array_equal(source[[0,1,2,4,5,6,7]],zx[[0,1,2,4,5,6,7]])
        assert np.linalg.norm(actual[3]-z[3])>.1
        assert receipt['original_corner_value_or_source_max']<1e-12
        assert receipt['physical_state_selected'] is False


def test_one_consumed_data_correction_repairs_initializer_not_boundary_data():
    app=control();corner,_=build_child_corner_compatibility(app);rng=np.random.default_rng(812)
    data=rng.normal(size=(8,384,2))+1j*rng.normal(size=(8,384,2))
    dx=rng.normal(size=data.shape)+1j*rng.normal(size=data.shape)
    data,dx,_=apply_child_corner_to_data(app,corner,'plus',data,dx)
    # Deliberately degraded numerical initializer, not a physical trial state.
    for key in list(app):
        if key.endswith('_response') or key.endswith('_response_source'):
            app[key]=app[key]+1e-7*(rng.normal(size=app[key].shape)+1j*rng.normal(size=app[key].shape))
    prepared=prepare_child_data_response(app,'plus',data)
    X,receipt=apply_child_data_source(prepared,dx)
    assert prepared['report']['value_stage_before_max']>1e-7
    assert prepared['report']['value_stage_after_max']<1e-12
    assert receipt['source_stage_before_max']>1e-7 and receipt['source_stage_after_max']<1e-12
    field=evaluate_child_data_response(prepared,X,times=[0],radii=app['radii'])
    np.testing.assert_allclose(field['value'][0],data[:3],atol=2e-13)
    np.testing.assert_allclose(field['source'][0],dx[:3],atol=2e-13)
    np.testing.assert_array_equal(prepared['data'],data)
