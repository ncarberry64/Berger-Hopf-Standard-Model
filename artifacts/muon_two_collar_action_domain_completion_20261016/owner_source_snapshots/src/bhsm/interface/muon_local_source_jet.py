"""Actual eight-lift M4 source actions and their complete one-action contact.

This is muon realization data, not an alternative native heat operator.
The source coordinate is b; the existing beta=T_b*b conversion gives
f_R=T_b/R. No quadratic-action trace index multiplies the Dirac source.
"""
from functools import lru_cache
import numpy as np
from sympy import Rational
from sympy.physics.wigner import clebsch_gordan
from scipy.special import exprel


@lru_cache(None)
def _cg(n1,m1,n2,m2,nt,mt):
    if any(abs(m)>n or (n-m)%2 for n,m in [(n1,m1),(n2,m2),(nt,mt)]):
        return 0.0
    return float(clebsch_gordan(Rational(n1,2),Rational(n2,2),Rational(nt,2),
                               Rational(m1,2),Rational(m2,2),Rational(mt,2)))


def _gaunt(target,gauge,source):
    nt,mt,kt=target;ng,mg,kg=gauge;ns,ms,ks=source
    return (np.sqrt((ns+1)*(ng+1)/(nt+1))*
            _cg(ns,ms,ng,mg,nt,mt)*_cg(ns,ks,ng,kg,nt,kt))


def _labels(levels):
    return [(n,s,m,k) for n in levels for s in range(2)
            for m in range(n,-n-1,-2) for k in range(n,-n-1,-2)]


def source_spin_frame(gamma):
    """Use the retained +--- gamma convention in the saved LR order."""
    gamma=np.asarray(gamma,complex)
    eye=np.eye(2);U=np.block([[eye,eye],[-eye,eye]])/np.sqrt(2)
    g=np.array([U.conj().T@a@U for a in gamma])
    return dict(Dirac_to_LR_columns=U,gamma_LR=g,
                sigma=np.array([a[:2,2:] for a in gamma[1:]]),
                charge_conjugation_spin_LR=U.conj().T@(1j*gamma[2])@U.conj())


