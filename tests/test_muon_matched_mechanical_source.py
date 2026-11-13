"""New actual-source checks, separate from physical native evaluations."""
import json
from math import comb
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_matched_mechanical_source import angular_blocks, epsilon

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts/muon_matched_mechanical_source_20261002'


@pytest.fixture(scope='module')
def packet():
    with np.load(ART/'replay_reference/matched_source_and_weak_actions.npz') as z:
        arrays={k:np.array(z[k]) for k in z.files}
    return arrays,json.loads((ART/'replay_reference/result.json').read_text())


def basis(n,w):
    # Independent symmetric-power evaluation of the normalized Wigner
    # functions, rather than the Gaunt multiplication used by the producer.
    D=np.zeros((n+1,n+1),complex)
    for r in range(n+1):
        for s in range(n+1):
            for a in range(n-s+1):
                b=r-a
                if 0<=b<=s:
                    D[r,s]+=np.sqrt(comb(n,s)/comb(n,r))*comb(n-s,a)*comb(s,b)*(
                        w[0,0]**(n-s-a)*w[1,0]**a*w[0,1]**(s-b)*w[1,1]**b)
    return np.sqrt(n+1)*D.conj()


def test_complete_one_form_matches_rank16_carrier_at_actual_modes(packet):
    a,_=packet
    # One generic quotient point checks orientation/conjugation. No
    # spectrum, physical state or environment is selected by this point.
    q=np.array([1.,2.,3.,4.]);q/=np.linalg.norm(q)
    sigma=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]])
    w=q[0]*np.eye(2)-1j*np.einsum('a,aij->ij',q[1:],sigma)
    carrier=a['unit_trace_carrier_basis']
    jmath=2*np.sqrt(2)*carrier[:3]
    U=q[0]*np.eye(16)+np.einsum('a,aij->ij',q[1:],jmath)
    # Weak singlets have U=1, not q0. Select them from existing carrier.
    singlet=np.sum(abs(jmath),axis=(0,1))==0
    U[np.diag_indices(16)]=np.where(singlet,1,U.diagonal())
    before=np.einsum('Acemk,mk,eij->Acij',a['original_n1'],basis(1,w),carrier)
    after=sum(np.einsum('Acemk,mk,eij->Acij',a[f'transformed_n{n}'],basis(n,w),carrier) for n in (1,3))
    direct=np.einsum('ij,Acjk,lk->Acil',U,before,U.conj())
    assert np.linalg.norm(after-direct)<2e-14
    assert np.linalg.norm(a['transformed_n3'])>3


def test_covariance_includes_connected_output_before_cancellation(packet):
    a,r=packet;lam=r['frontier_lambda']
    for n in (1,3):
        C,T,_,_,_=angular_blocks(n)
        v=a[f'transformed_n{n}'];f=v.reshape(8,12*(n+1),n+1)
        direct=np.einsum('ij,Ajk->Aik',C+(lam-1)*T,f).reshape(v.shape)
        assert np.linalg.norm(direct-a[f'covariance_rhs_n{n}'])<8e-15
    assert 'covariance_rhs_n5' in a
    assert np.linalg.norm(a['covariance_rhs_n5'])<1e-14
    assert r['checks']['source_covariance_absolute']<1e-14


def test_source_sign_matches_saved_lepton_Xi_without_new_contact_calculation(packet):
    a,_=packet
    with np.load(ROOT/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz') as z:
        old={k:np.array(z[k]) for k in ('Xi_complete','real_mode_coefficients','input_labels','output_labels')}
    coeff=-np.einsum('cij,Acmk->Aijmk',a['saved_gamma_LR'][1:],old['real_mode_coefficients'])
    ni=len(old['input_labels']);no=len(old['output_labels'])
    for oi,(n,spin,m,k) in enumerate(old['output_labels']):
        if n!=1:
            continue
        for ii,(nin,si,mi,ki) in enumerate(old['input_labels']):
            if nin!=0:
                continue
            for lr in range(2):
                for lr2 in range(2):
                    assert np.linalg.norm(old['Xi_complete'][:,lr*no+oi,lr2*ni+ii]-
                        coeff[:,2*lr+spin,2*lr2+si,(1-m)//2,(1-k)//2])<1e-14


def test_full_curvature_contact_from_rank16_commutators(packet):
    a,r=packet;lam=r['frontier_lambda'];E=epsilon()
    H=a['unit_trace_carrier_basis'];jm=2*np.sqrt(2)*H[:3]
    contact=np.zeros((3,4,3,4),complex)
    for i in range(3):
        for j in range(3):
            for c in range(4):
                for d in range(4):
                    F=2*lam*(lam-1)*np.einsum('k,kab->ab',E[:,i,j],jm)
                    contact[i,c,j,d]=np.trace(F.conj().T@(H[c]@H[d]-H[d]@H[c]))
    for n in (1,3):
        op=np.einsum('icjd,mn->icmjdn',contact,np.eye(n+1)).reshape(12*(n+1),-1)
        v=a[f'transformed_n{n}'];f=v.reshape(8,12*(n+1),n+1)
        expected=np.einsum('ij,Ajk->Aik',op,f).reshape(v.shape)
        assert np.linalg.norm(expected-a[f'curvature_contacts_n{n}'])<8e-15
    assert r['checks']['full_mixed_curvature_contact_norm']>4
    assert np.linalg.norm(a['QQ_curvature_contact_corner'])<1e-14


def test_corrected_row_is_consumed_with_weight_sign_and_scalar_contacts(packet):
    a,r=packet;lam=a['mechanical_lambda'];qnorm=16/3
    assert np.ptp(a['full_pointwise_W'])>0
    for n in (1,3):
        h=a[f'mixed_rows_n{n}']
        expected=-a['angular_density'][:,None,None,None,None,None]*(
            h[0][None]+lam[:,None,None,None,None,None]*h[1][None]+
            lam[:,None,None,None,None,None]**2*h[2][None])/qnorm
        assert np.linalg.norm(expected-a[f'weak_angular_row_n{n}'])==0
        # Independent trace-invariance contact, including BOTH lambda jets.
        J=a[f'gauss_contact_n{n}'];N=a['lambda_tau']-a['shift']*a['lambda_rho']
        expected=-(a['electric']*a['shift']*N+a['radial']*a['lambda_rho'])[:,None,None,None,None]*J[None]/qnorm
        assert np.linalg.norm(expected-a[f'constraint_radial_background_contact_n{n}'])<1e-13
    assert np.linalg.norm(a['constraint_temporal_background_contact_n3'])>0
    assert r['preserved_faces']['past_core_outward']==-1
    assert r['preserved_faces']['future_face']=='owned canonical stop'
    assert r['ledger']['exterior_affine_return'] is None
    assert r['ledger']['same_owner_induced_matching'] is None
    assert r['physical_a_mu'] is None and r['physical_g_mu'] is None
    assert r['actual_execution']['physical_transfer_directions']==0
