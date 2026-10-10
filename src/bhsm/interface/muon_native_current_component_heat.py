"""Current-normalized angular photon component and its reached heat form.

The common material geometry supplies every coefficient.  The available
mechanical angular action is re-solved in all 240 angular coordinates; an
old photon response or old radius is never inserted.  Temporal/radial,
independent-background, induced and constraint rows are not replaced by
this component.  The positive product core remains a numerical component.
"""
from __future__ import annotations

import numpy as np

from .muon_moving_geometric_action import _sqrt
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_gauge_geometry_correction import finite_common_iterate_at_time, MAXWELL_TO_CAP
from .muon_parent_maxwell_geometry_weak import geometric_connection_coefficient_jets
from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space, full_q_reference_operators
from .muon_parent_retarded_hypercharge import WALL, compact_trace_pulse
from .muon_native_photon_response import source_directed_component_response
from .muon_native_product_factor_graph import (
    _finite, _source_core_samples, _family_shell_heat_forms,
    _family_source_heat_blocks, lepton_unit_trace_gauge_representation,
)
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def current_geometric_photon_component(response, coordinate_time):
    """Apply the owned b-to-beta normalization and current angular density.

    Tb=(2*pi^2*R4)^(-1/2), beta=Tb*b.  Independent b coefficients are
    fixed in the material chart while Tb, lambda, density and measure move.
    The coefficient jets retain all 100 geometric value/rate coordinates.
    Their three polynomial matrices avoid allocating a dense matrix jet.
    """
    t=float(coordinate_time)
    if not np.isfinite(t) or t<response['time_shift'] or t>0:
        raise ValueError('current component cannot extrapolate the retained material family')
    d=finite_common_iterate_at_time(t,response['coefficients'],response['representation'],
        response['reference'],rho=np.array([WALL]))
    kw=dict(source_value=d['normal'],source_rate=d['normal_rate'])
    intrinsic=intrinsic_m4_weight_jet(12,d['q'],d['qdot'],d['m'],**kw)
    parent=geometric_connection_coefficient_jets(12,d['q'],d['qdot'],d['m'],np.array([WALL]),**kw)['rows'][0]
    R=intrinsic['R4'];Tb=1/(np.sqrt(2*np.pi**2)*_sqrt(R));lam=parent['connection_lambda']
    scale=-MAXWELL_TO_CAP*parent['angular']*Tb**2
    angular=retained_full_q_angular_space(response['repository'])
    operators=full_q_reference_operators(angular)
    C0,C1=operators['curl0']-operators['curl1'],operators['curl1']
    B=operators['magnetic_contact'][160:,160:]
    matrices=np.array((C0.T@C0,C0.T@C1+C1.T@C0-4*B,C1.T@C1+4*B))
    factors=(scale,scale*lam,scale*lam**2)
    K=sum(f.value*A for f,A in zip(factors,matrices));K=(K+K.T)/2
    # Parent radial-cut one-form pairing, not the Maxwell velocity Hessian.
    # 2*pi² Tb² * J*N_parent*C_rho*r_orbit = J*N_parent*C_rho at the wall.
    m=parent['material_jacobian']*intrinsic['fields']['N']*intrinsic['fields']['C']/2
    if not m.value>0:raise ValueError('positive current geometric cut pairing required')
    S=angular['source_coefficients'][160:]
    return dict(K_per_kappa1=K,M_geometric_scalar=float(m.value),source_inclusion=S,
        f_R=float((Tb/R).value),T_b=float(Tb.value),R4=float(R.value),coordinate_time=t,
        mechanical_lambda=float(lam.value),full_angular_coordinate_count=240,
        matrix_polynomial=matrices,coefficient_values=np.array([x.value for x in factors]),
        coefficient_geometric_jacobian=np.array([x.gradient for x in factors]),
        coefficient_geometric_hessians=np.array([x.hessian for x in factors]),
        T_b_geometric_gradient=Tb.gradient,T_b_geometric_hessian=Tb.hessian,
        geometric_pairing_gradient=m.gradient,geometric_pairing_hessian=m.hessian,
        angular=angular,intrinsic_geometry=intrinsic,
        source_frame_identity_residual=abs(2*np.pi**2*R.value*Tb.value**2-1),
        current_source_Gram_residual=float(np.linalg.norm(S.T@S-(16/3)*np.eye(8))),
        angular_action_normalization='MAXWELL_TO_CAP * current Tb² * same material angular density; no extra Haar or QNORM division',
        parent_geometric_pairing='2*pi²*Tb²*J*N_parent*C_rho*r_orbit',
        negative_Lorentz_angular_sign_retained=True,
        independent_background_angular_remainder_included=False,
        complete_photon_action_or_native_domain=False)


