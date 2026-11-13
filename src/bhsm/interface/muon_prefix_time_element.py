"""One inherited non-cut prefix weak element, using saved first actions.

This is muon realization code.  It does not supply a complete exterior or
stratified heat operator.  Descriptor-chart state/clock enclosures accompany
the numerical representative; the temporal density interpolant is explicit.
"""
from __future__ import annotations

import numpy as np
from flint import arb, ctx

from bhsm.interface.muon_cut_inverse_coverage import encoded
from bhsm.interface.muon_coupled_cut_forms import field_actions
from bhsm.interface.muon_radial_inclusion_action import affine_sin_squared_integral
from bhsm.interface.muon_parent_maxwell_velocity import current_parent_fields


def norm_ball(a):
    return sum((arb(float(x))**2 for x in np.asarray(a).ravel()),arb(0)).sqrt()


def box(lo,hi):
    lo,hi=arb(float(lo)),arb(float(hi))
    return arb(((lo+hi)/2).mid(),((hi-lo)/2).upper())


def interior_first_actions(x,step,record,branch,field,field_report,growth,response):
    """Original-center chart, not an extrapolation of endpoint data.

    Quadratic predictor values consume already-saved first actions.  A
    whole-step Lohner bound encloses the physical descriptor-fiber trajectory.
    No raw selected eigenvalue or sorted-eigenvalue branch rule is used.
    """
    ctx.prec=192
    sigma0=arb(record['segment']['signed_descriptor_start'])
    h=arb(record['segment']['signed_descriptor_step']); t=h*arb(float(x))
    sigma=sigma0+t;tf=float(t.mid())
    yc=step['center_state']; weights=step['state_weights']
    if not (np.array_equal(yc,branch['center_state']) and np.array_equal(yc,field['center_state'])
            and np.array_equal(weights,branch['state_weights'])):
        raise ValueError('original-center action/chart identities disagree')
    if record['segment']['endpoint_selected_branch']!=24:
        raise ValueError('different inherited branch; do not choose a new one')
    nominal_delta=tf*step['exact_center_field_action']+.5*tf*tf*step['center_acceleration_action']
    y=yc+nominal_delta/weights
    displacement=(y-yc)*weights
    represent_roundoff=norm_ball(displacement-nominal_delta)
    sec=record['second_variation'];dom=record['domain']
    L=arb(float(sec['fixed_s_first_variation_ball_upper']))
    mu=arb(float(sec['fixed_s_logarithmic_norm_ball_upper']))
    f=norm_ball(step['exact_center_field_action'])
    incoming=arb(float(dom['incoming_endpoint_tube_radius']))
    # The owned certificate is around Euler dense output; compensate the
    # stored partial-acceleration quadratic representative explicitly.
    trajectory=(mu*t).exp()*incoming+L*f*t*t/2+t*t*norm_ball(step['center_acceleration_action'])/2+represent_roundoff
    distance=norm_ball(displacement);use=distance+trajectory
    radius=arb(float(dom['selected_domain_radius']))
    if not use<radius:
        raise ValueError('interior trajectory set outside original whole-step chart')
    psi0=branch['selected_vector'];r0=branch['bordered_response']
    psi=psi0+branch['selected_vector_derivative_action']@displacement
    r=r0+branch['bordered_response_derivative_action']@displacement
    line=growth['fresh_line_bounds'];pf=growth['fresh_pole_free_bounds']
    p1=arb(float(line['weighted_selected_to_complement_first_variation_on_ball']))
    p2=arb(float(line['selected_line_second_variation_coefficient_upper']))
    x1=arb(float(sec['response_first_variation_upper']))
    x2=arb(float(sec['response_second_variation_upper']))
    forcing=branch['bordered_matrix']@r0
    b1=arb(float(response['ball']['b_psi_first_variation_center_upper']))
    b2=p2*norm_ball(forcing[:-1])+2*p1*arb(float(pf['rhs_raw_derivative_center']))+arb(float(pf['rhs_raw_second_derivative_upper']))
    perr=p2*distance*distance/2+p1*trajectory
    rerr=x2*distance*distance/2+x1*trajectory
    berr=b2*distance*distance/2+(b1+b2*radius)*trajectory
    pb=[arb(float(v),perr.upper()) for v in psi]
    hb=[arb(float(v),rerr.upper()) for v in r[:-1]]
    bb=arb(float(r[-1]),berr.upper())
    state=[arb(float(v),(trajectory/arb(float(w))).upper()) for v,w in zip(y,weights)]
    signs=(-1)**np.arange(1,13)
    Nb=sum((state[74+k]*int(signs[k]) for k in range(12)),arb(0)).exp()
    Nnom=float(np.exp(y[74:86]@signs))
    # Delta and input/output weights cancel symbolically before enclosure.
    from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
    qw,rw,_,_=metric_data()
    if not (np.array_equal(weights[:37],qw) and np.array_equal(weights[37:],rw)):
        raise ValueError('saved action/output weight cancellation is not applicable')
    q=[state[37+k]/Nb for k in range(37)]
    m=[(bb*pb[k]+sigma*hb[k])/(Nb*sigma) for k in range(37,61)]
    qnom=y[37:74]/Nnom
    mnom=(r[-1]*psi[37:61]+float(sigma.mid())*r[37:61])/(Nnom*float(sigma.mid()))
    # Nominal clock retains the first variation of the moving cubic and
    # response.  The true clock has the whole-step coefficient enclosure.
    c0=field_report['center_field']['moving_cubic_from_Dlambda_Psi']
    cubic=c0+field['moving_c_gradient_action']@displacement
    V=np.concatenate((qw*y[37:74],rw*r[:-1]))
    R=branch['lambda_gradient_action']@V
    Delta=float(cubic*r[-1]+float(sigma.mid())*R)
    dl,du=dom['Delta_interval'];cl,cu=dom['c_interval'];bl,bu=dom['b_psi_interval']
    Rbound=(arb(float(du))+arb(float(cu))*arb(float(bu)))/sigma0
    widen=h*Rbound
    delta_box=box(dl,du)+arb(0,widen.upper())
    if not delta_box>0 or not Delta>0:
        raise ValueError('owned clock chart not monotone')
    if not delta_box.contains(arb(Delta)):
        raise ValueError('nominal clock outside inherited descriptor-cell box')
    tau_x=Nb*sigma*h/delta_box
    tau_nom=float(h.mid())*Nnom*float(sigma.mid())/Delta
    result=dict(x=float(x),sigma=encoded(sigma),nominal_state_sha_scope='quadratic representative inside physical descriptor-fiber enclosure',
        descriptor_fiber='lambda_event(Y)=sigma; predictor is not promoted to an exact off-fiber history',
        branch=24,selection='continuation of retained branch_reference/eigenprojector within original chart; no sorted-eigenvalue index selection',
        trajectory_radius=encoded(trajectory),original_center_distance=encoded(distance),joint_chart_use=encoded(use),
        chart_radius=encoded(radius),q_tau=[encoded(v) for v in q],m_tau=[encoded(v) for v in m],
        q_tau_identity='q_tau=v/N_b',Delta_nominal=Delta,Delta_box=encoded(delta_box),
        explicit_sigma_clock_widening=encoded(widen),clock_tau_x=encoded(tau_x),clock_tau_x_nominal=tau_nom,
        first_action_remainders=dict(psi=encoded(perr),hard_response=encoded(rerr),b=encoded(berr)),
        action_scope='cached numerical first-action Taylor values plus whole-step line/response/trajectory enclosures; no new Hessian or Jacobian',
        new_raw_eigenvalues=0,new_branch_selections=0)
    return dict(y=y,delta_action=displacement,q=q,m=m,qnom=qnom,mnom=mnom,Nb=Nb,Nnom=Nnom,
                tau_x=tau_x,tau_nom=tau_nom,result=result)


