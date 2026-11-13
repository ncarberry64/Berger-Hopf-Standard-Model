"""Action-realified reflected lepton coefficients and local formal square.

Real field coefficients have a unique conjugate-reflected analytic germ.
Higgs H and its opposite LR entry are formed from the same four real
coordinates before continuation.  The metric, material temporal gauge,
mechanical spatial connection and inherited affine image are each pulled
back once.  This local coefficient application is not a global Wick or
relative-exterior theorem.
"""
from __future__ import annotations
import numpy as np
from scipy.interpolate import CubicSpline,CubicHermiteSpline
from scipy.sparse import diags,bmat,csc_matrix,eye
from scipy.sparse.linalg import splu
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from .muon_parent_maxwell_full_weak import M
from .aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_continued_action_dual import analytic_midpoint_action


def _geometry(raw):
    """Literal value extension of intrinsic_m4_weight_jet's coframe."""
    x=np.asarray(raw,complex);q,v,m=x[:37],x[37:74],x[74:98]
    k=np.arange(1,13);j=np.arange(12);signk=(-1.)**k;signj=(-1.)**j
    Cstar=RADIUS0*np.exp(q[0]+q[1:13]@signk+q[13:25]@signj)
    logCdot=v[0]+v[1:13]@signk+v[13:25]@signj
    delta=x[98]/Cstar;delta_rate=(x[99]-logCdot*x[98])/Cstar
    chi=np.pi/4+delta;ck=np.cos(4*k*chi);cj=np.cos(4*j*chi)
    window=np.sin(2*chi)**2;u=q[1:13]@ck;b=window*(q[25:37]@cj)
    w=window*(q[13:25]@cj);radius=RADIUS0*np.exp(q[0])
    C=radius*np.exp(u+w);A=radius*np.exp(u+b)*np.cos(chi)
    B=radius*np.exp(u-b)*np.sin(chi);N=np.exp(m[:12]@ck)
    beta=np.sin(4*chi)*(m[12:]@cj);den=A*A+B*B
    U=C*(delta_rate+beta)/N
    if den.real<=0 or (1-U*U).real<=0:raise ValueError('local analytic coframe left the chosen square-root chart')
    R=A*B/np.sqrt(den);lapse=N*np.sqrt(1-U*U)
    return dict(R4=R,N=lapse,mechanical_lambda=A*A/den,Cstar=Cstar,
        delta=delta,wall=chi,wall_rate=delta_rate,U=U,C=C,A=A,B=B,lapse_base=N)


def _affine_raw(raw,t):
    x=np.asarray(raw,complex).copy();x[:37]+=t*x[37:74];x[98]+=t*x[99]
    return x


def _higgs_mass_realified(real_coefficients):
    """Holomorphic realification; no conjugation of the complex parameter."""
    x=np.asarray(real_coefficients,complex);y=lepton_current_hilbert_representation()['family_Y']
    hp=x[:2]+1j*x[2:];hm=x[:2]-1j*x[2:]
    upper=np.einsum('a,fg,st->afsgt',hp,y,np.eye(2)).reshape(12,6)
    lower=np.einsum('a,fg,st->gt afs',hm,y.conj(),np.eye(2)).reshape(6,12)
    mass=np.zeros((18,18),complex);mass[:12,12:]=upper;mass[12:,:12]=lower
    return mass


def action_reality_coefficient(phase,coordinate_anchor,offset=0j):
    """Evaluate the exact inside-cell coefficient map at a complex offset.

    x is the saved affine coefficient curve, v/y stay at the same midpoint.
    Parent and reference clocks keep their declared affine law. This is an
    analytic extension of that explicit numerical representation, not of
    an uncomputed continuous nonlinear Euler solution.
    """
    sample=profile_preserving_raw_sample(phase,float(coordinate_anchor))
    raw=sample['raw_fields'].astype(complex)+complex(offset)*sample['raw_coordinate_time_derivative']
    geo=_geometry(raw);rep=phase['representation'];ng=rep['gauge_count']
    trace=np.einsum('fcj,j->fc',rep['wall_trace_map'],raw[100:100+ng])
    if phase['receipt']['side']=='outgoing':
        t=complex(coordinate_anchor)+complex(offset)
        p=_geometry(_affine_raw(phase['arrays']['initial_pair'][0],t))
        rp,rc=(_geometry(_affine_raw(x,t))for x in phase['arrays']['reference_pair'])
        image=p['mechanical_lambda']-geo['mechanical_lambda']-(rp['mechanical_lambda']-rc['mechanical_lambda'])
        trace[2:]+=M*image
    else:image=0j
    generators=lepton_unit_trace_gauge_representation()['generators']
    space=trace[2:]+M*(geo['mechanical_lambda']-1)
    Os=np.einsum('ac,cij->aij',space,generators)
    Omega=np.einsum('c,cij->ij',trace[0],generators)/geo['N']
    hilbert=lepton_current_hilbert_representation()
    mass=_higgs_mass_realified(raw[-8:-4])
    W=(-1j*np.einsum('aij,ajk->ik',hilbert['alpha'],Os)+1.5*hilbert['gamma5'])/geo['R4']+mass
    return dict(W=W,Omega=Omega,Hcan=W-1j*Omega,geometry=geo,
        raw=raw,wall_independent_plus_inherited=trace,inherited_image=image,
        offset=complex(offset),coordinate_anchor=float(coordinate_anchor))