def current_component_dual_response(component, *, multipliers=(1.25,2.,4.),target=1e-12):
    """Fresh full-angular solves on the eight source duals, with enrichment.

    A physical mode-current covector is not selected: the identity here
    indexes the eight test duals.  Given an actual current J=Jbasis*C, its
    component return is C†(Jbasis†u0)C and a native form needs u0†R u0.
    Spectral shifts are conditioning probes, not physical photon momenta.
    """
    S=component['source_inclusion'];J=S@np.linalg.solve(S.T@S,np.eye(8))
    current=dict(dual_current_basis=J,mode_current_covector=np.eye(8),reached_current_dual=J)
    solved=source_directed_component_response(component,current,multipliers=multipliers,target=target)
    projector=S@np.linalg.solve(S.T@S,S.T)
    for record in solved['records']:
        u=record['basis_response']
        outside=u-projector@u
        record['outside_original_Q8_absolute_norm']=float(np.linalg.norm(outside))
        record['outside_original_Q8_relative_norm']=float(np.linalg.norm(outside)/np.linalg.norm(u))
    solved.update(current=current,
        exact_consumer_reduction='J=Jbasis*C => adjoint/native contraction C†[u0† R u0]C, on the actual full-angular response columns',
        coefficient_response_scope='u_hat=kappa1*u for this available component; kappa1 is not assigned',
        original_Q8_heat_matrix_is_not_substituted_for_u0_pairing=True,
        actual_physical_current_covector_selected=False,
        physical_photon_momentum_or_complete_A0_selected=False)
    return solved


def component_response_fermion_image(component, response_record):
    """Full n1+n3 coefficient image of the newly solved b-frame directions."""
    b=_finite(response_record['basis_response'],'current component full response',(240,8))
    if np.max(abs(b.imag))>2e-12*max(1.,np.max(abs(b))):
        raise ValueError('real material one-form directions required for Hermitian source')
    coefficients=b.real.reshape(3,4,20,8)
    alpha=lepton_current_hilbert_representation()['alpha']
    G=lepton_unit_trace_gauge_representation()['generators']
    tensor=-1j*np.array([[alpha[a]@G[c] for c in range(4)] for a in range(3)])
    image=np.einsum('achA,acij->Ahij',coefficients,tensor)
    return dict(unit_radius_b_source_image=image,
        angular=component['angular'],full_response_coefficients=b,
        Hermiticity_coefficient_residual=float(np.linalg.norm(image-image.conj().transpose(0,1,3,2))),
        moving_normalization='at each core quadrature Xi=Tb(t)*profile(t)*image/R4(t); current Tb recomputed from common geometry',
        old_T_b_or_geometry_transplanted=False,physical_current_or_source_lift_selected=False)


def current_component_source_history(response, component, response_record, coordinate_times):
    """Bind the reached cut directions to the moving material one-form frame.

    The freshly solved cut b columns are fixed test directions.  They are
    not independently re-solved along the computational time chart.  The
    physical beta frame moves with Tb(t), whose derivative follows the
    SAME geometry and wall flow.  The returned unprofiled Q and Qdot can
    be combined with the source pulse as g*Q and gdot*Q+g*Qdot before the
    full Maxwell/scalar action assembly.  No fixed-Q replay is relabeled.
    """
    times=_finite(coordinate_times,'source coefficient times',real=True)
    if times.ndim!=1 or not len(times) or np.any(np.diff(times)<=0):raise ValueError('strictly increasing source coefficient times required')
    if times[0]<response['time_shift'] or times[-1]>0:raise ValueError('no material source extrapolation')
    b=_finite(response_record['basis_response'],'current angular response',(240,8))
    if np.max(abs(b.imag))>2e-12*max(1.,np.max(abs(b))):raise ValueError('real reached one-form required')
    b400=np.vstack((np.zeros((160,8)),b.real));values=[];rates=[];tb=[];tbd=[];radius=[];motions=[]
    for t in times:
        data=finite_common_iterate_at_time(t,response['coefficients'],response['representation'],response['reference'],rho=np.array([WALL]))
        g=intrinsic_m4_weight_jet(12,data['q'],data['qdot'],data['m'],source_value=data['normal'],source_rate=data['normal_rate'])
        f=g['fields'];lam=g['mechanical_connection_lambda'].value;wall_rate=g['wall_rate'].value
        logRdot=(1-lam)*(f['la'].value+wall_rate*f['ap'].value)+lam*(f['lb'].value+wall_rate*f['bp'].value)
        T=1/np.sqrt(2*np.pi**2*g['R4'].value);Td=-.5*logRdot*T
        values.append(T*b400);rates.append(Td*b400);tb.append(T);tbd.append(Td);radius.append(g['R4'].value)
        motions.append(dict(gradient=g['R4'].gradient,hessian=g['R4'].hessian))
    return dict(coordinate_times=times,response_times=times-response['time_shift'],
        full400_source_Q=np.array(values),full400_source_Qdot=np.array(rates),
        cut_b_source_coefficients=b400,T_b=np.array(tb),T_b_dot=np.array(tbd),R4=np.array(radius),
        source_normal_gradient=np.array([-.5*T/r*m['gradient'][-2:] for T,r,m in zip(tb,radius,motions)])[:,None,None,:]*b400[None,:,:,None],
        source_normal_hessian=np.array([T*(.75*np.outer(m['gradient'][-2:],m['gradient'][-2:])/r**2-.5*m['hessian'][-2:,-2:]/r) for T,r,m in zip(tb,radius,motions)])[:,None,None,:,:]*b400[None,:,:,None,None],
        field_order=('At','Ar','A1','A2','A3'),coefficient_axes='field5 x unitTr16internal4 x realoddharmonics20 x reached8',
        coordinate_scope='material-reference outgoing24 local numerical chart; fresh component response at the declared cut, fixed b test columns',
        source_profile_included=False,source_profile_rule='g*Q; derivative=gdot*Q+g*Qdot',
        normalization_derivative='Tb_dot=-0.5*dlogR4_dt*Tb, with qdot and material wall_rate from the same coefficient family',
        independent_physical_source_or_current_selected=False)


