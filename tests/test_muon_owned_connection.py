"""New actual background/source actions; no old producer is replayed."""
from pathlib import Path
import numpy as np
from scipy.linalg import expm

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts/muon_owned_connection_20261002/replay_reference'

def phi(n,alpha,beta,gamma):
    j=n/2;m=np.arange(n,-n-1,-2)/2;p=np.zeros((n+1,n+1))
    for k in range(1,n+1):p[k-1,k]=np.sqrt((j-m[k])*(j+m[k]+1))
    D=np.exp(-1j*m*alpha)[:,None]*expm(-1j*beta*(p-p.T)/(2j))*np.exp(-1j*m*gamma)[None]
    return np.sqrt(n+1)*D.conj()


def test_actual_background_action_against_pointwise_clifford_multiplication():
    with np.load(ART/'owned_connection_actions.npz') as p:
        action=p['unit_independent_background_actions'];out=p['output_labels'];sigma=p['spin_sigma'];weak=p['weak_sigma']
    with np.load(ROOT/'artifacts/muon_source_weak_extension_20261002/replay_reference/independent_source_quotient.npz') as p:U=p['angular_frame']
    with np.load(ROOT/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz') as p:inp=p['input_labels']
    with np.load(ROOT/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz') as p:R=p['rotation_coefficients']
    for angles in [(0.21,0.43,0.78),(1.1,1.3,2.2),(3.7,2.4,0.3)]:
        modes={n:phi(n,*angles) for n in range(4)}
        psi=np.zeros((2,16),complex)
        for j,(n,s,m,k) in enumerate(inp):psi[s]+=modes[n][(n-m)//2,(n-k)//2]*U[j]
        rp=np.einsum('admk,mk->ad',R,modes[2])
        direct=np.einsum('asi,dw,ad,ic->swc',sigma,weak[:,:,1],rp,psi)
        actual=np.zeros_like(direct)
        for j,(n,lr,s,w,m,k) in enumerate(out):
            if lr==0:actual[s,w]+=modes[n][(n-m)//2,(n-k)//2]*action[j]
        np.testing.assert_allclose(actual,direct,rtol=2e-14,atol=2e-14)


def test_weak_and_angular_complement_survive_the_actual_frame():
    with np.load(ART/'owned_connection_actions.npz') as p:
        whole=p['unit_independent_background_actions'];conn=p['unit_independent_connected_background_actions']
        labels=p['output_labels'];nu=np.array([lr==0 and w==0 for n,lr,s,w,m,k in labels])
        high=np.array([n>=2 for n,lr,s,w,m,k in labels])
        assert np.linalg.norm(conn)>4
        assert np.linalg.norm(whole[nu])>3.9
        assert np.linalg.norm(whole[high])>4.6
        np.testing.assert_allclose(p['unit_independent_background_compression'],p['unit_independent_background_compression'].conj().T,atol=2e-14)


def test_full_source_cross_is_retained_despite_small_selected_compression():
    with np.load(ART/'owned_connection_actions.npz') as p:
        X=p['background_source_cross_full_weak_unit']
        assert np.linalg.norm(X)>3.7
        np.testing.assert_allclose(X,X.conj().transpose(0,2,1),atol=2e-14)
        assert np.linalg.norm(p['background_source_cross_connected'])>1.8
        # Numerical cancellation in selected test columns is not an operator
        # state-independence result, Pauli number, or divergent-term proof.
        assert np.linalg.norm(p['background_source_cross_unit'])<2e-14


def test_regular_parent_coefficient_and_same_boundary_metric():
    with np.load(ROOT/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz') as p:
        A=p['A'];B=p['B'];r=p['base_radius'];Rb=p['boundary_radius']
    with np.load(ART/'owned_connection_actions.npz') as p:
        coeff=p['parent_sigma1_background_prefactor'];lam=p['mechanical_lambda_boundary']
        assert np.isfinite(coeff).all()
        np.testing.assert_array_equal(coeff[:,0],0)
        target=(-B*B/(A*A+B*B))[:,1:]/r[:,1:]
        np.testing.assert_allclose(coeff[:,1:],target,rtol=2e-14,atol=2e-14)
        np.testing.assert_allclose(p['child_background_prefactor'],lam/Rb,rtol=2e-14,atol=2e-14)