def reflected_action_reality_coefficient(phase,coordinate_anchor,offset=0j):
    """Compute Hsharp(z)=H(conj(z))† from the action's real coordinates."""
    a=action_reality_coefficient(phase,coordinate_anchor,offset)
    reflected=action_reality_coefficient(phase,coordinate_anchor,np.conj(offset))
    a.update(W_sharp=reflected['W'].conj().T,Omega_sharp=reflected['Omega'].conj().T,
        Hcan_sharp=reflected['Hcan'].conj().T,
        W_reflection_residual=float(np.max(abs(a['W']-reflected['W'].conj().T))),
        Omega_reflection_residual=float(np.max(abs(a['Omega']+reflected['Omega'].conj().T))),
        Hcan_reflection_residual=float(np.max(abs(a['Hcan']-reflected['Hcan'].conj().T))))
    return a


def actual_source_curve_coefficients(source_phase,velocity,contacts):
    """Derive the retained Hermite/cubic polynomials from their actual arrays."""
    t=np.asarray(source_phase['times'],float);state=np.asarray(source_phase['state'],float)
    if not np.array_equal(t,velocity['times'])or not np.array_equal(t,contacts['times']):
        raise ValueError('same actual source clocks required')
    return dict(times=t,
        positions=CubicHermiteSpline(t,state[:,:400],velocity['velocity']),
        temporal=CubicSpline(t,contacts['A_tau']),
        wall=CubicHermiteSpline(t,contacts['source_trace'],contacts['source_trace_rate']))


def _analytic_polynomial(p,anchor,offset):
    # Continue the unique cell polynomial. Complex scipy PPoly evaluation
    # discards imaginary arguments, so use its actual stored coefficients.
    j=min(max(np.searchsorted(p.x,float(anchor),side='right')-1,0),len(p.x)-2)
    z=complex(anchor)+complex(offset)-p.x[j]
    return sum(p.c[k,j]*z**(len(p.c)-1-k)for k in range(len(p.c)))


def action_reality_source(phase,anchor,source_curves,offset=0j):
    """Actual canonical magnetic Xi on the reflected coefficient branch."""
    app=action_reality_coefficient(phase,anchor,offset);geo=app['geometry']
    L=abs(float(phase['receipt']['span']));u=anchor+L if phase['receipt']['side']=='incoming'else anchor
    wall=_analytic_polynomial(source_curves['wall'],u,offset).T.reshape(8,5,4,20)
    p=_analytic_polynomial(source_curves['positions'],u,offset)
    H=p[320:400].T.reshape(8,4,20)
    generators=lepton_unit_trace_gauge_representation()['generators'];rep=lepton_current_hilbert_representation()
    vg=np.zeros((5,4,18,18),complex);vg[0]=-1j*generators/geo['N']
    vg[2:]=-1j*np.einsum('aij,cjk->acik',rep['alpha'],generators)/geo['R4']
    Xi=np.einsum('afch,fcij->ahij',wall,vg)
    Xi+=np.array([[_higgs_mass_realified(x)for x in a.T]for a in H])
    return dict(Xi=Xi,source_H=H,source_wall=wall,
        source_time_kind='same saved Hermite/cubic cell polynomials, complex parameter retained',electric_charge_added_again=False)


