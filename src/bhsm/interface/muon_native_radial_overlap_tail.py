"""Projected high-frequency control of the original constrained scalar pencil.

The algebraic At block is eliminated by its literal action equation. Named
Ar coordinates remain fixed with their reactions; no numerical null vector
is removed. Certificates enclose exact stored entries, not their production
or the physical continuum/native matching.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eig, lu_factor, lu_solve


def radial_schur_pencil(coefficients, source, frame_rows, *, At_count=64):
    """Return D(w)=K+w J-w^2 M for the Lorentz pencil at z=i*w.

    C(z)=C0+z*C1+z^2*C2 is the proper Lorentz Fourier action. Exact
    zero At kinetic/At-At linear entries are checked, rather than assumed.
    Both independent action placements are used even when stored rounding
    makes a coefficient slightly nonsymmetric.
    """
    C,S,F=map(np.asarray,(coefficients,source,frame_rows))
    n=C.shape[-1]
    if (C.shape!=(3,n,n) or S.ndim!=2 or S.shape[0]!=n or F.ndim!=2
            or F.shape[1]!=n or not np.isfinite(C).all()
            or not np.isfinite(S).all() or not np.isfinite(F).all()
            or type(At_count)is not int or not 0<At_count<n):
        raise ValueError('full polynomial, source, literal frame and At order required')
    if not np.isrealobj(S) or not np.isrealobj(F):
        raise ValueError('original real coefficient source/frame required')
    rejected=np.flatnonzero(np.any(F!=0,axis=0))
    if (len(rejected)!=len(F) or not np.array_equal(F@F.T,np.eye(len(F)))
            or np.any(rejected<At_count)):
        raise ValueError('literal named dynamic-coordinate frame rows required')
    kept=np.setdiff1d(np.arange(n),rejected)
    c=C[:,kept][:,:,kept]
    if (np.any(c[2,:At_count]) or np.any(c[2,:,:At_count])
            or np.any(c[1,:At_count,:At_count])):
        raise ValueError('At must be the action-owned algebraic block')
    if np.any(c[[0,2]].imag) or np.any((1j*c[1]).imag):
        raise ValueError('real Lorentz action with purely imaginary linear coefficient required')
    s=S[kept]
    if np.any(s[:At_count]):
        raise ValueError('this radial consumer has an exactly zero algebraic source')
    c0,c1,c2=c[0].real,(1j*c[1]).real,c[2].real
    p,u,v,q,w=(c0[:At_count,:At_count],c0[:At_count,At_count:],
        c0[At_count:,:At_count],c1[:At_count,At_count:],c1[At_count:,:At_count])
    pu,pq=np.linalg.solve(p,u),np.linalg.solve(p,q)
    k=c0[At_count:,At_count:]-v@pu
    j=c1[At_count:,At_count:]-v@pq-w@pu
    m=c2[At_count:,At_count:]+w@pq
    return dict(K=k,J=j,M=m,source=s[At_count:],kept_indices=kept,
        At_matrix=p,At_constant_right=u,At_constant_left=v,
        At_linear_right=q,At_linear_left=w,
        raw_K=c0[At_count:,At_count:],raw_J=c1[At_count:,At_count:],
        raw_M=c2[At_count:,At_count:],original_coefficients=C,
        original_source=S,original_frame_rows=F,At_count=At_count,
        all_Gauss_rows_eliminated_by_literal_equation=True,
        named_frames_are_BRST_quotient=False,
        Lorentz_frequency_continued_exactly_once=True)


def radial_schur_application(pencil,omega):
    """Apply the reduced action and reconstruct every At/frame reaction."""
    z=complex(omega);k,j,m,s=(pencil[a]for a in('K','J','M','source'))
    x=lu_solve(lu_factor(k+z*j-z*z*m),s)
    a=-np.linalg.solve(pencil['At_matrix'],
        (pencil['At_constant_right']+z*pencil['At_linear_right'])@x)
    full=np.zeros((len(pencil['original_source']),s.shape[1]),complex)
    full[pencil['kept_indices']]=np.r_[a,x]
    C=pencil['original_coefficients'];r=(C[0]+1j*z*C[1]-z*z*C[2])@full-pencil['original_source']
    F=pencil['original_frame_rows'];reaction=F@r
    return dict(canonical_radial_Green=s.T@x,full_source_response=full,
        original_frame_reactions=reaction,
        original_reaction_resolved_residual=r-F.T@reaction,
        original_Gauss_residual=r[:pencil['At_count']])


def certify_projected_radial_tail(pencil,*,matched_mass_action,fixed_Y,
        kinetic_residue,log_start=32.,precision_bits=192):
    """Uniform outward tail bound from the exact stored At Schur action.

    At t=1/w, -D(w)/w^2=M-tJ-t^2K. A fixed invertible real U
    whitens sym(M). Arb verifies
      U^T sym(M-tJ-t^2K) U >= (1-delta) I, 0<=t<=t0.
    No Neumann test on the poorly scaled full saddle is necessary. The
    analytic left-source contraction is bounded by
      |Tr S^T D(w)^-1 S|/r <= t^2 ||U^T S||_F^2/[r(1-delta)].
    With w=m*x/sqrt(1-x), x=1-exp(-y), its integrated covector tail is
      Y^2 Z gamma/(16 pi^2) [exp(-y0)+exp(-2y0)/2]/(1-delta).
    """
    from flint import arb,arb_mat,ctx
    ma,Y,Z,y0=map(float,(matched_mass_action,fixed_Y,kinetic_residue,log_start))
    if min(ma,Y,Z,y0)<=0 or not np.isfinite([ma,Y,Z,y0]).all()or precision_bits<128:
        raise ValueError('positive declared mass/Y/kinetic residue/log cutoff required')
    sym=lambda a:(a+a.T)/2
    # This is only a proposed preconditioner. Every claim is verified below
    # against the original stored coefficients with interval arithmetic.
    mm=sym(pencil['M']);ev,V=np.linalg.eigh(mm)
    if np.min(ev)<=0:raise ArithmeticError('positive high-frequency Schur metric needs action-derived reduction')
    U=V/np.sqrt(ev)[None,:]
    kw=sym(U.T@pencil['K']@U);ke,kV=np.linalg.eigh(kw)
    old=ctx.prec;ctx.prec=precision_bits
    try:
        def balls(a):return arb_mat([[arb(float(x))for x in row]for row in np.asarray(a)])
        def trans(a):return a.transpose()
        def sm(a):return(a+trans(a))*arb(.5)
        def frob(a):return sum((a[i,j]**2 for i in range(a.nrows())for j in range(a.ncols())),arb(0)).sqrt()
        def upper(a):return float(np.nextafter(float(a.upper()),np.inf))
        P,UR,VL,QR,WL,RK,RJ,RM=(balls(pencil[a])for a in
            ('At_matrix','At_constant_right','At_constant_left','At_linear_right','At_linear_left','raw_K','raw_J','raw_M'))
        # Verified flint solve; these balls enclose the exact stored saddle.
        PU=P.solve(UR);PQ=P.solve(QR)
        K=RK-VL*PU;J=RJ-VL*PQ-WL*PU;M=RM+WL*PQ
        UU,SS=balls(U),balls(pencil['source']);I=balls(np.eye(len(mm)))
        mw=trans(UU)*sm(M)*UU;jw=trans(UU)*sm(J)*UU;kwb=trans(UU)*sm(K)*UU
        delta_m=frob(mw-I);j_norm=frob(jw)
        VV=balls(kV);gram_defect=frob(trans(VV)*VV-I)
        congruence_error=frob(trans(VV)*kwb*VV-balls(np.diag(ke)))
        if not gram_defect<1:raise ArithmeticError('kernel congruence basis is not verified invertible')
        # Upper Loewner bound uses only the positive maximum, never the
        # large negative part of the high-frequency action.
        k_upper=(arb(max(0.,float(ke[-1])))+congruence_error)/(1-gram_defect)
        e0=(-arb(y0)).exp();x0=1-e0;t0=e0.sqrt()/(arb(ma)*x0)
        delta=delta_m+t0*j_norm+t0*t0*k_upper
        if not delta<1:raise ArithmeticError('uniform high-frequency action coercivity not proved')
        us=trans(UU)*SS;gamma=frob(us)**2/arb(SS.ncols())
        tail=arb(Y)**2*arb(Z)*gamma*(e0+e0**2/2)/(16*arb.pi()**2*(1-delta))
        return dict(precision_bits=precision_bits,log_start=y0,
            omega_start_lower=float(np.nextafter(float((1/t0).lower()),-np.inf)),
            inverse_frequency_start_upper=upper(t0),
            Schur_metric_whitening_defect_upper=upper(delta_m),
            Schur_linear_symmetric_norm_upper=upper(j_norm),
            Schur_constant_Loewner_upper=upper(k_upper),
            constant_congruence_error_upper=upper(congruence_error),
            constant_eigenvector_Gram_defect_upper=upper(gram_defect),
            uniform_coercivity_loss_upper=upper(delta),
            radial_whitened_source_square_average_upper=upper(gamma),
            canonical_kinetic_times_radial_source_square_upper=upper(arb(Z)*gamma),
            reached_omitted_tail_absolute_upper=upper(tail),
            exact_stored_imaginary_path_pole_free_for_y_ge_start=True,
            uniform_projected_tail_enclosed=True,
            original_Gauss_block_retained=True,
            named_frame_reactions_retained=True,numerical_mode_deletion=False,
            certificate_inputs='exact binary64 stored C and radial dual; exact declared binary64 m,Y,Z,y0; Arb transcendental and matrix operations',
            coefficient_production_or_continuum_error_enclosed=False,
            physical_native_overlap_or_Pauli_identification=False),U
    finally:ctx.prec=old


def radial_tail_quadrature(pencil,*,matched_mass_action,fixed_Y,kinetic_residue,
        log_start=32.,order=12):
    """Diagnostic tail value with stable reciprocal-frequency variables.

    v=exp(-(y-y0)) makes the whole remaining interval compact [0,1].
    The removable v=0 endpoint is the projected high-frequency limit.
    """
    if type(order)is not int or order<4:raise ValueError('explicit tail quadrature order required')
    m,Y,Z=map(float,(matched_mass_action,fixed_Y,kinetic_residue))
    gx,gw=np.polynomial.legendre.leggauss(order);v=(gx+1)/2;weights=gw/2
    e0=np.exp(-log_start);s=pencil['source'];values=[];defects=[]
    for b in v:
        endpoint=e0*b;x=1-endpoint;t=np.sqrt(endpoint)/(m*x)
        H=pencil['M']-t*pencil['J']-t*t*pencil['K']
        u=np.linalg.solve(H,s)
        # G=-t² S^T H^-1 S; m²*x²*t²=e0*v. dy=-dv/v.
        values.append(Y*Y*Z/(16*np.pi**2)*e0*(2-x)*np.trace(s.T@u)/s.shape[1])
        defects.append(np.max(abs(H@u-s)))
    return dict(quadrature_v=v,quadrature_weights=weights,
        tail_covector_samples=np.asarray(values),tail_covector_value=np.array(weights@values),
        scaled_Schur_equation_residual=np.asarray(defects),log_start=float(log_start),
        quadrature_order=order,quadrature_error_is_not_outward_bound=True)


def radial_soft_path_poles(pencil,*,imaginary_tolerance=1e-6):
    """All finite companion roots/residues, without deleting small returns.

    The roots are numerical diagnostics. A real-axis root is NOT certified
    solely from its small imaginary part. Degenerate clusters require a
    contour residue or complete cluster pairing before physical use.
    """
    K,J,M,S=(pencil[a]for a in('K','J','M','source'));d=len(K)
    A=np.block([[np.zeros((d,d)),np.eye(d)],[K,J]])
    B=np.block([[np.eye(d),np.zeros((d,d))],[np.zeros((d,d)),M]])
    w,vl,vr=eig(A,B,left=True,right=True)
    order=np.lexsort((w.imag,w.real));w=w[order];vl=vl[:,order];vr=vr[:,order]
    residues=[];defects=[]
    scale=np.array([np.linalg.norm(K),np.linalg.norm(J),np.linalg.norm(M)])
    for i,z in enumerate(w):
        v=vr[:d,i];l=vl[d:,i].conj();der=l@(J-2*z*M)@v
        residues.append(np.outer(S.T@v,l@S)/der)
        pol=K+z*J-z*z*M;den=scale@[1,abs(z),abs(z)**2]
        defects.append([np.linalg.norm(pol@v)/(np.linalg.norm(v)*den),
            np.linalg.norm(l@pol)/(np.linalg.norm(l)*den)])
    ids=np.flatnonzero((w.real>0)&(abs(w.imag)<imaginary_tolerance))
    return dict(all_omega_companion_roots=w,all_canonical_radial_omega_residues=np.asarray(residues),
        all_left_right_polynomial_relative_residual=np.asarray(defects),
        positive_real_path_candidate_indices=ids,
        candidates_are_not_interval_certified_axis_poles=True,
        infinitesimal_contour_branch_or_principal_value_assigned=False,
        original_Lorentz_frequency_z_is_i_omega=True,
        source_residue_not_replaced_by_eigenvector_norm=True)


def radial_cluster_contour_residue(pencil,*,center,radius,matched_mass_action,
        fixed_Y,kinetic_residue,order=32):
    """Evaluate both the Green residue and its actual soft-covector weight.

    This closed Cauchy integral is an analytic diagnostic of the original
    rational action, not a choice of Feynman vacuum or principal value.
    A path displaced above/below an enclosed real pole differs by this
    actual 2*pi*i weighted residue with sign from path orientation.
    """
    c,r,m,Y,Z=map(float,(center,radius,matched_mass_action,fixed_Y,kinetic_residue))
    if min(c,r,m,Y,Z)<=0 or r>=c or order<8:
        raise ValueError('isolated positive-frequency cluster circle required')
    theta=2*np.pi*(np.arange(order)+.5)/order;zs=c+r*np.exp(1j*theta)
    residues=[];weighted=[];residuals=[]
    S=pencil['source']
    for z in zs:
        D=pencil['K']+z*pencil['J']-z*z*pencil['M']
        u=np.linalg.solve(D,S);g=S.T@u
        # Solve z=m*x/sqrt(1-x) using a stable analytic branch near z>0.
        a=m/z; x=2/(1+np.sqrt(1+4*a*a))
        weight=-Y*Y/(16*np.pi**2)*2*m*m*x**3*Z/z
        residues.append((z-c)*g);weighted.append((z-c)*weight*np.trace(g)/S.shape[1])
        residuals.append(np.max(abs(D@u-S)))
    gr=np.mean(residues,axis=0);wr=np.mean(weighted)
    return dict(center=c,radius=r,quadrature_order=order,circle_frequencies=zs,
        radial_cluster_residue=gr,soft_covector_cluster_residue=np.array(wr),
        upper_minus_lower_path_bypass=np.array(-2j*np.pi*wr),
        original_Schur_residual=np.asarray(residuals),
        contour_error_is_not_outward_bound=True,
        native_Feynman_or_retarded_loop_branch_selected=False)


def radial_detoured_soft_covector(pencil,clusters,*,matched_mass_action,fixed_Y,
        kinetic_residue,reference_mass_squared,log_end=32.,order=16):
    """Execute BOTH oriented analytic bypasses of the reached rational action.

    Each real-frequency interval through a candidate cluster is replaced
    by a semicircle with the same endpoints, before contracting. 'Upper'
    means Im(omega)>0, hence Re(z)<0 for the Lorentz frequency z=i*omega.
    'Lower' is the positive-Lorentz-frequency rotation on the right side
    of the imaginary z axis. Neither branch is promoted to the adopted
    quantum Feynman loop on this off-shell finite action.
    """
    m,Y,Z,mu2=map(float,(matched_mass_action,fixed_Y,kinetic_residue,reference_mass_squared))
    if min(m,Y,Z,mu2)<=0 or order<4:raise ValueError('positive same-coordinate matching data required')
    rows=sorted([(float(c),float(r))for c,r in clusters])
    if any(c<=r or r<=0 for c,r in rows):raise ValueError('positive isolated cluster circles required')
    if any(c+r>=d-s for (c,r),(d,s)in zip(rows[:-1],rows[1:])):
        raise ValueError('cluster bypasses must be disjoint')
    K,J,M,S=(pencil[a]for a in('K','J','M','source'))
    def x_at(w):return 2/(1+np.sqrt(1+4*(m/w)**2))
    def y_at(w):
        # 1-x=(m*x/w)^2 is stable even at large positive frequency.
        x=x_at(w);return -2*np.log(m*x/w)
    def point(w):
        D=K+w*J-w*w*M;u=np.linalg.solve(D,S);g=np.trace(S.T@u)/S.shape[1]
        x=x_at(w);weight=-Y*Y/(16*np.pi**2)*2*m*m*x**3*Z/w
        ref=-1/(Z*(w*w+mu2))
        return weight*g,weight*ref,np.max(abs(D@u-S))
    cuts=[(float(y_at(c-r)),float(y_at(c+r)),c,r)for c,r in rows]
    if any(lo<=0 or hi>=log_end for lo,hi,_,_ in cuts):raise ValueError('bypass circles must lie inside the consumed finite interval')
    gx,gw=np.polynomial.legendre.leggauss(order)
    bounds=sorted(set([0.,float(log_end)]+[y for y in(4.,8.,12.,16.,20.,24.)if y<log_end]
        +[y for lo,hi,_,_ in cuts for y in(lo,hi)]))
    intervals=[];regular=0j;reference=0j;residuals=[]
    for lo,hi in zip(bounds[:-1],bounds[1:]):
        if any(lo>=a and hi<=b for a,b,_,_ in cuts):continue
        ys=lo+(hi-lo)*(gx+1)/2;weights=gw*(hi-lo)/2;vals=[];refs=[]
        for y in ys:
            endpoint=np.exp(-y);x=-np.expm1(-y);w=m*x/np.sqrt(endpoint)
            val,ref,err=point(w);jac=w*(2-x)/(2*x)
            vals.append(val*jac);refs.append(ref*jac);residuals.append(err)
        vv=weights@vals;rr=weights@refs;regular+=vv;reference+=rr
        intervals.append((lo,hi,vv,rr))
    arcs={'upper':[],'lower':[]}
    for lo,hi,c,r in cuts:
        for side,start in(('upper',np.pi),('lower',-np.pi)):
            theta=start*(1-(gx+1)/2);weights=-start*gw/2
            value=0j;refvalue=0j
            for th,wt in zip(theta,weights):
                w=c+r*np.exp(1j*th);dw=1j*r*np.exp(1j*th)
                v,ref,err=point(w);value+=wt*v*dw;refvalue+=wt*ref*dw;residuals.append(err)
            arcs[side].append((c,r,value,refvalue))
    upper=regular+sum(a[2]for a in arcs['upper']);lower=regular+sum(a[2]for a in arcs['lower'])
    ru=reference+sum(a[3]for a in arcs['upper']);rl=reference+sum(a[3]for a in arcs['lower'])
    return dict(regular_interval_records=np.asarray(intervals),
        upper_semicircle_records=np.asarray(arcs['upper']),lower_semicircle_records=np.asarray(arcs['lower']),
        upper_reached_covector=np.array(upper),lower_reached_covector=np.array(lower),
        upper_same_coordinate_reference=np.array(ru),lower_same_coordinate_reference=np.array(rl),
        upper_same_coordinate_subtraction=np.array(upper-ru),lower_same_coordinate_subtraction=np.array(lower-rl),
        upper_minus_lower=np.array(upper-lower),original_Schur_residual=np.asarray(residuals),
        quadrature_order=order,log_end=log_end,
        upper_Lorentz_frequency_side='Re(z)<0; z=i*omega',
        lower_Lorentz_frequency_side='Re(z)>0; positive real Lorentz-frequency rotation',
        branch_error_is_not_outward_bound=True,principal_value_selected=False,
        adopted_native_Feynman_loop_or_physical_Pauli_identified=False)
