"""Common temporal weak applications for the retained cap and intrinsic Higgs.

The geometry arrays are local L(q,qdot,m) derivatives.  A time test and its
actual derivative assemble them into a differential weak operator; qdot is
never promoted to an independent Euler coordinate.  Endpoint momentum is
returned explicitly.  Scalar insertions use the same geometric coordinates,
with the intrinsic M4 measure.  These applications do not assign primal
Higgs, matter, connection, or temporal trace data.
"""
from __future__ import annotations

import numpy as np

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_moving_geometric_action import weak_action_blocks


def _finite(value, shape=None):
    result=np.asarray(value,dtype=float)
    if (shape is not None and result.shape!=shape) or not np.isfinite(result).all():
        raise ValueError('finite arrays of the declared common-domain shape required')
    return result


def _local_hessian(block):
    qq=block['H_qq']; qv=block['H_qv']; qm=block['H_qm']
    vv=block['H_vv']; vm=block['H_vm']; mm=block['H_mm']
    return np.block([[qq,qv,qm],[block['H_vq'],vv,vm],
                     [np.asarray(qm).T,np.asarray(vm).T,mm]])


def temporal_geometry_weak_application(blocks, quadrature_weights, q_tests,
                                       q_test_rates, m_tests, normal,
                                       normal_rates, *, endpoints=(),
                                       q_test_shape=None, q_test_rate_shape=None,
                                       m_test_shape=None):
    """Apply geometry residual, Hessian and partial normal source to time tests.

    Test arrays are (node, local-coordinate, real-test).  ``q_test_rates``
    must represent D_t of the same q tests on the declared domain.  The
    function does not infer endpoint/retarded conditions from a reset node.
    Caller endpoints have orientation +/-1, a local block, q_tests,
    q_test_rates, m_tests, normal and normal_rate.  Optional q_test_shape
    supplies prescribed test transport in the endpoint source, not an
    induced internal response.  Its bulk test/rate/multiplier-test lifts
    must also be supplied; off-shell residual times test transport is kept.

    Action residual is integral(test*L_q + D_t(test)*L_qdot + test*L_m).
    Its integration-by-parts Euler volume pairing is action residual minus
    the oriented endpoint contact.  The same split is made for the source
    and Hessian.  Only the closed, fully assembled action may be treated as
    a symmetric Hessian; a subsequently reduced retarded map need not be.
    """
    if not blocks:
        raise ValueError('at least one temporal action node required')
    nq=len(blocks[0]['S_q']); nm=len(blocks[0]['multiplier_constraint_residual'])
    count=len(blocks); tq=_finite(q_tests); tv=_finite(q_test_rates); tm=_finite(m_tests)
    if tq.ndim!=3 or tq.shape[:2]!=(count,nq):
        raise ValueError('q tests must have node, q-coordinate and real-test axes')
    nt=tq.shape[2]; tv=_finite(tv,(count,nq,nt)); tm=_finite(tm,(count,nm,nt))
    w=_finite(quadrature_weights,(count,)); s=_finite(normal,(count,))
    sr=_finite(normal_rates,(count,))
    supplied=(q_test_shape is not None,q_test_rate_shape is not None,m_test_shape is not None)
    if any(supplied) and not all(supplied):
        raise ValueError('all three bulk test transport applications required')
    if any('q_test_shape' in e for e in endpoints) and not all(supplied):
        raise ValueError('endpoint test transport requires its bulk applications')
    tqs=np.zeros_like(tq) if not all(supplied) else _finite(q_test_shape,tq.shape)
    tvs=np.zeros_like(tv) if not all(supplied) else _finite(q_test_rate_shape,tv.shape)
    tms=np.zeros_like(tm) if not all(supplied) else _finite(m_test_shape,tm.shape)
    residual=np.zeros(nt); source=np.zeros(nt); hessian=np.zeros((nt,nt))
    for k,b in enumerate(blocks):
        transform=np.vstack((tq[k],tv[k],tm[k]))
        gradient=_finite(np.concatenate((b['S_q'],b['canonical_momentum'],
                                        b['multiplier_constraint_residual'])),(2*nq+nm,))
        mixed=_finite(np.concatenate((b['B_q_direct']*s[k]+b['B_q_rate_direct']*sr[k],
                       b['B_q_momentum_contact']*s[k]+b['B_q_rate_momentum_contact']*sr[k],
                       b['B_m']*s[k]+b['B_m_rate']*sr[k])),(2*nq+nm,))
        residual+=w[k]*(transform.T@gradient)
        source+=w[k]*(transform.T@mixed+np.vstack((tqs[k],tvs[k],tms[k])).T@gradient)
        hessian+=w[k]*(transform.T@_finite(_local_hessian(b),(2*nq+nm,2*nq+nm))@transform)
    contact=np.zeros(nt); source_contact=np.zeros(nt); hessian_contact=np.zeros((nt,nt))
    for e in endpoints:
        sign=e['orientation']
        if sign not in (-1,1):
            raise ValueError('endpoint orientation must be explicitly +/-1')
        b=e['block']; eq=_finite(e['q_tests'],(nq,nt))
        ev=_finite(e['q_test_rates'],(nq,nt)); em=_finite(e['m_tests'],(nm,nt))
        normal_value=float(e['normal']); normal_rate=float(e['normal_rate'])
        if not np.isfinite([normal_value,normal_rate]).all():
            raise ValueError('finite endpoint normal and rate required')
        contact+=sign*(eq.T@b['canonical_momentum'])
        source_contact+=sign*(eq.T@(b['B_q_momentum_contact']*normal_value
                                                +b['B_q_rate_momentum_contact']*normal_rate))
        if 'q_test_shape' in e:
            source_contact+=sign*(_finite(e['q_test_shape'],(nq,nt)).T@b['canonical_momentum'])
        hessian_contact+=sign*(eq.T@(np.asarray(b['H_vq'])@eq
                                       +np.asarray(b['H_vv'])@ev+np.asarray(b['H_vm'])@em))
    return dict(action_residual=residual,euler_volume_pairing=residual-contact,
                endpoint_momentum_pairing=contact,action_source=source,
                euler_source_pairing=source-source_contact,
                endpoint_source_pairing=source_contact,action_hessian=hessian,
                euler_hessian_pairing=hessian-hessian_contact,
                endpoint_hessian_pairing=hessian_contact,
                full_stationarity_claim=False,physical_domain_instantiated=False,
                qdot_role='actual temporal test derivative',
                retarded_reduced_Hermitian_claim=False)


