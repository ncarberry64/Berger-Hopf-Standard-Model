"""Current radial candidate inclusion, local Dirac action and weak interface.

This worked muon realization uses the retained full-cap radial prescription.
It does not identify this image with the excluded Gaussian normal image or
claim the global reset domain, native heat action or a physical muon state.
"""
from __future__ import annotations
import numpy as np
from flint import arb,acb,ctx
from bhsm.interface.muon_cut_inverse_coverage import encoded


def affine_sin_squared_integral(grid,values):
    """Arb enclosure of the full-cap affine C*sin(rho/2)^2 integral."""
    ctx.prec=192;total=arb(0)
    for k in range(len(grid)-1):
        l,h=map(lambda x:arb(float(x)),grid[k:k+2]);v,w=values[k:k+2]
        v,w=arb(v),arb(w);slope=(w-v)/(h-l);intercept=v-slope*l
        def F(x):return (intercept*x+slope*x*x/2-intercept*x.sin()-slope*(x*x.sin()+x.cos()))/2
        total+=F(h)-F(l)
    return total


def full_normalization(geometry):
    grid=geometry['rho'];C=geometry['C_rho']
    I=affine_sin_squared_integral(grid,C[0])
    dt=arb(float(geometry['proper_times'][1]))-arb(float(geometry['proper_times'][0]))
    # Difference exact input nodes before division; no rounded H substitute.
    Ct=[(arb(float(b))-arb(float(a)))/dt for a,b in zip(C[0],C[1])]
    Idot=affine_sin_squared_integral(grid,Ct)
    if not I>0:raise ArithmeticError('full-cap normalization not positive')
    return I,Idot,dict(I_rad=encoded(I),I_rad_dot=encoded(Idot),I_dot_over_I=encoded(Idot/I),
        normalization_domain=[float(grid[0]),float(grid[-1])],all_radial_cells=len(grid)-1,
        profile='outgoing daughter sin(rho/2)',
        metric_time_derivative='right first proper-time cell, at fixed rho; exact binary64 nodal affine model',
        source_support_used_as_norm=False,normalization_remainder_in_nodal_full_cap=0,
        continuum_or_history_normalization_error=None)


def nodal_jets(geometry,points,cells):
    grid=geometry['rho'];points=np.array(points);cells=np.array(cells,int)
    width=np.diff(grid)[cells];x=(points-grid[cells])/width
    dt=float(geometry['proper_times'][1]-geometry['proper_times'][0]);out={}
    for k in ('proper_lapse','C_rho','base_radius','proper_shift_rho','A','B'):
        z=geometry[k];out[k]=z[0,cells]*(1-x)+z[0,cells+1]*x
        out[k+'_r']=(z[0,cells+1]-z[0,cells])/width
        out[k+'_t']=((z[1,cells]-z[0,cells])*(1-x)+(z[1,cells+1]-z[0,cells+1])*x)/dt
    return out


