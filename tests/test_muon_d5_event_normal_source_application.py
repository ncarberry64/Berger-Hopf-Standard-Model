"""Source-only Gauss solve and explicit normal-source extension checks."""
import numpy as np
import pytest

from bhsm.interface.muon_d5_complement_bulk_response import _collocation_rule
from bhsm.interface.muon_d5_temporal_bulk_refinement import _rectangular_collocation
from bhsm.interface.muon_d5_event_normal_source_application import (
    ProvisionalNormalSourceHistory,source_gauss_update,evaluate_event_normal_source,
)


def test_source_only_stage_solve_is_the_derivative_of_original_value_stages():
    rng=np.random.default_rng(873);order=3;d=4;k=7
    _,_,_,A=_collocation_rule(order);h=-.04
    G=rng.normal(size=(order,d,d))*.2;Gx=rng.normal(size=G.shape)*.3
    V0=rng.normal(size=(d,k));V0x=rng.normal(size=V0.shape)*.1
    def value(eps):
        slopes=_rectangular_collocation(G+eps*Gx,np.zeros_like(G),V0+eps*V0x,np.zeros_like(V0),h,A)[0]
        return V0[None]+eps*V0x[None]+h*np.einsum('ij,jdk->idk',A,slopes),slopes
    V=value(0.)[0];guess=rng.normal(size=V.shape)
    slope,stage,report=source_gauss_update(G,Gx,V,V0x,h,A,guess)
    np.testing.assert_allclose(stage,(value(1e-6)[0]-value(-1e-6)[0])/2e-6,atol=4e-10,rtol=3e-8)
    np.testing.assert_allclose(slope,(value(1e-6)[1]-value(-1e-6)[1])/2e-6,atol=2e-10,rtol=2e-8)
    assert report['corrected_stage_residual_max']<2e-15
    assert report['initializer_residual_max']>1
    assert report['correction_norm']>1
    assert report['value_equations_resolved'] is False


def test_provisional_extension_has_analytic_kinematic_source_and_second_time_jet(monkeypatch):
    import bhsm.interface.muon_d5_event_normal_source_application as module
    class AffineHistory:
        times=np.array([-1.,0.])
        original_phase_operands={'resolved_phase_coordinate_lift':np.zeros((268,252))}
        gauge_basis=staticmethod(lambda r:np.zeros((len(r),20,80)))
        def value(self,t):
            x=np.zeros(268,complex);rate=x.copy()
            x[98]=.2+.3*t;x[99]=.3;rate[98]=.3
            return x,rate
        def source(self,t):return self.value(t)[1],np.zeros(268,complex)
    def shape(raw,P):
        gradient=np.zeros(100,complex);gradient[98:100]=2*raw[98:100]
        H=np.zeros((100,100),complex);H[98,98]=H[99,99]=2
        return dict(value=1+raw[98]**2+raw[99]**2,raw_gradient=gradient,raw_hessian=H)
    monkeypatch.setattr(module,'proper_normal_shape_coefficient',shape)
    history=AffineHistory();new=ProvisionalNormalSourceHistory(history,-.478)
    xi,xit=new.source(-.43);eps=1e-6
    np.testing.assert_allclose((new.source(-.43+eps)[0]-new.source(-.43-eps)[0])/2e-6,xit,atol=7e-11)
    np.testing.assert_allclose(xit[98],xi[99],atol=1e-16)
    np.testing.assert_allclose(xit[99],-.478*2*.3**2,atol=1e-16)
    np.testing.assert_array_equal(new.value(-.43)[0],history.value(-.43)[0])
    assert np.linalg.norm(xi-history.source(-.43)[0])>.4


def test_dense_source_evaluation_keeps_all_carrier_rows_and_108_input_columns():
    rng=np.random.default_rng(941);n=2;d=64;columns=6*108
    arrays=dict(times=np.array([-1.,0.]),radial_boundaries=np.array([1.,.99]),radial_order=np.array(3))
    expected={}
    for branch_index,branch in enumerate(('particle','conjugate')):
        op='minus_'+branch;arrays[op+'_block_count']=np.array(1);base=op+'_block0_'
        arrays[base+'indices']=np.arange(64)
        c0=rng.normal(size=(d,columns));c1=rng.normal(size=(d,columns))
        arrays[base+'source_initial']=np.concatenate([c0-c1,c0])[None].astype(complex)
        arrays[base+'source_slopes']=np.zeros((1,3,n*d,columns),complex)
        expected[branch]=(c0,c1)
    times=np.array([-.83,-.17]);radii=np.array([.998,.993])
    for label in ('minus_LR','minus_RL'):
        result=evaluate_event_normal_source(arrays,label,times,radii)
        for branch_index,branch in enumerate(('particle','conjugate')):
            c0,c1=expected[branch]
            for family in range(3):
                col=(0 if label=='minus_LR' else 3)+family;sl=slice(108*col,108*(col+1));rows=slice((2*family+branch_index)*64,(2*family+branch_index+1)*64)
                value=c0[None,:,sl]+times[:,None,None]*c1[None,:,sl]
                np.testing.assert_allclose(result['source'][:,:,rows],np.broadcast_to(value,(2,2,64,108)),atol=2e-15)
                np.testing.assert_allclose(result['time_source'][:,:,rows],np.broadcast_to(c1[:,sl],(2,2,64,108)),atol=2e-15)
        assert np.max(abs(result['radial_source']))==0
    with pytest.raises(ValueError):evaluate_event_normal_source(arrays,'plus_seed',times,radii)
