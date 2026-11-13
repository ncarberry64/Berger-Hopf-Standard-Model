import numpy as np
from bhsm.interface.muon_d5_child_characteristic_field import (
    characteristic_bases,solve_child_characteristic_cell,apply_child_cell_field,
)
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def test_original_principal_characteristics_keep_both_half_carriers():
    full=full_d5_localized_lepton_trace()
    for branch in ('particle','conjugate'):
      g=full['gamma5D_'+branch];A=np.kron(g[0]@g[4],np.eye(16))
      for eps in (-1,1):
        inner,outer=characteristic_bases(branch,eps)
        np.testing.assert_allclose(inner@inner.conj().T+outer@outer.conj().T,np.eye(64),atol=3e-16)
        np.testing.assert_allclose(A@inner,eps*inner,atol=3e-16)
        np.testing.assert_allclose(A@outer,-eps*outer,atol=3e-16)
        assert inner.shape==outer.shape==(64,32)


def test_actual_field_and_source_on_nonzero_complete_characteristic_data():
    # Analytic coefficient control only, not a benchmark state or vacuum.
    t=np.linspace(0,.2,6);r=np.array([.1,.3,.5]);full=full_d5_localized_lepton_trace()
    c={};rng=np.random.default_rng(516)
    vectors=rng.normal(size=(384,2))+1j*rng.normal(size=(384,2))
    for side,eps in (('plus',1),('minus',-1)):
      for branch in ('particle','conjugate'):
        g=full['gamma5D_'+branch];A=eps*np.kron(g[0]@g[4],np.eye(16))
        T=1j*np.kron(g[0],np.eye(16));shape=(6,3,64,64);z=np.zeros(shape,complex)
        c[side+'_'+branch]=dict(time=np.broadcast_to(T,shape),
            radial=np.broadcast_to(T@A,shape),body=z,time_source=z[None],radial_source=z[None],
            body_source=np.broadcast_to(T,(1,*shape)))
    app,report=solve_child_characteristic_cell(c,t,r)
    for side,eps in (('plus',1),('minus',-1)):
        V=np.zeros((6,3,384,1),complex)
        for family in range(3):
          for bi,branch in enumerate(('particle','conjugate')):
            sl=slice((2*family+bi)*64,(2*family+bi+1)*64)
            g=full['gamma5D_'+branch];A=eps*np.kron(g[0]@g[4],np.eye(16))
            for ti,time in enumerate(t):
              for ri,radius in enumerate(r):V[ti,ri,sl,0]=vectors[sl,0]+radius*vectors[sl,1]-time*A@vectors[sl,1]
        X=-t[:,None,None,None]*V
        data=np.zeros((8,384,1),complex);dx=np.zeros_like(data);data[:3]=V[0];dx[:3]=X[0]
        for family in range(3):
          for bi,branch in enumerate(('particle','conjugate')):
            sl=slice((2*family+bi)*64,(2*family+bi+1)*64)
            inner,outer=characteristic_bases(branch,eps)
            for ti in range(1,6):
                data[ti+2,sl]=np.r_[inner.conj().T@V[ti,0,sl],outer.conj().T@V[ti,-1,sl]]
                dx[ti+2,sl]=np.r_[inner.conj().T@X[ti,0,sl],outer.conj().T@X[ti,-1,sl]]
        times=[.037,.143];radii=[.137,.419]
        actual=apply_child_cell_field(app,side,data,dx,times=times,radii=radii)
        for it,time in enumerate(times):
          for ir,radius in enumerate(radii):
            for family in range(3):
              for bi,branch in enumerate(('particle','conjugate')):
                sl=slice((2*family+bi)*64,(2*family+bi+1)*64)
                g=full['gamma5D_'+branch];A=eps*np.kron(g[0]@g[4],np.eye(16))
                expected=vectors[sl,0]+radius*vectors[sl,1]-time*A@vectors[sl,1]
                np.testing.assert_allclose(actual['value'][it,ir,sl,0],expected,atol=1e-13)
                np.testing.assert_allclose(actual['source'][it,ir,sl,0],-time*expected,atol=1e-13)
        unknown=apply_child_cell_field(app,side,data,times=[0],radii=[r[-1]])
        assert unknown['source'] is None and unknown['radial_source'] is None
    assert report['coordinates_per_collar']==3072


def test_outgoing_source_differentiates_inverse_time_covector():
    # A finite analytic coefficient control with fixed numerical boundary
    # covectors isolates d(T^-1). It is not an adopted physical background.
    t=np.linspace(0,.2,6);r=np.array([.1,.3,.5]);f=full_d5_localized_lepton_trace()
    g=f['gamma5D_particle'];T=1j*np.kron(g[0],np.eye(16));R=1j*np.kron(g[4],np.eye(16))
    Td=.3*np.eye(64);shape=(6,3,64,64);zero=np.zeros(shape,complex)
    def coefficients(a,source):
        return dict(plus_particle=dict(time=np.broadcast_to(T+a*Td,shape),
            radial=np.broadcast_to(R,shape),body=zero,time_source=np.broadcast_to(source,(1,*shape)),
            radial_source=zero[None],body_source=zero[None]))
    app,_=solve_child_characteristic_cell(coefficients(0,Td),t,r)
    h=1e-6;plus,_=solve_child_characteristic_cell(coefficients(h,np.zeros((64,64))),t,r)
    minus,_=solve_child_characteristic_cell(coefficients(-h,np.zeros((64,64))),t,r)
    for bi in range(int(app['plus_particle_block_count'])):
        p='plus_particle_block'+str(bi)+'_'
        finite=(plus[p+'response']-minus[p+'response'])/(2*h)
        np.testing.assert_allclose(app[p+'response_source'][0],finite,atol=2e-8,rtol=2e-6)
