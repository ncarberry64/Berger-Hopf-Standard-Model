"""Actual reached-direction source contacts and the next native source jet.

The frozen angular responses are not repeated or used as native P0. This
module constructs NEW affine cut source contacts in the same Spin4 x SM16
carrier. It does not equate a cut contact with a heat-weighted global trace.
"""
from __future__ import annotations
import numpy as np
from bhsm.interface.muon_parent_source_contact import parent_insertion


def split_coefficients(columns):
    """Frozen angular coefficient order: coframe, carrier, m, k at n1,n3."""
    x=np.asarray(columns)
    if x.shape[0]!=240:raise ValueError('retained 240 coefficient directions required')
    return {1:x[:48].T.reshape(-1,3,4,2,2),3:x[48:].T.reshape(-1,3,4,4,4)}


def reality(columns):
    """Antilinear real-one-form involution in the SAVED Wigner convention."""
    out=[]
    for n,x in split_coefficients(columns).items():
        k=np.arange(n+1);phase=(-1.)**(k[None,:]-k[:,None])
        y=x[...,::-1,::-1].conj()*phase
        out.append(y.reshape(len(x),-1).T)
    return np.vstack(out)


def real_source_frame(frozen,m):
    """Real coordinates in the SAME frozen32 space, without enrichment.

    Real photon variations must obey harmonic reality. Complex current loads
    are then treated by complex-bilinear extension of the real Hessian.
    """
    candidates=np.column_stack(((frozen+reality(frozen))/2,
                                (frozen-reality(frozen))/(2j)))
    columns=[]
    for i in range(candidates.shape[1]):
        v=candidates[:,i].copy()
        for _ in range(2):
            for w in columns:v-=w*(m*np.vdot(w,v)).real
        norm=np.sqrt(m*np.vdot(v,v).real)
        if norm>1e-10:columns.append(v/norm)
    if len(columns)!=32:
        raise ArithmeticError('frozen response span does not admit the expected real32 coordinates')
    F=np.column_stack(columns)
    U=m*frozen.conj().T@F
    checks=dict(real_frame_reality_residual=float(np.linalg.norm(F-reality(F))),
        real_frame_M_Gram_residual=float(np.linalg.norm(m*F.conj().T@F-np.eye(32))),
        same_frozen_span_residual=float(np.linalg.norm(F-frozen@U)),
        source_basis_changed_not_enriched=True)
    return F,U,checks


def affine_cut_jets(component, frozen_frame, saved_source, cached_parent):
    """NEW mixed source-square contacts on the32 test directions and8 modes.

    This uses source-affine, unreduced fixed-frame connection coordinates:
    Xi_v=f_R c_src(v); D_vA=0 at this LOCAL scope. The full stationary
    source lift/domain jet is deliberately not assigned zero.
    """
    m=float(component['M_geometric_scalar']);fR=float(component['f_R'])
    F,U,checks=real_source_frame(frozen_frame,m)
    coeff=split_coefficients(F)
    contacts=np.zeros((32,8,64,64),complex)
    source_actions={}
    for n,val in coeff.items():
        # Source-index factors NEVER enter the Clifford insertion.
        Xv=fR*parent_insertion(saved_source['saved_gamma_LR'],val,
                              saved_source['unit_trace_carrier_basis'])
        Xa=fR*cached_parent[f'Xi_A_unit_n{n}']
        v=Xv.transpose(0,1,3,4,2).reshape(32,-1,64)
        a=Xa.transpose(0,1,3,4,2).reshape(8,-1,64)
        contacts+=np.einsum('voi,aoj->vaij',v.conj(),a,optimize=True)
        contacts+=np.einsum('aoi,voj->vaij',a.conj(),v,optimize=True)
        source_actions[f'Xi_v_cut_n{n}']=Xv
    S=component['source_inclusion'];G=S.conj().T@S
    # J is a covector, not automatically a photon field. This is its LOCAL
    # geometric Riesz identification. Native continuation is a different jet.
    eta=np.linalg.solve(G,component['mode_current_covector'])/m
    # Complex-bilinear extension: no accidental conjugation of eta in the
    # reverse term. The64 x64 fibre action is not physically supertraced.
    # Retain the exact factorization for ALL224 labels. A dense32x224x64x64
    # tensor would add no information. No column is dropped or heat-restricted.
    flat=contacts.transpose(1,0,2,3).reshape(8,-1)
    contact_gram=flat.conj()@flat.T
    column_norm2=np.einsum('ac,ab,bc->c',eta.conj(),contact_gram,eta).real
    reached_norm=float(np.sqrt(np.sum(column_norm2)))
    fibre_trace=np.einsum('va,ac->vc',np.trace(contacts,axis1=2,axis2=3),eta)
    checks.update(contact_real_direction_Hermiticity=float(np.linalg.norm(contacts-contacts.conj().transpose(0,1,3,2))),
        source_inclusion_reality_residual=float(np.linalg.norm(S-reality(S))),
        local_Riesz_identity_residual=float(np.linalg.norm(m*S@eta-component['reached_current_dual'])),
        mixed_contact_norm=float(np.linalg.norm(contacts)),
        reached_contact_norm=reached_norm,
        real_frame_dimension=32,full_carrier_input_dimension=64,
        connected_n3_test_source_action_norm=float(np.linalg.norm(source_actions['Xi_v_cut_n3'])))
    return dict(real_test_frame=F,real_frame_from_frozen_coordinates=U,
        local_Riesz_current_coordinates=eta,local_real_contact_P_vA=contacts,
        reached_contact_fibre_trace=fibre_trace,
        reached_contact_column_norms=np.sqrt(np.maximum(column_norm2,0)),
        # Xi_v is exactly reconstructible from F, gamma, carrier and fR.
        # Save its norms rather than duplicate40MiB of coefficients.
        local_contact_source_Gram=contact_gram),checks