def attached_geometry(y,cut_state,cut_geometry):
    """Same radius attachment by relative coordinates; no RADIUS0 inserted."""
    q,qc=y[:37],cut_state[:37]
    sk=(-1.)**np.arange(1,13);sj=(-1.)**np.arange(12)
    vb=q[25:37]@sj;vbc=qc[25:37]@sj
    dx=(q[0]-qc[0])+(q[1:13]-qc[1:13])@sk-.5*(np.log(np.cosh(2*vb))-np.log(np.cosh(2*vbc)))
    logR=np.log(float(cut_geometry['boundary_radius'][0]))+dx
    f=current_parent_fields(y[None],np.array([logR]),cut_geometry['rho'])
    return f


def moving_coefficients(first,geometry,contact,radial,norm,cut_geometry):
    """Current E_tau and D5 coefficients at a non-cut retained state."""
    ctx.prec=192
    grid=geometry['rho'];Cnodes=geometry['C_rho'][0];rnodes=geometry['base_radius'][0]
    An,Bn=geometry['A'][0],geometry['B'][0];q=first['qnom'];m=first['mnom']
    k=np.arange(1,13);j=np.arange(12);ck=np.cos(2*grid[:,None]*k);cj=np.cos(2*grid[:,None]*j)
    win=np.sin(grid)**2
    ud=ck@q[1:13];wd=win*(cj@q[13:25]);vd=win*(cj@q[25:37])
    Cdot=Cnodes*(q[0]+ud+wd)
    rdot=rnodes*(q[0]+ud-(An**2-Bn**2)/(An**2+Bn**2)*vd)
    vb=first['y'][25:37]@((-1.)**np.arange(12))
    H=float(q[0]+q[1:13]@((-1.)**k)-np.tanh(2*vb)*(q[25:37]@((-1.)**np.arange(12))))
    reused=np.array_equal(Cnodes,cut_geometry['C_rho'][0])
    I=arb(norm['I_rad']['arb']) if reused else affine_sin_squared_integral(grid,Cnodes)
    Idot=affine_sin_squared_integral(grid,Cdot)
    points=radial['points'];cells=radial['cells'];width=np.diff(grid)[cells];x=(points-grid[cells])/width
    val=lambda nodes:nodes[cells]*(1-x)+nodes[cells+1]*x
    dr=lambda nodes:np.diff(nodes)[cells]/width
    nu,C,r,z=(val(geometry[key][0]) for key in ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    nr,Cr,rr,zr=(dr(geometry[key][0]) for key in ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    Ct,rt=val(Cdot),val(rdot)
    Lnu=(np.cos(2*points[:,None]*k)-(-1.)**k)@m[:12]
    Rb=float(geometry['boundary_radius'][0]);nb=float(geometry['proper_lapse'][0,-1])
    u=np.sin(points/2)/np.sqrt(float(I.mid())*(nu/nb)*(r/Rb)**3)
    lt=-float(Idot.mid())/(2*float(I.mid()))-Lnu/2-3*rt/(2*r)+1.5*H
    lr=-nr/(2*nu)-3*rr/(2*r)+.5/np.tan(points/2)
    h0=(Ct/C+3*rt/r-z*(Cr/C+3*rr/r)-zr)/(2*nu)
    h4=(nr/nu+3*rr/r)/(2*C);eta=-.5/(C*np.tan(points/2))
    a0=(-float(Idot.mid())/(2*float(I.mid()))-Lnu/2+1.5*H+Ct/(2*C)-z*Cr/(2*C)-zr/2+z*nr/(2*nu)-.5*z/np.tan(points/2))/nu
    hatnodes=contact['spinor_probe_hat_nodes'];hat=val(hatnodes);hatr=dr(hatnodes)
    Tb=float(contact['T_b'])*np.sqrt(float(cut_geometry['boundary_radius'][0])/Rb)
    p=Tb*hat/r;pr=Tb*(hatr/r-hat*rr/r**2);pt=(-H/2-rt/r)*p
    volume=2*np.pi**2*nu*C*r**3;cauchy=volume/nu;gw=radial['radial_weights']
    M4=2*np.pi**2*nb*Rb**3
    T=float(gw@(volume*u*p));Gs=float(gw@(cauchy*u*u));Ts=float(gw@(cauchy*u*p))
    lv=Lnu+Ct/C+3*rt/r;ls=Ct/C+3*rt/r;lp=-H/2-rt/r
    Tdot=float(gw@(volume*u*p*(lv+lt+lp)))
    Tsdot=float(gw@(cauchy*u*p*(ls+lt+lp)))
    Gsdot=float(gw@(cauchy*u*u*(ls+2*lt)))
    b=T/M4;bd=(Tdot-3*H*T)/M4;bs=Ts/Gs;bsd=(Tsdot-Gsdot*bs)/Gs
    s=dict(points=points,cells=cells,nu=nu,C=C,r=r,z=z,u=u,p=p,pr=pr,pt=pt,h0=h0,h4=h4,eta=eta,a0=a0,
        bg=-val(Bn)/(val(An)*np.hypot(val(An),val(Bn))),volume=volume,cauchy=cauchy)
    rcp=dict(I=encoded(I),I_tau=encoded(Idot),instantaneous_I_certificate_reused=reused,H=H,T_b=Tb,
        bulk_B=b,bulk_B_tau=bd,Cauchy_B=bs,Cauchy_B_tau=bsd,
        proper_boundary_Lnu='exact zero in boundary Fourier basis',
        spatial_derivatives='same64-cell affine nodal geometry; direct Fourier Lnu, no temporal nodal derivative substitution')
    return s,dict(C_tau_nodes=Cdot,r_tau_nodes=rdot,Lnu_direct=Lnu,a0=a0,u=u,p=p),rcp


def spatial_weak_actions(s,basis,carrier,cut,coefficient_receipt):
    """F0/F1 of the actual moving W/p frame; full source outputs retained."""
    d=cut['independent_source_map'].shape[1];dim=2*d
    A=np.zeros((dim,dim),complex);B=A.copy();C=A.copy()
    gw=cut['radial_weights'];coef=cut['source_coordinates'];selected={}
    for n in (1,3):
        reached=[[],[],[],[]]
        for lo in range(0,len(gw),32):
            hi=min(lo+32,len(gw));sc={k:v[lo:hi] for k,v in s.items()}
            f=field_actions(sc,basis[n],n,carrier)
            F0=np.concatenate(f[:2],axis=-1).reshape(hi-lo,-1,dim)
            F1=np.concatenate(f[2:],axis=-1).reshape(hi-lo,-1,dim)
            w=(gw*s['volume'])[lo:hi]
            gram=lambda u,v:np.einsum('g,gai,gaj->ij',w,u.conj(),v,optimize=True)
            A+=gram(F0,F0);B+=gram(F0,F1);C+=gram(F1,F1)
            for k,v in enumerate(f):reached[k].append(np.einsum('gomki,i->gomk',v,coef))
        DW,Dp,DtW,Dtp=[np.concatenate(a) for a in reached]
        b=coefficient_receipt['bulk_B'];bt=coefficient_receipt['bulk_B_tau']
        selected.update({f'Dp_n{n}':Dp,f'DWp_n{n}':DW,f'DtauW_n{n}':DtW,
            f'Dchi_n{n}':Dp-b*DW-bt*DtW})
    S=cut['independent_source_map'];G=S.conj().T@cut['source_Haar_Gram']@S
    scalar=lambda measure,left,right:float(gw@(measure*left*right))
    M=np.kron(np.array([[scalar(s['volume'],s['u'],s['u']),scalar(s['volume'],s['u'],s['p'])],
        [scalar(s['volume'],s['u'],s['p']),scalar(s['volume'],s['p'],s['p'])]]),G)
    Ms=np.kron(np.array([[scalar(s['cauchy'],s['u'],s['u']),scalar(s['cauchy'],s['u'],s['p'])],
        [scalar(s['cauchy'],s['u'],s['p']),scalar(s['cauchy'],s['p'],s['p'])]]),G)
    return dict(A=A,B=B,C=C,M=M,Ms=Ms,**selected)


def assemble_time_element(x,w,points,scale):
    """Integrate explicit temporal density polynomials, including E_tau.

    Atilde=tau_x A, Btilde=B, Ctilde=C/tau_x, Mtilde=tau_x M.
    Degree n-1 density interpolants and degree1 basis products are exactly
    integrated by n-point Gauss for n>=3. This exactness is model-scoped.
    """
    dim=points[0]['A'].shape[0];K=np.zeros((2*dim,2*dim),complex);M=K.copy()
    densities={key:[] for key in ('A','B','C','M')}
    for xi,wi,p in zip(x,w,points):
        jac=p['tau_x'];h=np.array([1.,scale*(xi-.5)]);dh=np.array([0.,scale])
        aa=jac*p['A'];bb=p['B'];cc=p['C']/jac;mm=jac*p['M']
        for key,v in zip(('A','B','C','M'),(aa,bb,cc,mm)):densities[key].append(v)
        for i in range(2):
            for j in range(2):
                K[i*dim:(i+1)*dim,j*dim:(j+1)*dim]+=wi*(h[i]*h[j]*aa+h[i]*dh[j]*bb+dh[i]*h[j]*bb.conj().T+dh[i]*dh[j]*cc)
                M[i*dim:(i+1)*dim,j*dim:(j+1)*dim]+=wi*h[i]*h[j]*mm
    V=np.polynomial.legendre.legvander(2*np.asarray(x)-1,len(x)-1)
    polys={key:np.linalg.solve(V,np.array(value).reshape(len(x),-1)).reshape(len(x),dim,dim) for key,value in densities.items()}
    return K,M,polys


def consume_prefix_element(K,M,cut,scale):
    """Insert this numerical weak element in coupled temporal trace assembly."""
    d=cut['independent_source_map'].shape[1];dim=2*d
    src=np.zeros(2*dim,complex);src[d:2*d]=cut['source_coordinates']
    # Constant original source in unprojected coordinates. No subtraction
    # of inclusion/complement form blocks or two large nodal derivatives.
    source_pairing=M@src;form_action=K@src
    I=np.eye(dim);trace=np.block([[I,-scale*I/2],[I,scale*I/2]])
    arrays=dict(element_K=K,element_M=M,source_constant_coefficients=src,
        source_weak_rhs=source_pairing,source_form_cotangent=form_action,
        hierarchical_to_endpoint_coefficients=trace,left_source_trace=src[:dim],right_source_trace=src[:dim])
    receipt=dict(assembled=True,kind='source-reached local Dirac temporal element inside inherited prefix',
        left_face='C2 step1221 endpoint / step1222 original center; artificial internal element face',
        right_face='C2 step1222 artificial cut; prefix outward +tau, core outward -tau',
        left_outward_orientation=-1,right_outward_orientation=1,
        inherited_reset='earlier physical reset unchanged; total inclusion-plus-complement graph retained',
        canonical_stop='unchanged; this element introduces no endpoint law',
        source_element_energy=float(np.vdot(src,form_action).real),
        source_element_mass=float(np.vdot(src,source_pairing).real),
        local_Dirac_block_assembled=True,full_stratified_block_assembled=False,
        element_inverse_taken=False,full_exterior_solved=False,solution=None,stationary_residual=None,
        stationary_conormal=None,heat=None,physical_a_mu=None,physical_g_mu=None,
        remaining_blocks=dict(adjacent_history_actions=None,owned_wall_interface_and_Higgs_seam=None,
            full_domain_coupling=None,gauge_constraint_BRST=None,relative_completion=None))
    return arrays,receipt


def retained_arc_first_action(y,action_rate,weights,clock_density,descriptor,mode_record):
    """A retained numerical-center tangent with its own cancelled-arc clock.

    This does not extrapolate the1222 descriptor chart.  The cached field is
    G/||G|| and d_tau/d_arc=N_b*sigma/||G||.  Their common normalization and
    Delta cancel before division; no raw tiny eigenvalue is reconstructed.
    """
    if mode_record['selected_branch']!=24 or not descriptor>0 or not clock_density>0:
        raise ValueError('retained positive-descriptor branch/clock required')
    Nb=float(np.exp(y[74:86]@((-1.)**np.arange(1,13))))
    cancelled_norm=float(mode_record['cancelled_field_norm'])
    clock_identity=Nb*descriptor/cancelled_norm
    Y_tau=action_rate/(weights*clock_density)
    expected=y[37:74]/Nb
    relative=np.linalg.norm(Y_tau[:37]-expected)/np.linalg.norm(expected)
    if relative>1e-12 or abs(clock_identity/clock_density-1)>1e-12:
        raise ValueError('retained same-action physical-clock identities disagree')
    return dict(y=y,qnom=Y_tau[:37],mnom=Y_tau[74:98],Y_tau=Y_tau,Nnom=Nb,
        result=dict(branch=24,selected_line_gap=mode_record['selected_line_gap'],
            branch_rule='retained continuation from branch_reference; not sorted eigenvalue selection',
            signed_descriptor=float(descriptor),proper_clock_density=float(clock_density),
            cancelled_field_norm=cancelled_norm,q_tau_relative=relative,
            clock_identity_relative=abs(clock_identity/clock_density-1),
            coefficient_class='same-action retained numerical point tangent; no interval authority',
            cancelled_formula='Y_tau=(G/||G||)/(W_Y*N_b*sigma/||G||); Delta cancels upstream',
            reconstruction='cached action_rates/(state_weights*proper_time_density)',
            new_field_campaigns=0,new_raw_eigenvalues=0))


def integrate_linear_density_element(points,scale):
    """Exact moments of degree-one weak densities between two actual nodes.

    No interior point field is fabricated. This computes the declared
    density interpolant, not a certified integral of the continuous history.
    """
    densities={}
    for key in ('A','B','C','M'):
        values=[]
        for p in points:
            values.append(p[key]*(p['tau_x'] if key in ('A','M') else
                                  1/p['tau_x'] if key=='C' else 1))
        densities[key]=np.array([(values[0]+values[1])/2,(values[1]-values[0])/2])
    A,B,C,M=(densities[k] for k in ('A','B','C','M'))
    K=np.block([[A[0],scale*(A[1]/6+B[0])],
        [scale*(A[1]/6+B[0].conj().T),
         scale**2*(A[0]/12+(B[1]+B[1].conj().T)/6+C[0])]])
    mass=np.block([[M[0],scale*M[1]/6],
        [scale*M[1]/6,scale**2*M[0]/12]])
    return K,mass,densities
