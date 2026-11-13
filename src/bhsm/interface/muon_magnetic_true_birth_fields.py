"""True attached E1 Legendre/Gauss reconstruction of magnetic first fields.

This applies the endpoint action to the already reached canonical state.
It does not replace the solved finite source-cell trajectory, whose primal
velocity/algebraic fields were held at the midpoint of that cell.
"""
from __future__ import annotations
import numpy as np


def birth_constitutive_response(sample, canonical_state):
    """Recover velocities and At from the same-action canonical x/p.

    L=.5 zdot M zdot+z B zdot+.5 z K z, z=(x,g).
    At was eliminated by its complete sourced algebraic equation.  At
    birth g=I8, gdot=0; p=Mxx v+Bxx.T x+Bgx.T.  No velocity is copied
    across the event and no unforced Gauss equation is substituted.
    """
    state=np.asarray(canonical_state)
    if not np.isrealobj(state) or state.shape!=(800,8) or not np.isfinite(state).all():
        raise ValueError('complete finite canonical x400/p400 source state required')
    r=sample['reduced'];M,B=(np.asarray(r[k]) for k in ('M','B'))
    if M.shape!=(408,408) or B.shape!=M.shape or any(not np.isrealobj(a) or not np.isfinite(a).all() for a in (M,B)):
        raise ValueError('complete actual sourced Legendre matrices required')
    if np.max(abs(M-M.T))>1e-9*max(1.,np.max(abs(M))):
        raise ValueError('same-action mass must be symmetric')
    x,p=state[:400],state[400:];z=np.r_[x,np.eye(8)]
    velocity=np.linalg.solve(M[:400,:400],p-B[:400,:400].T@x-B[400:,:400].T)
    zd=np.r_[velocity,np.zeros((8,8))]
    At=r['At_value_map']@z+r['At_velocity_map']@zd
    legendre=(M@zd+B.T@z)[:400]-p
    gauss=r['Gauss_matrix']@At+r['Gauss_value_row']@z+r['Gauss_velocity_row']@zd
    return dict(canonical_state=state.copy(),velocity=velocity,A_tau=At,
        Legendre_residual=legendre,Gauss_residual=gauss,
        source_canonical_momentum=(M@zd+B.T@z)[400:],
        canonical_state_preserved=True,velocities_transferred_across_birth=False,
        actual_source_value=1.,actual_source_rate=0.)


def true_magnetic_birth_fields(inputs, *, repository):
    """Evaluate the true full220 endpoint and all reached first fields there."""
    from .muon_birth_attached_phase import load_attached_endpoint
    from .muon_primal_electromagnetic_source import retained_phase_source_inputs
    from .muon_electromagnetic_soft_magnetic_source import uniform_magnetic_source_first_jets
    from .muon_trace_enriched_reached_action import enriched_coupled_reached_sample
    from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
    from .muon_parent_retarded_hypercharge import regular_radial_basis
    side=inputs['receipt']['side'];index=-1 if side=='incoming' else 0
    if side not in ('incoming','outgoing'):raise ValueError('actual attached birth arm required')
    bound=retained_phase_source_inputs(inputs['actual_attached_phase_path'],repository=repository)
    endpoint=load_attached_endpoint(bound['receipt']['consumed_paired_endpoint_path'],side=side,repository=repository,
        radial_points=bound['receipt']['radial_points'],cap_points=bound['receipt']['cap_points'])
    raw=endpoint['raw'];rep=endpoint['representation'];angular=retained_full_q_angular_space(repository)
    for key in ('gauge_basis','gauge_radial_basis','wall_trace_map','rho','radial_quadrature'):
        if not np.array_equal(rep[key],inputs['representation'][key]):raise ValueError('endpoint and source response numerical frames differ')
    source=uniform_magnetic_source_first_jets(raw,angular,electric_charge=inputs['electric_charge'])
    params=endpoint['receipt']['action_parameters']
    sample=enriched_coupled_reached_sample(raw,rep,angular,source['Q'],source['Qdot'],nu_squared_action=params['nu_squared_action'])
    result=birth_constitutive_response(sample,inputs['phase']['state'][index])
    state=result['canonical_state'];velocity=result['velocity']
    interior=np.r_[result['A_tau'],state[:320]].T.reshape(8,5,4,20)
    wall=source['Q'].T.reshape(8,5,4,20);wall_rate=source['Qdot'].T.reshape(8,5,4,20)
    # Atdot is not an input to this literal Maxwell/Higgs weak action.
    interior_rate=np.r_[np.zeros_like(result['A_tau']),velocity[:320]].T.reshape(8,5,4,20)
    basis,derivative=regular_radial_basis(rep['rho'],1)
    shape=lambda a:a[:,None,None,None,None]
    fields=dict(raw_fields=raw,first_gauge=shape(basis[:,0])*interior+shape(basis[:,1])*wall,
        first_gauge_rate=shape(basis[:,0])*interior_rate+shape(basis[:,1])*wall_rate,
        first_gauge_radial=shape(derivative[:,0])*interior+shape(derivative[:,1])*wall,
        first_wall_gauge=wall,first_wall_gauge_rate=wall_rate,
        first_H=state[320:400].T.reshape(8,4,20),first_H_rate=velocity[320:400].T.reshape(8,4,20),
        profile=1.,profile_rate=0.,coordinate_time=0.,
        response_time=float(inputs['times'][index]),
        At_rate_zero_slot_scope='literal action does not consume temporal derivative of At; no value of actual At rate claimed',
        primal_fields_from_true_attached_E1=True,canonical_first_state_from_reached_source_cell=True,
        full_physical_endpoint_response_solved=False)
    result.update(fields=fields,source=source,sample=sample,representation=rep,
        endpoint=endpoint,input_hashes={**inputs['input_hashes'],**bound['input_hashes']},
        side=side,action_parameters=params,
        classification='EVALUATED_TRUE_ATTACHED_BIRTH_MAGNETIC_LEGENDRE_GAUSS_APPLICATION',
        scope='new local endpoint action application to reached canonical first state; not a new response trajectory or stationarity claim')
    return result
