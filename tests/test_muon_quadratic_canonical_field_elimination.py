import numpy as np
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_quadratic_canonical_field_elimination import eliminate_quadratic_canonical_fields


def test_exact_field_Gauss_saddle_and_geometry_Schur_match_reduced_action_direction():
    n=4;m=3;field=np.array([1,2,3,5,6]);geometry=np.array([0,4])
    C=np.zeros((2,n+m));C[0,5]=1;C[1,6]=1
    Z=np.zeros((n+m,2));Z[[1,5],0]=1;Z[[2,6],1]=1
    def evaluate(e):
        x=[Jet.affine(v,np.eye(n+m)[j])for j,v in enumerate(e[n:])]
        a=x[0].exp();b=(.3*x[4]).exp();c=2+.2*x[0]*x[4]
        L=x[0]**2/2+x[4]**2+.5*a*(x[1]-x[5])**2+.5*b*(x[2]-x[6])**2
        L+=.5*c*x[3]**2+(x[0]+.2j*x[4])*x[3]
        G=np.r_[np.zeros(n,complex),L.gradient];H=np.zeros((2*n+m,)*2,complex);H[n:,n:]=L.hessian
        return dict(value=L.value,gradient=G,hessian=H)
    eta=np.r_[np.zeros(n),np.array([.2+.1j,.5j,.4,.6,.3-.1j,.2j,-.4])]
    p=np.array([.2,0,0,.7+.1j]);frame=dict(named_frame_covectors=C,literal_generators=Z)
    args=dict(field_indices=field,geometry_indices=geometry,frame_reference=eta[n:].copy())
    a=eliminate_quadratic_canonical_fields(eta,p,evaluate,frame,**args)
    np.testing.assert_allclose(a['original_field_rows'],0,atol=5e-16)
    np.testing.assert_allclose(C@(a['coefficients'][n:]-eta[n:]),0,atol=5e-16)
    np.testing.assert_allclose(a['literal_generator_image'],0,atol=5e-16)
    np.testing.assert_allclose(a['field_frame_reactions'],0,atol=5e-16)
    direction=np.array([.3+.2j,-.4j]);eps=2e-6
    ep,em=eta.copy(),eta.copy();ep[n+geometry]+=eps*direction;em[n+geometry]-=eps*direction
    ap=eliminate_quadratic_canonical_fields(ep,p,evaluate,frame,**args)
    am=eliminate_quadratic_canonical_fields(em,p,evaluate,frame,**args)
    fd=(ap['reduced_geometry_rows']-am['reduced_geometry_rows'])/(2*eps)
    np.testing.assert_allclose(a['reduced_geometry_Jacobian']@direction,fd,rtol=2e-10,atol=2e-10)
    np.testing.assert_allclose(a['implicit_original_field_geometry_rows'],0,atol=5e-16)