def certify_local_coframe_disk(phase,anchor,radius,*,source_curves=None,precision_bits=128):
    """Outward coframe chart check on the exact stored affine coefficient disk.

    Acb encloses the rectangle |Re z|,|Im z|<=radius, hence the disk.
    Re(A²+B²)>0 and |U|<1 fix both square-root branches analytically.
    This certifies that local value representation and its denominator
    charts, not a continuous Euler solution or global relative contour.
    """
    from flint import acb,arb,ctx
    anchor=float(anchor);radius=float(radius)
    if not np.isfinite(radius)or radius<=0:raise ValueError('positive local disk required')
    s=profile_preserving_raw_sample(phase,anchor);h=float(s['cell_signed_step'])
    left,right=sorted((s['stage']*h,(s['stage']+1)*h))
    if not radius<min(anchor-left,right-anchor):raise ValueError('disk crosses a represented primal cell face')
    L=abs(float(phase['receipt']['span']));u=anchor+L if phase['receipt']['side']=='incoming'else anchor
    if source_curves is not None:
        knots=source_curves['times'];j=np.searchsorted(knots,u,side='right')-1
        if j<0 or j>=len(knots)-1 or not radius<min(u-knots[j],knots[j+1]-u):
            raise ValueError('disk crosses a source Hermite/cubic face')
    old=ctx.prec;ctx.prec=precision_bits
    try:
        z=acb(arb(0,radius),arb(0,radius));pi=arb(float(np.pi));R0=arb(float(RADIUS0))
        def linear_raw(x,rate,time=0.):
            return [acb(arb(float(a)))+(z+arb(float(time)))*arb(float(b))for a,b in zip(x,rate)]
        def geom(x):
            q,v,m=x[:37],x[37:74],x[74:98]
            ks=range(1,13);js=range(12)
            cs=R0*(q[0]+sum((q[1+j]*((-1)**k)for j,k in enumerate(ks)),acb(0))
                +sum((q[13+j]*((-1)**j)for j in js),acb(0))).exp()
            logdot=v[0]+sum((v[1+j]*((-1)**k)for j,k in enumerate(ks)),acb(0))
            logdot+=sum((v[13+j]*((-1)**j)for j in js),acb(0))
            delta=x[98]/cs;dr=(x[99]-logdot*x[98])/cs;chi=pi/4+delta
            ck=[(4*k*chi).cos()for k in ks];cj=[(4*j*chi).cos()for j in js]
            window=(2*chi).sin()**2;u=sum((a*b for a,b in zip(q[1:13],ck)),acb(0))
            b=window*sum((a*b for a,b in zip(q[25:37],cj)),acb(0))
            w=window*sum((a*b for a,b in zip(q[13:25],cj)),acb(0));rad=R0*q[0].exp()
            C=rad*(u+w).exp();A=rad*(u+b).exp()*chi.cos();B=rad*(u-b).exp()*chi.sin()
            N=sum((a*b for a,b in zip(m[:12],ck)),acb(0)).exp()
            beta=(4*chi).sin()*sum((a*b for a,b in zip(m[12:],cj)),acb(0))
            U=C*(dr+beta)/N;den=A*A+B*B
            return dict(denominator_real_lower=den.real.lower(),one_minus_U_squared_real_lower=(1-U*U).real.lower(),
                wall_U_absolute_upper=U.abs_upper(),Cstar_absolute_lower=cs.abs_lower(),
                A_absolute_lower=A.abs_lower(),B_absolute_lower=B.abs_lower(),N_absolute_lower=N.abs_lower())
        raws=[('child_or_incoming',s['raw_fields'],s['raw_coordinate_time_derivative'],0.)]
        if phase['receipt']['side']=='outgoing':
            for name,x in [('parent',phase['arrays']['initial_pair'][0]),
                ('reference_parent',phase['arrays']['reference_pair'][0]),('reference_child',phase['arrays']['reference_pair'][1])]:
                base=np.asarray(x,float);rate=np.zeros_like(base);rate[:37]=base[37:74];rate[98]=base[99]
                raws.append((name,base,rate,anchor))
        records=[]
        for name,x,rate,time in raws:
            vals=geom(linear_raw(x,rate,time))
            if not (vals['denominator_real_lower']>0 and vals['one_minus_U_squared_real_lower']>0
                and vals['wall_U_absolute_upper']<1 and min(vals[k]for k in('Cstar_absolute_lower','A_absolute_lower','B_absolute_lower','N_absolute_lower'))>0):
                raise ArithmeticError('coframe disk not enclosed in the action chart: '+name)
            records.append(dict(name=name,**{k:str(v)for k,v in vals.items()}))
        return dict(classification='CERTIFIED_EXACT_STORED_LOCAL_AFFINE_COFRAME_ANALYTIC_DISK',
            anchor=anchor,radius=radius,precision_bits=precision_bits,records=records,
            source_polynomial_cell_preserved=source_curves is not None,
            enclosure_region='Acb square containing the closed complex disk',
            exact_input_convention='stored binary64 primal/affine coefficients and representation constants',
            physical_continuum_solution_or_global_contour_certified=False)
    finally:ctx.prec=old


