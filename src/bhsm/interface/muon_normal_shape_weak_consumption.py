"""Consume both moving-normal weak covectors, including temporal returns."""
import numpy as np


def integrate_shape_rate_contact(source,gradient,gradient_coordinate_first,
        shape_coefficient_gradient,shape_coefficient_Hessian,coordinate_rate,
        *,normal_position,normal_velocity):
    """D_t(g_rate) is computed, never presumed equal to the embedding term.

    The remaining term (L_s-D_t Pi_s)*psi*D_eta a retains the actual
    canonical equation residual. Area coefficients need not separately
    satisfy that equation along a gammaNone base.
    """
    G=np.asarray(gradient,complex);Gt=np.asarray(gradient_coordinate_first,complex)
    da=np.asarray(shape_coefficient_gradient,complex);dd=np.asarray(shape_coefficient_Hessian,complex)
    rate=np.asarray(coordinate_rate,complex);psi=source['normal_amplitude'].item();pt=source['normal_amplitude_coordinate_first'].item()
    s=int(normal_position);v=int(normal_velocity)
    if Gt.shape!=G.shape or da.shape!=G.shape or dd.shape!=(len(G),len(G)) or rate.shape!=G.shape:
        raise ValueError('complete literal state/rate/clock shape contact required')
    Jt=(Gt[v]*psi+G[v]*pt)*da+G[v]*psi*(dd@rate)
    bulk=source['full_weak_state_source']-Jt
    equation=(G[s]-Gt[v])*psi*da
    return dict(weak_phase_rate_source_time_first=Jt,integrated_weak_bulk_source=bulk,
        original_normal_canonical_equation=np.array(Gt[v]-G[s]),
        canonical_equation_shape_contact=equation,
        integrated_minus_ordinary_and_equation=bulk-source['ordinary_action_shape_source']-equation,
        temporal_boundary_source_covector=source['full_weak_phase_rate_source'].copy(),
        rate_contact_consumed_not_dropped=True)


def weak_shape_action_pairing(midpoint_sources,midpoint_directions,steps,
        initial_source,initial_direction,final_source,final_direction,
        corner_left_sources,corner_left_directions,corner_right_sources,corner_right_directions):
    """Execute sum h g_bulk.delta plus all temporal/conormal rate returns.

    No endpoint or coefficient-corner term is silently absent. A declared
    continuous true-face germ is provided on both sides to prove its zero
    corner. Natural responses are read, rather than constrained to zero.
    """
    if len(midpoint_sources)!=len(midpoint_directions)or len(steps)!=len(midpoint_sources):
        raise ValueError('every actual weak cell source/direction/clock required')
    initial=np.asarray(initial_source)@np.asarray(initial_direction);final=np.asarray(final_source)@np.asarray(final_direction)
    bulk=sum(h*(np.asarray(g)@np.asarray(u))for h,g,u in zip(steps,midpoint_sources,midpoint_directions))
    if not (len(corner_left_sources)==len(corner_left_directions)==len(corner_right_sources)==len(corner_right_directions)):
        raise ValueError('all left/right temporal coefficient/source corners required')
    corner=sum((np.asarray(l)@np.asarray(u)-np.asarray(r)@np.asarray(v))for l,u,r,v in
        zip(corner_left_sources,corner_left_directions,corner_right_sources,corner_right_directions))if len(corner_left_sources)else np.zeros_like(bulk)
    return dict(bulk_shape_action_pairing=bulk,initial_rate_contact=initial,final_rate_contact=final,
        coefficient_corner_rate_contact=corner,complete_shape_action_pairing=bulk+final-initial+corner)