def scalar_monomial_coefficients(weights):
    """Exact Higgs action coefficient map at a supplied geometric application.

    S_H=wT |D_tH|^2-wS |D_S3H|^2-wV[lambda*(|H|^2-nu^2)^2
    +2 Re(H^dagger J)].  The coefficient map is evaluated even when the
    primal monomials are unsolved.  In particular coefficient 1 does not
    mean a physical unit field/source.  All gradients/Hessians occupy the
    unchanged (q,qdot,m,s,sdot) slots, including lapse and mixed contacts.
    """
    return dict(time_kinetic=weights['time_weight'],
                spatial_kinetic=-weights['spatial_weight'],
                potential_and_explicit_source=-weights['potential_weight'])


def fixed_covariant_scalar_geometry_action_jet(weights, H, DH, J, lambda_H,
                                               nu_squared, quadrature_weights):
    """Insert a specified scalar application into the geometry action rows.

    H,DH,J have point shapes (p,2),(p,4,2),(p,2).  The supplied covariant
    components and tests are held fixed in these partial geometry jets.
    Connection/frame/trace dependence must be supplied as additional
    explicit applications from the scalar weak backend; this component
    alone is not the complete metric derivative in a varying connection.
    """
    h=np.asarray(H,dtype=complex); dh=np.asarray(DH,dtype=complex); j=np.asarray(J,dtype=complex)
    if h.ndim!=2 or h.shape[1]!=2 or dh.shape!=(len(h),4,2) or j.shape!=h.shape:
        raise ValueError('common-point Higgs doublet and covariant derivative shapes required')
    if not all(np.isfinite(x).all() for x in (h,dh,j)):
        raise ValueError('finite supplied primal scalar application required')
    lam=float(lambda_H); nu=float(nu_squared)
    if not np.isfinite([lam,nu]).all() or lam<=0 or nu<0:
        raise ValueError('positive lambda_H and nonnegative nu_squared required')
    w=_finite(quadrature_weights,(len(h),))
    kt=np.sum(np.abs(dh[:,0])**2,axis=1)
    ks=np.sum(np.abs(dh[:,1:])**2,axis=(1,2))
    norm=np.sum(np.abs(h)**2,axis=1)
    potential=lam*(norm-nu)**2+2*np.real(np.sum(h.conj()*j,axis=1))
    coefficients=scalar_monomial_coefficients(weights)
    result=Jet.constant(0.,len(weights['time_weight'].gradient))
    for key,value in (('time_kinetic',kt),('spatial_kinetic',ks),
                      ('potential_and_explicit_source',potential)):
        result=result+coefficients[key]*float(w@value)
    return dict(total=result,qdim=weights['qdim'],mdim=weights['mdim'],
                source_indices=weights['source_indices'],
                complete_connection_frame_derivative=False,
                fixed_covariant_components=('H','DH','J'),stationarity_claim=False)


