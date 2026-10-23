"""Endpoint/tube proper-clock contractions of the retained C2 action field.

Delta cancels before intervals. This muon realization consumes the existing
selected-line/response data; it does not call an action Hessian or select a
physical history. Certificates are conditional on their retained chart bounds.
"""
from __future__ import annotations
import numpy as np
from flint import arb,ctx
from bhsm.interface.muon_cut_inverse_coverage import encoded
from bhsm.interface.muon_radial_inclusion_action import affine_sin_squared_integral,nodal_jets


def norm_ball(values):
    return sum((arb(float(x))**2 for x in np.asarray(values).ravel()),arb(0)).sqrt()


def around(center,radius):
    return arb(float(center),radius.upper())


def bounds(values):return np.array([encoded(x)['interval'] for x in values])
def mids(values):return np.array([float(x.mid()) for x in values])


def endpoint_rates(step,record,branch,growth,response_bounds,*,tube):
    """Enclose endpoint value, optionally including its inherited state tube.

    Nominals use only cached first actions on the predictor displacement.
    Enclosures also contain the centered Lipschitz/Taylor ranges independently
    of that nominal shift. No tiny descriptor is obtained from a raw eigenvalue.
    """
    ctx.prec=192
    y=step['endpoint_predictor_center'];yc=step['center_state'];weights=step['state_weights']
    if not np.array_equal(yc,branch['center_state']) or not np.array_equal(weights,branch['state_weights']):
        raise ValueError('endpoint and response center/weights do not match')
    displacement=(y-yc)*weights;distance=norm_ball(displacement)
    rt=arb(float(record['segment']['endpoint_tube_radius_upper'])) if tube else arb(0)
    radius=distance+rt
    if tube:radius=arb(float(record['segment']['joint_domain_use_upper']))
    domain=arb(float(record['domain']['selected_domain_radius']))
    if not radius<domain:raise ValueError('endpoint set outside retained selected domain')
    sigma=arb(record['segment']['signed_descriptor_end'])
    if not sigma>0:raise ValueError('nonzero selected signed descriptor required')
    if record['segment']['endpoint_selected_branch']!=24:raise ValueError('selected branch changed')
    psi=branch['selected_vector'];response=branch['bordered_response'];first=branch['bordered_response_derivative_action']
    psi_mid=psi+branch['selected_vector_derivative_action']@displacement
    response_mid=response+first@displacement
    line=growth['fresh_line_bounds'];pf=growth['fresh_pole_free_bounds']
    p1=arb(float(line['weighted_selected_to_complement_first_variation_on_ball']))
    p2=arb(float(line['selected_line_second_variation_coefficient_upper']))
    rhs=branch['bordered_matrix']@response
    b1=arb(float(response_bounds['ball']['b_psi_first_variation_center_upper']))
    b2=p2*norm_ball(rhs[:-1])+2*p1*arb(float(pf['rhs_raw_derivative_center']))+arb(float(pf['rhs_raw_second_derivative_upper']))
    bchange=b1*radius+b2*radius**2/2
    b=around(response_mid[-1],bchange+abs(arb(float(response_mid[-1]))-arb(float(response[-1]))))
    if tube:
        lo,hi=map(lambda x:arb(float(x)),record['domain']['b_psi_interval'])
        b=arb((lo+hi).mid()/2,((hi-lo)/2).upper())
    # The separate b interval uses the same enlarged STEP domain. The centered
    # interval is already sufficient; save their consistency without choosing
    # independent branches or discarding the signed b*psi cross.
    x1=arb(float(record['second_variation']['response_first_variation_upper']))
    psi_balls=[around(z,p1*radius+abs(arb(float(z))-arb(float(a)))) for z,a in zip(psi_mid,psi)]
    hard_balls=[around(z,x1*radius+abs(arb(float(z))-arb(float(a)))) for z,a in zip(response_mid[:-1],response[:-1])]
    signs=(-1)**np.arange(1,13)
    state=[around(z,rt/arb(float(w))) for z,w in zip(y,weights)]
    logNb=sum((state[74+k]*int(signs[k]) for k in range(12)),arb(0));Nb=logNb.exp()
    if tube:
        lo,hi=map(lambda x:arb(float(x)),record['domain']['lapse_interval'])
        Nb=arb((lo+hi).mid()/2,((hi-lo)/2).upper())
    # For these rows Psi_w=reduced_weight*psi and V_w=reduced_weight*hard.
    # The saved state and output weights are identical. Preserve the exact
    # common b, sigma and Nb, and cancel weights before interval multiplication.
    from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
    qw,rw,_,_=metric_data()
    if not np.array_equal(weights[37:],rw) or not np.array_equal(weights[:37],qw):raise ValueError('raw/output weight cancellation invalid')
    m=[(b*psi_balls[k]+sigma*hard_balls[k])/(Nb*sigma) for k in range(37,61)]
    q=[state[37+k]/Nb for k in range(37)]
    result=dict(scope='endpoint plus inherited tube' if tube else 'endpoint predictor value enclosure',
        coordinate='boundary proper tau; sigma is the signed descriptor',
        equation='Y_tau=W^-1(b Psi_w+sigma V_w)/(N_b sigma); Delta canceled before intervals',
        sigma=encoded(sigma),Nb=encoded(Nb),center_distance=encoded(distance),tube_radius=encoded(rt),
        total_radius=encoded(radius),selected_domain_radius=encoded(domain),branch=24,
        raw_line_variation_upper=encoded(p1*radius),raw_response_variation_upper=encoded(x1*radius),
        b_centered_change_upper=encoded(bchange),b_centered_remainder_coefficient=encoded(b2),
        b=encoded(b),b_domain_interval=record['domain']['b_psi_interval'],
        m_tau=[encoded(x) for x in m[:12]],shift_tau=[encoded(x) for x in m[12:]],
        proof_center_substituted=False,new_action_jets=0,new_eigensolves=0,new_derivative_campaigns=0,
        nominal='cached first actions at endpoint displacement; independently enclosed by centered variation bounds',
        error_scope='outward Arb arithmetic and inherited selected-domain/response bounds; original saved branch/derivative numerical realization and continuum errors not upgraded')
    return dict(q=q,m=m,state=state,Nb=Nb,result=result)


