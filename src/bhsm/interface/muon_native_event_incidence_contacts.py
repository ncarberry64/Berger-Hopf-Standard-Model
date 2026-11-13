"""Actual endpoint clock/density contacts in the native factor incidence.

This evaluates a coefficient in a CONDITIONAL transmission equation. It
does not assert that the two histories have that transmission, identify a
formed mechanical mode, or turn a stationary native return into a causal
Lorentz return. No native heat or completed Weyl precision work is repeated.
"""
from __future__ import annotations

import numpy as np

from .aether_exact_radial_schur_lift_v15_83 import Jet
from .muon_cutoff_domain_binding import surface_inertia_forms
from .muon_moving_geometric_action import _sqrt
from .muon_stationary_native_reference_load import factor_twojet
from .retained_response.retained_magnetic_application import wall_data


CONTACT_SIZE = 46  # parent theta22, child theta22, parent kappa, child kappa


def endpoint_theta(raw):
    """Retained own+independent coefficients; inherited image is separate."""
    raw = np.asarray(raw, float)
    d = wall_data(raw)
    return np.r_[d['R4'], d['lapse'], d['connection'][0],
                 d['connection'][2:].ravel(), raw[260:264]]


def _scalar_matrix_product(a, value, gradient, hessian):
    """Ordinary, non-Hermitian two-jet product, preserving both orders."""
    av, ag, ah = a.value, a.gradient, a.hessian
    return (av*value,
            ag[:, None, None]*value + av*gradient,
            ah[:, :, None, None]*value
            + ag[:, None, None, None]*gradient[None]
            + ag[None, :, None, None]*gradient[:, None]
            + av*hessian)


def native_density_clock_contact(parent_theta, child_theta,
                                 parent_kappa, child_kappa):
    """Evaluate the complete46 two-jet of the known contact K_density.

    If a physical common-time transmission q_c=T q_p is established,
      v_c=r T v_p + (N_c^-1 Tdot+C_c T-r T C_p)q_p.
    For its KNOWN density factor d=(R_c/R_p)^(3/2),
      K_density=d[(kappa_c-r kappa_p)I+C_c-r C_p].
    Normal-profile ratios, their derivatives, spin/gauge holonomy and
    physical event-source contacts are separate, unassigned operands.
    kappa=3/2 D_tau log R; ambient N is never used for the proper clock.
    """
    p, c = np.asarray(parent_theta, float), np.asarray(child_theta, float)
    if p.shape != (22,) or c.shape != (22,):
        raise ValueError('two labelled native theta22 coordinates required')
    values = np.r_[p, c, float(parent_kappa), float(child_kappa)]
    if not np.isfinite(values).all() or min(p[:2]) <= 0 or min(c[:2]) <= 0:
        raise ValueError('finite timelike endpoint data required')
    eye = np.eye(CONTACT_SIZE)
    v = [Jet.affine(a, eye[i]) for i, a in enumerate(values)]
    r = v[1]/v[23]
    d = _sqrt((v[22]/v[0])**3)
    k = v[45]-r*v[44]
    cp, cc = [], []
    for t, offset, target in ((p, 0, cp), (c, 22, cc)):
        f = factor_twojet(t)
        # Fixed analytic sharp: never re-dagger the continued right factor.
        fv = f['W'][0]-1j*f['Omega'][0]
        fg = np.zeros((CONTACT_SIZE, 18, 18), complex)
        fh = np.zeros((CONTACT_SIZE, CONTACT_SIZE, 18, 18), complex)
        fg[offset:offset+22] = f['W'][1]-1j*f['Omega'][1]
        fh[offset:offset+22, offset:offset+22] = f['W'][2]-1j*f['Omega'][2]
        target.extend((fv, fg, fh))
    rcp = _scalar_matrix_product(r, *cp)
    ident = np.eye(18)
    a = (k.value*ident+cc[0]-rcp[0],
         k.gradient[:, None, None]*ident+cc[1]-rcp[1],
         k.hessian[:, :, None, None]*ident+cc[2]-rcp[2])
    kv, kg, kh = _scalar_matrix_product(d, *a)
    return dict(contact_value18=kv, contact_gradient46=kg,
                contact_Hessian46=kh, parent_C18=cp[0], child_C18=cc[0],
                proper_clock_ratio=float(r.value), density_ratio=float(d.value),
                proper_density_contact=float(k.value),
                coordinate46=values,
                Hessian_symmetry_defect=float(np.max(abs(kh-kh.swapaxes(0, 1)))))