def scalar_action(geometry,points,cells,I,Idot,cut_rate):
    """Displayed scalar W in the common parent frame, no added Spin boost."""
    j=nodal_jets(geometry,points,cells);nu,C,r,z=(j[k] for k in ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    nr,Cr,rr,zr=(j[k+'_r'] for k in ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    nt,Ct,rt=(j[k+'_t'] for k in ('proper_lapse','C_rho','base_radius'))
    nb=float(geometry['proper_lapse'][0,-1]);Rb=float(geometry['base_radius'][0,-1]);H=float(cut_rate['value'])
    invI=float(I.mid());ratio=float((Idot/I).mid());rho=np.array(points)
    Jr=(r/Rb)**3;Jv=nu/nb*Jr;u=np.sin(rho/2)/np.sqrt(invI*Jv)
    lr=-nr/(2*nu)-3*rr/(2*r)+.5/np.tan(rho/2)
    lt=-ratio/2-nt/(2*nu)-3*rt/(2*r)+3*H/2  # nb_dot=0 in the declared proper boundary clock
    h0=(Ct/C+3*rt/r-z*(Cr/C+3*rr/r)-zr)/(2*nu)
    h4=(nr/nu+3*rr/r)/(2*C)
    mrad=-.5/(C*np.tan(rho/2))
    a0=(lt-z*lr)/nu+h0
    # Stable equivalent expression: r_t/r and z*r_r/r cancel exactly.
    stable=(-ratio/2-nt/(2*nu)+3*H/2+Ct/(2*C)-z*Cr/(2*C)-zr/2+z*nr/(2*nu)-.5*z/np.tan(rho/2))/nu
    return dict(**j,u_vol=u,J_rad=Jr,J_vol=Jv,log_u_tau=lt,log_u_rho=lr,
        h0=h0,h4=h4,m_eta_radial=mrad,zero_time_coefficient=a0,
        zero_time_stable=stable,zero_normal_geometric=lr/C+h4,
        zero_normal_with_owned_radial_eta=lr/C+h4+mrad,
        radial_probability=C*np.sin(rho/2)**2/invI,wall_H_owned=H)


def carrier_matrices(source,corrected):
    G=corrected['parent_gamma'];G64=np.array([np.kron(g,np.eye(16)) for g in G])
    spin=-1.5j*np.kron(G[1]@G[2]@G[3],np.eye(16))
    jmath=2*np.sqrt(2)*source['unit_trace_carrier_basis'][:3]
    gauge=sum(np.kron(1j*G[a+1],jmath[a]) for a in range(3))
    return G64,spin,gauge


def angular_generators(n):
    j=n/2;weights=np.arange(n,-n-1,-2)/2;p=np.zeros((n+1,n+1),complex)
    for k in range(1,n+1):p[k-1,k]=np.sqrt((j-weights[k])*(j+weights[k]+1))
    return np.array([(p+p.T)/2,(p-p.T)/(2j),np.diag(weights)])


def certified_source_scalar(geometry,contact,I,*,cauchy_trace=False):
    """Validated integration of the SAME nodal saved-source scalar density."""
    ctx.prec=160;grid=geometry['rho'];Tb=arb(float(contact['T_b']));Rb=arb(float(geometry['base_radius'][0,-1]));nb=arb(float(geometry['proper_lapse'][0,-1]))
    total=acb(0);records=[]
    for k in range(24,40):
        l,h=map(lambda v:acb(float(v)),grid[k:k+2]);d=h-l
        def val(key,z):
            a=arb(float(geometry[key][0,k]));b=arb(float(geometry[key][0,k+1]))
            return a+(b-a)*(z-l)/d
        hl,hr=map(lambda v:arb(float(v)),contact['spinor_probe_hat_nodes'][k:k+2])
        def integrand(z,analytic):
            nu=val('proper_lapse',z);C=val('C_rho',z);r=val('base_radius',z);hat=hl+(hr-hl)*(z-l)/d
            nufactor=1/nu.sqrt(analytic=analytic) if cauchy_trace else nu.sqrt(analytic=analytic)
            return 2*arb.pi()**2*Tb*Rb**arb('1.5')*(nb/I).sqrt()*C*nufactor*r.sqrt(analytic=analytic)*hat*(z/2).sin()
        ball=acb.integral(integrand,l,h,rel_tol=arb('1e-24'),abs_tol=arb('1e-26'),eval_limit=20000)
        if not ball.is_finite():raise ArithmeticError(f'source integral unresolved in cell {k}')
        total+=ball;records.append(dict(cell=k,scalar=encoded(ball.real)))
    if not total.imag.contains(0):raise ArithmeticError('real source integral did not enclose zero imaginary part')
    return total.real,dict(scalar=encoded(total.real),cells=records,
        equation=('2*pi^2 T_b R_b^(3/2) sqrt(nu_b/I) integral C sqrt(r/nu) hat sin(rho/2) d rho' if cauchy_trace else
            '2*pi^2 T_b R_b^(3/2) sqrt(nu_b/I) integral_full_source_support C sqrt(nu*r) hat sin(rho/2) d rho'),
        cauchy_trace_pairing=cauchy_trace,
        scope='validated scalar integral of exact binary64 nodal fields/hat and full-cap norm; complex coefficient arithmetic error separate')


def projected_means(geometry,I,Idot,cut_rate):
    """Small scalar contractions of full radial actions, not a heat block."""
    ctx.prec=128;grid=geometry['rho'];dt=arb(float(geometry['proper_times'][1]))-arb(float(geometry['proper_times'][0]));H=arb(float(cut_rate['value']));means=[]
    for target in ('time','angular','zero_time','gauge'):
        total=acb(0)
        for k in range(len(grid)-1):
            l,h=map(lambda z:acb(float(z)),grid[k:k+2]);d=h-l
            def v(key,z):
                a,b=map(lambda w:arb(float(w)),geometry[key][0,k:k+2]);return a+(b-a)*(z-l)/d
            def dr(key):return (arb(float(geometry[key][0,k+1]))-arb(float(geometry[key][0,k])))/d
            def vt(key,z):
                q=geometry[key];a=(arb(float(q[1,k]))-arb(float(q[0,k])))/dt;b=(arb(float(q[1,k+1]))-arb(float(q[0,k+1])))/dt
                return a+(b-a)*(z-l)/d
            def integrand(z,analytic):
                nu,C,r,shift=[v(key,z) for key in ('proper_lapse','C_rho','base_radius','proper_shift_rho')]
                sine=(z/2).sin();prob=C*sine*sine/I
                if target=='time':return prob/nu
                if target=='angular':
                    return C*z*(z/2).sinc()**2/(4*dr('base_radius')*I) if k==0 else prob/r
                if target=='zero_time':
                    zcot=2*dr('proper_shift_rho')*(z/2).cos()/(z/2).sinc() if k==0 else shift*(z/2).cot()
                    a=(-Idot/(2*I)-vt('proper_lapse',z)/(2*nu)+3*H/2+vt('C_rho',z)/(2*C)
                       -shift*dr('C_rho')/(2*C)-dr('proper_shift_rho')/2+shift*dr('proper_lapse')/(2*nu)-zcot/2)/nu
                    return prob*a
                A,B=v('A',z),v('B',z)
                return -prob*B/(A*(A*A+B*B).sqrt(analytic=analytic))
            ball=acb.integral(integrand,l,h,rel_tol=arb('1e-21'),abs_tol=arb('1e-23'),eval_limit=10000)
            if not ball.is_finite():raise ArithmeticError(f'{target} moment unresolved at cell {k}')
            total+=ball
        means.append(total.real)
    return dict(zip(('time','angular','zero_time','gauge'),means))


def source_actions_and_interface(geometry,source,contact,corrected,pairing,cut_rate,I,Idot,means,Tscalar,trace_scalar):
    """Actual retained source directions; full n1/n3 and all64 carrier rows."""
    points=pairing['gauss_rho'];cells=pairing['gauss_cells'];s=scalar_action(geometry,points,cells,I,Idot,cut_rate)
    G,spin,gauge=carrier_matrices(source,corrected);u=s['u_vol'];r=s['base_radius'];nu=s['proper_lapse']
    A,B=s['A'],s['B'];bg=-B/(A*np.sqrt(A*A+B*B))
    zero=s['zero_time_coefficient'][:,None,None]*(1j*G[0])+spin[None]/r[:,None,None]+bg[:,None,None]*gauge[None]
    normal_geo=s['zero_normal_geometric'][:,None,None]*(1j*G[4])
    eta=s['m_eta_radial'][:,None,None]*(1j*G[4])
    nb=float(geometry['proper_lapse'][0,-1]);Rb=float(geometry['base_radius'][0,-1]);H=float(cut_rate['value'])
    wall_bg=-float(geometry['B'][0,-1])/(float(geometry['A'][0,-1])*float(np.hypot(geometry['A'][0,-1],geometry['B'][0,-1])))
    mu4=float(pairing['M4_wall_geometric_density'][0,0])
    mean={k:float(v.mid()) for k,v in means.items()}
    wall0=1.5*H*1j*G[0]+spin/Rb+wall_bg*gauge
    projected0=mean['zero_time']*1j*G[0]+mean['angular']*spin+mean['gauge']*gauge
    gx,gw=np.polynomial.legendre.leggauss(4);weights=np.tile(gw/2,16)*np.diff(geometry['rho'])[cells]
    vol=pairing['mu5_volume_density_per_tau_normalized_Haar'];w=weights*vol
    tau_matrix=u[:,None,None]/nu[:,None,None]*(1j*G[0])
    dwH=1.5*tau_matrix
    arrays=dict(gauss_rho=points,gauss_cells=cells,radial_u_vol=u,
        radial_log_u_tau=s['log_u_tau'],radial_log_u_rho=s['log_u_rho'],
        D5W_tau_coefficient=tau_matrix,D5W_angular_coefficient=u[:,None,None,None]/r[:,None,None,None]*(1j*G[1:4])[None],
        D5W_zero_geometric_commonA=u[:,None,None]*(zero+normal_geo),
        D5W_owned_radial_eta=u[:,None,None]*eta,D5W_zero_with_radial_eta=u[:,None,None]*zero,
        DeltaD4_tau=(mean['time']-1/nb)*1j*G[0],
        DeltaD4_angular=(mean['angular']-1/Rb)*1j*G[1:4],DeltaD4_zero=projected0-wall0,
        Rperp_scalar_coefficients=np.array([1/nu-mean['time'],1/r-mean['angular'],s['zero_time_coefficient']-mean['zero_time'],bg-mean['gauge']]).T,
        common_parent_Gamma=G,angular_spin=spin,commonA_gauge_unit=gauge,
        wall_M4=pairing['M4_wall_geometric_density'],wall_M4_tau=pairing['M4_wall_geometric_density_tau'],
        cut_Cauchy_trace_Gram=mu4*mean['time']*np.eye(64),
        source_node_volume_weights=w,normal_cancellation_residual=s['zero_normal_with_owned_radial_eta'],
        time_expression_equivalence_residual=s['zero_time_coefficient']-s['zero_time_stable'])
    norms={}
    for n in (1,3):
        xi=contact[f'Xi_A_unit_n{n}'][:,:,corrected['source_image_probe_columns']];J=angular_generators(n)
        angular=sum(np.einsum('oi,Aicmk,vm->Aocvk',1j*G[a+1],xi,2j*J[a],optimize=True) for a in range(3))
        DW=(np.einsum('goi,Aicmk->gAocmk',u[:,None,None]*zero,xi,optimize=True)
            +angular[None]*(u/r)[:,None,None,None,None,None])
        Dt=np.einsum('goi,Aicmk->gAocmk',tau_matrix,xi,optimize=True)
        p=pairing[f'actual_source_trial_n{n}'];Dp=corrected[f'D5_on_same_source_image_b_coefficient_n{n}']
        Dp_eta=Dp+np.einsum('goi,gAicmk->gAocmk',eta,p,optimize=True)
        DpH=-.5*corrected[f'D5_on_same_source_image_b_tau_coefficient_n{n}']
        T4=np.einsum('g,g,gAocmk->Aocmk',weights,u,pairing[f'known_T_integrand_factor_mu5_p_n{n}'],optimize=True)
        T=float(Tscalar.mid())*xi
        Ttrace=float(trace_scalar.mid())*xi
        Btrace=Ttrace/(mu4*mean['time'])
        trace_perp=p-u[:,None,None,None,None,None]*Btrace[None]
        # For wall angular mode m, the adjoint derivative contributes
        # conjugate(E)_{v,m}; k spectator, no compression of either index.
        def cross(zero_left,angular_left,right,angular_scale=None):
            out=np.einsum('g,goi,gAocmk->Aicmk',w,zero_left.conj(),right,optimize=True)
            if angular_left:
                scale=u/r if angular_scale is None else angular_scale
                for a in range(3):
                    out+=np.einsum('g,oi,vm,gAocvk->Aicmk',w*scale,(1j*G[a+1]).conj(),(2j*J[a]).conj(),right,optimize=True)
            return out
        q0=cross(u[:,None,None]*zero,True,Dp_eta)
        qt=cross(tau_matrix,False,Dp_eta)
        qH=cross(dwH,False,Dp_eta)+cross(u[:,None,None]*zero,True,DpH)
        qHH=2*cross(dwH,False,DpH)
        projected_cross=cross(u[:,None,None]*projected0[None],True,Dp_eta,angular_scale=u*mean['angular'])
        perp_cross=q0-projected_cross
        projected_tau=cross(u[:,None,None]*mean['time']*(1j*G[0]),False,Dp_eta)
        arrays.update({f'D5W_actual_source_zero_n{n}':DW,f'D5W_actual_source_tau_n{n}':Dt,
            f'candidate_T_saved4_n{n}':T4,f'candidate_T_certified_scalar_n{n}':T,
            f'candidate_B_required_n{n}':T/mu4,
            f'candidate_cut_trace_T_n{n}':Ttrace,f'candidate_cut_trace_B_n{n}':Btrace,
            f'candidate_cut_trace_connected_remainder_n{n}':trace_perp,
            f'local_interface_K54_zero_n{n}':q0,f'local_interface_K54_tau_n{n}':qt,
            f'local_interface_K54_projected_zero_n{n}':projected_cross,
            f'local_interface_K54_connected_perp_zero_n{n}':perp_cross,
            f'local_interface_K54_connected_perp_tau_n{n}':qt-projected_tau,
            f'local_interface_K54_zero_H_derivative_n{n}':qH,f'local_interface_K54_zero_H_second_derivative_n{n}':qHH,
            f'local_interface_K54_tau_H_derivative_n{n}':cross(tau_matrix,False,DpH),
            f'angular_E_n{n}':2j*J})
        nonzero=np.flatnonzero(abs(xi.ravel())>0)[0]
        T4scalar=float((T4.ravel()[nonzero]/xi.ravel()[nonzero]).real)
        norms[f'n{n}']=dict(T_norm=float(np.linalg.norm(T)),B_norm=float(np.linalg.norm(T/mu4)),
            saved4_T_scalar_error_norm=float(np.linalg.norm(T4-T)),weak_K54_zero_norm=float(np.linalg.norm(q0)),weak_K54_tau_norm=float(np.linalg.norm(qt)),
            weak_K54_connected_perp_zero_norm=float(np.linalg.norm(perp_cross)),
            weak_K54_connected_perp_tau_norm=float(np.linalg.norm(qt-projected_tau)),
            candidate_cut_trace_projection_norm=float(np.linalg.norm(Btrace)),
            candidate_cut_trace_connected_remainder_norm=float(np.linalg.norm(trace_perp)),
            actual_D5W_zero_norm=float(np.linalg.norm(DW)),actual_D5W_tau_norm=float(np.linalg.norm(Dt)),
            interface_pairing_residual=float(np.linalg.norm(mu4*(T/mu4)-T)),
            scalar_T_radial_error_only=encoded(Tscalar-T4scalar))
    return arrays,dict(norms=norms,projected_means={k:encoded(v) for k,v in means.items()},
        DeltaD4_reference='current canonical wall geometric/common-A symbol at the supplied cut; no new action absorbed',
        complement='Rperp retained as four radial scalar functions times the full Clifford/angular/carrier factors; no invariance or resolvent-tail theorem',
        weak_interface='q_local(W wall coefficient,p_source)=<D5_local_eta W,D5_local_eta p>5; separate wall-time derivative coefficient',
        physical_interface_promoted=False,global_reset_domain_verified=False,
        remaining_owner_terms=['stratified/Higgs/seam realization where required','full inherited reset/range matching','domain/source/pairing derivatives under physical photon variation','native finite-E1 and completion'],
        errors='scalar norm/source/projection integrals certified in nodal model; matrix contractions and four-point weak-form quadrature unvalidated; inherited H dependence saved as shared signed jets; continuum/history error separate')