def _charge_conjugation(labels,spin_conjugation):
    """Retained gamma charge conjugation and Wigner complex conjugation.

    Y_nmk*=(-1)^((m-k)/2)Y_n,-m,-k. This is a basis conversion;
    it does not select a CAR covariance or a particle/antiparticle state.
    """
    d=len(labels);index={v:i for i,v in enumerate(labels)}
    out=np.zeros((2*d,2*d),complex)
    for lr in range(2):
        for i,(n,s,m,k) in enumerate(labels):
            for lr2 in range(2):
                for s2 in range(2):
                    out[lr2*d+index[n,s2,-m,-k],lr*d+i]=(
                        (-1.)**((m-k)//2)*spin_conjugation[2*lr2+s2,2*lr+s])
    return out


def full_local_source(angular,gamma,charge=-1.):
    """Multiply the saved real photon modes on n0+n1, including n2 output.

    Wigner multiplication proves that a single such action has no n>=3
    component. This finite support is not a tail theorem for a resolvent.
    """
    frame=source_spin_frame(gamma);sigma=frame['sigma']
    input_labels=_labels((0,1));output_labels=_labels((0,1,2))
    complex_modes=np.zeros((8,3,2,2),complex)
    basis=angular['cartesian_transverse_basis_one_right_copy'].reshape(3,2,4)
    gauge_labels=angular['transverse_mode_labels_twice_spectator_weight_twice_total_M']
    for g,(k,M) in enumerate(gauge_labels):
        complex_modes[g,:,:,list((1,-1)).index(int(k))]=basis[:,:,list((3,1,-1,-3)).index(int(M))]
    real_modes=np.einsum('ab,bcij->acij',angular['real_gauge_basis_transform'],complex_modes)
    J=np.zeros((8,len(output_labels),len(input_labels)),complex)
    for out,(nt,st,mt,kt) in enumerate(output_labels):
        for inp,(ns,ss,ms,ks) in enumerate(input_labels):
            if nt not in (abs(ns-1),ns+1):
                continue
            for mi,mg in enumerate((1,-1)):
                for ki,kg in enumerate((1,-1)):
                    gaunt=_gaunt((nt,mt,kt),(1,mg,kg),(ns,ms,ks))
                    if gaunt:
                        J[:,out,inp]+=gaunt*np.einsum('ga,a->g',real_modes[:,:,mi,ki],sigma[:,st,ss])
    ni,no=len(input_labels),len(output_labels)
    V=np.zeros((8,2*no,2*ni),complex)
    V[:,:no,:ni]=-charge*J;V[:,no:,ni:]=charge*J
    g0=np.block([[np.zeros((no,no)),np.eye(no)],[np.eye(no),np.zeros((no,no))]])
    Xi=np.einsum('ij,ajk->aik',g0,V)
    indices=np.r_[np.arange(ni),no+np.arange(ni)]
    V_retained=V[:,indices]
    Xi_retained=Xi[:,indices]
    C_in=_charge_conjugation(input_labels,frame['charge_conjugation_spin_LR'])
    C_out=_charge_conjugation(output_labels,frame['charge_conjugation_spin_LR'])
    # Real physical source; conjugating the charged sector reverses Q.
    conjugated=np.einsum('ij,ajk,kl->ail',C_out,Xi.conj(),C_in.conj().T)
    return dict(**frame,J_complete=J,V_complete=V,Xi_complete=Xi,
                V_retained=V_retained,Xi_retained=Xi_retained,
                gamma0_output=g0,retained_output_indices=indices,
                input_labels=np.asarray(input_labels),output_labels=np.asarray(output_labels),
                real_mode_coefficients=real_modes,C_input=C_in,C_output=C_out,
                conjugate_charge_Xi_complete=-Xi,
                charge_conjugation_residual=float(np.linalg.norm(conjugated+Xi)))


def contact_forms(source):
    """The full Xi_A/Xi_B terms, including the connected n2 complement."""
    X=source['Xi_complete'];r=source['retained_output_indices']
    pair=np.einsum('aoi,boj->abij',X.conj(),X)
    full=pair+pair.transpose(1,0,2,3)
    pair_r=np.einsum('aoi,boj->abij',X[:,r].conj(),X[:,r])
    retained=pair_r+pair_r.transpose(1,0,2,3)
    return dict(contact_full=full,contact_retained=retained,
                contact_connected_complement=full-retained)


def _moment(x,h,k):
    """Integral exp(-k logR) on the supplied affine-logR history segments."""
    return h*np.exp(-k*x[:-1])*exprel(-k*np.diff(x))


def evaluated_child_forms(source,contacts,body,frame,mixed):
    """Evaluate q_A,q_AB,M on the actual E0 and generated current profiles.

    Columns are [E0,f_R V_0E0,...,f_R V_7E0]. The canonical BH and covariant
    gamma0 BH norms agree by the saved unitary gamma0. Direct b variation
    holds the history and these test columns fixed, so local M jets are zero.
    This is the child contribution, not an AE4 positive-parent substitution.
    """
    E=mixed['external_n0_test_frame_E0'];V=source['V_retained']
    W=mixed['Gamma_s_unit_source_fermion_boson_external'].reshape(20,32)
    x=frame['log_radius'];h=frame['proper_durations'];c=1/np.sqrt(2*np.pi**2)
    H=np.diff(x)/h;kin=body['kinetic_generator'];mass=body['mass_generator']
    first=np.zeros((len(h),8,36,36),complex)
    second=np.zeros((8,8,36,36),complex);tail=np.zeros_like(second)
    M=np.zeros((36,36),complex)
    kinetic_pair=np.array([kin@v+v@kin for v in V])
    mass_pair=np.array([mass@v+v@mass for v in V])
    frames=[E,W];slices=[slice(0,4),slice(4,36)]
    factors={}
    for i,(U,si) in enumerate(zip(frames,slices)):
        for j,(T,sj) in enumerate(zip(frames,slices)):
            z=i+j
            wt=c**z*_moment(x,h,1.5*z)
            M[si,sj]=wt.sum()*(U.conj().T@T)
            electric=c**(1+z)*_moment(x,h,2.5+1.5*z)
            time=c**(1+z)*_moment(x,h,1.5*(1+z))*(-1.5*H)*(j-i)
            for a in range(8):
                first[:,a,si,sj]=(-electric[:,None,None]*(U.conj().T@kinetic_pair[a]@T)
                                  +1j*time[:,None,None]*(U.conj().T@V[a]@T))
            contact_w=c**(2+z)*_moment(x,h,1.5*(2+z))
            second[:,:,si,sj]=contact_w.sum()*np.einsum('ki,abkl,lj->abij',U.conj(),contacts['contact_full'],T)
            tail[:,:,si,sj]=contact_w.sum()*np.einsum('ki,abkl,lj->abij',U.conj(),contacts['contact_connected_complement'],T)
            factors[str(z)]=contact_w
    f_nodes=frame['canonical_physical_volume_factor_nodes']
    f_mid=mixed['physical_volume_source_factor']
    XiE=np.einsum('aoi,ic->aoc',source['Xi_complete'],E)
    XiW=np.einsum('aoi,ibc->aboc',source['Xi_complete'],mixed['Gamma_s_unit_source_fermion_boson_external'])
    # Exact continuity of the reconstructed nodal source/test profiles;
    # this is the child mesh, not the unknown physical parent interface.
    left=f_nodes[1:-1].copy();right=f_nodes[1:-1].copy()
    return dict(child_q_A_segment_first_forms=first,child_q_A_integrated=first.sum(axis=0),
                child_q_AB_integrated=second,child_q_AB_connected_complement=tail,
                child_M_test_Gram=M,local_mass_first_jet_coefficient=mass_pair,
                Xi_actions_E0_nodes=f_nodes[:,None,None,None]*XiE[None],
                Xi_actions_generated_midpoint_profiles=f_mid[:,None,None,None,None]**2*XiW[None],
                generated_profile_node_values=f_nodes[:,None,None]*W[None],
                child_mesh_source_trace_residual=left-right,
                contact_segment_weight_2=factors['0'],contact_segment_weight_4=factors['2'])


def missing_native_lift():
    """An exact missing evaluated map, not a synthetic positive body."""
    return dict(name='E_plus_54_Q_on_eight_saved_source_profiles',
        input_space='span{T_b(tau)*Y_A Q, A=0..7} with the retained temporal profiles on M4',
        output_space='admissible connection one-forms A_A^(5,+) in the owned current positive-parent gauge form/domain, including the M5-to-M4 and reset trace',
        equation='B5 E_plus_54_Q a4=a4; delta_A5 Gamma_AE4^(2)[E_plus_54_Q a4]=0 on fixed-trace bulk variations if the owned source prescription is stationary elimination',
        prescription_boundary='The stationary-extension equation is not adopted as an invented choice; the actual retained source path/pullback must supply it or its equivalent.',
        Clifford_trace_equation='T54 c_src,5(E_plus_54_Q a4) Q = c_src,4(a4) Q T54 with the actual Clifford-module identification',
        reset_equation='a_child U_R - U_R a_event=0 after the actual base pullback for the fixed transition; if U_R varies, retain d(delta U_R)+a_child U_R+A_child delta U_R-delta U_R A_event-U_R a_event',
        supplied_values=None,parent_interface_residual=None,
        prevents='parent/cross-stratum Xi_A and Xi_AB, their q_A/q_AB induced matching contribution, finite-E1 supertrace Hessian and the completed K+sM source solve',
        classification='SELECTED_OWNER_WITH_UNINSTANTIATED_POSITIVE_PARENT_SOURCE_REALIZATION; not a numerical value furnished by an abstract block assembler')