def evaluate_endpoint_incidence_contacts(parent_raw, parent_rate,
                                         child_raw, child_rate, *,
                                         saved_child_density=None):
    """Consume actual endpoint geometry/density in that native-domain row.

    Returns arrays, report. The original common-time factor identity is
    checked on the WHOLE18 coefficient kernel, not a chosen wavefunction.
    Its derivative is a conditional algebraic identity, not event admission.
    """
    p, c = np.asarray(parent_raw, float), np.asarray(child_raw, float)
    pd, cd = np.asarray(parent_rate, float), np.asarray(child_rate, float)
    if any(a.shape != (268,) for a in (p, c, pd, cd)):
        raise ValueError('actual endpoint raw268 and coordinate-time rates required')
    parent = surface_inertia_forms(p[:100])
    kp = float(parent['proper_density_connection'].value)
    logp = 1.5*np.dot(parent['radius'].gradient, pd[:100])/parent['radius'].value
    if saved_child_density is None:
        child = surface_inertia_forms(c[:100])
        kc = float(child['proper_density_connection'].value)
        logc = 1.5*np.dot(child['radius'].gradient, cd[:100])/child['radius'].value
    else:
        saved = saved_child_density
        if not np.array_equal(c, saved['raw268']) or not np.array_equal(cd, saved['rate268']):
            raise ValueError('saved child density has a different history identity')
        kc = float(saved['kappa_value'])
        logc = np.dot(saved['density_gradient100'], cd[:100])/saved['density_value']
    pt, ct = endpoint_theta(p), endpoint_theta(c)
    app = native_density_clock_contact(pt, ct, kp, kc)
    r, d = app['proper_clock_ratio'], app['density_ratio']
    # Independent history-chain derivative of d; no equality of history jets.
    density_dot = d*(logc-logp)
    independent = (density_dot/ct[1]*np.eye(18)
                   + app['child_C18']*d-r*d*app['parent_C18'])
    original_defect = float(np.max(abs(independent-app['contact_value18'])))
    arrays = {key: value for key, value in app.items()
              if isinstance(value, np.ndarray)}
    arrays['independent_original_factor_contact18'] = independent
    if saved_child_density is not None:
        for key in ('kappa_value', 'kappa_gradient100', 'kappa_Hessian100',
                    'density_value', 'density_gradient100', 'density_Hessian100'):
            arrays['reused_child_'+key] = np.asarray(saved_child_density[key])
    report = dict(
        chart='[parent theta22, child theta22, kappa_parent, kappa_child]; neither c nor native lambda',
        equation='K_density=d*((kappa_child-r*kappa_parent)*I+C_child-r*C_parent)',
        conditional_complete_relation='v_child=r*T*v_parent+(Tdot/N_child+C_child*T-r*T*C_parent)*q_parent; physical T and event source NOT assigned',
        density_ratio=d, proper_clock_ratio=r,
        parent_proper_density_connection=kp, child_proper_density_connection=kc,
        density_coordinate_time_derivative=float(density_dot),
        contact_Frobenius=float(np.linalg.norm(app['contact_value18'])),
        contact_max=float(np.max(abs(app['contact_value18']))),
        gradient_norm=float(np.linalg.norm(app['contact_gradient46'])),
        Hessian_norm=float(np.linalg.norm(app['contact_Hessian46'])),
        original_factor_chain_rule_max=original_defect,
        Hessian_symmetry_defect=app['Hessian_symmetry_defect'],
        unknown_normal_profile_ratio_and_derivative_retained=True,
        coefficient_scope='retained own+independent wall data; outgoing inherited connection image and its vertices remain explicit corrections to C_child',
        physical_transmission_or_common_time_flow_established=False,
        Lorentz_to_native_contour_continuation_established=False,
        stationary_return_recomputed=False, native_heat_recomputed=False,
        saved_child_density_and_connection_reused=saved_child_density is not None,
        added_as_action_or_force=False, complete_physical_residual=None)
    return arrays, report
