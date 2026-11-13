"""Independent finite source equation on all branch/family carrier rows."""
import numpy as np
import pytest
from bhsm.interface.muon_d5_complement_bulk_response import _collocation_rule
from bhsm.interface.muon_d5_temporal_bulk_refinement import time_evaluation_matrix
from bhsm.interface.muon_d5_corrected_homogeneous_source import (
    apply_corrected_family,corrected_source_factor,
)


def control():
    times=np.array([-2.,0.]);bounds=np.array([1.,.9]);nodes=_collocation_rule(2)[0]
    rho=bounds[0]+np.diff(bounds)[0]*nodes;theta=(rho-bounds[0])/np.diff(bounds)[0]
    saved=dict(times=times,radial_boundaries=bounds,radial_order=np.array(2))
    source=dict(times=times,radial_boundaries=bounds,radial_order=np.array(2),represented_radial_theta=theta[None])
    a=np.diag(np.linspace(.7,1.4,64));A=np.kron(np.eye(2),a)
    for side in ('plus','minus'):
        for branch in ('particle','conjugate'):
            op=side+'_'+branch;prefix=op+'_block0_'
            saved[op+'_block_count']=source[op+'_block_count']=np.array(1)
            saved[prefix+'indices']=source[prefix+'indices']=np.arange(64)
            saved[prefix+'initial']=np.eye(128)[None]
            saved[prefix+'initial_source']=np.zeros((1,128,128))
            saved[prefix+'slopes']=np.zeros((1,2,128,128))
            saved[prefix+'slopes_source']=np.full((1,2,128,128),123.)
            source[prefix+'source_initial']=np.zeros((1,128,128))
            source[prefix+'source_slopes']=np.broadcast_to(-A,(1,2,128,128)).copy()
            source[prefix+'wall_source_initial']=np.eye(128)[None]
            source[prefix+'wall_source_slopes']=np.zeros((1,2,128,128))
    return saved,source,a


@pytest.mark.parametrize('side',['plus','minus'])
def test_new_direction_and_full_wall_product_satisfy_original_source_equation(side):
    saved,source,a=control();rng=np.random.default_rng(465)
    w=rng.normal(size=(2,384,2))+1j*rng.normal(size=(2,384,2))
    wx=rng.normal(size=w.shape)+1j*rng.normal(size=w.shape)
    times=np.array([-1.7,-.31]);radii=np.array([.97,.914])
    result=apply_corrected_family(saved,source,side,w,wx,times=times,radii=radii)
    E=time_evaluation_matrix(saved['times'],times);Et=time_evaluation_matrix(saved['times'],times,1)
    V=np.einsum('ij,jdk->idk',E,w);Vx=np.einsum('ij,jdk->idk',E,wx)
    Vt=np.einsum('ij,jdk->idk',Et,w);Vxt=np.einsum('ij,jdk->idk',Et,wx)
    afull=np.tile(np.diag(a),6)[None,:,None]
    for i,r in enumerate(radii):
        np.testing.assert_allclose(result['value'][i],V,atol=2e-15)
        np.testing.assert_allclose(result['source'][i],Vx-(r-1)*afull*V,atol=3e-15)
        np.testing.assert_allclose(result['radial_source'][i]+afull*V,0,atol=2e-15)
        np.testing.assert_allclose(result['time_source'][i],Vxt-(r-1)*afull*Vt,atol=3e-15)
    # Fundamental source zero at the wall is distinct from its nonzero
    # physical wall-data variation, which must remain exactly present.
    atwall=apply_corrected_family(saved,source,side,w,wx,times=saved['times'],radii=[1.])
    np.testing.assert_allclose(atwall['source'][0],wx,atol=1e-15)
    assert np.linalg.norm(atwall['source'])>1


def test_source_factor_domain_and_wall_operands_are_not_silently_completed():
    saved,source,_=control()
    with pytest.raises(ValueError):corrected_source_factor(source,'plus_particle_block0_',[.89])
    with pytest.raises(ValueError):apply_corrected_family(saved,source,'plus',np.ones((2,384,1)),None,times=[0.],radii=[1.])