def Fourier_log_lapse(rho,m,*,proper_boundary=False):
    if proper_boundary:return arb(0)
    z=arb(float(rho))
    return sum((m[k]*((2*(k+1)*z).cos()-int((-1)**(k+1))) for k in range(12)),arb(0))


def geometric_time_jets(geometry,rate):
    """Differentiate the current attachment, using the same endpoint clock.

    Instantaneous arrays are the fixed retained nodal fields. These temporal
    jets replace their right-cell derivatives, not the instantaneous pairing.
    """
    rho=geometry['rho'];q=rate['q'];state=rate['state'];order=12
    Cdot=[];rdot=[];Lnu=[];zeta_dot=[];logNb_dot=sum((rate['m'][k]*int((-1)**(k+1)) for k in range(order)),arb(0))
    vb=sum((state[25+k]*int((-1)**k) for k in range(order)),arb(0))
    ub_dot=sum((q[1+k]*int((-1)**(k+1)) for k in range(order)),arb(0))
    vb_dot=sum((q[25+k]*int((-1)**k) for k in range(order)),arb(0))
    H=q[0]+ub_dot-(2*vb).tanh()*vb_dot
    for i,x in enumerate(rho):
        z=arb(float(x));boundary=i==len(rho)-1
        ck=[arb(int((-1)**(k+1))) if boundary else (2*(k+1)*z).cos() for k in range(order)]
        cj=[arb(int((-1)**k)) if boundary else (2*k*z).cos() for k in range(order)]
        window=arb(1) if boundary else z.sin()**2
        ud=sum((q[1+k]*ck[k] for k in range(order)),arb(0))
        wd=window*sum((q[13+k]*cj[k] for k in range(order)),arb(0))
        vd=window*sum((q[25+k]*cj[k] for k in range(order)),arb(0))
        C=arb(float(geometry['C_rho'][0,i]));r=arb(float(geometry['base_radius'][0,i]))
        A=arb(float(geometry['A'][0,i]));B=arb(float(geometry['B'][0,i]))
        Cdot.append(C*(q[0]+ud+wd))
        rdot.append(r*(q[0]+ud-(A*A-B*B)/(A*A+B*B)*vd))
        Lnu.append(Fourier_log_lapse(x,rate['m'],proper_boundary=boundary))
        shift=arb(float(geometry['proper_shift_rho'][0,i]))
        raw=2*(2*z).sin()*sum((rate['m'][12+k]*cj[k] for k in range(order)),arb(0))/rate['Nb']
        zeta_dot.append(raw-shift*logNb_dot)
    Idot=affine_sin_squared_integral(rho,Cdot)
    return dict(Cdot=Cdot,rdot=rdot,Lnu=Lnu,zeta_dot=zeta_dot,H=H,Idot=Idot,logNb_dot=logNb_dot)


