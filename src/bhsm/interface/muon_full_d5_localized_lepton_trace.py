"""Exact full-carrier Clifford and localized lepton trace representation.

One self-dual carrier has Spin4 x (SM16 + conjugate SM16), dimension128
per family. Its conjugate copy is a charge-conjugation representation, not
another independently counted fermion species. The two oriented collars
remain separate geometric branches of the original D5 action. This module
supplies fixed coefficient trace maps; the action-owned normalized normal
eta mode, coframe/density map and exterior domain must still be applied.
"""
from __future__ import annotations
import numpy as np

from .completion.foundational_dirac_spin_glue_v14_45 import dirac_gamma_matrices
from .muon_local_source_jet import source_spin_frame
from .particle_chirality_anomaly_normalization import one_family_multiplets
from .bhsm_standard_model_gauge_vertices import su2_fundamental_generators


def full_d5_localized_lepton_trace():
    """Return exact fixed full trace/dual maps and their complements.

    The localized order is L[weak,family,spin2], e_R[family,spin2].
    L is the ordinary L_L6,7 carrier in left Spin4; e_R is the conjugate
    e_c14 carrier in right Spin4. No gamma_perp is invented on18.
    The charge-conjugate Clifford is -B Gamma_A* B^-1, as derived by
    conjugating i Gamma_A D_A Psi=0. Its odd-dimensional normal matrix
    has the opposite sign; the separate collar orientation is still eps.
    Fixed representation conjugation never conjugates source coefficients.
    """
    frame=source_spin_frame(np.asarray(dirac_gamma_matrices()))
    gamma=np.asarray(frame['gamma_LR']);B=np.asarray(frame['charge_conjugation_spin_LR'])
    gamma5=1j*gamma[0]@gamma[1]@gamma[2]@gamma[3]
    gamma5d=np.concatenate((gamma,(1j*gamma5)[None]))
    # Charge-conjugation module is derived, rather than selecting a new
    # normal sign or pretending all oddD gammas commute with conjugation.
    conjugate=np.array([-B@g.conj()@np.linalg.inv(B)for g in gamma5d])
    I16=np.eye(16,dtype=complex)
    fullgamma=np.array([np.block([[np.kron(g,I16),np.zeros((64,64),complex)],
        [np.zeros((64,64),complex),np.kron(gc,I16)]])for g,gc in zip(gamma5d,conjugate)])
    multiplets=one_family_multiplets(include_neutral_singlet=True)
    labels=[];charges=[];positions={};start=0
    for row in multiplets:
        positions[row.name]=np.arange(start,start+row.complex_dimension)
        labels.extend((row.name,j)for j in range(row.complex_dimension))
        charges.extend([float(row.Y)]*row.complex_dimension);start+=row.complex_dimension
    if start!=16 or not np.array_equal(positions['L_L'],[6,7])or not np.array_equal(positions['e_c'],[14]):
        raise ValueError('retained ordered fullSM16 carrier changed')
    G=np.zeros((4,16,16),complex);weak=np.asarray(su2_fundamental_generators())
    # Q_L is color-major weak-doublet order; the lepton doublet follows.
    for a in range(3):
        G[a,:6,:6]=-1j*np.kron(np.eye(3),weak[a])/np.sqrt(2)
        G[a,6:8,6:8]=-1j*weak[a]/np.sqrt(2)
    G[3]=-1j*np.diag(charges)/np.sqrt(10/3)
    G128=np.array([np.block([[np.kron(np.eye(4),g),np.zeros((64,64),complex)],
        [np.zeros((64,64),complex),np.kron(np.eye(4),g.conj())]])for g in G])
    W=np.zeros((3*128,18),complex)
    for weak_index in range(2):
        for family in range(3):
            for spin in range(2):
                row=family*128+spin*16+6+weak_index
                col=(weak_index*3+family)*2+spin;W[row,col]=1
    for family in range(3):
        for spin in range(2):
            row=family*128+64+(2+spin)*16+14
            W[row,12+2*family+spin]=1
    C128=np.block([[np.zeros((64,64),complex),np.kron(B,I16)],
        [np.kron(B,I16),np.zeros((64,64),complex)]])
    C384=np.kron(np.eye(3),C128)
    Wcharge=C384@W.conj()
    pair=np.c_[W,Wcharge]
    # These fixed rows are coefficient duals. The actual continued
    # analytic left field/source is supplied independently, not conjugated.
    dual=W.T;dual_charge=Wcharge.T
    Q=np.eye(384,dtype=complex)-pair@pair.conj().T
    G384=np.array([np.kron(np.eye(3),g)for g in G128])
    alpha128=np.array([fullgamma[0]@fullgamma[a]for a in range(1,4)])
    alpha384=np.array([np.kron(np.eye(3),a)for a in alpha128])
    return dict(gamma_LR=gamma,gamma5=gamma5,gamma5D_particle=gamma5d,
        gamma5D_conjugate=conjugate,gamma5D_self_dual128=fullgamma,
        charge_conjugation_spin_LR=B,charge_conjugation_self_dual128=C128,
        charge_conjugation_all_families=C384,unitTr16_gauge_particle=G,
        unitTr16_gauge_self_dual128=G128,unitTr16_gauge_all_families=G384,
        localized_lepton18_trace_lift=W,localized_lepton18_literal_dual=dual,
        localized_antilepton18_trace_lift=Wcharge,localized_antilepton18_literal_dual=dual_charge,
        particle_antiparticle36_trace_lift=pair,full_retained_complement=Q,
        localized_gauge_intertwiner=np.array([dual@g@W for g in G384]),
        localized_canonical_angular_clifford=np.array([dual@a@W for a in alpha384]),
        source_coefficients_conjugated=False,
        self_dual_copy_is_not_an_additional_physical_loop_multiplicity=True,
        normal_mode_factor='u_eta(s)=N J(s)^(-1/2)sin(f_child(X(s))) supplied by the same collar action; integral J|u_eta|²ds=1',
        trace_value_rule='Gamma0(Psi)=u_eta(seam)*W*psi_intrinsic in the transported common frame; inverse localized coefficient trace requires its same mode/Gram, not a raw point selector alone',
        trace_dual_rule='Independent analytic left trace acts through the literal coefficient dual and its independently continued normal/density factor',
        normal_operator_rule='i eps Gamma_perp [partial_s+half partial_s log J−partial_s log sin f_child(X)]',
        Higgs_rule='fixedY Higgs bridge is the once-only intrinsic/seam action; no bulkD5 Higgs mass appended',
        reset_rule='Gamma0_child=U_R Gamma0_parent; Gamma1_child=−U_R Gamma1_parent only on Dom(D_AE2²)',
        conormal_rule='Gamma1 is the originating weak square conormal, not bare normal derivative',
        collar_orientation_selected=False,normal_mode_overlap_or_exterior_evaluated=False,
        physical_pole_charge_or_Pauli_selected=False,
        full_carrier_order='family3, (particle SM16,conjugate SM16), Spin4, ordered internal16',
        localized_order='L[weak2,family3,spin2], e_R[family3,spin2]',
        SM16_labels=tuple(labels))