def scalar_geometry_higgs_cross(weights, H, DH, J, h_trials, Dh_trials,
                                 lambda_H, nu_squared, quadrature_weights):
    """Geometry/Higgs mixed block of the same fixed-connection action.

    Columns are real variations, including imaginary Higgs components.
    h_trials:(p,2,k), Dh_trials:(p,4,2,k).  The source J is an independent
    matter-source application, held fixed in this HH block.  Its actual
    matter-field cross is supplied by lepton_higgs_source_variation.
    """
    H=np.asarray(H,dtype=complex); DH=np.asarray(DH,dtype=complex); J=np.asarray(J,dtype=complex)
    h=np.asarray(h_trials,dtype=complex); dh=np.asarray(Dh_trials,dtype=complex)
    if H.ndim!=2 or H.shape[1]!=2 or DH.shape!=(len(H),4,2) or J.shape!=H.shape:
        raise ValueError('common primal field point axes required')
    if h.ndim!=3 or h.shape[:2]!=H.shape or dh.shape!=(len(H),4,2,h.shape[2]):
        raise ValueError('real Higgs trial columns and covariant derivatives required')
    if not all(np.isfinite(x).all() for x in (H,DH,J,h,dh)):
        raise ValueError('finite realified mixed application required')
    w=_finite(quadrature_weights,(len(H),)); lam=float(lambda_H); nu=float(nu_squared)
    if not np.isfinite([lam,nu]).all() or lam<=0 or nu<0:
        raise ValueError('positive lambda_H and nonnegative nu_squared required')
    dkt=2*np.real(np.einsum('pa,pak->pk',DH[:,0].conj(),dh[:,0]))
    dks=2*np.real(np.einsum('pia,piak->pk',DH[:,1:].conj(),dh[:,1:]))
    A=np.sum(np.abs(H)**2,axis=1)-nu
    force=2*lam*A[:,None]*H+J
    dV=2*np.real(np.einsum('pa,pak->pk',force.conj(),h))
    c=scalar_monomial_coefficients(weights)
    return sum(np.outer(c[key].gradient,w@value) for key,value in
               (('time_kinetic',dkt),('spatial_kinetic',dks),('potential_and_explicit_source',dV)))


def combine_local_action_applications(geometry, *applications):
    """Add unreduced action sectors before assembling the common weak solve.

    All applications must have the same coordinate/domain identification.
    This adds action derivatives, never independently reduced impedances.
    An application may be a supplied symbolic-coefficient surface sector
    already multiplied by gamma.  Caller owns that coefficient; no default.
    """
    total=geometry['total']
    for a in applications:
        for key in ('qdim','mdim','source_indices'):
            if a[key]!=geometry[key]:
                raise ValueError('same signed action coordinates and domain required')
        if len(a['total'].gradient)!=len(total.gradient):
            raise ValueError('common action jet dimension required')
        total=total+a['total']
    return weak_action_blocks(dict(total=total,qdim=geometry['qdim'],
                                  mdim=geometry['mdim'],source_indices=geometry['source_indices']))