def apply_endpoint(geometry,contact,corrected,pairing,old,norm,point,tube):
    """Only dependent source actions and local weak interface updates."""
    ctx.prec=192;I=arb(norm['I_rad']['arb']);oldIdot=arb(norm['I_rad_dot']['arb'])
    rho=pairing['gauss_rho'];cells=pairing['gauss_cells'];grid=geometry['rho']
    x=(rho-grid[cells])/np.diff(grid)[cells];j=nodal_jets(geometry,rho,cells)
    interp=lambda a:[a[k]*(1-arb(float(t)))+a[k+1]*arb(float(t)) for k,t in zip(cells,x)]
    jets=geometric_time_jets(geometry,point);tjets=geometric_time_jets(geometry,tube)
    direct=[Fourier_log_lapse(z,point['m']) for z in rho]
    direct_tube=[Fourier_log_lapse(z,tube['m']) for z in rho]
    nu_nodes=geometry['proper_lapse'][0]
    nodal=[z/arb(float(nu)) for z,nu in zip(interp([arb(float(v))*a for v,a in zip(nu_nodes,jets['Lnu'])]),j['proper_lapse'])]
    oldL=j['proper_lapse_t']/j['proper_lapse']
    u=old['radial_u_vol'];nu=j['proper_lapse'];C=j['C_rho'];r=j['base_radius']
    G=old['common_parent_Gamma'];g0=1j*G[0]
    dc=[-(a-arb(float(b)))/(2*arb(float(v))) for a,b,v in zip(direct,oldL,nu)]
    dct=[-(a-arb(float(b)))/(2*arb(float(v))) for a,b,v in zip(direct_tube,oldL,nu)]
    Ct=interp(jets['Cdot']);rt=interp(jets['rdot'])
    H_old=float(old['wall_M4_tau'][0,0]/(3*old['wall_M4'][0,0]));dH=jets['H']-arb(H_old)
    all_delta=[( -(jets['Idot']-oldIdot)/(2*I)-(l-arb(float(ol)))/2+3*dH/2
        +(ct-arb(float(oct)))/(2*arb(float(cc))))/arb(float(v))
        for l,ol,ct,oct,cc,v in zip(direct,oldL,Ct,j['C_rho_t'],C,nu)]
    dp_delta=[((ct-arb(float(oct)))/(2*arb(float(cc)))+(rr-arb(float(ort)))/(2*arb(float(rv)))-dH/2)/arb(float(v))
        for ct,oct,cc,rr,ort,rv,v in zip(Ct,j['C_rho_t'],C,rt,j['base_radius_t'],r,nu)]
    coeff=mids(dc)*u;all_coeff=mids(all_delta)*u
    arrays=dict(endpoint_lapse_rate_point=bounds(point['m'][:12]),endpoint_lapse_rate_tube=bounds(tube['m'][:12]),
        endpoint_source_Lnu_direct=bounds(direct),endpoint_source_Lnu_tube=bounds(direct_tube),
        endpoint_source_Lnu_nodal=bounds(nodal),endpoint_source_Lnu_old=oldL,
        endpoint_lapse_only_D5W_scalar=bounds([a*arb(float(v)) for a,v in zip(dc,u)]),
        endpoint_lapse_only_D5W_scalar_tube=bounds([a*arb(float(v)) for a,v in zip(dct,u)]),
        endpoint_all_time_D5W_scalar=bounds([a*arb(float(v)) for a,v in zip(all_delta,u)]),
        endpoint_D5p_time_delta_scalar=bounds(dp_delta),
        action_C_tau_nodes=bounds(jets['Cdot']),action_r_tau_nodes=bounds(jets['rdot']),
        action_shift_tau_nodes=bounds(jets['zeta_dot']),action_q_tau=bounds(point['q']))
    lapse_delta=coeff[:,None,None]*g0
    all_DW=all_coeff[:,None,None]*g0
    arrays['endpoint_lapse_only_D5W_delta']=lapse_delta
    arrays['endpoint_all_time_D5W_delta']=all_DW
    arrays['updated_D5W_zero']=old['D5W_zero_with_radial_eta']+all_DW
    volume=old['source_node_volume_weights'];summaries={}
    eta=(-.5/(C*np.tan(rho/2)))[:,None,None]*(1j*G[4])
    for n in (1,3):
        xi=contact[f'Xi_A_unit_n{n}'][:,:,corrected['source_image_probe_columns']]
        p=pairing[f'actual_source_trial_n{n}'];E=old[f'angular_E_n{n}']
        dp=corrected[f'D5_on_same_source_image_b_coefficient_n{n}']+np.einsum('goi,gAicmk->gAocmk',eta,p,optimize=True)
        ddp=np.einsum('oi,gAicmk,g->gAocmk',g0,p,mids(dp_delta),optimize=True)
        dws=np.einsum('goi,Aicmk->gAocmk',all_DW,xi,optimize=True)
        dl=np.einsum('goi,Aicmk->gAocmk',lapse_delta,xi,optimize=True)
        def cross(left,right):return np.einsum('g,goi,gAocmk->Aicmk',volume,left.conj(),right,optimize=True)
        # The old angular wall derivative acts on the right output index v.
        angular_cross=np.zeros_like(old[f'local_interface_K54_zero_n{n}'])
        for a in range(3):
            angular_cross+=np.einsum('g,oi,vm,gAocvk->Aicmk',volume*u/r,(1j*G[a+1]).conj(),E[a].conj(),ddp,optimize=True)
        lapse_q=cross(lapse_delta,dp)
        delta_q=cross(all_DW,dp)+cross(old['D5W_zero_with_radial_eta'],ddp)+angular_cross+cross(all_DW,ddp)
        delta_tau=cross(old['D5W_tau_coefficient'],ddp)
        arrays.update({f'lapse_only_action_n{n}':dl,f'all_time_action_delta_n{n}':dws,
            f'updated_D5W_source_action_n{n}':old[f'D5W_actual_source_zero_n{n}']+dws,
            f'updated_D5p_source_action_n{n}':dp+ddp,
            f'lapse_only_interface_K54_delta_n{n}':lapse_q,f'all_time_interface_K54_delta_n{n}':delta_q,
            f'updated_local_K54_zero_n{n}':old[f'local_interface_K54_zero_n{n}']+delta_q,
            f'updated_local_K54_tau_n{n}':old[f'local_interface_K54_tau_n{n}']+delta_tau})
        # A conservative scalar enclosure propagates to a reached output using
        # ||e_iGamma0 Xi||_F <= ||Gamma0||_F ||Xi||_F. Matrix arithmetic remains
        # separately unvalidated. Do not call this a global operator norm.
        def reached_error_bound(coefficients):
            return (sum((a*a for a in coefficients),arb(0)).sqrt()*norm_ball(G[0].real)*
                    (norm_ball(xi.real)**2+norm_ball(xi.imag)**2).sqrt())
        errors=[(a-arb(float(float(a.mid())))).abs_upper()*arb(float(v)) for a,v in zip(dc,u)]
        tube_errors=[(a-arb(float(float(p.mid())))).abs_upper()*arb(float(v)) for a,p,v in zip(dct,dc,u)]
        interp_errors=[(a-b).abs_upper()*arb(float(v))/(2*arb(float(nn))) for a,b,v,nn in zip(direct,nodal,u,nu)]
        bound=reached_error_bound(errors)
        summaries[f'n{n}']=dict(lapse_action_norm=float(np.linalg.norm(dl)),lapse_K54_delta_norm=float(np.linalg.norm(lapse_q)),
            all_time_K54_delta_norm=float(np.linalg.norm(delta_q)),updated_K54_norm=float(np.linalg.norm(arrays[f'updated_local_K54_zero_n{n}'])),
            coefficient_only_lapse_action_error_bound=encoded(bound),
            endpoint_tube_lapse_action_error_bound=encoded(reached_error_bound(tube_errors)),
            direct_vs_nodal_action_difference_bound=encoded(reached_error_bound(interp_errors)),
            matrix_roundoff=None,weak_quadrature_error=None)
    interpolation=[a-b for a,b in zip(direct,nodal)]
    result=dict(endpoint_point=point['result'],endpoint_tube=tube['result'],
        source_Lnu_range=[float(min(bounds(direct)[:,0])),float(max(bounds(direct)[:,1]))],
        source_Lnu_tube_range=[float(min(bounds(direct_tube)[:,0])),float(max(bounds(direct_tube)[:,1]))],
        direct_minus_nodal_max_upper=encoded(max((a.abs_upper() for a in interpolation),key=lambda a:float(a.mid()))),
        proper_boundary_Lnu=encoded(Fourier_log_lapse(grid[-1],point['m'],proper_boundary=True)),
        action_I_dot=encoded(jets['Idot']),action_I_dot_tube_fixed_instantaneous=encoded(tjets['Idot']),
        preserved_nodal_I_dot=encoded(oldIdot),action_H=encoded(jets['H']),
        q_tau_identity='exact algebraic q_tau=v/N_b because Psi_q=0 and V_q=W_q v; no raw eigenvalue descriptor',
        lapse_change_equation='delta D5W=-u iGamma0 delta Lnu/(2nu)',
        source_action_time_change='delta D5p=iGamma0 p/nu [delta C_tau/(2C)+delta r_tau/(2r)-delta H/2]',
        all_time_change='delta D5W=u iGamma0/nu [-delta I_dot/(2I)-delta Lnu/2+3delta H/2+delta C_tau/(2C)]',
        norms=summaries,local_interface_consumed=True,physical_current_jet_promoted=False,
        instantaneous_pairings='unchanged fixed retained volume and Cauchy operands; material multiplier/full complement preserved',
        required_global_terms='same-owner stratified/interface/completion and connected propagation; not supplied by local rows alone',
        physical_a_mu=None,physical_g_mu=None,native_heat=None,
        error_scope='conditional retained endpoint/tube bounds; scalar outward arithmetic; fixed-instantaneous temporal update; no global domain/continuum/matrix-quadrature certificate')
    return arrays,result
