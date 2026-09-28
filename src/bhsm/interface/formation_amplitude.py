"""Contractions for the existing endpoint-labelled formation amplitude.

Amplitude is the incoming signed descriptor at the moving birth endpoint.
These contractions do not select its value or solve the joint saddle.
"""
from flint import arb, arb_mat
from bhsm.interface.gate7_current_action import checked


def orbit_cut_endpoint(*, density, momentum, velocity, state_amplitude,
                       coordinate_time_amplitude, state_source, time_source):
    """Lower-endpoint contribution and the temporal tangential Ward replay.

    The endpoint action term is -pi*dq-(L-pi*v)*dt. For a cut along the
    same orbit dq=v*dt, this equals -L*dt; the integrated temporal source
    contracted with the orbit direction is identically zero. This does
    NOT discard constraint derivatives of another, non-tangential KKT lift.
    """
    q = momentum.nrows()
    checked(momentum, q, 1, 'momentum')
    checked(velocity, q, 1, 'velocity')
    checked(state_amplitude, state_source.nrows(), 1, 'birth state direction')
    checked(state_source, state_amplitude.nrows(), 1, 'state source')
    if state_amplitude.nrows() < q:
        raise ValueError('state must contain the configuration coordinates')
    dt = arb(coordinate_time_amplitude)
    dq = arb_mat(q, 1, state_amplitude.entries()[:q])
    pi_v = (momentum.transpose()*velocity)[0, 0]
    configuration = -(momentum.transpose()*dq)[0, 0]
    clock = -(arb(density)-pi_v)*dt
    direct = -arb(density)*dt
    ward = (state_source.transpose()*state_amplitude)[0, 0]+arb(time_source)*dt
    return dict(configuration=configuration, clock=clock,
                endpoint=configuration+clock, leibniz=direct,
                kinematic_replay=dq-velocity*dt,
                endpoint_replay=arb_mat([[configuration+clock-direct]]),
                temporal_tangential_replay=arb_mat([[ward]]))


def dirichlet_birth_heat_pressure(*, eigenvalues, squared_conormals,
                                  signed_weights, heat_length, tail):
    """Full-domain boundary spectral contraction, with an explicit tail.

    For an extension dT>0 at the zero-source birth reference, d lambda is
    -|partial_tau u(birth)|^2*dT for L2-normalized coupled-domain modes.
    Thus d Gamma_heat/dT = -1/2 sum w exp(-ell^2 lambda)/lambda * |u'|^2.
    Product-Dirac conormals equal u' on the Dirichlet birth trace.
    Neither local incoming modes nor an arbitrary far cutoff own the input.
    A maximal-domain realization may instead supply the equivalent relative
    spectral-measure contraction; this finite-list kernel is not that oracle.
    """
    if tail is None:
        raise ValueError('explicit full-domain graded tail enclosure required')
    if not (len(eigenvalues) == len(squared_conormals) == len(signed_weights)):
        raise ValueError('one common graded boundary spectral family required')
    ell = arb(heat_length)
    if not ell > 0 or not arb(tail).is_finite():
        raise ValueError('positive heat length and finite tail required')
    pressure = arb(0)
    for value, norm, weight in zip(eigenvalues, squared_conormals, signed_weights):
        value, norm, weight = map(arb, (value, norm, weight))
        if not value > 0 or not norm >= 0 or not weight.is_finite():
            raise ValueError('positive quotient spectrum and nonnegative conormal norm required')
        pressure -= weight*(-ell*ell*value).exp()*norm/(2*value)
    return pressure+arb(tail)