def coupled_scalar_geometry_application(*, weight_nodes, quadrature, metric_maps,
                                        H, DH, J, test_values, test_derivatives,
                                        lambda_H, nu_squared, normal, normal_rates,
                                        mechanical_patch=None, mechanical_rotation=None):
    """Assemble nonlinear scalar residual and its common geometry/HH blocks.

    ``metric_maps[p,100,g]`` maps real geometry coefficients to the same
    local (q,qdot,m,s,sdot) coordinates at each scalar quadrature point.
    Its last two rows must vanish: shape is a partial source, not an
    additional internal Euler coordinate.  Test arrays use the scalar
    backend's (real-basis,point,doublet) convention.  Actual gauge/frame,
    matter, constraint and matching applications must be combined with
    these unreduced blocks; none is replaced by a physical zero here.
    When mechanical_patch is supplied, DH/test_derivatives contain D0
    excluding that background.  The owned Sp1 connection, its field cross
    and geometric/normal jets are then inserted exactly once.
    """
    from .muon_intrinsic_higgs_weak_action import (
        higgs_weak_residual,realified_higgs_weak_jacobian,higgs_explicit_weak_variation,
    )
    p=len(weight_nodes)
    if not p:
        raise ValueError('scalar quadrature/action nodes required')
    maps=_finite(metric_maps)
    if maps.ndim!=3 or maps.shape[:2]!=(p,len(weight_nodes[0]['wT'].gradient)):
        raise ValueError('common scalar-point/local-geometry/real-trial maps required')
    ns,nr=weight_nodes[0]['source_indices']
    if np.any(maps[:,[ns,nr],:]!=0):
        raise ValueError('normal source is not an internal Euler coordinate')
    quad=_finite(quadrature,(p,)); s=_finite(normal,(p,)); sr=_finite(normal_rates,(p,))
    tests=np.asarray(test_values,dtype=complex); Dt=np.asarray(test_derivatives,dtype=complex)
    if tests.ndim!=3 or tests.shape[1:]!=(p,2) or Dt.shape!=(len(tests),p,4,2):
        raise ValueError('real scalar test basis on the common quadrature required')
    h=np.asarray(H,dtype=complex); dh=np.asarray(DH,dtype=complex); j=np.asarray(J,dtype=complex)
    if h.shape!=(p,2) or dh.shape!=(p,4,2) or j.shape!=h.shape:
        raise ValueError('actual common-chart primal H, DH and J applications required')
    if mechanical_patch is not None and mechanical_rotation is None:
        raise ValueError('explicit common coframe rotation required with mechanical background')
    covDH=dh.copy(); covDt=Dt.copy(); explicitDH=np.zeros_like(dh)
    explicitDt=np.zeros_like(Dt)
    G=np.zeros((p,4,4)); dG=np.zeros_like(G); vol=np.zeros(p); dv=np.zeros(p)
    ng=maps.shape[2]; nh=len(tests)
    rg=np.zeros(ng); Hgg=np.zeros((ng,ng)); Hgh=np.zeros((ng,nh)); bg=np.zeros(ng)
    for a,w in enumerate(weight_nodes):
        if w['source_indices']!=(ns,nr):
            raise ValueError('one common normal chart required')
        if mechanical_patch is None:
            application=fixed_covariant_scalar_geometry_action_jet(w,h[a:a+1],dh[a:a+1],
                j[a:a+1],lambda_H,nu_squared,[quad[a]])['total']
        else:
            mechanical=mechanical_scalar_action_coefficients(w,patch=mechanical_patch,
                rotation=mechanical_rotation)
            kap=mechanical['kappa']; tau=mechanical['unit_connection_generators']
            AH=np.einsum('iab,b->ia',tau,h[a])
            Aphi=np.einsum('iab,kb->kia',tau,tests[:,a])
            covDH[a,1:]+=kap.value*AH; covDt[:,a,1:]+=kap.value*Aphi
            kap_source=kap.gradient[ns]*s[a]+kap.gradient[nr]*sr[a]
            explicitDH[a,1:]=kap_source*AH; explicitDt[:,a,1:]=kap_source*Aphi
            application=mechanical_scalar_geometry_action_jet(w,h[a:a+1],dh[a:a+1],
                j[a:a+1],lambda_H,nu_squared,[quad[a]],patch=mechanical_patch,
                rotation=mechanical_rotation)['total']
        rg+=maps[a].T@application.gradient
        Hgg+=maps[a].T@application.hessian@maps[a]
        bg+=maps[a].T@(application.hessian[:,ns]*s[a]+application.hessian[:,nr]*sr[a])
        cross=scalar_geometry_higgs_cross(w,h[a:a+1],covDH[a:a+1],j[a:a+1],
            np.transpose(tests[:,a:a+1,:],(1,2,0)),
            np.transpose(covDt[:,a:a+1,:,:],(1,2,3,0)),lambda_H,nu_squared,[quad[a]])
        if mechanical_patch is not None:
            dcross=2*np.real(np.einsum('kia,ia->k',Dt[:,a,1:].conj(),AH)
                              +np.einsum('ia,kia->k',dh[a,1:].conj(),Aphi))
            dnorm=2*np.real(np.einsum('a,ka->k',h[a].conj(),tests[:,a]))
            cross+=np.outer(-w['wS'].value*kap.gradient,quad[a]*(dcross+6*kap.value*dnorm))
        Hgh+=maps[a].T@cross
        for index,key,sign in ((0,'wT',1),(1,'wS',-1),(2,'wS',-1),(3,'wS',-1)):
            G[a,index,index]=sign*w[key].value
            dG[a,index,index]=sign*(w[key].gradient[ns]*s[a]+w[key].gradient[nr]*sr[a])
        vol[a]=w['wV'].value
        dv[a]=w['wV'].gradient[ns]*s[a]+w['wV'].gradient[nr]*sr[a]
    kwargs=dict(quadrature=quad,kinetic_density=G,volume_density=vol,H=h,DH=covDH,J=j,
                lambda_H=lambda_H,nu_squared=nu_squared)
    rh=np.array([higgs_weak_residual(**kwargs,phi=t,Dphi=dt) for t,dt in zip(tests,covDt)])
    bh=np.array([higgs_explicit_weak_variation(**kwargs,phi=t,Dphi=dt,
        delta_kinetic_density=dG,delta_volume_density=dv,delta_DH=explicitDH,
        delta_Dphi=ddt) for t,dt,ddt in zip(tests,covDt,explicitDt)])
    Hhh=realified_higgs_weak_jacobian(quadrature=quad,kinetic_density=G,
        volume_density=vol,H=h,test_values=tests,test_derivatives=covDt,
        trial_values=tests,trial_derivatives=covDt,lambda_H=lambda_H,nu_squared=nu_squared)
    return dict(scalar_action_residual=np.concatenate((rg,rh)),
                scalar_action_jacobian=np.block([[Hgg,Hgh],[Hgh.T,Hhh]]),
                scalar_partial_metric_normal_source=np.concatenate((bg,bh)),
                geometry_rows=ng,real_scalar_rows=nh,
                partial_fixed_connection_application=True,
                mechanical_background_derivatives_included=mechanical_patch is not None,
                full_stationarity_claim=False,physical_domain_instantiated=False,
                additional_applications_required=('connection/frame','matter source',
                    'material-response constraint and adjoint','inherited matching'))


