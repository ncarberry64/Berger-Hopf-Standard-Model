"""Compact, domain-valid first-order reduction of the UNADOPTED seam.

This is a restricted stationary action diagnostic on one retained interior
element. It is not the retarded complementary Green action or a native
operator update. Cached mode norms, point clocks and profiles are reused.
"""
from __future__ import annotations
import numpy as np
from bhsm.interface.muon_parent_maxwell_velocity import current_parent_fields
from bhsm.interface.muon_coupled_cut_forms import field_actions


def point_coefficients(point, receipt, log_radius, grid, cut, contact):
    """Only coefficient reconstruction needed for first-order columns.

    No field/clock/normalization producer is rerun. u,p,I,I_tau,proper
    clock and metric time jets are the actual retained point operands.
    """
    f=current_parent_fields(point['actual_state'][None],np.array([log_radius]),grid)
    rho=cut['points'];cells=cut['cells'];width=np.diff(grid)[cells]
    x=(rho-grid[cells])/width
    val=lambda a:a[cells]*(1-x)+a[cells+1]*x
    dr=lambda a:np.diff(a)[cells]/width
    nu,C,r,z=(val(f[k][0]) for k in ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    nr,Cr,rr,zr=(dr(f[k][0]) for k in ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    Ct=val(point['C_tau_nodes']);rt=val(point['r_tau_nodes'])
    H=float(receipt['H']);Tb=float(receipt['T_b'])
    hat=val(contact['spinor_probe_hat_nodes']);hatr=dr(contact['spinor_probe_hat_nodes'])
    p=point['p'];pr=Tb*(hatr/r-hat*rr/r**2);pt=(-H/2-rt/r)*p
    h0=(Ct/C+3*rt/r-z*(Cr/C+3*rr/r)-zr)/(2*nu)
    h4=(nr/nu+3*rr/r)/(2*C);eta=-.5/(C*np.tan(rho/2))
    s=dict(points=rho,cells=cells,nu=nu,C=C,r=r,z=z,u=point['u'],p=p,
        pr=pr,pt=pt,h0=h0,h4=h4,eta=eta,a0=point['a0'],
        bg=-val(f['B'][0])/(val(f['A'][0])*np.hypot(val(f['A'][0]),val(f['B'][0]))),
        volume=point['volume'],cauchy=point['Cauchy'],Ct_over_C=Ct/C)
    # Formal divergence is evaluated algebraically, with this same density.
    div_time=(Ct/C+3*rt/r)/nu
    div_shift=-(zr+z*(Cr/C+3*rr/r))/nu
    div_normal=(nr/nu+3*rr/r)/C
    proof=dict(geometric_formal_dual_time_divergence_residual=float(np.max(abs(div_time+div_shift-2*h0))),
        geometric_formal_dual_normal_divergence_residual=float(np.max(abs(div_normal-2*h4))),
        source_profile_reconstruction_residual=float(np.max(abs(p-Tb*hat/r))),
        radial_probe_end_traces=[float(contact['spinor_probe_hat_nodes'][0]),float(contact['spinor_probe_hat_nodes'][-1])],
        normalization_producer_rerun=False,clock_producer_rerun=False)
    return s,proof


def canonical_map(point, receipt, radius, cut, s, previous=None):
    """Use saved WW Cauchy norm; compute only a newly consumed time jet."""
    if previous is not None:
        return float(previous['canonical_field_C'][0]),float(previous['canonical_field_C_tau'][0])
    mu4=2*np.pi**2*radius**3
    diagonal=point['Ms'][0,0]
    if abs(diagonal.imag)>1e-13*abs(diagonal.real):raise ValueError('Cauchy diagonal not real within saved arithmetic scope')
    Z=1+float(diagonal.real)/mu4
    # I_tau/I is already supplied. No new integral selects or refines u.
    from flint import arb
    ratio=float((arb(receipt['I_tau']['arb'])/arb(receipt['I']['arb'])).mid())
    probability=cut['radial_weights']*point['volume']*point['u']**2/mu4
    # nu is the saved ratio, avoiding reinterpretation of Cauchy pairing.
    nu=point['volume']/point['Cauchy']
    # C_tau was already interpolated when constructing h0; obtain it from
    # the defining identity with existing r_tau, shift and geometric rates.
    # The caller supplies the direct scalar expression below.
    Ct_over_C=s['Ct_over_C']
    Zt=float(probability@((Ct_over_C-ratio-point['Lnu_direct'])/nu))
    c=Z**-.5;return c,-Zt*c/(2*Z)


def first_order_moments(point, s, xi, radial, cut, Cfield, Cfield_tau, source, r_transform):
    """Literal symmetrized action, with Gamma0 as the bar map once.

    Matrix S0 is 1/2(E† M B0+B0† M E); S1 is E†M(i/nu)E.
    It is not F0†MF0. All n1/n3 output channels enter the contraction.
    """
    d=len(source);rd=r_transform.shape[1];dim=d+rd;S0=np.zeros((dim,dim),complex);S1=S0.copy()
    G0=radial['common_parent_Gamma'][0];eta_unit=1j*G0@radial['common_parent_Gamma'][4]
    apply=lambda a,z:np.einsum('oi,gimkj->gomkj',a,z,optimize=True)
    data={};selected_checks={};normal_norm=normal_outside=0.
    gqq=np.zeros((d,d),complex);qrbody=np.zeros((d,rd),complex)
    forcing_norm=forcing_perp=0.
    all_forcing=[]
    weight=cut['radial_weights']*point['volume']
    for n in (1,3):
        a=xi[n];ra=np.einsum('omki,ij->omkj',a,r_transform,optimize=True)
        normal_unit=np.einsum('oi,imkj->omkj',eta_unit,ra)
        stored_normal=[];stored_forcing=[];wp_error=pp_error=0.
        for lo in range(0,len(weight),32):
            hi=min(lo+32,len(weight));sl=slice(lo,hi)
            sc={k:v[sl] for k,v in s.items()}
            E=np.concatenate([Cfield*sc['u'][:,None,None,None,None]*ra[None],
                sc['p'][:,None,None,None,None]*a[None]],axis=-1)
            DW,Dp,DtW,Dtp=field_actions(sc,a,n,radial)
            rcols=lambda z:np.einsum('gomki,ij->gomkj',z,r_transform,optimize=True)
            BR0=Cfield*rcols(apply(G0,DW))+Cfield_tau*rcols(apply(G0,DtW))
            BQ0=apply(G0,Dp)
            B0=np.concatenate([BR0,BQ0],axis=-1)
            B1=np.concatenate([Cfield*rcols(apply(G0,DtW)),apply(G0,Dtp)],axis=-1)
            count=hi-lo;Ef=E.reshape(count,-1,dim);Bf=B0.reshape(count,-1,dim)
            pair=lambda x,y:np.einsum('g,gai,gaj->ij',weight[sl],x.conj(),y,optimize=True)
            S0+=(pair(Ef,Bf)+pair(Bf,Ef))/2
            S1+=pair(Ef,B1.reshape(count,-1,dim))
            contract=lambda z:np.einsum('gomki,i->gomk',z,source,optimize=True)
            pp_error+=np.linalg.norm(contract(Dp)-point[f'Dp_n{n}'][sl])**2
            wp_error+=np.linalg.norm(contract(DW)-point[f'DWp_n{n}'][sl])**2
            normal=-Cfield*sc['u'][:,None,None,None,None]*sc['eta'][:,None,None,None,None]*normal_unit[None]
            forcing=BR0+normal;nf=normal
            normal_norm+=float(np.einsum('g,gomkj,gomkj->',weight[sl],nf.conj(),nf).real)
            normal_outside+=float(np.einsum('g,gomkj,gomkj->',weight[sl]*(sc['p']==0),nf.conj(),nf).real)
            q=sc['p'][:,None,None,None,None]*a[None]
            gqq+=pair(q.reshape(count,-1,d),q.reshape(count,-1,d))
            qrbody+=np.einsum('g,gomki,gomkj->ij',weight[sl],q.conj(),forcing,optimize=True)
            stored_normal.append(nf);stored_forcing.append(forcing)
        forcing=np.concatenate(stored_forcing);nf=np.concatenate(stored_normal)
        selected_checks[f'n{n}']=dict(raw_p_columns_vs_cache=float(np.sqrt(pp_error)),
            raw_W_columns_vs_cache=float(np.sqrt(wp_error)))
        all_forcing.append((a,forcing))
        data.update({f'normal_Euler_unit_LL_columns_n{n}':normal_unit,
            f'normal_Euler_LL_columns_n{n}':nf,f'full_Euler_LL_columns_n{n}':forcing})
    projection=np.linalg.solve(gqq,qrbody)
    for a,forcing in all_forcing:
        q_project=s['p'][:,None,None,None,None]*np.einsum('omki,ij->omkj',a,projection,optimize=True)[None]
        residual=forcing-q_project
        forcing_norm+=float(np.einsum('g,gomkj,gomkj->',weight,forcing.conj(),forcing).real)
        forcing_perp+=float(np.einsum('g,gomkj,gomkj->',weight,residual.conj(),residual).real)
    proof=dict(selected_cached_raw_actions=selected_checks,
        symmetric_density_Hermitian_residual=float(np.linalg.norm(S0-S0.conj().T)),
        first_order_time_density_skew_residual=float(np.linalg.norm(S1+S1.conj().T)),
        normal_Euler_LL_columns_L2_norm=float(np.sqrt(normal_norm)),
        normal_Euler_outside_compact_p_support_L2_norm=float(np.sqrt(normal_outside)),
        full_Euler_LL_columns_L2_norm=float(np.sqrt(forcing_norm)),
        full_Euler_off_p_frame_L2_norm=float(np.sqrt(forcing_perp)),
        diagnostic_L2_not_used_as_first_order_inverse=True)
    return S0,S1,data,proof


def bubble_element(left,right,jacobians,r_columns):
    """Exact Gauss moments of declared linear FIRST-ORDER densities.

    phi0=x(1-x), phi1=x(1-x)(2x-1). Compact extension by zero is H1;
    both artificial element faces have zero traces. They are trial tests,
    not selected physical endpoint conditions or a causal inverse.
    """
    d=left[0].shape[0];A=np.zeros((2*d,2*d),complex)
    x,w=np.polynomial.legendre.leggauss(5);x=(x+1)/2;w=w/2
    for t,wt in zip(x,w):
        phi=np.array([t*(1-t),t*(1-t)*(2*t-1)])
        dp=np.array([1-2*t,-6*t*t+6*t-1])
        h0=(1-t)*jacobians[0]*left[0]+t*jacobians[1]*right[0]
        h1=(1-t)*left[1]+t*right[1]
        for i in range(2):
            for j in range(2):
                A[i*d:(i+1)*d,j*d:(j+1)*d]+=wt*(phi[i]*phi[j]*h0+
                    (phi[i]*dp[j]-dp[i]*phi[j])*h1/2)
    # R,Q at each temporal bubble -> all R coordinates then all Q.
    ri=np.r_[np.arange(r_columns),d+np.arange(r_columns)]
    qi=np.r_[np.arange(r_columns,d),d+np.arange(r_columns,d)]
    return dict(A_full=A,A_RR_parent=A[np.ix_(ri,ri)],A_RQ=A[np.ix_(ri,qi)],
        A_QR=A[np.ix_(qi,ri)],A_QQ=A[np.ix_(qi,qi)])


def restricted_solve(blocks,source):
    """One solve with all required R columns, never an explicit inverse."""
    A=blocks['A_QQ'];B=blocks['A_QR'];C=blocks['A_RQ']
    X=np.linalg.solve(A,B)
    correction=-C@X
    rhs=B@source;solution=-X@source
    residual=A@solution+rhs
    scale=np.linalg.norm(A)*np.linalg.norm(solution)+np.linalg.norm(rhs)
    result=dict(A_QQ_condition=float(np.linalg.cond(A)),
        actual_equation_residual=float(np.linalg.norm(residual)),
        actual_equation_backward_residual=float(np.linalg.norm(residual)/scale) if scale else 0.,
        matrix_equation_residual=float(np.linalg.norm(A@X-B)),
        restricted_correction_contraction=complex(np.vdot(source,correction@source)),
        restricted_correction_matrix_norm=float(np.linalg.norm(correction)),
        full_retarded_complementary_action=False,regularizer_added=False,
        positive_squared_inverse_used=False)
    return dict(complement_solution_map=-X,complement_rhs=rhs,complement_solution=solution,
        complement_equation_residual=residual,restricted_correction=correction,
        A_eff_parent_restricted=blocks['A_RR_parent']+correction),result
