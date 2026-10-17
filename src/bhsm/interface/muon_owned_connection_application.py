"""Current lepton connection from the adopted common-A Dirac action.

This is one BHSM muon realization, not a new universal engine. The weak
doublet and right singlet are the independent SM factor, not the k5 CG
subspace. Inputs are the saved Wigner labels/coframe and child profiles.
No physical state, new mass, source extension or heat tail is selected.
"""
import numpy as np
from bhsm.interface.muon_local_source_jet import _gaunt


def lepton_labels(levels):
    return [(n,lr,s,w,m,k) for lr in (0,1) for n in levels for s in (0,1)
            for w in ((0,1) if lr==0 else (-1,))
            for m in range(n,-n-1,-2) for k in range(n,-n-1,-2)]


def charged_embedding(spin_labels,full_labels):
    """Existing charged child coefficient space into L=(nu,e), e_R.

    This is an SM field-coordinate embedding, not a precursor wavefunction.
    """
    index={tuple(v):i for i,v in enumerate(full_labels)}
    d=len(spin_labels);out=np.zeros((len(full_labels),2*d),complex)
    for lr in (0,1):
        for j,(n,s,m,k) in enumerate(spin_labels):
            out[index[int(n),lr,int(s),1 if lr==0 else -1,int(m),int(k)],lr*d+j]=1
    return out


def mechanical_background_action(spin_labels,sigma,rotation):
    """H_L,0=(lambda/r) sigma_spin^a R_ad sigma_weak^d; H_R,0=0.

    The sign follows the retained H_a=diag(Q sigma.a,-Q sigma.a).
    jmath=-i sigma_weak is already the physical doublet representation.
    Returned unit action includes every n2-times-(n0+n1) output.
    """
    if np.asarray(rotation).shape!=(3,3,3,3):raise ValueError('saved Ad_w required')
    inp=lepton_labels((0,1));out=lepton_labels((0,1,2,3))
    weak=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    matrix=np.zeros((len(out),len(inp)),complex)
    for oi,(nt,lrt,st,wt,mt,kt) in enumerate(out):
        if lrt!=0:continue
        for ii,(ns,lrs,ss,ws,ms,ks) in enumerate(inp):
            if lrs!=0 or nt not in range(abs(ns-2),ns+3,2):continue
            for mi,mg in enumerate((2,0,-2)):
                for ki,kg in enumerate((2,0,-2)):
                    g=_gaunt((nt,mt,kt),(2,mg,kg),(ns,ms,ks))
                    if g:
                        matrix[oi,ii]+=g*np.einsum('a,d,ad->',sigma[:,st,ss],weak[:,wt,ws],rotation[:,:,mi,ki])
    Iin=charged_embedding(spin_labels,inp);Iout=charged_embedding(spin_labels,out)
    return dict(input_labels=np.asarray(inp),output_labels=np.asarray(out),
        full_weak_background_unit_action=matrix,charged_input_embedding=Iin,
        charged_output_embedding=Iout,charged_background_unit_action=matrix@Iin,
        spin_sigma=sigma,weak_sigma=weak)


def apply_saved_child_profiles(action,angular_frame,profiles,lam,radius):
    """One new action on retained test functions; no basis construction.

    The finite complement is retained in the ambient output. It is not
    an evolution, shifted-resolvent or heat-kernel tail theorem.
    """
    B=action['charged_background_unit_action']
    Uout=action['charged_output_embedding']@angular_frame
    BU=B@angular_frame
    compressed=Uout.conj().T@BU
    connected=BU-Uout@compressed
    coefficient=lam/radius
    node=coefficient[:,None,None]*np.einsum('oi,tij->toj',B,profiles)
    left_nu=np.array([lr==0 and w==0 for n,lr,s,w,m,k in action['output_labels']])
    high=np.array([n>=2 for n,lr,s,w,m,k in action['output_labels']])
    return dict(unit_independent_background_actions=BU,
        unit_independent_background_compression=compressed,
        unit_independent_connected_background_actions=connected,
        node_background_actions=node,child_background_prefactor=coefficient,
        node_left_neutrino_background_actions=node[:,left_nu],
        node_n2_n3_background_actions=node[:,high],
        checks=dict(compressed_Hermitian_residual=float(np.linalg.norm(compressed-compressed.conj().T)),
            complement_orthogonality_residual=float(np.linalg.norm(Uout.conj().T@connected)),
            unit_full_norm=float(np.linalg.norm(BU)),unit_connected_norm=float(np.linalg.norm(connected)),
            unit_left_neutrino_norm=float(np.linalg.norm(BU[left_nu])),
            unit_n2_n3_norm=float(np.linalg.norm(BU[high])),
            first_node_background_norm=float(np.linalg.norm(node[0]))))


def regular_parent_background_prefactor(A,B):
    """(lambda-1)/r=-B/(A sqrt(A²+B²)), including the regular pole.

    Use the already retained Lorentz parent geometry; no cap or metric is
    selected. This is sigma1, whereas child actions above use sigma0.
    """
    return -B/(A*np.sqrt(A*A+B*B))