def owner_length_jet(I,C,Ftau,*,Itau,Itautau,Ftautau,Iv,Ij,Ivj,Fv,Fj,Fvj,Itauv,Itauj,Ftauv,Ftauj):
    """Implicit differentiation of the ADOPTED crossing, not a new cutoff.

    Conditional on a simple first-future crossing and persistent support
    branch. The retained physical coefficients have not been supplied.
    Works on symbolic scalars; does not invent an impedance-energy evaluator.
    """
    tv=-Fv/Ftau;tj=-Fj/Ftau
    tvj=-(Fvj+Ftauv*tj+Ftauj*tv+Ftautau*tv*tj)/Ftau
    Ev=Iv+Itau*tv;Ej=Ij+Itau*tj
    Evj=Ivj+Itauv*tj+Itauj*tv+Itautau*tv*tj+Itau*tvj
    return dict(tau_v=tv,tau_J=tj,tau_vJ=tvj,E_v=Ev,E_J=Ej,E_vJ=Evj,
        ell=1/I,ell_v=-Ev/I**2,ell_J=-Ej/I**2,
        ell_vJ=2*Ev*Ej/I**3-Evj/I**2,
        c_v=-2*Ev/I**3,c_J=-2*Ej/I**3,
        c_vJ=6*Ev*Ej/I**4-2*Evj/I**3)


def compact_weak_first_jets(frame,component,source,parent,rate):
    """Actual unreduced parent K_v/K_J on cached compact source directions.

    Columns: the SAME eight p_A=Xi_A phi diagnostic fields and four compact
    charged-carrier phi columns. They are not a native Hilbert basis. Use the
    corrected cached D0 p, not a new history or point-action campaign.
    K_x(p_A,phi)=<D0 p_A,Xi_x phi>+<p_A,Xi_x^dagger D0 phi>.
    Local source-affinity fixes these trial columns during this derivative;
    movement of global physical states/domain is not inferred from it.
    """
    coeff=split_coefficients(frame);indices=rate['source_image_probe_columns']
    rho=rate['gauss_rho'];nodes=parent['rho']
    chi=np.interp(rho,nodes,parent['spinor_probe_hat_nodes'])
    r=np.interp(rho,nodes,parent['base_radius'])
    nu=np.interp(rho,nodes,parent['nu'])
    kernel=float(parent['T_b'])/r;f=kernel*chi
    weights=rate['node_volume_quadrature_weights']
    d0=rate['D5_metric_common_A_on_compact_probes'][:,:,indices]
    G0=np.kron(rate['parent_gamma'][0],np.eye(16))
    d0tau=(1j*G0[:,indices])[None]*((chi/nu)[:,None,None])
    result={k:np.zeros((40,8,4,4),complex) for k in ('K_0','K_tau0','K_0tau')}
    for n,val in coeff.items():
        xv=parent_insertion(source['saved_gamma_LR'],val,source['unit_trace_carrier_basis'])
        xa=parent[f'Xi_A_unit_n{n}']
        x=np.concatenate((xv,xa),axis=0)
        px=xa[:,:,indices]
        dx=rate[f'D5_on_same_source_image_b_coefficient_n{n}']
        dxtau=rate[f'D5_on_same_source_image_b_tau_coefficient_n{n}']
        xp=x[:,:,indices]
        # Dagger of the COMPLETE angular field: both fibre dagger and saved
        # harmonic-conjugation involution. Merely daggering each coefficient
        # misses the reversed weights and phase in the second weak product.
        k=np.arange(n+1);phase=(-1.)**(k[None,:]-k[:,None])
        xd=x[...,::-1,::-1].conj().transpose(0,2,1,3,4)*phase
        first=np.einsum('g,gAocxy,vodxy->vAcd',weights*f,dx.conj(),xp,optimize=True)
        first_tau=np.einsum('g,gAocxy,vodxy->vAcd',weights*f,dxtau.conj(),xp,optimize=True)
        contracted=np.einsum('Aocxy,voixy->vAci',px.conj(),xd,optimize=True)
        second=np.einsum('vAci,gid,g->vAcd',contracted,d0,weights*f*kernel,optimize=True)
        second_tau=np.einsum('vAci,gid,g->vAcd',contracted,d0tau,weights*f*kernel,optimize=True)
        result['K_0']+=first+second
        result['K_tau0']+=first_tau
        result['K_0tau']+=second_tau
    S=component['source_inclusion']
    eta=np.linalg.solve(S.conj().T@S,component['mode_current_covector'])/float(component['M_geometric_scalar'])
    arrays={}
    for name,value in result.items():
        arrays[f'parent_compact_{name}_v']=value[:32]
        arrays[f'parent_compact_{name}_A']=value[32:]
        arrays[f'parent_compact_{name}_J']=np.einsum('aAcd,aj->jAcd',value[32:],eta)
    arrays['compact_phi_carrier_indices']=indices
    checks=dict(local_weak_K_v_norm=float(np.linalg.norm(result['K_0'][:32])),
        local_weak_K_J_norm=float(np.linalg.norm(arrays['parent_compact_K_0_J'])),
        local_weak_K_v_tau0_norm=float(np.linalg.norm(result['K_tau0'][:32])),
        local_weak_K_v_0tau_norm=float(np.linalg.norm(result['K_0tau'][:32])),
        corrected_D0_source_actions_consumed=True,
        endpoint_H_placeholder_consumed=False,radial_quadrature_repeated=False,
        local_radial_integral_only_not_temporal_history=True)
    return arrays,checks