def current_component_response_heat_core(response, component, response_record, *,
        time_nodes,quadrature_order,family_indices=(1,2)):
    """Evaluate source square and both insertions on the full reached image.

    The angular response is computed at the declared cut and held as a
    b-frame direction; its physical beta coefficient moves with current Tb.
    The compact profile is the inherited numerical-source test.  The
    background geometry, active H and connection remain the actual common
    finite iterate.  A new response to these enriched source columns is
    not borrowed from the older eight-Q coupled-response packet.
    """
    nodes=_finite(time_nodes,'current-response heat nodes',real=True)
    if nodes.ndim!=1 or len(nodes)<3 or np.any(np.diff(nodes)<=0):raise ValueError('increasing finite core nodes required')
    if nodes[0]<response['time_shift'] or nodes[-1]>0:raise ValueError('no current-response heat extrapolation')
    if type(quadrature_order) is not int or quadrature_order<2:raise ValueError('explicit quadrature order>=2 required')
    families=tuple(family_indices)
    if not families or len(set(families))!=len(families) or any(type(f) is not int or f not in (0,1,2) for f in families):
        raise ValueError('distinct retained family indices required')
    source=component_response_fermion_image(component,response_record)
    samples=_source_core_samples(response['coefficients'],response['representation'],response['reference'],nodes,
        np.ones((len(nodes),8)),quadrature_order)
    for s in samples:
        t=nodes[s['cell']]+s['x']*s['h'];u=t-response['time_shift']
        Tb=1/np.sqrt(2*np.pi**2*s['R'])
        s['beta']=np.ones(8)*Tb*float(compact_trace_pulse(u,response['duration'])[0])
    angular=source['angular'];D=angular['derivative_matrices'];labels=angular['harmonic_labels'];rows={}
    for f in families:
        fiber=np.array([2*f,2*f+1,6+2*f,7+2*f,12+2*f,13+2*f]);zero=_family_shell_heat_forms(samples,len(nodes),None,fiber)
        contact=np.zeros((8,8,len(zero['eigenvalues'])),complex);shells={}
        for n in (1,3):
            ids=np.array([i for i,label in enumerate(labels) if label[0]==n])
            shell=_family_shell_heat_forms(samples,len(nodes),D[:,ids][:,:,ids],fiber)
            Xi=source['unit_radius_b_source_image'][:,ids][:,:,fiber][:,:,:,fiber].reshape(8,6*len(ids),6)
            block=_family_source_heat_blocks(samples,len(nodes),Xi,zero,shell,fiber)
            contact+=block['mixed_contact_n0_spectral_diagonal']
            shells[str(n)]=dict(eigenvalues=shell['eigenvalues'],first_jet_n0=block['first_jet_n0'],
                full_shell_scalar_count=len(ids),all_complementary_eigenmodes_retained=True,
                generalized_eigen_residual_relative=shell['generalized_eigen_residual_relative'])
        rows[str(f)]=dict(inherited_family=('heavy','middle','light')[f],n0_eigenvalues=zero['eigenvalues'],
            mixed_contact_n0_spectral_diagonal=contact,intermediate_shells=shells,
            generalized_eigen_residual_relative=zero['generalized_eigen_residual_relative'])
    return dict(families=rows,temporal_core_nodes=nodes,quadrature_order=quadrature_order,
        angular_response_cut_time=component['coordinate_time'],
        angular_response_zeta_over_kappa1=response_record['zeta_over_kappa1'],
        reached_full_angular_response_columns=True,original_Q8_compression_substituted=False,
        response_scale='the evaluated pair is on u_hat=kappa1*u; the physical component pair has the unassigned kappa1^-2 factor',
        source_normalization='beta=Tb(current R4)*b; physical one-form coefficient; no old radius, e, or family/statistics factor',
        source_profile='retained compact pulse, computational outgoing24 backward core only',
        fixed_field_affine_source_component=True,
        genuine_coupled_source_geometry_H_gauge_response_included=False,
        complete_native_supertrace_or_Pauli_evaluated=False)
