"""Scalar birth images from the current mechanics worldvolume IVP.

The carrier-reset owner is covariant_bubble_interface_mechanics.build_payload:
its correspondence is the solved worldvolume flow with bundle parallel
transport.  The induced-ADM normal flow below is a foliation representative,
not an additional material velocity law.  A supplied tangential relabeling
may change that representative without adding a constitutive force.

All metric, connection and scalar coefficients come from one caller vector.
The initial geometric/bundle identification and formation time interval are
owned IVP conditions or coupled unknowns.  They are never replaced by an
identity map, a unit duration, or a zero time connection.  The resulting map
identifies two charts at the SAME E1 birth; it does not make H parallel along
its interior dynamical evolution or propagate the child into a later slice.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp


MECHANICS_OWNER = 'covariant_bubble_interface_mechanics.build_payload.carrier_reset'
CLOCK_OWNER = 'ae4_stratified_dirac_zeta_induced_owner.forward_time_domain_contract'
RETARDED_OWNER = 'ae4_future_collapse_relative_boundary_domain.future_collapse_domain_contract'


def _array(value, name, shape=None, complex_value=False):
    if value is None:
        raise ValueError(f'explicit {name} required')
    result = np.asarray(value, dtype=complex if complex_value else float)
    if shape is not None and result.shape != shape:
        raise ValueError(f'{name} needs shape {shape}')
    if not np.isfinite(result).all():
        raise ValueError(f'finite {name} required')
    return result


def _frames(q):
    """Linear right-invariant frame; also applies to a variation of q."""
    w,x,y,z=q.T
    return np.stack((np.stack((-x,w,-z,y),axis=1),
                     np.stack((-y,z,w,-x),axis=1),
                     np.stack((-z,-y,x,w),axis=1)),axis=2)


def unit_s3_material_frame(points):
    """Inherited right frame i*q,j*q,k*q, with bracket -2 epsilon.

    With g=w I-i(x sigma1+y sigma2+z sigma3), E_a g=-i sigma_a g.
    Thus the scalar basis sqrt(n+1) conjugate(D(g)) has the inherited
    active-index coefficient derivatives 2i J_a.  No Ad_g is made constant.
    """
    q=_array(points,'material unit-S3 points')
    if q.ndim!=2 or q.shape[1]!=4 or len(q)==0:
        raise ValueError('nonempty material points need (points,4)')
    if not np.allclose(np.sum(q*q,axis=1),1,rtol=0,atol=1e-9):
        raise ValueError('material points must lie on unit S3')
    return _frames(q)


def unit_quaternion_to_su2(points):
    """Bind the material quaternion chart to the inherited scalar SU2 chart."""
    q=_array(points,'material unit-S3 points');unit_s3_material_frame(q)
    w,x,y,z=q.T
    result=np.empty((len(q),2,2),complex)
    result[:,0,0]=w-1j*z;result[:,0,1]=-y-1j*x
    result[:,1,0]=y-1j*x;result[:,1,1]=w+1j*z
    return result


def su2_to_unit_quaternion(matrices):
    """Inverse chart binding; reject a general U2 phase rather than discard it."""
    g=_array(matrices,'scalar SU2 chart',complex_value=True)
    if g.ndim!=3 or g.shape[1:]!=(2,2) or len(g)==0:
        raise ValueError('scalar SU2 chart needs (points,2,2)')
    q=np.column_stack((g[:,0,0].real,-g[:,0,1].imag,
                       -g[:,0,1].real,-g[:,0,0].imag))
    if not np.allclose(unit_quaternion_to_su2(q),g,rtol=0,atol=1e-9):
        raise ValueError('scalar chart must be SU2 in the inherited quaternion convention')
    return q


def _antihermitian(value,name,shape):
    result=_array(value,name,shape,True)
    if not np.allclose(result+result.conj().swapaxes(-1,-2),0,rtol=0,atol=1e-11):
        raise ValueError(f'anti-Hermitian {name} required')
    return result


def induced_worldvolume_flow(metric, metric_spatial_derivatives, *,
                            metric_spatial_second_derivatives=None):
    """b=-beta=gamma^-1 h_it and its Haar divergence from the same metric.

    Spatial derivatives are E_a h and E_c E_a h in the displayed quaternion
    frame.  The frame is divergence-free for unit-S3 Haar measure.  The
    physical normal clock density is ell=sqrt(h_tt+h_ti b^i).
    """
    h=_array(metric,'induced metric')
    if h.ndim!=3 or h.shape[1:]!=(4,4):
        raise ValueError('induced metric needs (points,4,4)')
    p=len(h); dh=_array(metric_spatial_derivatives,'E_a metric',(p,3,4,4))
    if not np.allclose(h,h.swapaxes(1,2),rtol=0,atol=1e-12):
        raise ValueError('symmetric induced metric required')
    gamma=-h[:,1:,1:]; u=h[:,1:,0]
    try:
        np.linalg.cholesky(gamma)
    except np.linalg.LinAlgError as error:
        raise ValueError('positive induced spatial metric required') from error
    inv=np.linalg.inv(gamma); b=np.einsum('pij,pj->pi',inv,u)
    dg=-dh[:,:,1:,1:]; du=dh[:,:,1:,0]
    db=np.einsum('pij,paj->pai',inv,du-np.einsum('paij,pj->pai',dg,b))
    div=np.einsum('paa->p',db)
    lapse2=h[:,0,0]+np.einsum('pi,pi->p',u,b)
    if np.any(lapse2<=0):
        raise ValueError('future timelike worldvolume clock required')
    lapse=np.sqrt(lapse2)
    lapse_gradient=(dh[:,:,0,0]+np.einsum('pai,pi->pa',du,b)
                    +np.einsum('pi,pai->pa',u,db))/(2*lapse[:,None])
    out=dict(b=b,b_spatial_derivatives=db,haar_divergence=div,
             lapse=lapse,lapse_spatial_derivatives=lapse_gradient,
             gamma=gamma,inverse_gamma=inv,u=u,dgamma=dg,du=du)
    if metric_spatial_second_derivatives is not None:
        ddh=_array(metric_spatial_second_derivatives,'E_c E_a metric',(p,3,3,4,4))
        ddg=-ddh[:,:,:,1:,1:]; ddu=ddh[:,:,:,1:,0]
        ddb=np.einsum('pij,pcaj->pcai',inv,ddu
             -np.einsum('pcaij,pj->pcai',ddg,b)
             -np.einsum('paij,pcj->pcai',dg,db)
             -np.einsum('pcij,paj->pcai',dg,db))
        out['haar_divergence_spatial_derivatives']=np.einsum('pcaa->pc',ddb)
    return out


def induced_worldvolume_flow_variation(flow, metric_variation,
                                      metric_spatial_derivative_variation):
    """Partial coefficient variation at fixed material points, without h=0."""
    p=len(flow['b']); v=_array(metric_variation,'metric variation',(p,4,4))
    dv=_array(metric_spatial_derivative_variation,'E_a metric variation',(p,3,4,4))
    dg=-v[:,1:,1:]; du=v[:,1:,0]
    b,inv=flow['b'],flow['inverse_gamma']
    vb=np.einsum('pij,pj->pi',inv,du-np.einsum('pij,pj->pi',dg,b))
    vdb=np.einsum('pij,paj->pai',inv,dv[:,:,1:,0]
         +np.einsum('paij,pj->pai',dv[:,:,1:,1:],b)
         -np.einsum('paij,pj->pai',flow['dgamma'],vb)
         -np.einsum('pij,paj->pai',dg,flow['b_spatial_derivatives']))
    vl=(v[:,0,0]+np.einsum('pi,pi->p',du,b)
        +np.einsum('pi,pi->p',flow['u'],vb))/(2*flow['lapse'])
    return dict(b=vb,haar_divergence=np.einsum('paa->p',vdb),lapse=vl)


def _owned_evaluation(evaluator,t,q,coefficients,variation):
    data=evaluator(t,q,coefficients,variation)
    required=('metric','metric_spatial_derivatives','connection')
    for key in required:
        if key not in data or data[key] is None:
            raise ValueError(f'coefficient evaluator must bind {key}; omitted A_t is not zero')
    p=len(q)
    A=_antihermitian(data['connection'],'Higgs connection A_t,A_i',(p,4,2,2))
    flow=induced_worldvolume_flow(data['metric'],data['metric_spatial_derivatives'],
        metric_spatial_second_derivatives=data.get('metric_spatial_second_derivatives'))
    if variation is not None:
        for key in ('metric_variation','metric_spatial_derivative_variation',
                    'metric_spatial_second_derivatives','connection_variation',
                    'connection_spatial_derivatives'):
            if key not in data or data[key] is None:
                raise ValueError(f'coefficient tangent evaluator must bind {key}')
        vflow=induced_worldvolume_flow_variation(flow,data['metric_variation'],
                                               data['metric_spatial_derivative_variation'])
        vA=_antihermitian(data['connection_variation'],'Higgs connection variation',(p,4,2,2))
        dA=_antihermitian(data['connection_spatial_derivatives'],'E_a Higgs connection',(p,3,4,2,2))
    else:
        vflow=vA=dA=None
    # Relabeling is an explicitly declared gauge chart, never a fluid law.
    if 'tangential_relabeling' in data:
        if not data.get('tangential_relabeling_owner'):
            raise ValueError('tangential relabeling requires its owned chart provenance')
        flow['b']+=_array(data['tangential_relabeling'],'tangential relabeling',(p,3))
        dr=_array(data.get('tangential_relabeling_spatial_derivatives'),
                  'E_a tangential relabeling',(p,3,3))
        flow['b_spatial_derivatives']+=dr;flow['haar_divergence']+=np.einsum('paa->p',dr)
        if variation is not None:
            ddr=_array(data.get('tangential_relabeling_spatial_second_derivatives'),
                       'E_c E_a tangential relabeling',(p,3,3,3))
            flow['haar_divergence_spatial_derivatives']+=np.einsum('pcaa->pc',ddr)
            vflow['b']+=_array(data.get('tangential_relabeling_variation'),
                              'tangential relabeling variation',(p,3))
            vr=_array(data.get('tangential_relabeling_spatial_derivative_variation'),
                      'E_a tangential relabeling variation',(p,3,3))
            vflow['haar_divergence']+=np.einsum('paa->p',vr)
    return flow,A,vflow,vA,dA


def worldvolume_scalar_transport_ivp(*, coefficients, times, initial_material_points,
                                    initial_bundle_transport, initial_jacobian,
                                    evaluator, rtol, atol, coefficient_variation=None,
                                    initial_material_points_variation=None,
                                    initial_bundle_transport_variation=None,
                                    initial_jacobian_variation=None):
    """Integrate the represented mechanics flow, U2 lift and Haar Jacobian.

    The evaluator takes (t, material_points, coefficients, variation) and
    derives its fields from that SAME vector.  Geometry/bundle initial maps
    and time interval are explicit owned conditions, not scalar field data.
    With a variation it supplies partial coefficient and spatial jets; the
    integrator composes the moving-point tangent itself.  Reported tolerances
    are numerical integration controls, not an enclosure of physical error.
    """
    c=_array(coefficients,'coupled coefficients'); ts=_array(times,'owned physical time samples')
    if c.ndim!=1 or ts.ndim!=1 or len(ts)<2 or np.any(np.diff(ts)<=0):
        raise ValueError('one coefficient vector and strictly future time interval required')
    if not all(np.isfinite(x) and x>0 for x in (rtol,atol)):
        raise ValueError('explicit positive numerical integration tolerances required')
    q=_array(initial_material_points,'initial geometric identification')
    unit_s3_material_frame(q);p=len(q)
    U=_array(initial_bundle_transport,'initial Higgs bundle identification',(p,2,2),True)
    if not np.allclose(U.conj().swapaxes(-1,-2)@U,np.eye(2),rtol=0,atol=1e-10):
        raise ValueError('initial unitary Higgs bundle identification required')
    J=_array(initial_jacobian,'initial material Jacobian',(p,))
    if np.any(J<=0):raise ValueError('orientation-preserving initial Jacobian required')
    tangent=coefficient_variation is not None
    vc=_array(coefficient_variation,'coupled coefficient variation',c.shape) if tangent else None
    def pack(q,U,J,tau):return np.concatenate((q.ravel(),U.ravel(),J,tau)).astype(complex)
    def unpack(y):
        return (y[:4*p].reshape(p,4).real,y[4*p:8*p].reshape(p,2,2),
                y[8*p:9*p].real,y[9*p:10*p].real)
    initial=pack(q,U,J,np.zeros(p))
    if tangent:
        vq=_array(initial_material_points_variation,'initial geometric identification variation',q.shape)
        vU=_array(initial_bundle_transport_variation,'initial bundle identification variation',U.shape,True)
        vJ=_array(initial_jacobian_variation,'initial Jacobian variation',J.shape)
        if not np.allclose(np.sum(q*vq,axis=1),0,rtol=0,atol=1e-10):
            raise ValueError('initial point variation must be tangent to S3')
        if not np.allclose(vU.conj().swapaxes(-1,-2)@U+U.conj().swapaxes(-1,-2)@vU,
                           0,rtol=0,atol=1e-10):
            raise ValueError('initial bundle variation must be tangent to the unitary identification')
        initial=np.concatenate((initial,pack(vq,vU,vJ,np.zeros(p))))
    def rhs(t,y):
        q,U,J,_=unpack(y[:10*p]);norm=np.linalg.norm(q,axis=1)
        if np.any(norm==0):raise ValueError('worldvolume material flow left regular chart')
        # Roundoff normalization is only for coefficient evaluation, not a
        # replacement evolution equation or a selected physical map.
        point=q/norm[:,None];E=_frames(point)
        f,A,vf,vA,dA=_owned_evaluation(evaluator,t,point,c,vc)
        b=f['b']; Aflow=A[:,0]+np.einsum('pa,paij->pij',b,A[:,1:])
        base=pack(np.einsum('pia,pa->pi',E,b),-Aflow@U,
                  f['haar_divergence']*J,f['lapse'])
        if not tangent:return base
        vq,vU,vJ,_=unpack(y[10*p:]);xi=np.einsum('pia,pi->pa',E,vq)
        vb=vf['b']+np.einsum('paj,pa->pj',f['b_spatial_derivatives'],xi)
        totalvA=vA+np.einsum('pamij,pa->pmij',dA,xi)
        vAflow=totalvA[:,0]+np.einsum('pa,paij->pij',b,totalvA[:,1:])
        vAflow+=np.einsum('pa,paij->pij',vb,A[:,1:])
        vdiv=vf['haar_divergence']+np.einsum('pa,pa->p',
                    f['haar_divergence_spatial_derivatives'],xi)
        vlapse=vf['lapse']+np.einsum('pa,pa->p',f['lapse_spatial_derivatives'],xi)
        varied=pack(np.einsum('pia,pa->pi',E,vb)+np.einsum('pia,pa->pi',_frames(vq),b),
                    -vAflow@U-Aflow@vU,vdiv*J+f['haar_divergence']*vJ,vlapse)
        return np.concatenate((base,varied))
    solution=solve_ivp(rhs,(ts[0],ts[-1]),initial,t_eval=ts,method='DOP853',rtol=rtol,atol=atol)
    if not solution.success:raise RuntimeError(f'worldvolume transport IVP failed: {solution.message}')
    base=[unpack(y[:10*p]) for y in solution.y.T]
    points,bundle,jacobian,proper=[np.stack([row[i] for row in base]) for i in range(4)]
    out=dict(times=ts,material_points=points,bundle_transport=bundle,
             haar_jacobian=jacobian,normal_proper_clock=proper,
             coefficients=c,coefficient_variation=vc,
             point_norm_defect=float(np.max(abs(np.sum(points*points,axis=2)-1))),
             bundle_unitarity_defect=float(np.max(abs(bundle.conj().swapaxes(-1,-2)@bundle-np.eye(2)))),
             numerical_integration=dict(method='DOP853',rtol=rtol,atol=atol,evaluations=solution.nfev),
             mechanics_owner=MECHANICS_OWNER,clock_owner=CLOCK_OWNER,
             flow_representative='future induced-ADM normal plus explicitly owned relabeling',
             spatial_coframe='inherited right: E_a g=-i sigma_a g; quaternion e_a*q',
             scalar_interior_parallel_transport_claim=False,stationary_base_claim=False)
    if tangent:
        varied=[unpack(y[10*p:]) for y in solution.y.T]
        for i,key in enumerate(('material_points_variation','bundle_transport_variation',
                                'haar_jacobian_variation','normal_proper_clock_variation')):
            out[key]=np.stack([row[i] for row in varied])
    return out


def scalar_birth_transport_application(*, transport, parent_birth_points,
                                      birth_parent_time, birth_child_time,
                                      quadrature, basis_evaluator, density_evaluator,
                                      parent_coefficient_map, child_coefficient_map,
                                      pairing='real_2Re', time_index=-1,
                                      parent_birth_points_variation=None):
    """Apply T to unknown scalar coefficients and return its paired dual.

    Basis/density evaluators receive (side, points, coefficients, variation).
    They return basis (p,2,d) / density (p), and with a tangent their E_a
    derivatives and partial coefficient variation.  Both coefficient maps
    extract the parent/child fields from the one transport coefficient vector.
    The exact sampled trace image is retained even when a finite projected
    child basis does not contain it.  No universal finite invariance is claimed.
    Densities are endpoint geometric pairings; canonical fluxes already carrying
    measure must be converted to their Riesz vectors before using this dual.
    """
    if not np.isfinite(birth_parent_time) or birth_parent_time!=birth_child_time:
        raise ValueError('parent and child traces must be at the same physical E1 birth')
    if birth_child_time!=transport['times'][time_index]:
        raise ValueError('produced worldvolume endpoint must be the common E1 birth')
    c=transport['coefficients']; vc=transport['coefficient_variation'];tangent=vc is not None
    child_points=transport['material_points'][time_index]
    parent_points=_array(parent_birth_points,'parent birth-chart points',child_points.shape)
    Ep=unit_s3_material_frame(parent_points);Ec=unit_s3_material_frame(child_points)
    p=len(parent_points);quad=_array(quadrature,'common unit-S3 reference quadrature',(p,))
    if np.any(quad<=0):raise ValueError('positive trace quadrature required')
    U=transport['bundle_transport'][time_index];J=transport['haar_jacobian'][time_index]
    if np.any(J<=0):raise ValueError('positive produced material Jacobian required')
    basis=[];density=[];dbasis=[];ddensity=[]
    if tangent:
        vp=_array(parent_birth_points_variation,'parent birth-chart point variation',parent_points.shape)
        if not np.allclose(np.sum(parent_points*vp,axis=1),0,rtol=0,atol=1e-10):
            raise ValueError('parent birth-chart variation must be tangent to S3')
        vpoints=(vp,transport['material_points_variation'][time_index])
    for i,(side,points,E) in enumerate((('parent',parent_points,Ep),('child',child_points,Ec))):
        data=basis_evaluator(side,points,c,vc);B=_array(data.get('basis'),f'{side} scalar basis',complex_value=True)
        if B.ndim!=3 or B.shape[:2]!=(p,2):raise ValueError('scalar doublet basis needs (points,2,columns)')
        rho=density_evaluator(side,points,c,vc);mu=_array(rho.get('density'),f'{side} endpoint pairing',(p,))
        if np.any(mu<=0):raise ValueError('positive endpoint pairing density required')
        basis.append(B);density.append(mu)
        if tangent:
            xi=np.einsum('pia,pi->pa',E,vpoints[i])
            dB=_array(data.get('basis_variation'),f'{side} partial basis variation',B.shape,True)
            grad=_array(data.get('basis_spatial_derivatives'),f'{side} E_a basis',(p,3,2,B.shape[2]),True)
            dbasis.append(dB+np.einsum('paid,pa->pid',grad,xi))
            dmu=_array(rho.get('density_variation'),f'{side} partial density variation',(p,))
            gmu=_array(rho.get('density_spatial_derivatives'),f'{side} E_a density',(p,3))
            ddensity.append(dmu+np.einsum('pa,pa->p',gmu,xi))
    Bp,Bc=basis;mp,mc=density
    maps=[_array(x,name,complex_value=pairing=='complex_L2') for x,name in (
          (parent_coefficient_map,'parent scalar coefficient map'),(child_coefficient_map,'child scalar coefficient map'))]
    if maps[0].shape!=(Bp.shape[2],len(c)) or maps[1].shape!=(Bc.shape[2],len(c)):
        raise ValueError('scalar extraction maps must act on the one coupled vector')
    if pairing not in ('real_2Re','complex_L2'):raise ValueError('owned real 2Re or complex L2 pairing required')
    def pair(A,B,w):
        val=np.einsum('pid,pie,p->de',A.conj(),B,w)
        return 2*val.real if pairing=='real_2Re' else val
    image=np.einsum('pij,pjd->pid',U,Bp);wp=quad*mp;wc=quad*mc*J
    Gp=pair(Bp,Bp,wp);Gc=pair(Bc,Bc,wc);K=pair(Bc,image,wc)
    try:
        np.linalg.cholesky(Gp);np.linalg.cholesky(Gc)
    except np.linalg.LinAlgError as error:
        raise ValueError('independent scalar trace basis under its owned pairing required') from error
    T=np.linalg.solve(Gc,K);dual=np.linalg.solve(Gp,T.conj().T@Gc)
    pc,cc=maps[0]@c,maps[1]@c
    Hp=np.einsum('pid,d->pi',Bp,pc);Hc=np.einsum('pid,d->pi',Bc,cc)
    projected=Bc@T;residual=Hc-np.einsum('pij,pj->pi',U,Hp)
    out=dict(parent_trace=Hp,child_trace_at_carried_points=Hc,transported_parent_trace=U@Hp[...,None],
             trace_residual=residual,trace_transport=T,dual_trace_return=dual,
             parent_pairing=Gp,child_pairing=Gc,scalar_transport_image=image,
             image_projection_residual=image-projected,
             image_projection_weighted_norm=float(np.sqrt((2 if pairing=='real_2Re' else 1)
                                                *np.sum(wc[:,None,None]*abs(image-projected)**2))),
             pairing=pairing,birth_parent_time=birth_parent_time,birth_child_time=birth_child_time,
             child_pulled_pairing_density=mc*J,mechanics_owner=MECHANICS_OWNER,
             finite_scalar_image_invariance_claim=False,physical_base_claim=False)
    out['transported_parent_trace']=out['transported_parent_trace'][...,0]
    if tangent:
        vU=transport['bundle_transport_variation'][time_index];vJ=transport['haar_jacobian_variation'][time_index]
        vBp,vBc=dbasis;vmp,vmc=ddensity
        vimage=vU@Bp+U@vBp;vwp=quad*vmp;vwc=quad*(vmc*J+mc*vJ)
        vGp=pair(vBp,Bp,wp)+pair(Bp,vBp,wp)+pair(Bp,Bp,vwp)
        vGc=pair(vBc,Bc,wc)+pair(Bc,vBc,wc)+pair(Bc,Bc,vwc)
        vK=pair(vBc,image,wc)+pair(Bc,vimage,wc)+pair(Bc,image,vwc)
        vT=np.linalg.solve(Gc,vK-vGc@T)
        vdual=np.linalg.solve(Gp,vT.conj().T@Gc+T.conj().T@vGc-vGp@dual)
        vHp=np.einsum('pid,d->pi',vBp,pc)+np.einsum('pid,d->pi',Bp,maps[0]@vc)
        vHc=np.einsum('pid,d->pi',vBc,cc)+np.einsum('pid,d->pi',Bc,maps[1]@vc)
        out.update(trace_transport_variation=vT,dual_trace_return_variation=vdual,
                   parent_pairing_variation=vGp,child_pairing_variation=vGc,
                   trace_residual_variation=vHc-np.einsum('pij,pj->pi',vU,Hp)-np.einsum('pij,pj->pi',U,vHp),
                   scalar_transport_image_variation=vimage)
    return out


def current_scalar_time_and_load_contract():
    """Equations consumed by the primal driver, without assigning their data."""
    return dict(mechanics_owner=MECHANICS_OWNER,clock_owner=CLOCK_OWNER,retarded_owner=RETARDED_OWNER,
                scalar_space='scalar S3 sections tensor Higgs fundamental C2; temporal H1/Cauchy realization',
                momentum='p_H=G^{t nu} D_nu H; complex flux paired by 2 Re, without another factor two',
                time_row='D_t H=(G^{tt})^{-1}(p_H-G^{ti}D_i H)',
                momentum_row='D_t p_H=-D_S3^dagger(wS D_S3 H)-wV[2 lambda_H(|H|^2-nu^2)H+J_H] in the diagonal chart',
                source='J_H=bar(e_R)Y_l^dagger L_L from the applicable same-action matter unknowns',
                physical_time='future directed; child t>=parent t; formation interval and initial geometric/bundle identification follow the event/environment coupled IVP',
                retarded='actual child operator boundary value omega+i0, future regular/outgoing; homogeneous Cauchy component remains part of coupled conditions',
                birth_trace='H_child(F(x))=U_H(x) H_parent(x) at common E1 time',
                birth_flux='oriented parent flux plus paired returned child flux plus owned source/reaction =0',
                direct_area_H_contact=0,direct_material_response_H_contact=0,
                direct_material_response_Hs_contact=0,
                zero_contact_scope='fixed geometry and independent material-response chart only',
                zero_contact_owners=dict(
                    surface='covariant_bubble_interface_mechanics.build_payload.total_action',
                    response='muon_moving_material_response.response_constraint_jet'),
                zero_contact_equations=('S_W=-gamma integral mu_h, with no direct H argument',
                                        'C_sigma=n_eta dot D sigma-W[f]/Z[f], with no direct H argument'),
                induced_geometry_response_zero_claim=False,
                other_scalar_event_or_gauge_constraints_zero_claim=False,
                physical_time_interval_assigned=False,homogeneous_scalar_Cauchy_component_assigned=False,
                eliminated_native_term_added_to_classical_force=False)