def local_formal_reflected_square(weights,body,body_sharp,*,rotation=1j):
    """Analytic weak product using the independently evaluated reflection.

    K=Abar^T G_contour A, Abar=Delta/(r*w)+Hsharp^T midpoint.
    Its coefficient conjugation/reality is composed BEFORE changing r;
    the derivative coefficient is not conjugated anew on the imaginary
    slice. At r=1 with a Hermitian real-anchor body it is the usual weak
    square. At r=i it has the continued negative temporal principal part.
    The final natural contact remains K's full last row, not Dirichlet.
    """
    w=np.asarray(weights,complex);H,Hs=np.asarray(body,complex),np.asarray(body_sharp,complex)
    if w.ndim!=1 or np.any(w.real<=0)or not np.isfinite(w).all()or not np.isfinite(H).all()or Hs.shape!=H.shape:
        raise ValueError('complete local continued weights and reflected body germ required')
    a=_complex_midpoint_maps(w,H,rotation)
    bar=_complex_midpoint_maps(w,Hs.swapaxes(-1,-2),rotation)
    A,Abar=a['A'],bar['A'];G=a['G']
    K=(Abar.T@G@A).tocsc()
    # M has the same fixed midpoint density quadrature as the coefficient
    # square. Its complex contour phase is retained explicitly.
    n,m=H.shape[:2];d=w/3;d[:-1]+=w[1:]/3
    t=np.diag(d)+np.diag(w[1:]/6,1)+np.diag(w[1:]/6,-1)
    return dict(A=A,Abar=Abar,K=K,variable_Gram=complex(rotation)*np.kron(t,np.eye(m)),
        source_Gram=G,formal_reflection_body=Hs,
        final_natural_contact_rows=K[-m:,:],ordinary_imaginary_slice_positive_square=(A.conj().T@diags(np.repeat(abs(w),m))@A).tocsc(),
        original_Green_rows=a['Green_rows'],Green_identity_max=a['Green_identity_max'],
        real_Euclidean_relative_domain_or_sectorial_completion_proved=False)


def _complex_midpoint_maps(weights,body,rotation):
    w,H=np.asarray(weights,complex),np.asarray(body,complex);r=complex(rotation)
    n,m=H.shape[:2];blocks=[[None]*(n+1)for _ in range(n)];av=[[None]*(n+1)for _ in range(n)]
    flat=[[None]*(n+1)for _ in range(n)]
    for j in range(n):
        d=csc_matrix(np.eye(m)/(r*w[j]));h=csc_matrix(H[j]/2);ht=csc_matrix(H[j].T/2)
        blocks[j][j],blocks[j][j+1]=h-d,h+d
        flat[j][j],flat[j][j+1]=ht+d,ht-d
        av[j][j]=av[j][j+1]=eye(m,format='csc')/2
    full=bmat(blocks,format='csc');left=bmat(flat,format='csc');B=bmat(av,format='csc')
    G=diags(np.repeat(r*w,m),format='csc')
    E=diags(np.r_[-np.ones(m),np.zeros((n-1)*m),np.ones(m)],format='csc')
    rows=(B.T@G@full-left.T@G@B-E).tocsc()
    return dict(A=full[:,m:].tocsc(),G=G,Green_rows=rows,
        Green_identity_max=float(np.max(abs(rows.data)))if rows.nnz else 0.)


def formal_square_current_application(factor,source_right,literal_target):
    """Actual analytic numerator and original free-final domain application."""
    R=np.asarray(source_right,complex);L=np.asarray(literal_target,complex)
    numerator=factor['Abar'].T@factor['source_Gram']@R
    u=splu(factor['K']).solve(numerator);direct=splu(factor['A']).solve(R)
    left=splu(factor['K'].T.tocsc()).solve(L.T)
    value=L@u
    return dict(response=u,source_numerator=numerator,analytic_left=left,current=value,
        original_right_rows=factor['A']@u-R,original_form_rows=factor['K']@u-numerator,
        analytic_pairing=left.T@numerator,inverse_identity_max=float(np.max(abs(u-direct))),
        pairing_max=float(np.max(abs(value-left.T@numerator))))


def formal_square_magnetic_application(source,target,R,delta_forward,delta_bar_reverse):
    """Keep both analytic product contacts and numerator before inversion.

    delta_bar_reverse is the continued REFLECTED coefficient factor's
    reverse block, derived from the action-realified full source, rather
    than a new pointwise conjugation of delta_forward on the contour.
    """
    R=np.asarray(R,complex);dA=csc_matrix(delta_forward);dbar=csc_matrix(delta_bar_reverse)
    s,t=source,target
    u=splu(s['A']).solve(R)
    dK=(dbar.T@s['source_Gram']@s['A']+t['Abar'].T@t['source_Gram']@dA).tocsc()
    dB=dbar.T@s['source_Gram']@R
    response=splu(t['K']).solve(dB-dK@u)
    direct=splu(t['A']).solve(-dA@u)
    return dict(response=response,delta_form=dK,delta_numerator=dB,
        original_right_rows=t['A']@response+dA@u,
        original_form_rows=t['K']@response-(dB-dK@u),
        c0_inverse_contact_identity_max=float(np.max(abs(response-direct))))
