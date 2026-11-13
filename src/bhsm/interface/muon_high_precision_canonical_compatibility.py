"""Original-coordinate constitutive Newton with a literal precise gradient.

Only the fixed-position velocity/algebraic gradient is evaluated at higher
precision.  The original signed-action Hessian and position force remain
the independently checked binary applications.  No quadratic re-elimination
or transformed position force is used by this additive consumer.
"""
from __future__ import annotations
import numpy as np
from .muon_holomorphic_child_action import holomorphic_inherited_child_action
from .muon_high_precision_constitutive_gradient import high_precision_original_constitutive_gradient


def high_precision_original_constitutive_action(raw, time, initial_pair,
        reference_pair, representation, *, decimal_precision=60,
        nu_squared_action=4, surface_gamma=None):
    parameters=dict(nu_squared_action=nu_squared_action,surface_gamma=surface_gamma)
    original=holomorphic_inherited_child_action(raw,time,initial_pair,
        reference_pair,representation,**parameters)
    precise=high_precision_original_constitutive_gradient(raw,time,initial_pair,
        reference_pair,representation,decimal_precision=decimal_precision,**parameters)
    gradient=np.asarray(original['gradient'],complex).copy()
    n=len(gradient)-len(precise['constitutive_gradient'])
    gradient[n:]=precise['constitutive_gradient']
    result=dict(original)
    result.update(gradient=gradient,value=precise['value'],
        canonical_momentum=gradient[n:2*n],
        binary_original_gradient=np.asarray(original['gradient'],complex).copy(),
        high_precision_gradient_decimal_strings=precise['gradient_decimal_strings'],
        original_tail_gradient_precision_difference=gradient[n:]-original['gradient'][n:],
        constitutive_gradient_decimal_precision=int(decimal_precision),
        original_position_force_and_Hessian_retained=True,
        positional_response_and_inherited_coefficients_scope=precise['positional_response_and_inherited_coefficients_scope'])
    return result


def precise_constitutive_directional_control(eta,direction,evaluate,*,
        position_count=106,steps=(2e-4,2e-3)):
    """Independent precise-gradient differences versus the original Hessian.

    Original fixed-position directions are supplied explicitly.  Every
    derivative row is retained, including the weak rate and multiplier
    rows; neither the error nor the chosen steps are enclosure claims.
    """
    eta=np.asarray(eta,complex);d=np.asarray(direction,complex)
    n=position_count
    if d.shape!=(len(eta)-n,):raise ValueError('all original velocity/algebraic directions required')
    at=evaluate(eta);exact=at['hessian'][n:,n:]@d;records=[];arrays={
        'original_master':eta,'original_tail_direction':d,
        'original_Hessian_tail_action':exact,'original_action_Hessian':at['hessian']}
    for index,h in enumerate(steps):
        plus=eta.copy();minus=eta.copy();plus[n:]+=h*d;minus[n:]-=h*d
        gp=evaluate(plus)['gradient'][n:];gm=evaluate(minus)['gradient'][n:]
        fd=(gp-gm)/(2*h);difference=fd-exact
        records.append(dict(step=float(h),absolute_difference_max=float(np.max(abs(difference))),
            absolute_difference_norm=float(np.linalg.norm(difference)),
            relative_difference_norm=float(np.linalg.norm(difference)/max(np.linalg.norm(exact),np.finfo(float).tiny)),
            original_Hessian_action_norm=float(np.linalg.norm(exact))))
        arrays.update({f'plus_gradient_{index}':gp,f'minus_gradient_{index}':gm,
            f'difference_quotient_{index}':fd,f'difference_from_original_Hessian_{index}':difference})
    return dict(records=records,arrays=arrays,application=at,
        higher_precision_Hessian_or_outward_derivative_bound=False)
