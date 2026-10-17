"""Independent spectral Hessian and generalized-pairing checks."""
import numpy as np
from scipy.linalg import eigh
from scipy.special import exp1
from bhsm.interface.muon_changing_closed_source_heat import source_heat_pair_at_y


def test_both_orders_and_contact_match_full_matrix_function_projected_trace():
    rng=np.random.default_rng(31017)
    p=np.diag([2.,3.]);pn=np.diag([5.,7.,9.])
    f=rng.normal(size=(3,3,2))*.1+1j*rng.normal(size=(3,3,2))*.1
    c=rng.normal(size=(3,3,2,2))*.04
    c=(c+c.swapaxes(0,1))/2;c=(c+c.swapaxes(2,3))/2
    polynomial=dict(n0_pencil=(p,p*0,p*0),n1_pencil=(pn,pn*0,pn*0),
        first_source=(f,f*0,f*0),contact=(c,c*0,c*0),n0_Gram=np.eye(2),n1_Gram=np.eye(3))
    out=source_heat_pair_at_y(polynomial,0.,.3,lag_order=64)
    def trace(a,b):
        full=np.block([[p+a*b*c[0,1],a*f[0].conj().T+b*f[1].conj().T],
            [a*f[0]+b*f[1],pn]])
        lam,U=eigh(full)
        return np.sum(abs(U[:2])**2*exp1(.3*lam)[None])
    step=2e-4
    fd=(trace(step,step)-trace(step,-step)-trace(-step,step)+trace(-step,-step))/(4*step**2)
    assert abs(out['available_source_pair'][0,1]-fd)<2e-8
    assert np.array_equal(out['opposite_order_two_insertion'],out['ordered_two_insertion'].T)
    assert abs(out['source_square_contact'][0,1])>1e-4
    assert abs(out['ordered_two_insertion'][0,1])>1e-4


def test_generalized_gram_change_of_coordinates_keeps_each_term():
    p=np.diag([4.,6.]);pn=np.diag([8.,12.,15.]);rng=np.random.default_rng(412)
    f=rng.normal(size=(3,3,2))+1j*rng.normal(size=(3,3,2))
    c=np.einsum('Aki,Bkj->ABij',f.conj(),f);c+=c.swapaxes(0,1).copy()
    plain=dict(n0_pencil=(p,p*0,p*0),n1_pencil=(pn,pn*0,pn*0),first_source=(f,f*0,f*0),
        contact=(c,c*0,c*0),n0_Gram=np.eye(2),n1_Gram=np.eye(3))
    t=np.array([[2.,.3],[0.,.7]]);tn=np.array([[.6,.2,0.],[0.,1.2,.1],[0.,0.,1.8]])
    transformed=dict(n0_pencil=tuple(t.T@a@t for a in plain['n0_pencil']),
        n1_pencil=tuple(tn.T@a@tn for a in plain['n1_pencil']),
        first_source=tuple(np.einsum('ij,Ajk,kl->Ail',tn.T,a,t) for a in plain['first_source']),
        contact=tuple(np.einsum('ij,ABjk,kl->ABil',t.T,a,t) for a in plain['contact']),
        n0_Gram=t.T@t,n1_Gram=tn.T@tn)
    a=source_heat_pair_at_y(plain,0.,.2);b=source_heat_pair_at_y(transformed,0.,.2)
    for key in a:np.testing.assert_allclose(a[key],b[key],rtol=2e-13,atol=1e-14)