def inherited_scalar_event_matching(*, parent_trace, child_trace, trace_transport,
                                    parent_flux, child_flux, parent_pairing, child_pairing,
                                    parent_orientation, child_orientation,
                                    boundary_source_covector, response_H_covector,
                                    trace_transport_shape, parent_pairing_shape,
                                    child_pairing_shape, parent_flux_shape,
                                    child_flux_shape, boundary_source_shape,
                                    response_H_shape):
    """Apply a supplied inherited trace and its correctly paired flux return.

    Fluxes are Riesz vectors under the explicitly supplied pairings.
    These flux inputs have not yet included the endpoint orientation signs
    multiplied here.  Already oriented higgs_conormal_flux output must
    therefore be factored consistently; do not apply that sign twice.
    ``G_p Pi_p+T^dagger G_c Pi_c`` is a parent *covector*.  If a flux already
    includes its measure, its extraction must use the reference pairing;
    applying the metric measure again would double count it.  T is the
    actual inherited scalar trace map, never an inferred fermion map.
    All shape arrays are partial applications at fixed primal coordinates
    and multipliers.  The response covector is already R_H^dagger Lambda;
    its supplied shape is R_H,s^dagger Lambda, not multiplier response.
    """
    p=np.asarray(parent_trace,dtype=complex); c=np.asarray(child_trace,dtype=complex)
    T=np.asarray(trace_transport,dtype=complex); Gp=np.asarray(parent_pairing,dtype=complex)
    Gc=np.asarray(child_pairing,dtype=complex)
    if p.ndim!=1 or c.ndim!=1 or T.shape!=(len(c),len(p)):
        raise ValueError('actual parent/child scalar trace and transport required')
    for G,n in ((Gp,len(p)),(Gc,len(c))):
        if G.shape!=(n,n) or not np.isfinite(G).all() or not np.allclose(G,G.conj().T,atol=1e-13,rtol=0):
            raise ValueError('Hermitian positive trace pairings required')
        np.linalg.cholesky(G)
    if parent_orientation not in (-1,1) or child_orientation not in (-1,1):
        raise ValueError('explicit parent and child endpoint orientations required')
    def array(x,shape):
        y=np.asarray(x,dtype=complex)
        if y.shape!=shape or not np.isfinite(y).all():
            raise ValueError('finite common-domain matching application required')
        return y
    pp=array(parent_flux,p.shape); cp=array(child_flux,c.shape)
    Ts=array(trace_transport_shape,T.shape); gps=array(parent_pairing_shape,Gp.shape)
    gcs=array(child_pairing_shape,Gc.shape); pps=array(parent_flux_shape,p.shape)
    cps=array(child_flux_shape,c.shape); source=array(boundary_source_covector,p.shape)
    response=array(response_H_covector,p.shape); js=array(boundary_source_shape,p.shape)
    rs=array(response_H_shape,p.shape)
    if not all(np.isfinite(x).all() for x in (p,c,T)):
        raise ValueError('finite actual trace application required')
    cotangent=parent_orientation*(Gp@pp)+child_orientation*(T.conj().T@Gc@cp)+source+response
    partial=parent_orientation*(gps@pp+Gp@pps)+child_orientation*(
        Ts.conj().T@Gc@cp+T.conj().T@gcs@cp+T.conj().T@Gc@cps)+js+rs
    return dict(trace_residual=c-T@p,flux_covector_residual=cotangent,
                partial_trace_shape=-Ts@p,partial_flux_shape=partial,
                dual_trace_return=np.linalg.solve(Gp,T.conj().T@Gc),
                full_stationarity_claim=False,retarded_reduced_Hermitian_claim=False)