def generalized_form_jets(D0,Dv,Dj,Dvj,M,Mv,Mj,Mvj):
    """Algebra control for supplied SAME-convention first-order actions.

    Native data are not generated here. Both moving-M terms are retained.
    """
    K=D0.conj().T@D0
    Kv=Dv.conj().T@D0+D0.conj().T@Dv
    Kj=Dj.conj().T@D0+D0.conj().T@Dj
    Kvj=Dv.conj().T@Dj+Dj.conj().T@Dv+Dvj.conj().T@D0+D0.conj().T@Dvj
    A=np.linalg.solve(M,K)
    Av=np.linalg.solve(M,Kv-Mv@A);Aj=np.linalg.solve(M,Kj-Mj@A)
    Avj=np.linalg.solve(M,Kvj-Mvj@A-Mv@Aj-Mj@Av)
    return dict(K=K,K_v=Kv,K_J=Kj,K_vJ=Kvj,A=A,A_v=Av,A_J=Aj,A_vJ=Avj)


def first_length_response():
    """One concrete scalar operand INSIDE the retained mixed length jet.

    A stationary source extension is NOT a prerequisite for differentiating
    the unreduced fixed-trace functional. Do not introduce that circular gate.
    """
    return dict(name='mixed impedance-energy response on the selected crossing',
        operand='E_vJ = d_v d_J I(tau_star(v,J),v,J)',
        defining_equation='I=E_impedance; F=I-E_core=0 at the first future support-loss crossing; ell=1/I',
        contraction='E_vJ=I_vJ+I_tau_v tau_J+I_tau_J tau_v+I_tau_tau tau_v tau_J+I_tau tau_vJ',
        consumer='c_vJ=6 E_v E_J/E^4-2 E_vJ/E^3 in [STr exp(-c P)/(2c)] c_vJ, plus the SAME relative completion length jet',
        input_space='the32 real fixed-background b directions and224 complex-linearly extended geometric Riesz current directions, continued by the same owned source prescription',
        output_space='one scalar bilinear per consumed v,J at the selected crossing, not a full history reconstruction',
        producer='ae4_stratified_dirac_zeta_induced_owner.native_spectral_length_contract, together with the action-defined scalar impedance/core energy functional and its same-source response',
        inspected_equations='native_spectral_length_contract supplies the crossing/rule; seam_wronskian_lower sums supplied lower bounds; H_impedance is an operator ratio; spectral_formation_number accepts an impedance input',
        retained_data_insufficiency='None of those producers supplies I(tau,b), its source-energy response, or a scalar-energy contraction of H_impedance. The stored primitive photon resolvents and Spin4xSM16 parent solution are not that scalar functional.',
        classification='UNEVALUATED owner-required scalar response; no zero-jet theorem or numerical energy supplied by the inspected equations',
        other_native_terms_remain_unevaluated=True,supplied_value=None)


def local_subtraction_component(component,frame,current_coordinates):
    """Only the already-owned angular Maxwell/curvature density per kappa1.

    This is an evaluated subtraction operand, not subtraction from an
    unevaluated full Hessian. Temporal/radial/other local terms are not zero.
    """
    field=component['source_inclusion']@current_coordinates
    return frame.conj().T@component['K_per_kappa1']@field


def lower_limit_mixed(c,cv,cj,cvj,trace_heat,trace_P_heat,trace_heat_Pv,trace_heat_Pj):
    """Exact moving-lower-limit terms for Gamma=-integral_c^inf T(t)/2t.

    Input traces include the SAME grading/quotient. No trace is supplied or
    generated by this scalar identity, and no physical length default exists.
    """
    return (-cv*trace_heat_Pj/2-cj*trace_heat_Pv/2
            +trace_heat*cvj/(2*c)
            -(trace_P_heat/c+trace_heat/c**2)*cv*cj/2)
