"""Independent original-component and dual-pairing controls."""
import numpy as np

from bhsm.interface.electromagnetic_carrier_original_maxwell import (
    even_angular_space,geometric_dual_split,original_maxwell_covectors,
)
from bhsm.interface.muon_baton_zoo_original_validation import independent_original_maxwell_weak


def test_factored_all_rows_equal_literal_indexed_tests():
    space=even_angular_space();nr=3;nh=len(space['weights'])
    rng=np.random.default_rng(161016)
    a,at,ar=[rng.normal(size=(nr,nh,5,4))*0.07 for _ in range(3)]
    ea=rng.normal(size=(nr,nh,3,5,4))*0.03
    density=np.broadcast_to(np.array([1.4,0.8,0.7,1.6,0.12]),(nr,nh,5))
    b=rng.normal(size=(nr,4));br=rng.normal(size=(nr,4));wr=np.array([0.2,0.3,0.5])
    factored=original_maxwell_covectors(a,at,ar,ea,density,wr,b,br,space,normalization=0.9)
    # Independent direct test tensors for diverse coordinates, including At,
    # Ar and an angular derivative. No local-jet factorization is reused.
    indices=[(0,0,2,0),(1,1,0,3),(2,3,1,8),(3,4,3,9)]
    v=np.zeros((nr,nh,len(indices),5,4));vt=v.copy();vr=v.copy()
    ev=np.zeros((nr,nh,len(indices),3,5,4))
    for k,(r,f,c,h) in enumerate(indices):
        v[:,:,k,f,c]=b[:,r,None]*space['values'][None,:,h]
        vr[:,:,k,f,c]=br[:,r,None]*space['values'][None,:,h]
        ev[:,:,k,:,f,c]=b[:,r,None,None]*space['derivatives'][None,:,:,h]
    def literal(value,time,radial,angular):
        return independent_original_maxwell_weak(connection=a.reshape(-1,5,4),time_derivative=at.reshape(-1,5,4),
            radial_derivative=ar.reshape(-1,5,4),angular_derivative=ea.reshape(-1,3,5,4),
            tests=value.reshape(-1,len(indices),5,4),tests_time=time.reshape(-1,len(indices),5,4),
            tests_radial=radial.reshape(-1,len(indices),5,4),tests_angular=angular.reshape(-1,len(indices),3,5,4),
            metric_densities=density.reshape(-1,5),quadrature=(0.9*wr[:,None]*space['weights']).ravel())['original_weak_rows']
    direct=literal(v,vt,vr,ev)
    direct_rate=literal(vt,v,vt,np.zeros_like(ev))
    np.testing.assert_allclose(direct,[factored['value_rows'][i] for i in indices],atol=1e-16,rtol=1e-14)
    np.testing.assert_allclose(direct_rate,[factored['rate_rows'][i] for i in indices],atol=1e-16,rtol=1e-14)


def test_covector_complement_is_covariant_under_shifted_basis_change():
    rng=np.random.default_rng(1526)
    x=rng.normal(size=(5,5));g=x.T@x+np.eye(5)
    s=rng.normal(size=(5,2));r=rng.normal(size=5)
    first=geometric_dual_split(r,g,s)
    c=np.eye(5);c[0,1]=0.37;c[1,0]=-0.14
    second=geometric_dual_split(c.T@r,c.T@g@c,np.linalg.solve(c,s))
    np.testing.assert_allclose(second['complement_covector'],c.T@first['complement_covector'],atol=2e-15)
    np.testing.assert_allclose(second['tangent_covector'],first['tangent_covector'],atol=1e-15)
    assert first['complement_annihilation_defect']<2e-15


def test_degree_five_rule_does_not_certify_degree_eight_action():
    small=even_angular_space();large=even_angular_space(haar_degree=8)
    assert small['reconstruction_defect']<2e-15
    assert large['reconstruction_defect']<2e-14
    # Explicit witness guards against promoting the small rule to finite
    # nonabelian nonlinear action integration.
    assert abs(small['weights']@(small['quaternions'][:,0]**8)-11/128)<1e-16
    assert abs(large['weights']@(large['quaternions'][:,0]**8)-7/128)<1e-16


def test_complete_higgs_neutral_pullback_has_no_amplitude_restoring_force():
    from bhsm.interface.muon_primal_electromagnetic_source import higgs_aligned_charge
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    h=np.array([0.2+0.3j,0.9-0.1j]);dh=np.array([0.3-0.2j,-0.1+0.4j])
    a=higgs_aligned_charge(h,dh);t=higgs_u2_real_representation()['complex_generators']
    q=np.einsum('c,cij->ij',a['unit_Tr16_coefficients'],t)
    dq=np.einsum('c,cij->ij',a['unit_Tr16_coefficient_rate'],t)
    np.testing.assert_allclose(q@h,0,atol=9e-17)
    # A held-Q H partial is nonzero; the moving charge contact cancels it.
    assert np.linalg.norm(q@dh)>0.1
    np.testing.assert_allclose(dq@h+q@dh,0,atol=1e-16)
    # Literal covariant Higgs derivative remains equal after adding an
    # aligned neutral field, even when H itself changes off the base point.
    connection=np.array([[0.1j,0.2],[-0.2,-0.1j]])
    for step in (-0.1,0.,0.1):
        hp=h+step*dh
        ap=higgs_aligned_charge(hp,dh)
        qp=np.einsum('c,cij->ij',ap['unit_Tr16_coefficients'],t)
        np.testing.assert_allclose((connection+0.7*qp)@hp,connection@hp,atol=9e-17)