def real_scalar_weak_coefficient_map(weights, *, derivative_index=None):
    """Evaluate the nonlinear weak polynomial coefficients, leaving H unsolved.

    Real coordinates are (Re H1,Re H2,Im H1,Im H2), with no rescaling.
    The quartic tensor multiplies lambda_H*x_j*x_k*x_l; the linear tensor
    multiplies lambda_H*nu_squared*x_j.  Source coordinates are realified
    J, not a selected covariance or fermion field.  Angular/time derivative
    terms contract actual covariant test/field derivatives on a common
    domain; this pointwise coefficient map is not their integral value.
    """
    I=np.eye(4)
    def coefficient(key):
        a=weights[key]
        return float(a.value if derivative_index is None else a.gradient[derivative_index])
    wt,ws,wv=(coefficient(k) for k in ('wT','wS','wV'))
    symmetric=np.einsum('ij,kl->ijkl',I,I)+np.einsum('ik,jl->ijkl',I,I)+np.einsum('il,jk->ijkl',I,I)
    return dict(time_derivative_pairing=2*wt*I,spatial_derivative_pairing=-2*ws*I,
                cubic_tensor_times_lambda_H=-(4*wv/3)*symmetric,
                linear_tensor_times_lambda_H_nu_squared=4*wv*I,
                source_pairing=-2*wv*I,
                real_coordinate_order=('Re H1','Re H2','Im H1','Im H2'),
                primal_H_evaluated=False,partial_fixed_connection=True)


