"""Original E1 wall metric and connection incidence, without choosing its glue.

The represented round-S3 wall fixes a local future clock differential.  It
does not fix an angular isometry, a radial extension, or a bundle initial
identification.  Curvature invariants below are necessary compatibility
equations, not a fermion-trace fit or a sufficient event solution.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import brentq

from .muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients
from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from .muon_parent_retarded_hypercharge import WALL
from .muon_parent_maxwell_full_weak import FIELD_ORDER
from .muon_birth_trace_enriched_action import trace_enriched_radial_basis
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_full_d5_localized_lepton_trace import (
    full_d5_localized_lepton_trace, moving_d5_material_trace_frame,
)
from .muon_holomorphic_normal_geometry import _geometry_variables, _fields, _sqrt
from .aether_exact_radial_schur_lift_v15_83 import Jet


def _real(value, name):
    a = np.asarray(value)
    if np.iscomplexobj(a) and np.any(a.imag != 0):
        raise ValueError('real '+name+' required; complex values are not projected')
    out = np.asarray(a.real if np.iscomplexobj(a) else a, float)
    if not np.isfinite(out).all():
        raise ValueError('finite '+name+' required')
    return out


def original_event_coefficients(history, time, radial_points, *, side, directions=None):
    """Use the recovered original basis and inherited pp-rp+rc application.

    The explicit first slot is the saved common Xi, not an asserted complete
    physical event tangent.  No phase, field or source solve is rerun.
    """
    if side not in ('parent', 'child'):
        raise ValueError('explicit parent or inherited child required')
    raw, _ = history.value(time)
    source, _ = history.source(time)
    operands = history.original_phase_operands
    if side == 'child':
        pair, refs0 = (np.asarray(operands[k]) for k in ('initial_pair', 'reference_pair'))
        if pair.shape != (2, 268) or refs0.shape != pair.shape:
            raise ValueError('original complete inherited parent/reference operands required')
    rho = np.asarray(radial_points, float)
    basis, radial = trace_enriched_radial_basis(history.original_radial_representation, rho)
    B = np.zeros((len(rho), 80, 1, 5, 4))
    Br = np.zeros_like(B)
    for k, label in enumerate(history.original_radial_representation['gauge_labels']):
        f, i, j = FIELD_ORDER.index(label['field']), label['internal'], label['radial']
        B[:, k, 0, f, i] = basis[:, j]
        Br[:, k, 0, f, i] = radial[:, j]
    def geometry_rate(x):
        out = np.zeros_like(x)
        out[:37], out[98] = x[37:74], x[99]
        return out
    if side == 'child':
        parent = affine_geometry_germ(pair[0], time)
        refs = np.array([affine_geometry_germ(x, time) for x in refs0])
    else:
        # These API arguments are never consumed in side='parent': its
        # mechanical profile is solely the raw own-parent profile.  The
        # placeholders do not assign a physical inherited reference.
        parent, refs = raw, np.array([raw, raw])
    if directions is None:
        dx = np.asarray(source)[:, None]
        if side == 'child':
            dp = geometry_rate(pair[0])[:, None]
            dr = np.array([geometry_rate(x)[:, None] for x in refs0])
        else:
            dp, dr = dx, np.array([dx, dx])
    else:
        if set(directions) != {'raw', 'parent', 'references'}:
            raise ValueError('every raw, born-parent and reference direction must be supplied explicitly')
        dx, dp, dr = (np.asarray(directions[k]) for k in ('raw', 'parent', 'references'))
    return d5_trial_stage_coefficients(raw, dx, parent, dp, refs, dr,
        dict(rho=rho, gauge_basis=B, gauge_radial_basis=Br), rho, side=side)


def right_frame_curvature(connection, connection_first):
    """F_jk in the original homogeneous [E_j,E_k]=-2 eps_jki E_i frame.

    The output order is F23,F31,F12.  The independent angular derivatives
    vanish for this represented constant angular component only.
    """
    A, Ax = np.asarray(connection, complex), np.asarray(connection_first, complex)
    if A.ndim != 3 or A.shape[0] != 3 or A.shape[1] != A.shape[2] or Ax.shape != A.shape:
        raise ValueError('three complete same-size connection and first matrices required')
    F, Fx = [], []
    for i, j, k in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        F.append(2*A[i]+A[j]@A[k]-A[k]@A[j])
        Fx.append(2*Ax[i]+Ax[j]@A[k]+A[j]@Ax[k]-Ax[k]@A[j]-A[k]@Ax[j])
    return np.asarray(F), np.asarray(Fx)


def curvature_invariants(curvature, curvature_first):
    """Gauge- and SO3-invariant necessary data, with analytic firsts.

    -Tr(F_i F_j) uses the action's anti-Hermitian real-background pairing.
    No conjugation of the supplied first slot is introduced.
    """
    F, Fx = np.asarray(curvature, complex), np.asarray(curvature_first, complex)
    gram = -np.einsum('iab,jba->ij', F, F)
    gramx = -np.einsum('iab,jba->ij', Fx, F)-np.einsum('iab,jba->ij', F, Fx)
    # Real anti-Hermitian base matrices have real trace pairings. Record
    # floating cancellation separately instead of treating a complex
    # analytic background as a real one.
    anti = max(np.max(abs(F+F.conj().swapaxes(-1, -2))),
        np.max(abs(Fx+Fx.conj().swapaxes(-1, -2))))
    imag = max(np.max(abs(gram.imag)), np.max(abs(gramx.imag)))
    floor = 64*np.finfo(float).eps*max(1., np.linalg.norm(F)**2,
        np.linalg.norm(F)*np.linalg.norm(Fx))
    if anti > floor or imag > floor:
        raise ValueError('real anti-Hermitian curvature background and first required')
    G, Gx = gram.real, gramx.real
    values = np.array([np.trace(G), np.trace(G@G), np.linalg.det(G)])
    # The polynomial determinant differential also works at singular G.
    cofactor = np.column_stack((np.cross(G[:, 1], G[:, 2]),
        np.cross(G[:, 2], G[:, 0]), np.cross(G[:, 0], G[:, 1])))
    first = np.array([np.trace(Gx), 2*np.trace(G@Gx), np.sum(cofactor*Gx)])
    return dict(gram=G, gram_first=Gx, invariants=values, invariants_first=first,
        gram_eigenvalues=np.linalg.eigvalsh(G), real_pairing_imaginary_roundoff=imag,
        antihermitian_roundoff=anti)


def _connection_data(coefficients, generators):
    a = np.asarray(coefficients['gauge_connection_material'])[0]
    ax = np.asarray(coefficients['gauge_connection_material_first'])[0, 0]
    A, Ax = np.einsum('ic,cab->iab', a, generators), np.einsum('ic,cab->iab', ax, generators)
    F, Fx = right_frame_curvature(A[2:], Ax[2:])
    return A, Ax, F, Fx


def temporal_transition_generator(parent_time_connection, child_time_connection,
        parent_clock_differential, *, parent_first, child_first, clock_first):
    """Solve the connection equation for dU, retaining every value of U.

    With F_B: child -> parent, dU+A_c U-kappa U A_p=0.  The returned
    row-major superoperator is dU=L vec(U); it selects no U0 or phase.
    """
    Ap, Ac, Apx, Acx = map(np.asarray, (parent_time_connection, child_time_connection,
        parent_first, child_first))
    if Ap.ndim != 2 or Ap.shape[0] != Ap.shape[1] or any(a.shape != Ap.shape for a in (Ac, Apx, Acx)):
        raise ValueError('complete equal-size temporal connections and firsts required')
    I = np.eye(len(Ap))
    k, kx = parent_clock_differential, clock_first
    return (k*np.kron(I, Ap.T)-np.kron(Ac, I),
        kx*np.kron(I, Ap.T)+k*np.kron(I, Apx.T)-np.kron(Acx, I))


def wall_event_incidence(parent, child):
    """Execute necessary same-E1 wall equations before an angular glue choice.

    Metric matching on the represented round-S3 wall implies kappa=ell_c /
    ell_p and R_p=R_c for an SO3 spatial tangent.  Its angular isometry O,
    spin lift and central phase remain independent unknowns.  The reported
    relative boost is the evaluated factor S_c (...) S_p^-1, not U_R.
    """
    for c in (parent, child):
        if not np.array_equal(np.asarray(c['radial_points']), [WALL]):
            raise ValueError('this application owns only the actual E1 wall, not a radial event extension')
    get = lambda c, k: complex(np.asarray(c[k])[0])
    first = lambda c, k: complex(np.asarray(c[k+'_first'])[0, 0])
    ep, ec = (get(c, 'surface_proper_clock_rate') for c in (parent, child))
    epx, ecx = (first(c, 'surface_proper_clock_rate') for c in (parent, child))
    rp, rc = (get(c, 'radius') for c in (parent, child))
    rpx, rcx = (first(c, 'radius') for c in (parent, child))
    if min(_real([ep, ec], 'future wall clocks')) <= 0:
        raise ValueError('future timelike wall clocks required')
    kappa = ec/ep
    kappax = ecx/ep-ec*epx/ep**2
    up, uc = (get(c, 'material_wall_velocity') for c in (parent, child))
    upx, ucx = (first(c, 'material_wall_velocity') for c in (parent, child))
    full = full_d5_localized_lepton_trace()
    bp = moving_d5_material_trace_frame(up, upx, full_representation=full)
    bc = moving_d5_material_trace_frame(uc, ucx, full_representation=full)
    boost = bc['spin_boost128']@bp['spin_boost_inverse128']
    boostx = (bc['spin_boost_first128']@bp['spin_boost_inverse128']
        +bc['spin_boost128']@bp['spin_boost_inverse_first128'])
    output = dict(material_clock_differential=np.array(kappa),
        material_clock_differential_first=np.array(kappax),
        parent_wall_lapse=np.array(ep), child_wall_lapse=np.array(ec),
        parent_wall_radius=np.array(rp), child_wall_radius=np.array(rc),
        parent_material_velocity=np.array(up), child_material_velocity=np.array(uc),
        clock_metric_row=np.array(ep**2*kappa**2-ec**2),
        clock_metric_first_row=np.array(2*ep*epx*kappa**2+2*ep**2*kappa*kappax-2*ec*ecx),
        spatial_metric_row=(rc**2-rp**2)*np.eye(3),
        spatial_metric_Xi_row=(2*rc*rcx-2*rp*rpx)*np.eye(3),
        parent_spin_boost128=bp['spin_boost128'], child_spin_boost128=bc['spin_boost128'],
        parent_spin_boost_first128=bp['spin_boost_first128'],
        child_spin_boost_first128=bc['spin_boost_first128'],
        child_from_parent_boost_factor128=boost,
        child_from_parent_boost_factor_first128=boostx,
        parent_current_frame_rows=bp['real_wall_Hilbert_current_isometry_rows'],
        child_current_frame_rows=bc['real_wall_Hilbert_current_isometry_rows'])
    reports = {}
    generators_by_name = dict(Higgs2=higgs_u2_real_representation()['complex_generators'],
        SM16=full['unitTr16_gauge_particle'])
    for name, generators in generators_by_name.items():
        Ap, Apx, Fp, Fpx = _connection_data(parent, generators)
        Ac, Acx, Fc, Fcx = _connection_data(child, generators)
        ip, ic = curvature_invariants(Fp, Fpx), curvature_invariants(Fc, Fcx)
        L, Lx = temporal_transition_generator(Ap[0], Ac[0], kappa,
            parent_first=Apx[0], child_first=Acx[0], clock_first=kappax)
        prefix = name+'_'
        output.update({prefix+k: v for k, v in dict(parent_connection=Ap,
            child_connection=Ac, parent_connection_first=Apx, child_connection_first=Acx,
            parent_curvature=Fp, child_curvature=Fc, parent_curvature_first=Fpx,
            child_curvature_first=Fcx, temporal_transition_generator=L,
            temporal_transition_generator_first=Lx,
            curvature_invariant_rows=ic['invariants']-ip['invariants'],
            curvature_invariant_Xi_rows=ic['invariants_first']-ip['invariants_first'],
            parent_curvature_gram=ip['gram'], child_curvature_gram=ic['gram'],
            curvature_gram_spectral_rows=ic['gram_eigenvalues']-ip['gram_eigenvalues']).items()})
        reports[name] = dict(curvature_invariant_max=float(np.max(abs(ic['invariants']-ip['invariants']))),
            curvature_invariant_Xi_max=float(np.max(abs(ic['invariants_first']-ip['invariants_first']))),
            Gram_spectral_max=float(np.max(abs(ic['gram_eigenvalues']-ip['gram_eigenvalues']))),
            temporal_transition_generator_norm=float(np.linalg.norm(L)))
    report = dict(classification='EVALUATED_NECESSARY_E1_WALL_METRIC_AND_BUNDLE_INCIDENCE',
        clock_equation='ell_parent^2*kappa^2-ell_child^2=0; kappa>0',
        clock_differential_child_to_parent=float(kappa.real),
        clock_residual=float(abs(output['clock_metric_row'])),
        clock_Xi_residual=float(abs(output['clock_metric_first_row'])),
        spatial_metric_max=float(np.max(abs(output['spatial_metric_row']))),
        spatial_metric_Xi_max=float(np.max(abs(output['spatial_metric_Xi_row']))),
        curvature=reports,
        connection_equation='dU+A_child U-kappa U A_parent=0 along the mapped material time',
        spatial_curvature_equation='F_child,ij U=U (F_B^* F_parent),ij',
        spin_factorization='U_ambient=S_child R_spatial/gauge S_parent^-1; middle lift remains unknown',
        relative_boost_departure_from_identity=float(np.max(abs(boost-np.eye(128)))),
        angular_base_map_selected=False,angular_SO3_tangent_selected=False,
        radial_event_extension_selected=False,physical_bundle_initial_map_selected=False,
        physical_event_solved=False,physical_admission=False,
        derivative_scope='saved common Xi at fixed E1 wall only; point/base, normal-profile and state variations remain independent',
        normal_profile_normalization=None,
        density_scope='spatial wall metric only; no Cauchy half-density or unknown radial Jacobian is inferred',
        curvature_scope='evaluated SU2/U1 homogeneous angular component; complementary angular/strong fields are not defaulted to zero')
    return output, report


def radial_cauchy_geometry(raw, raw_first, rho):
    """Original R,C and their exact radial two-jet at one actual point.

    A new independent Jet coordinate is the original material rho.  This
    differentiates the original trigonometric geometry, not sampled values.
    The supplied coefficient direction is independent of point motion.
    """
    x, dx = np.asarray(raw, complex), np.asarray(raw_first, complex)
    if x.shape != (268,) or dx.shape != x.shape:
        raise ValueError('complete same-background raw268 and coefficient source required')
    if not 0 < rho <= WALL:
        raise ValueError('original positive material radial point required')
    q, v, m, _, _, wall, _ = _geometry_variables(x[:100])
    def lift(a):
        d = np.zeros(101, complex); d[:100] = a.gradient
        h = np.zeros((101, 101), complex); h[:100, :100] = a.hessian
        return Jet(a.value, d, h)
    q, v, m = ([lift(a) for a in group] for group in (q, v, m))
    wall = lift(wall)
    direction = np.zeros(101); direction[-1] = 1
    r = Jet.affine(complex(rho), direction)
    f = _fields(12, q, v, m, r*wall/WALL)
    R = f['A']*f['B']/_sqrt(f['A']**2+f['B']**2)
    C = f['C']*wall/WALL
    out = dict(radius=R.value, radial_coframe=C.value,
        radius_radial=R.gradient[-1], radius_radial_second=R.hessian[-1, -1],
        radial_coframe_radial=C.gradient[-1],
        radius_first=R.gradient[:100]@dx[:100],
        radius_radial_first=R.hessian[-1, :100]@dx[:100],
        radial_coframe_first=C.gradient[:100]@dx[:100])
    return {k: complex(v) for k, v in out.items()}


def radial_cauchy_incidence_point(parent_raw, parent_first, child_raw, child_first,
        child_rho, *, parent_bounds, child_rho_first):
    """Test an extra radial-isometric-extension candidate, not the wall map.

    R_parent(f)=R_child determines a radial candidate without a fermion
    residual. Its f'=R_child,r/R_parent,r would separately have to satisfy
    C_parent(f) f'-C_child=0 IF a radial bulk isometry were required.
    The original wall/worldvolume glue does not require such an extension;
    failure is an extension diagnostic and is not a formation constraint.
    No candidate is evaluated outside the SAVED parent-response interval.
    This does not determine the angular map, time incidence or its spin lift.
    """
    a, b = sorted(map(float, parent_bounds))
    if a <= 0 or b > WALL or a == b:
        raise ValueError('explicit nonempty original saved parent interval required')
    c = radial_cauchy_geometry(child_raw, child_first, float(child_rho))
    child_motion = complex(child_rho_first)
    target = _real(c['radius'], 'child radius').item()
    def geometry(rho):
        return radial_cauchy_geometry(parent_raw, parent_first, rho)
    def equation(rho):
        return _real(geometry(rho)['radius'], 'parent radius').item()-target
    ends = np.array([equation(a), equation(b)])
    report = dict(classification='CONDITIONAL_RADIAL_ISOMETRIC_EXTENSION_DIAGNOSTIC_ONLY',
        equation='R_parent(0,f(rho_child))-R_child(0,rho_child)=0',
        independent_equation='C_parent(0,f)*f_prime-C_child(0,rho_child)=0',
        parent_response_bounds=[a, b], child_rho=float(child_rho),
        bracket_radius_rows=ends.tolist(), root_in_saved_parent_domain=False,
        full_event_map_selected=False, angular_map_selected=False,
        radial_bulk_isometry_required_by_original_wall_action=False,
        diagnostic_added_to_formation_constraints=False,
        physical_admission=False)
    arrays = dict(child_rho=np.array(child_rho), child_rho_first=np.array(child_motion),
        bracket_radius_rows=ends)
    if np.prod(np.sign(ends)) > 0:
        report['remaining_equation'] = 'radius incidence has no bracketed root in the saved response interval; no extrapolation performed'
        return arrays, report
    root = brentq(equation, a, b, xtol=np.spacing(WALL), rtol=4*np.finfo(float).eps)
    p = geometry(root)
    pr, cr = p['radius_radial'], c['radius_radial']
    if abs(pr) < 1e-12:
        raise ValueError('radius incidence is not a simple root at this precision')
    fp = cr/pr
    rootx = (c['radius_first']+cr*child_motion-p['radius_first'])/pr
    # Moving child evaluation occurs once in total child derivatives; the
    # implicit parent point motion then enters its own original geometry.
    crx = c['radius_radial_first']+c['radius_radial_second']*child_motion
    prx = p['radius_radial_first']+p['radius_radial_second']*rootx
    fpx = (crx-fp*prx)/pr
    cp, cc = p['radial_coframe'], c['radial_coframe']
    cpx = p['radial_coframe_first']+p['radial_coframe_radial']*rootx
    ccx = c['radial_coframe_first']+c['radial_coframe_radial']*child_motion
    metric_row = cp*fp-cc
    metric_first = cpx*fp+cp*fpx-ccx
    radius_first_row = p['radius_first']+pr*rootx-c['radius_first']-cr*child_motion
    # A numerical same-coordinate comparison is recorded only as a prior
    # residual; it is never selected as the physical map.
    before = geometry(float(child_rho)) if a <= child_rho <= b else None
    arrays.update(parent_rho=np.array(root), parent_rho_first=np.array(rootx),
        radial_tangent=np.array(fp), radial_tangent_first=np.array(fpx),
        radius_row=np.array(equation(root)), radius_first_row=np.array(radius_first_row),
        radial_metric_row=np.array(metric_row), radial_metric_first_row=np.array(metric_first),
        parent_radius_radial=np.array(pr), child_radius_radial=np.array(cr),
        parent_radius_radial_second=np.array(p['radius_radial_second']),
        child_radius_radial_second=np.array(c['radius_radial_second']),
        parent_radial_coframe=np.array(cp), child_radial_coframe=np.array(cc))
    if before is not None:
        arrays.update(same_coordinate_radius_row=np.array(before['radius']-c['radius']),
            same_coordinate_radial_metric_row=np.array(before['radial_coframe']-cc))
    report.update(root_in_saved_parent_domain=True, parent_rho=float(root),
        radius_residual=float(abs(equation(root))), radius_first_residual=float(abs(radius_first_row)),
        radial_metric_residual=float(abs(metric_row)), radial_metric_first_residual=float(abs(metric_first)),
        radial_tangent=float(_real(fp, 'radial tangent')), root_simple_in_this_finite_application=True,
        derivative_scope='supplied coefficient directions plus explicit child evaluation motion once; independent time/angular incidence and remaining physical sources unresolved',
        remaining_equation='radial-isometric extension would require C_parent(f)*f_prime-C_child=0; this is not imposed by the original wall glue',
        error_scope='finite binary64 radius root and exact finite-basis geometry jets; root conditioning, bulk response errors and continuum error are separate')
    return arrays, report