def lift_localized_analytic_source(matrix, *, full_representation=None):
    """Lift an already action-owned18 matrix, with coefficients unchanged.

    This is a trace/source image, not a fullD5 operator completion. For a
    Higgs matrix it is to be used at the seam only. All complement rows
    remain explicit in the returned384 matrix and its projector.
    """
    a=full_d5_localized_lepton_trace()if full_representation is None else full_representation
    M=np.asarray(matrix,complex)
    if M.shape[-2:]!=(18,18)or not np.isfinite(M).all():raise ValueError('same localized18 action/source matrix required')
    W=a['localized_lepton18_trace_lift'];D=a['localized_lepton18_literal_dual']
    return W@M@D


def moving_d5_material_trace_frame(material_normal_velocity,
        material_normal_velocity_first, *, full_representation=None):
    """Apply the inherited Lorentz boost and its analytic source first jet.

    U is the actual wall velocity in its orthonormal (time,normal) plane;
    it is not a guessed lapse ratio. S=exp[-atanh(U)Gamma0Gamma_perp/2]
    sends the adapted coframe into the ambient coframe. Its analytic left
    dual is S^-1, not S^dagger. On a real timelike wall the originating
    current Gram verifies S^dagger(Gamma0 Gamma_T)S=I; no positive
    Euclidean action is substituted for the Lorentz action.
    """
    a=full_d5_localized_lepton_trace()if full_representation is None else full_representation
    U=complex(material_normal_velocity);dU=complex(material_normal_velocity_first)
    if not np.isfinite(U)or not np.isfinite(dU)or abs(1-U*U)<1e-12:
        raise ValueError('actual nonnull analytic wall velocity and source first required')
    G=a['gamma5D_self_dual128'];A=G[0]@G[4];eta=np.arctanh(U)
    S=np.cosh(eta/2)*np.eye(128)-np.sinh(eta/2)*A
    Sinv=np.cosh(eta/2)*np.eye(128)+np.sinh(eta/2)*A
    deta=dU/(1-U*U);dS=-deta*A@S/2;dSinv=deta*A@Sinv/2
    norm=np.sqrt(1-U*U);GT=(G[0]+U*G[4])/norm;GN=(U*G[0]+G[4])/norm
    dGT=dU*(G[4]+U*G[0])/(norm**3);dGN=dU*(G[0]+U*G[4])/(norm**3)
    W=a['localized_lepton18_trace_lift'];D=a['localized_lepton18_literal_dual']
    SS=np.kron(np.eye(3),S);SI=np.kron(np.eye(3),Sinv)
    return dict(ambient_trace_lift=SS@W,ambient_literal_trace_dual=D@SI,
        ambient_trace_lift_first=np.kron(np.eye(3),dS)@W,
        ambient_literal_trace_dual_first=D@np.kron(np.eye(3),dSinv),
        spin_boost128=S,spin_boost_inverse128=Sinv,spin_boost_first128=dS,
        spin_boost_inverse_first128=dSinv,unit_time_Clifford128=GT,unit_normal_Clifford128=GN,
        unit_time_Clifford_first128=dGT,unit_normal_Clifford_first128=dGN,
        boost_inverse_rows=Sinv@S-np.eye(128),
        adapted_time_Clifford_rows=Sinv@GT@S-G[0],
        adapted_normal_Clifford_rows=Sinv@GN@S-G[4],
        real_wall_Hilbert_current_isometry_rows=S.conj().T@(G[0]@GT)@S-np.eye(128),
        real_wall_Hilbert_rows_are_only_a_real_U_identity=True,
        actual_source_tangent_or_analytic_dual_conjugated=False,
        normal_mode_density_domain_and_exterior_not_supplied_by_spin_boost=True)


