"""Reached local restriction and scalar matching contacts on the owned factor.

The normal first jet is an action application, not a statement that its
one-point comparator has the same exterior domain or loop as the finite
graph.  The scalar consumer retains the original coupled gauge/H pencil,
canonical radial dual, and all named frame reactions before comparison.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import lu_factor, lu_solve

from .muon_continued_action_reality import _higgs_mass_realified
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection
from .muon_primal_electromagnetic_source import higgs_aligned_charge

VOLUME = 2*np.pi**2


def _finite(x, shape, name, *, real=False):
    a=np.asarray(x,float if real else complex)
    if a.shape!=shape or not np.isfinite(a).all():
        raise ValueError('complete finite '+name+' required')
    return a


def native_local_normal_matching(node,H,wall_connection,*,family,
        matched_mass_action,electric_charge,H_proper_rate=None):
    """Apply the local Wilson first jet and canonical EM coframe conversion.

    U(0)=I, D_tau U=-Omega_tau and E_i U=-Omega_i.  This removes
    the connection from the first-order coefficient at one normal point;
    derivatives/curvature and the finite boundary graph remain present.
    The mass load is the required local matching counterterm, not a refit
    of the fixed Yukawa or a selection of a global physical pole.
    """
    if type(family)is not int or family not in (1,2):raise ValueError('retained family1/2 required')
    h=_finite(H,(2,),'actual Higgs doublet');A=_finite(wall_connection,(5,4),'full material wall connection',real=True)
    m,e=float(matched_mass_action),float(electric_charge)
    if not np.isfinite([m,e]).all()or min(m,e)<=0 or np.linalg.norm(h)==0:
        raise ValueError('positive declared matched mass/charge and nonzero actual H required')
    fi=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
    if not np.array_equal(node['family_indices'],fi):raise ValueError('the SAME full C6 native node is required')
    R,N=float(node['R']),float(node['N']);I=np.eye(6);rep=lepton_current_hilbert_representation()
    if min(R,N)<=0:raise ValueError('positive actual coframe required')
    alpha=_finite(node['alpha'],(3,6,6),'native C6 alpha')
    G=lepton_unit_trace_gauge_representation()['generators'][:,fi,:][:,:,fi]
    g5=rep['gamma5'][np.ix_(fi,fi)]
    space=np.einsum('ac,cij->aij',A[2:],G)/R+1j*np.einsum('aij,jk->aik',alpha,g5)/(2*R)
    Om=_finite(node['Omega_factor'],(6,6),'actual factor temporal connection')
    U_tau=-Om;U_spatial=-space
    normal_body=node['factor_body']+U_tau-1j*np.einsum('aij,ajk->ik',alpha,U_spatial)
    real_h=np.r_[h.real,h.imag];M=_higgs_mass_realified(real_h)[np.ix_(fi,fi)]
    inj=charged_dirac_injection(h,family=family);J=inj['charged'][fi];Jn=inj['neutral'][fi]
    frame=np.column_stack((J,Jn));Y=float(rep['family_Y'][family,family].real);tree_mass=Y*np.linalg.norm(h)
    beta=J.conj().T@M@J/tree_mass;ac=np.einsum('si,aij,jt->ast',J.conj().T,alpha,J)
    mass_load=(m-tree_mass)*J@beta@J.conj().T
    matched_body=normal_body+mass_load
    charge=higgs_aligned_charge(h,np.zeros(2,complex));s=charge['unit_Tr16_coefficients']
    Q=charge['charge'][np.ix_(fi,fi)]
    # At_L is a coordinate one-form: -i*N converts the factor tangent
    # to the proper canonical Lorentz Hamiltonian source. Spatial R once.
    native_time=e*np.einsum('c,cij->ij',s,node['native_temporal_vertices'])
    source=np.empty((4,6,6),complex);source[0]=-1j*N*native_time
    source[1:]=e*R*np.einsum('c,acij->aij',s,node['vertices'][:20].reshape(5,4,6,6)[2:])
    expected=np.r_[(-e*Q)[None],-e*np.einsum('aij,jk->aik',alpha,Q)]
    charged_source=np.einsum('si,aij,jt->ast',J.conj().T,source,J)
    target_source=e*np.r_[np.eye(4)[None],ac]
    radial_real=real_h/np.linalg.norm(real_h)/np.sqrt(2)
    radial_vertex=np.einsum('c,cij->ij',radial_real,node['vertices'][20:])
    dh=np.zeros(2,complex)if H_proper_rate is None else _finite(H_proper_rate,(2,),'same proper H rate')
    Mt=_higgs_mass_realified(np.r_[dh.real,dh.imag])[np.ix_(fi,fi)]
    cov_mass_tau=Mt+Om@M-M@Om
    cov_mass_space=space@M[None]-M[None]@space
    comm_charge=Q@node['factor_body']-node['factor_body']@Q
    return dict(charged_injection=J,neutral_injection=Jn,complete_C6_frame=frame,
        local_Wilson_proper_time_first=U_tau,local_Wilson_spatial_first=U_spatial,
        local_normal_body=normal_body,full_fixed_Y_mass=M,normal_body_residual=normal_body-M,
        actual_tree_mass_action=tree_mass,matched_mass_action=m,required_mass_matching_load=mass_load,
        matched_normal_body=matched_body,charged_gamma0=beta,charged_alpha=ac,
        mass_matching_residual=J.conj().T@matched_body@J-m*beta,
        neutral_mass_return=Jn.conj().T@matched_body@J,
        native_temporal_EM_source=native_time,canonical_coframe_EM_source=source,
        full_EM_current_restriction_residual=source-expected,
        charged_EM_current=charged_source,charged_EM_current_residual=charged_source-target_source,
        neutral_EM_source=np.einsum('si,aij,jt->ast',Jn.conj().T,source,J),
        selected_charge=Q,charge_frame_coefficients=s,charge_factor_body_commutator=comm_charge,
        radial_fixed_Y_vertex=radial_vertex,fixed_Y=Y,
        charged_radial_vertex=J.conj().T@radial_vertex@J,
        charged_radial_vertex_residual=J.conj().T@radial_vertex@J-Y*beta/np.sqrt(2),
        covariant_mass_time_first=cov_mass_tau,covariant_mass_spatial_first=cov_mass_space,
        fixed_Y_refitted=False,normal_first_jet_cancels_global_curvature_or_domain=False,
        current_normalization='point fiber unit Gram; modes Y_h/sqrt(V), V=2pi²; no extra V^-2 or charge factor',
        local_matching_equation='U^-1 A U at one normal point; mass CT=(m_match-Y|H|)J beta J†; current At_L conversion -iN, Ai coframe R',
        physical_outer_domain_or_LSZ_established=False,continuum_overlap_subtracted=False)


def matched_local_square_application(matching,*,proper_frequency,spatial_momentum):
    """Execute the one-point charged symbol/adjoint on declared test momentum."""
    w=float(proper_frequency);p=_finite(spatial_momentum,(3,),'local physical coframe momentum',real=True)
    if not np.isfinite(w):raise ValueError('finite declared frequency required')
    J=matching['charged_injection'];M=matching['matched_normal_body'];alpha=matching['charged_alpha']
    Jbody=J.conj().T@M@J;sp=np.einsum('a,aij->ij',p,alpha)
    right=1j*w*np.eye(4)+sp+Jbody;left=-1j*w*np.eye(4)+sp+Jbody
    P=left@right;target=(w*w+p@p+matching['matched_mass_action']**2)*np.eye(4)
    return dict(right_local_symbol=right,left_local_symbol=left,matched_local_square=P,
        flat_matched_square=target,square_matching_residual=P-target,
        no_derivative_or_curvature_complement_discarded_from_actual_graph=True,
        local_symbol_is_not_the_finite_graph_resolvent=True)


def coupled_radial_matching_contacts(forms,trace_map,frame_indices,H,*,lapse,radius,
        matched_scalar_mass_action,frequencies):
    """Solve the original n1 coupled action for all canonical radial currents.

    The four n1 sources have dual 2r, deltaH=r*h and r²=1/2.  Their
    Green is therefore 4 r^T G_HH r. A same-field-coordinate reference
    retains its actual scalar kinetic residue and the n1 Laplacian3/R².
    This reference is not identified with a continuum loop or an exterior
    pole. The inverse matching contacts and every surviving gauge return
    are evaluated rather than replaced by a fitted scalar propagator.
    """
    M,B,K=[_finite(a,(336,336),'original n1 M/B/K')for a in forms]
    T=_finite(trace_map,(96,336),'original all24 wall trace x n1',real=True)
    f=np.asarray(frame_indices,int);h=_finite(H,(4,),'actual realified H',real=True)
    N,R,Mh=float(lapse),float(radius),float(matched_scalar_mass_action)
    zlist=np.asarray(frequencies,complex)
    if f.shape!=(16,)or len(set(f.tolist()))!=16 or np.any((f<64)|(f>=336)):
        raise ValueError('all16 named central radial frame coordinates required')
    if min(N,R,Mh,np.linalg.norm(h))<=0 or not np.isfinite([N,R,Mh]).all()or zlist.ndim!=1 or not np.isfinite(zlist).all():
        raise ValueError('positive same-coframe scalar mass probe and frequencies required')
    allowed=np.setdiff1d(np.arange(336),f);Q=np.eye(336)[:,allowed];F=np.eye(336)[f]
    C=np.array([K/N,1j*(B-B.T),N*M]);r=h/np.linalg.norm(h)/np.sqrt(2)
    D=np.zeros((96,4));D[80:]=np.kron((2*r)[:,None],np.eye(4));S=np.column_stack((T.T@D,T.T))
    # C already divides the coordinate action by N and uses the proper
    # frequency.  N*M has scalar block2*R³/V; no second lapse survives.
    Z=R**3/VOLUME;ref=np.array([-Z*(3/R**2+Mh**2)*np.eye(4),np.zeros((4,4)),Z*np.eye(4)])
    results=[]
    for z in np.r_[0j,zlist]:
        A=sum(C[k]*z**k for k in range(3));Ap=C[1]+2*z*C[2]
        fac=lu_factor(Q.T@A@Q);u=Q@lu_solve(fac,Q.T@S)
        up=Q@lu_solve(fac,-Q.T@Ap@u)
        upp=Q@lu_solve(fac,-2*Q.T@C[2]@u-2*Q.T@Ap@up)
        G=S.T@u;Gp=S.T@up;Gpp=S.T@upp;gh=G[:4,:4];eff=np.linalg.solve(gh,np.eye(4))
        ep=-eff@Gp[:4,:4]@eff
        epp=2*eff@Gp[:4,:4]@eff@Gp[:4,:4]@eff-eff@Gpp[:4,:4]@eff
        residual=A@u-S;reaction=F@residual
        results.append(dict(frequency=np.array(z),canonical_radial_Green=gh,
            radial_inverse=eff,radial_inverse_first=ep,radial_inverse_second=epp,
            radial_gauge_wall_Green=G[:4,4:84],gauge_wall_radial_Green=G[4:84,:4],
            full_joint_wall_Green=G[4:,4:],full_source_response=u,
            original_frame_reactions=reaction,original_reaction_resolved_residual=residual-F.T@reaction,
            original_Gauss_reaction_resolved_residual=(residual-F.T@reaction)[:64],
            full_frame_residual=F@u))
    zero=results[0];actual_coeff=np.array([zero['radial_inverse'],zero['radial_inverse_first'],zero['radial_inverse_second']/2])
    contacts=actual_coeff-ref
    for row in results[1:]:
        z=complex(row['frequency']);reference=sum(ref[k]*z**k for k in range(3))
        nonquad=row['radial_inverse']-sum(actual_coeff[k]*z**k for k in range(3))
        row.update(reference_radial_inverse=reference,
            full_minus_reference_inverse=row['radial_inverse']-reference,
            surviving_nonquadratic_inverse=nonquad,
            inverse_matching_identity_residual=row['radial_inverse']-reference-
                (sum(contacts[k]*z**k for k in range(3))+nonquad))
    tangent=np.zeros((96,4));tangent[80:]=np.kron(r[:,None],np.eye(4));Rmap=T.T@tangent
    return dict(original_proper_frequency_coefficients=C,original_trace_map=T,canonical_radial_dual_wall=D,
        original_frame_rows=F,actual_radial_restricted_kinetic=Rmap.T@C[2]@Rmap,
        same_coordinate_reference_coefficients=ref,actual_scalar_kinetic_residue=Z,
        local_scalar_mode_vertex_conversion=1/np.sqrt(Z),
        static_linear_kinetic_matching_contacts=contacts,actual_inverse_zero_frequency_coefficients=actual_coeff,
        zero_application=zero,probe_applications=results[1:],
        scalar_and_gauge_sectors_summed_separately=False,canonical_to_weak_radial_pairing_factor=4,
        source_harmonics='all four real n1 copies; original84 point coordinates x4; all64 At rows',
        matching_reference='same proper-action scalar kinetic residue Z=R³/V and n1 eigenvalue3/R², independently matched scalar mass/E_kappa',
        named_Ar_frames_are_BRST_quotient=False,physical_mass_or_relative_domain_selected=False,
        physical_continuum_overlap_subtracted=False,physical_F2=None)


def radial_scalar_Pauli_covector_probe(matching,*,matched_fermion_mass_action,
        fixed_Y,quadrature_order,log_endpoint_edges=None):
    """Apply the known local scalar soft covector to this radial restriction.

    Both internal and external lepton masses in this calibrated local
    covector are m_match. The actual graph's interacting lepton Green is
    not replaced by this application: this is a matching diagnostic on
    the reached coupled scalar Green. The n1 trace-average is an explicit
    finite source readout, not a continuum spectator sum or a physical F2.
    """
    m,Y=float(matched_fermion_mass_action),float(fixed_Y)
    if not np.isfinite([m,Y]).all()or min(m,Y)<=0 or type(quadrature_order)is not int or quadrature_order<4:
        raise ValueError('positive matched mass, unchanged Y and explicit order required')
    C=matching['original_proper_frequency_coefficients'];D=matching['canonical_radial_dual_wall']
    F=matching['original_frame_rows'];T=matching['original_trace_map']
    ids=np.setdiff1d(np.arange(336),np.flatnonzero(np.any(F!=0,axis=0)));Q=np.eye(336)[:,ids]
    S=T.T@D;Z=matching['actual_scalar_kinetic_residue'];reference=matching['same_coordinate_reference_coefficients']
    gx,gw=np.polynomial.legendre.leggauss(quadrature_order)
    if log_endpoint_edges is None:
        xs=(gx+1)/2;ws=gw/2;ys=None
    else:
        edges=np.asarray(log_endpoint_edges,float)
        if edges.ndim!=1 or len(edges)<2 or edges[0]!=0 or np.any(np.diff(edges)<=0)or edges[-1]>36:
            raise ValueError('explicit increasing log endpoint partition0..at most36 required')
        ys=np.concatenate([lo+(hi-lo)*(gx+1)/2 for lo,hi in zip(edges[:-1],edges[1:])])
        ws=np.concatenate([gw*(hi-lo)/2 for lo,hi in zip(edges[:-1],edges[1:])])
        xs=-np.expm1(-ys)
    values=[];reference_values=[];residuals=[];returns=[]
    for j,x in enumerate(xs):
        endpoint=(1-x)if ys is None else np.exp(-ys[j])
        z=1j*m*x/np.sqrt(endpoint);A=sum(C[k]*z**k for k in range(3))
        u=Q@lu_solve(lu_factor(Q.T@A@Q),Q.T@S);g=S.T@u
        ref=sum(reference[k]*z**k for k in range(3))
        weight=-Y*Y/(16*np.pi**2)*m*m*x*x*(2-x)/(endpoint if ys is None else 1)
        values.append(weight*Z*np.trace(g)/4)
        reference_values.append(weight*Z*np.trace(np.linalg.solve(ref,np.eye(4)))/4)
        r=A@u-S;residuals.append(np.max(abs(r-F.T@(F@r))))
        returns.append(g)
    values,reference_values=np.array(values),np.array(reference_values)
    return dict(quadrature_x=xs,quadrature_weights=ws,canonical_radial_Green_samples=np.array(returns),
        radial_current_Pauli_covector_samples=values,same_coordinate_reference_covector_samples=reference_values,
        reached_radial_covector_value=np.array(ws@values),same_coordinate_reference_covector_value=np.array(ws@reference_values),
        reached_minus_reference_covector=np.array(ws@(values-reference_values)),
        original_reaction_resolved_equation_residual=np.array(residuals),
        matched_internal_and_external_fermion_mass_action=m,fixed_Y=Y,
        canonical_mode_kinetic_residue_removed_once=Z,
        log_endpoint_coordinates=np.array([])if ys is None else ys,
        log_endpoint_max=None if ys is None else float(edges[-1]),
        reference_omitted_endpoint_tail_upper=None if ys is None else float(2*Y*Y/(16*np.pi**2)*np.exp(-edges[-1])),
        reached_omitted_endpoint_tail_enclosed=False,
        consumer_equation='-Y²/(16pi²) integral m² x²(2-x)/(1-x) Z Tr4 G_h(i m x/sqrt(1-x))/4 dx; log form x=1-exp(-y), dx/(1-x)=dy',
        soft_covector_owner='muon_fixed_y_scalar_soft_overlap.scalar_parameter_pauli_numerator; both LR scalar vertices, matched internal/external poles',
        finite_n1_trace_average_is_continuum_propagator=False,
        replaced_native_interacting_fermion_Green=False,
        contour_poles_between_quadrature_nodes_certified=False,
        continuum_overlap_subtracted_from_native_current=False,physical_F2=None)