def mechanical_scalar_action_coefficients(weights, *, patch, rotation):
    """Evaluate the action-owned Sp1/H kinetic coefficient subapplication.

    The parent section has kappa=lambda_geom-1; the child section has
    kappa=lambda_geom.  In unit-S3 derivatives A_i=kappa R_id(-i sigma_d).
    The physical-orthonormal coefficient is kappa/R4.  This radius is not
    multiplied into wS a second time.  The quaternion/Sp1 Lie algebra uses
    -i sigma, hence twice the retained Hermitian weak generators sigma/2.

    With D0 containing all remaining connection terms,
    S_mechanical=-wS sum_i[2 Re(D0_iH)^dagger A_i H+|A_i H|^2].
    Returned cross and H^dagger H coefficients are actual local action
    two-jets.  They do not assign D0, H or a sourced gauge fluctuation.
    """
    from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation
    R=_finite(rotation,(3,3))
    if not np.allclose(R@R.T,np.eye(3),atol=1e-12,rtol=0) or not np.isclose(np.linalg.det(R),1.,atol=1e-12,rtol=0):
        raise ValueError('orientation-preserving common Sp1 coframe rotation required')
    if patch not in ('parent','child'):
        raise ValueError('owned parent or child mechanical patch required')
    generators=-2j*retained_higgs_spin_charge_representation()['higgs_su2_generators']
    tau=np.einsum('id,dab->iab',R,generators)
    lam=weights['mechanical_connection_lambda']
    kappa=lam-1 if patch=='parent' else lam
    cross_coefficient=-weights['wS']*kappa
    norm_coefficient=-3*weights['wS']*kappa*kappa
    return dict(kappa=kappa,unit_connection_generators=tau,
                D0H_connection_cross_coefficient=cross_coefficient,
                H_norm_coefficient=norm_coefficient,
                identity_matrix=np.eye(2),patch=patch,
                coefficient_owner=('muon_owned_connection_application.regular_parent_background_prefactor'
                    if patch=='parent' else 'muon_owned_connection_application.apply_saved_child_profiles'),
                remaining_connection_in_D0=True,primal_H_evaluated=False,
                full_stationary_base=False)


def mechanical_scalar_geometry_action_jet(weights,H,D0H,J,lambda_H,nu_squared,
                                         quadrature_weights,*,patch,rotation):
    """Differentiate the scalar action including its recovered Sp1 background.

    H, D0H and J are specified applications held fixed, with D0 containing
    the time derivative and all remaining connection terms.  This keeps
    internal/mixed/shape derivatives of the background connection as well
    as the metric weights.  It is still partial for source, remaining
    connection/frame and inherited-domain applications.
    """
    base=fixed_covariant_scalar_geometry_action_jet(weights,H,D0H,J,lambda_H,
                                                   nu_squared,quadrature_weights)
    h=np.asarray(H,dtype=complex); dh=np.asarray(D0H,dtype=complex)
    w=_finite(quadrature_weights,(len(h),))
    c=mechanical_scalar_action_coefficients(weights,patch=patch,rotation=rotation)
    AH=np.einsum('iab,pb->pia',c['unit_connection_generators'],h)
    cross=2*np.real(np.einsum('pia,pia->p',dh[:,1:].conj(),AH))
    norm=np.sum(np.abs(h)**2,axis=1)
    base['total']=base['total']+c['D0H_connection_cross_coefficient']*float(w@cross)
    base['total']=base['total']+c['H_norm_coefficient']*float(w@norm)
    base['mechanical_background_derivatives_included']=True
    base['fixed_covariant_components']=('H','D0H excluding mechanical Sp1 background','J')
    base['mechanical_patch']=patch
    return base