def normalized_d5_point_trace(right_normal_value,left_normal_value,
        right_normal_first,left_normal_first,material_normal_velocity,
        material_normal_velocity_first, *, full_representation=None):
    """Normalized local Gamma0 and its independently supplied analytic dual.

    This executes the normalized WALL SPINOR TRACE B of the unified M5/M4
    parent-boundary functional. It is an unbounded geometric point trace,
    not the bounded volume-mode projection. In canonical coefficient
    covectors on a given chiral subbundle,
      Psi5|wall=u_R S W psi4,
      leftPsi5|wall=leftpsi4 u_L W^T S^-1.
    Therefore g_R=W^T S^-1 Gamma0(Psi5)/u_R and
    g_L=barGamma0(Psi5) S W/u_L. Their seam bilinear has the DERIVED
    scalar chart factor 1/(u_L u_R). It is not an appended bulk mass or a
    fitted coefficient. The trace-domain identification is explicit here;
    scalar radial normalization alone is not full kinetic/pole normalization.
    The off-mode complement remains in the original D5/operator domain.
    The unsquared D5 Dirac-bar action requires the explicit Gamma0
    conversion returned by normalized_d5_dirac_bar_trace, once.
    """
    ur,ul=complex(right_normal_value),complex(left_normal_value)
    dr,dl=np.asarray(right_normal_first,complex),np.asarray(left_normal_first,complex)
    dv=np.asarray(material_normal_velocity_first,complex)
    if dr.ndim!=1 or dl.shape!=dr.shape or dv.shape!=dr.shape or not len(dr)or min(abs(ur),abs(ul))<1e-14:
        raise ValueError('both independent nonzero normal trace values and all analytic first slots required')
    if not np.isfinite(np.r_[ur,ul,dr,dl,dv]).all():raise ValueError('finite inherited normal traces required')
    a=full_d5_localized_lepton_trace()if full_representation is None else full_representation
    b=moving_d5_material_trace_frame(material_normal_velocity,0,full_representation=a)
    W=b['ambient_trace_lift'];D=b['ambient_literal_trace_dual']
    BR=D/ur;BL=W/ul;ER=ur*W;EL=ul*D
    dBR=[];dBL=[];dER=[];dEL=[]
    for rr,ll,v in zip(dr,dl,dv):
        z=moving_d5_material_trace_frame(material_normal_velocity,v,full_representation=a)
        dW=z['ambient_trace_lift_first'];dD=z['ambient_literal_trace_dual_first']
        dBR.append(dD/ur-D*rr/ur**2);dBL.append(dW/ul-W*ll/ul**2)
        dER.append(rr*W+ur*dW);dEL.append(ll*D+ul*dD)
    return dict(normalized_right_Gamma0=BR,normalized_literal_left_Gamma0=BL,
        normalized_right_Gamma0_first=np.asarray(dBR),normalized_literal_left_Gamma0_first=np.asarray(dBL),
        normal_mode_right_point_lift=ER,normal_mode_literal_left_point_lift=EL,
        normal_mode_right_point_lift_first=np.asarray(dER),normal_mode_literal_left_point_lift_first=np.asarray(dEL),
        right_normalized_trace_recovery_rows=BR@ER-np.eye(18),
        literal_left_normalized_trace_recovery_rows=EL@BL-np.eye(18),
        normalized_seam_scalar_chart_factor=np.array(1/(ul*ur)),
        normalized_seam_scalar_chart_factor_first=-(dl/ul+dr/ur)/(ul*ur),
        pointtrace_not_volumeprojection=True,normal_trace_values_or_sources_conjugated=False,
        complement_operator_or_boundary_traces_not_deleted=True,
        normalized_trace_domain='g4=B_norm Gamma0(Psi5) on the specified transmitted chiral trace; original fullD5 complement and other trace equations retained',
        left_covector_pairing='canonical coefficient pairing; Dirac-bar conversion is a separate fixed Gamma0 application',
        complete_four_dimensional_kinetic_or_pole_normalization_not_inferred=True)


