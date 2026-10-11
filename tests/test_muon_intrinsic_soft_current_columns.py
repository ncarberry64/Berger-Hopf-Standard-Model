"""Independent source-image and original Gaussian-action checks."""
import numpy as np
from scipy.linalg import block_diag,eigh
from bhsm.interface.muon_intrinsic_soft_current_columns import _branch_application,soft_current_angular_images


def control():
    rng=np.random.default_rng(1845)
    C=lambda shape:rng.normal(size=shape)+1j*rng.normal(size=shape)
    Ao,Ae=C((2,2)),C((3,3));Po=1000*np.eye(2)+Ao.conj().T@Ao;Pe=1000*np.eye(3)+Ae.conj().T@Ae
    po,Vo=eigh(Po);pe,Ve=eigh(Pe);Xi,Xadj=C((3,2,3)),C((3,2,3))
    d=dict(A_odd=Ao,A_even=Ae,p_odd=po,p_even=pe,V_odd=Vo,V_even=Ve,
        Xi=Xi,Xadj=Xadj,square_left=Ao.conj().T@Xi,square_right=Xadj@Ae,
        left_odd=C((2,2,2)),right_even=C((2,3,1)),left_even=C((3,3,2)),right_odd=C((3,2,1)),length=1.,lapse=1.)
    so=rng.normal(size=(2,2));se=rng.normal(size=(3,3))
    s=dict(positive_H_odd=30*np.eye(2)+so.T@so,positive_H_even=40*np.eye(3)+se.T@se,
        delta_positive_H_even_odd=rng.normal(size=(3,3,2)),action_Gram_scalar=1.7)
    return d,s


def original(d,s,axis,epsilon):
    A=block_diag(d['A_odd'],d['A_even']);A[:2,2:]=epsilon*d['Xi'][axis];A[2:,:2]=epsilon*d['Xadj'][axis].conj().T
    GF=np.linalg.solve(1000*np.eye(5)+A.conj().T@A,A.conj().T)
    H=block_diag(s['positive_H_odd'],s['positive_H_even']);H[2:,:2]=epsilon*s['delta_positive_H_even_odd'][axis];H[:2,2:]=H[2:,:2].T
    GH=np.linalg.inv(H)/s['action_Gram_scalar'];B=np.zeros((5,5,3),complex)
    B[:2,:2,:2]=d['left_odd'];B[:2,2:,2:]=d['right_even'];B[2:,2:,:2]=d['left_even'];B[2:,:2,2:]=d['right_odd']
    return np.einsum('aiu,ij,bjv,ab->uv',B.conj(),GF,B,GH)


def test_two_field_placements_match_original_source_action():
    d,s=control();r=_branch_application(d,s,0,12,.75,6)
    for axis in range(3):
        h=1e-5;finite=(original(d,s,axis,h)-original(d,s,axis,-h))/(2*h)
        np.testing.assert_allclose(r['forward']['total'][axis],finite[:2,2:],rtol=2e-7,atol=2e-13)
        np.testing.assert_allclose(r['reverse']['total'][axis],finite[2:,:2],rtol=2e-7,atol=2e-13)
    for placement in ('forward','reverse'):
        assert np.linalg.norm(r[placement]['scalar_propagator_left_field_image'])>0
        assert np.linalg.norm(r[placement]['scalar_propagator_right_field_image'])>0


def test_complete_reached_products_and_exact_degree_zeros():
    a=soft_current_angular_images()
    assert len(a['labels']['Fodd'])==56 and len(a['labels']['Feven'])==84
    assert len(a['labels']['Xout'])==10 and len(a['labels']['Xin'])==4
    assert max(a['product_residuals'].values())<2e-13
    G=a['gaunts']['right_even']
    n6=[i for i,l in enumerate(a['labels']['Feven'])if l[0]==6]
    assert not np.any(G[n6]) # n1 times n1+n3 cannot reach n6.
    assert a['no_starting_Higgs_loop_complement_bound']


def test_constant_orientation_reuses_same_factor_and_exact_identity_vertex():
    from bhsm.interface.muon_intrinsic_soft_constant_columns import constant_input_image_data
    a=soft_current_angular_images();no,ne=56*6,84*6
    d=dict(angular=a,length=1.,lapse=1.,Xi=np.zeros((3,no,ne)),Xadj=np.zeros((3,no,ne)))
    for parity,n in (('odd',no),('even',ne)):
        d['A_'+parity]=np.eye(n);d['P_'+parity]=np.eye(n);d['p_'+parity]=np.ones(n);d['V_'+parity]=np.eye(n)
    M=np.array([np.eye(6)*(c+1)for c in range(4)])
    b=constant_input_image_data(d,M)
    assert b['A_odd']is d['A_even']and b['A_even']is d['A_odd']
    assert b['left_odd'].shape==(80,ne,24)and b['left_even'].shape==(140,no,24)
    for c in range(4):
        for h in range(20):
            np.testing.assert_array_equal(b['right_even'][c*20+h,h*6:(h+1)*6],.75*M[c])
    assert not np.any(b['right_even'][:,120:])
