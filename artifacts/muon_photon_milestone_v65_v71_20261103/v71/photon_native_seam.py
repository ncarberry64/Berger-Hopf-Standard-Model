"""Electromagnetic specialization of the owned independent-left seam row.

This evaluates coefficients and their local derivatives, never physical traces
or a complete relative/native kernel. Normal monomials remain unassigned.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json
import numpy as np
from prepare_evidence import save,npz
HERE=Path(__file__).resolve().parent
def comm(a,b):return a@b-b@a
def maximum(a):return float(np.max(abs(a)))
def split(m):
    lr=np.zeros_like(m);rl=np.zeros_like(m)
    lr[...,:12,12:]=m[...,:12,12:];rl[...,12:,:12]=m[...,12:,:12]
    return np.stack((lr,rl))
def lower(m):
    a=np.zeros((36,36),complex);a[18:,:18]=m;return a
def block(a,b):
    z=np.zeros((36,36),complex);z[:18,:18]=a;z[18:,18:]=b;return z

def photon_jets(h):
    """H-selected generator and all real H first/mixed derivatives."""
    H=h[:2]+1j*h[2:];dH=np.array([[1,0],[0,1],[1j,0],[0,1j]])
    T=np.outer(H,H.conj());n=np.vdot(H,H).real
    if n<=0:raise ValueError('H-selected photon requires nonzero owned H')
    Ti=np.array([np.outer(v,H.conj())+np.outer(H,v.conj()) for v in dH])
    ni=2*np.real(dH.conj()@H)
    Tij=np.array([[np.outer(v,w.conj())+np.outer(w,v.conj()) for w in dH] for v in dH])
    nij=2*np.real(dH.conj()@dH.T)
    P=T/n;Pi=Ti/n-ni[:,None,None]*T/n**2
    Pij=Tij/n-(Ti[:,None]*ni[None,:,None,None]+Ti[None]*ni[:,None,None,None]
                    +nij[:,:,None,None]*T)/n**2+2*ni[:,None,None,None]*ni[None,:,None,None]*T/n**3
    Q=np.zeros((18,18),complex);Q[:12,:12]=-np.kron(P,np.eye(6));Q[12:,12:]=-np.eye(6)
    Gi=np.zeros((4,18,18),complex);Gij=np.zeros((4,4,18,18),complex)
    for i in range(4):
        Gi[i,:12,:12]=1j*np.kron(Pi[i],np.eye(6))
        for j in range(4):Gij[i,j,:12,:12]=1j*np.kron(Pij[i,j],np.eye(6))
    return -1j*Q,Gi,Gij

def angular_kernel(theta,matrices):
    R=theta[0];M=split(np.einsum('h,hij->ij',theta[18:22],matrices[13:17]))
    G=1j*matrices[17:21];alpha=1j*matrices[21:24]
    g,_,_=photon_jets(theta[18:22]);A=np.einsum('ac,cij->aij',theta[6:18].reshape(3,4),G)
    return np.array([[-alpha[a]@comm(comm(A[a],g),mh)/R for a in range(3)] for mh in M])

def calculate():
    path=HERE/'evidence/inputs.npz';prov=json.loads((HERE/'evidence/provenance.json').read_text())
    assert sha256(path.read_bytes()).hexdigest()==prov['input_sha256']
    b=dict(np.load(path,allow_pickle=False));t=b['theta22'];mat=b['term_matrices']
    assert mat.shape==(24,18,18) and np.array_equal(b['term_slots'][21:],[1,2,3])
    R,N=t[:2];G=1j*mat[17:21];alpha=1j*mat[21:24];mass_basis=mat[13:17]
    M=split(np.einsum('h,hij->ij',t[18:22],mass_basis));Mi=split(mass_basis)
    g,gi,gij=photon_jets(t[18:22]);s=np.sqrt(16/3)*b['stabilizer_value']
    sg=np.sqrt(16/3)*b['stabilizer_gradient']
    A=np.einsum('ac,cij->aij',t[6:18].reshape(3,4),G)
    Dg=np.array([comm(ai,g) for ai in A]);K=angular_kernel(t,mat)
    zero=1j*comm(g,M)
    zero_i=np.array([[1j*(comm(gi[i],mh)+comm(g,Mi[ch,i])) for i in range(4)] for ch,mh in enumerate(M)])
    zero_ij=np.array([[[1j*(comm(gij[i,j],mh)+comm(gi[i],Mi[ch,j])+comm(gi[j],Mi[ch,i]))
                      for j in range(4)] for i in range(4)] for ch,mh in enumerate(M)])
    checks=dict(original_charge_representation=maximum(G-b['gauge36'][:,:18,:18]),
        original_H_selected_photon=maximum(g-np.einsum('c,cij->ij',s,G)),
        original_photon_first_derivative=maximum(gi-np.einsum('ch,cij->hij',sg,G)),
        scalar_seam_zero=maximum(zero),scalar_seam_total_first_zero=maximum(zero_i),
        scalar_seam_total_mixed_zero=maximum(zero_ij),
        harmonic_derivative_seam_zero=maximum(np.array([[-a@comm(g,mh)/R for a in alpha] for mh in M])))
    # Gauge covariance converts the surviving source to the covariant Higgs mass gradient.
    alternative=np.array([[alpha[a]@comm(g,comm(A[a],mh))/R for a in range(3)] for mh in M])
    checks['covariant_Higgs_gradient_identity']=maximum(K-alternative)
    # Reconcile this connection insertion with the ORIGINAL full spatial
    # coefficient of P_lambda=L R_lambda+L_lambda R. The temporal factor
    # and domain pieces are not in this check and remain required.
    W0=1.5*mat[0]/R+M.sum(axis=0)-1j*sum(alpha[a]@A[a] for a in range(3))/R
    U=-1j*g/N
    spatial_factor_source=comm(W0,U)
    connection_insertion=-sum(alpha[a]@Dg[a] for a in range(3))/(R*N)
    checks['original_spatial_factor_connection_insertion']=maximum(spatial_factor_source-connection_insertion)
    mechanical=np.sqrt(8)*np.column_stack((np.eye(3),np.zeros(3)))
    owned_A=b['gauge_values49x5x4'][-1,2:]+(b['density49x8'][-1,5]-1)*mechanical
    checks['same_initializer_angular_connection']=maximum(t[6:18].reshape(3,4)-owned_A)
    # Original independent-left Green row, with both symbolic normal channels.
    J=-1j*N*R**3*block(np.zeros((18,18)),np.zeros((18,18)))
    J[:18,18:]=-1j*N*R**3*np.eye(18);J[18:,:18]=-1j*N*R**3*np.eye(18)
    Ns=[lower(1j*mh) for mh in M]
    for ch,nn in enumerate(Ns):
        u=-1j*g/N;f=-J@comm(block(u,u),nn)
        checks[f'original_scalar_Green_row_{ch}']=maximum(f-block(R**3*zero[ch],np.zeros((18,18))))
        for a in range(3):
            v=-alpha[a]@Dg[a]/(R*N);uu=block(v,-v)
            f=-J@comm(uu,nn)
            checks[f'original_angular_Green_row_{ch}_{a}']=maximum(f-block(R**3*K[ch,a],np.zeros((18,18))))
            for d,n2 in enumerate(Ns):checks[f'no_quadratic_normal_monomial_{ch}_{d}_{a}']=maximum(J@nn@uu@n2)
    # Actual first coordinate jets, including moving Higgs photon and radius.
    grad=np.zeros((22,2,3,18,18),complex)
    grad[0]=-K/R
    for j in range(6,18):
        a,c=divmod(j-6,4)
        for ch,mh in enumerate(M):grad[j,ch,a]=-alpha[a]@comm(comm(G[c],g),mh)/R
    for h in range(4):
        for ch,mh in enumerate(M):
            for a in range(3):grad[18+h,ch,a]=-alpha[a]@(comm(comm(A[a],gi[h]),mh)+comm(Dg[a],Mi[ch,h]))/R
    full_grad=np.einsum('tcaij,tv->vcaij',grad,b['theta_full_gradient189'])
    fd=[]
    # Richardson differences verify the newly consumed coefficient axes only.
    for j in (0,6,7,10,14,18,19,20,21):
        e=np.eye(22)[j];step=2**-11
        def centered(h):return (angular_kernel(t+h*e,mat)-angular_kernel(t-h*e,mat))/(2*h)
        observed=(4*centered(step/2)-centered(step))/3
        fd.append(maximum(observed-grad[j]))
    checks['new_angular_first_jets']=max(fd)
    assert max(checks.values())<2e-11,checks
    norms=np.array([[np.linalg.norm(x,2) for x in row] for row in K])
    summed=K.sum(axis=1)
    result=dict(schema='bhsm.muon-photon-native-seam.v71',
        classification='EXACT_ELECTROMAGNETIC_LOCAL_SEAM_REDUCTION_AND_INITIALIZER_ANGULAR_COEFFICIENT',
        checks=checks,maximum_check_defect=max(checks.values()),
        scalar_local_seam_coefficient_zero=True,angular_harmonic_derivative_seam_coefficient_zero=True,
        angular_connection_seam_coefficient_zero=False,angular_operator_norms=norms.tolist(),
        summed_angular_operator_norms=[float(np.linalg.norm(x,2)) for x in summed],
        rank_scope='Local 18-dimensional coefficient only; no physical trace or full relative kernel',
        scalar_identity_scope='Each LR/RL normal monomial separately; independent left data and moving-Higgs photon; not full native source or event transfer',
        angular_coefficient_scope='Local paired Green row for the angular-connection part of the factor source; not a complete edge current or proof of noncancellation with temporal, native/relative and domain terms',
        local_coordinates=22,chain_coordinates=189,independent_left_assigned=False,
        normal_monomials_assigned=False,relative_kernel_evaluated=False,
        entering_pole_event_work_evaluated=False,physical_guard=2e-10,method_tolerance=2e-11,
        physical_background=False,physical_total_Y_evaluated=False,physical_a_mu=None,
        physical_reconnection_proved=False,total_physical_uncertainty=None,pushed=False,
        next_operand='Same-domain native/relative contraction of the surviving angular Higgs-covariant seam coefficient with independent left/right and normal traces, plus actual entering/pole/event transfer and zero-order bulk source. No complete common physical graph/kernel application is instantiated.')
    arrays=dict(theta22=t,scalar_seam_channels2x18x18=zero,
        scalar_first_H_jets2x4x18x18=zero_i,scalar_mixed_H_jets2x4x4x18x18=zero_ij,
        angular_connection_channels2x3x18x18=K,summed_angular_channels2x18x18=summed,
        angular_gradient22x2x3x18x18=grad,angular_full_gradient189x2x3x18x18=full_grad,
        photon_generator18=g,photon_first_H4=gi,photon_mixed_H4x4=gij)
    arrays['original_spatial_factor_source18']=spatial_factor_source
    return arrays,result
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('Preserve previous output')
    arrays,r=calculate();a.out.mkdir();npz(a.out/'photon_native_seam.npz',arrays);save(a.out/'result.json',r)
    print(json.dumps({k:r[k] for k in ('maximum_check_defect','angular_operator_norms','summed_angular_operator_norms','relative_kernel_evaluated')}))
if __name__=='__main__':main()