def normalized_d5_dirac_bar_trace(right_normal_value,left_normal_value,
        right_normal_first,left_normal_first,material_normal_velocity,
        material_normal_velocity_first, *, full_representation=None):
    """Convert normalized canonical left covectors to the original Dirac bar.

    For the full signed D5 action barPsi=Psi^dagger Gamma0 on real bases.
    Its analytic independent left covector is not conjugated in source
    derivatives. Since S^dagger Gamma0=Gamma0 S^-1 on a real wall,
      EL_bar=u_L D Gamma0 S^-1, BL_bar=S Gamma0 W/u_L.
    Thus EL_bar BL_bar=I, and the once-only canonical intrinsic/seam
    matrix M18 pulls back to BL_bar M18 BR in the Dirac-bar bulk pairing.
    No Gamma0 may be appended again to these returned left maps.
    """
    a=full_d5_localized_lepton_trace()if full_representation is None else full_representation
    q=normalized_d5_point_trace(right_normal_value,left_normal_value,
        right_normal_first,left_normal_first,material_normal_velocity,
        material_normal_velocity_first,full_representation=a)
    G0=np.kron(np.eye(3),a['gamma5D_self_dual128'][0])
    b=moving_d5_material_trace_frame(material_normal_velocity,0,full_representation=a)
    S=np.kron(np.eye(3),b['spin_boost128']);SI=np.kron(np.eye(3),b['spin_boost_inverse128'])
    W=a['localized_lepton18_trace_lift'];D=a['localized_lepton18_literal_dual']
    ul=complex(left_normal_value);dl=np.asarray(left_normal_first,complex)
    BL=S@G0@W/ul;EL=ul*D@G0@SI;dBL=[];dEL=[]
    for du,v in zip(dl,np.asarray(material_normal_velocity_first,complex)):
        jet=moving_d5_material_trace_frame(material_normal_velocity,v,full_representation=a)
        dS=np.kron(np.eye(3),jet['spin_boost_first128']);dSI=np.kron(np.eye(3),jet['spin_boost_inverse_first128'])
        dBL.append(dS@G0@W/ul-BL*du/ul)
        dEL.append(du*D@G0@SI+ul*D@G0@dSI)
    return dict(q,normalized_Dirac_bar_left_Gamma0=BL,
        normalized_Dirac_bar_left_Gamma0_first=np.asarray(dBL),
        normal_mode_Dirac_bar_left_point_lift=EL,
        normal_mode_Dirac_bar_left_point_lift_first=np.asarray(dEL),
        Dirac_bar_trace_recovery_rows=EL@BL-np.eye(18),
        Dirac_bar_to_canonical_factor=G0,
        original_Dirac_bar_Gamma0_count=1,
        analytic_left_source_coefficients_conjugated=False)
