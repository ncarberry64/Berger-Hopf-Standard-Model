"""Apply the owned anchored reciprocal-join response on a moving material chart.

Owners: ``ae3_reciprocal_join_localization.interface_variation_ledger`` and
``theory/ae3_reciprocal_join_localization_enclosure.md``.  The earlier
``aether_eta_sigma_response_constraint_v15_40`` supplies the literal weight
W(f)=sin(f)^2 cos(f)^2 and its derivative.  No weight functional is selected
here.  The caller supplies the pullback of proper orbit length dℓ=a dχ and
all its jets.  The retained v15.40 coordinate-measure chart is evaluated by
supplying a=1; its later covariant promotion requires the actual measure and
derivative pullbacks, rather than a silent replacement of Z by ∫C W dχ.

The routines apply trial directions, including metric/measure motion.  They
do not select the physical formation mode, impose full bulk stationarity,
or identify a common coordinate advection with formation.  Composite
trapezoidal quadrature is a numerical representation, not an error bound.
"""

from __future__ import annotations

import numpy as np


def _grid(coordinate):
    x = np.asarray(coordinate, dtype=float)
    if x.ndim != 1 or x.size < 2 or not np.all(np.isfinite(x)):
        raise ValueError("a finite one-dimensional orbit grid is required")
    if np.any(np.diff(x) <= 0):
        raise ValueError("the orbit grid must be strictly increasing")
    return x


def _field(value, shape, name):
    result = np.asarray(value, dtype=float)
    if result.shape == ():
        result = np.full(shape, float(result))
    if result.shape != shape or not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite and have shape {shape}")
    return result


def _cumulative(coordinate, density):
    """Use one quadrature for the cumulative integral and its total."""
    dx = np.diff(coordinate).reshape((-1,) + (1,) * (density.ndim - 1))
    cells = 0.5 * (density[1:] + density[:-1]) * dx
    return np.concatenate((np.zeros_like(density[:1]), np.cumsum(cells, axis=0)))


def reciprocal_weight_jet(f, f_x, f_y, f_xy):
    """Literal W, W_x, W_y, W_xy; derivatives rather than Taylor coefficients."""
    f = np.asarray(f, dtype=float)
    if not np.all(np.isfinite(f)):
        raise ValueError("f must be finite")
    fx, fy, fxy = [_field(v, f.shape, name) for v, name in
                   ((f_x, "f_x"), (f_y, "f_y"), (f_xy, "f_xy"))]
    weight = np.sin(f) ** 2 * np.cos(f) ** 2
    first = 0.5 * np.sin(4 * f)
    second = 2 * np.cos(4 * f)
    return dict(W=weight, W_x=first * fx, W_y=first * fy,
                W_xy=first * fxy + second * fx * fy)


def identity_material_trial_jet(coordinate, *, normal_velocity, C_star):
    """Exact order-two response trial preserving both material wall traces.

    On the retained full identity interval [0,π/2], dχ normalization, take
    f_s(χ)=χ+s h(χ), χ_wall(s)=π/4+s k with k=normal_velocity/C_star.
    h=a1 sin(2χ)+a3 sin(6χ), a1=−21k/16, a3=−5k/16.  These coefficients
    solve δf_wall=0 and δσ_wall=0 simultaneously.  Both endpoint eta anchors
    are preserved.  Geometry is held Eulerian fixed: this is a relative eta
    trial, not a common coordinate advection or a selected formation mode.

    The formulas retain the generally nonzero Z_ss and normalized σ_ss.
    The two material wall traces vanish through order two; affine f and wall
    are not asserted to solve higher orders.  Normal velocity is normalized
    only at the base by the supplied physical C_star, not by the full inertia.
    Here velocity means dX/ds for the variation source, not the phase flow or
    a prescribed physical-clock D_tau X.
    """
    x = np.asarray(coordinate, dtype=float)
    if (not np.all(np.isfinite(x)) or np.any(x < 0) or np.any(x > np.pi / 2)
            or not np.isfinite(normal_velocity) or not np.isfinite(C_star) or C_star <= 0):
        raise ValueError("finite identity-interval coordinates, velocity and positive C_star required")
    k = float(normal_velocity / C_star)
    a1, a3 = -21 * k / 16, -5 * k / 16
    h = a1 * np.sin(2 * x) + a3 * np.sin(6 * x)
    w = np.sin(x) ** 2 * np.cos(x) ** 2
    wx = 0.5 * np.sin(4 * x) * h
    wxx = 2 * np.cos(4 * x) * h**2
    z = np.pi / 16
    sigma = -0.5 + 2 * x / np.pi - np.sin(4 * x) / (2 * np.pi)
    bx = (a1 * (np.sin(2 * x) / 8 - np.sin(6 * x) / 24)
          + a3 * (np.sin(2 * x) / 8 - np.sin(10 * x) / 40))
    # Fourier coefficients of 2*cos(4χ)*h²: no density or profile is fitted.
    coeff = {0: -a1**2 / 2 + a1 * a3,
             4: a1**2 + a3**2 - a1 * a3,
             8: -(a1**2 + a3**2) / 2 + a1 * a3,
             12: -a1 * a3, 16: -a3**2 / 2}
    bxx = coeff[0] * x + sum(c * np.sin(n * x) / n for n, c in coeff.items() if n)
    zxx = coeff[0] * np.pi / 2
    sx = bx / z
    sxx = bxx / z - (sigma + 0.5) * zxx / z
    sigma_wall_x = 8 / np.pi * (a1 / 3 + a3 / 5)
    sigma_wall_rate = 4 / np.pi
    return dict(f=x, f_x=h, f_xx=np.zeros_like(x), W=w, W_x=wx, W_xx=wxx,
                Z=float(z), Z_x=0.0, Z_xx=float(zxx),
                sigma=sigma, sigma_x=sx, sigma_xx=sxx,
                sigma_coordinate_gradient=w / z,
                sigma_coordinate_gradient_x=wx / z,
                sigma_coordinate_gradient_xx=wxx / z - w * zxx / z**2,
                localization=1 - 4 * sigma**2,
                localization_x=-8 * sigma * sx,
                localization_xx=-8 * (sx**2 + sigma * sxx),
                eta_trial_coefficients=np.array([a1, a3]),
                wall_coordinate=np.pi / 4, wall_coordinate_x=k, wall_coordinate_xx=0.0,
                base_proper_normal_velocity=float(normal_velocity),
                wall_sigma_eulerian_x=float(sigma_wall_x),
                wall_sigma_embedding_x=float(sigma_wall_rate * k),
                wall_eta_material_x=float(a1 - a3 + k),
                wall_sigma_material_x=float(sigma_wall_x + sigma_wall_rate * k),
                # Reflection parity yields σ_xx(wall)=0; h'(wall), σ_x'(wall)
                # and σ0''(wall) are also zero, so both material second rows vanish.
                wall_eta_material_xx=0.0, wall_sigma_material_xx=0.0,
                sufficient_monotone_neighborhood_abs_parameter_times_k=2 / 9)


def anchored_response_jet(coordinate, f, orbit_length_density, *,
                          f_x, f_y, f_xy,
                          length_log_x, length_log_y, length_log_xy):
    """Apply σ=B/Z−1/2 and its first/mixed jets with the fixed left anchor.

    B(χ)=∫_(Q−)^χ W dℓ, Z=B(Q+).  The integration interval is a common fixed
    pullback: endpoint/embedding motion must be represented in the supplied
    fields and length jets before this call.  ``length_log_xy`` is δ_xy log a,
    so a_xy=a*(length_log_xy+length_log_x*length_log_y).  μ_Q is deliberately
    absent from Z: the owned normalization is ∫W dℓ, not ∫μ_Q W dℓ.
    """
    x = _grid(coordinate)
    f = _field(f, x.shape, "f")
    a = _field(orbit_length_density, x.shape, "orbit_length_density")
    if np.any(a <= 0):
        raise ValueError("proper orbit length density must be positive")
    mx, my, mxy = [_field(v, x.shape, name) for v, name in
                  ((length_log_x, "length_log_x"),
                   (length_log_y, "length_log_y"),
                   (length_log_xy, "length_log_xy"))]
    w = reciprocal_weight_jet(f, f_x, f_y, f_xy)
    j = a * w["W"]
    jx = a * (w["W_x"] + w["W"] * mx)
    jy = a * (w["W_y"] + w["W"] * my)
    jxy = a * (w["W_xy"] + w["W_x"] * my + w["W_y"] * mx
               + w["W"] * (mxy + mx * my))
    b, bx, by, bxy = [_cumulative(x, v) for v in (j, jx, jy, jxy)]
    z, zx, zy, zxy = [float(v[-1]) for v in (b, bx, by, bxy)]
    if z <= 0:
        raise ValueError("the owned join normalization must be positive")
    sigma = b / z - 0.5
    sx = bx / z - b * zx / z**2
    sy = by / z - b * zy / z**2
    sxy = (bxy / z - (bx * zy + by * zx + b * zxy) / z**2
           + 2 * b * zx * zy / z**3)
    rate = w["W"] / z
    rate_x = w["W_x"] / z - w["W"] * zx / z**2
    rate_y = w["W_y"] / z - w["W"] * zy / z**2
    rate_xy = (w["W_xy"] / z
               - (w["W_x"] * zy + w["W_y"] * zx + w["W"] * zxy) / z**2
               + 2 * w["W"] * zx * zy / z**3)
    # Differentiating ∂χσ=a W/Z includes the metric-normal term −m Dℓσ
    # when converted back to Dℓ; it is not a second response contribution.
    return dict(coordinate=x, orbit_length_density=a, **w,
                Z=z, Z_x=zx, Z_y=zy, Z_xy=zxy,
                sigma=sigma, sigma_x=sx, sigma_y=sy, sigma_xy=sxy,
                D_ell_sigma=rate, D_ell_sigma_x=rate_x,
                D_ell_sigma_y=rate_y, D_ell_sigma_xy=rate_xy,
                coordinate_sigma_gradient=a * rate,
                coordinate_sigma_gradient_x=a * (rate_x + mx * rate),
                coordinate_sigma_gradient_y=a * (rate_y + my * rate),
                coordinate_sigma_gradient_xy=a *
                (rate_xy + mx * rate_y + my * rate_x + (mxy + mx * my) * rate))


def apply_anchored_trials(coordinate, f, orbit_length_density, *,
                          f_trials, length_log_trials):
    """Apply a supplied finite trial basis to the response without selecting ψ.

    Columns are trial directions on the common anchored domain.  Their
    response tangents have zero endpoint values.  These columns certify only
    the response constraint; all other coupled constraints remain applicable.
    """
    x = _grid(coordinate)
    f = _field(f, x.shape, "f")
    a = _field(orbit_length_density, x.shape, "orbit_length_density")
    if np.any(a <= 0):
        raise ValueError("proper orbit length density must be positive")
    df = np.asarray(f_trials, dtype=float)
    dm = np.asarray(length_log_trials, dtype=float)
    if (df.ndim != 2 or df.shape[0] != x.size or dm.shape != df.shape
            or not np.all(np.isfinite(df)) or not np.all(np.isfinite(dm))):
        raise ValueError("finite N×k eta and log-length trial arrays are required")
    w = np.sin(f) ** 2 * np.cos(f) ** 2
    dw = 0.5 * np.sin(4 * f)[:, None] * df
    b = _cumulative(x, a * w)
    z = float(b[-1])
    if z <= 0:
        raise ValueError("the owned join normalization must be positive")
    db = _cumulative(x, a[:, None] * (dw + w[:, None] * dm))
    dz = db[-1]
    return dict(sigma=b / z - 0.5, Z=z, W=w,
                sigma_trials=db / z - b[:, None] * dz / z**2,
                Z_trials=dz, W_trials=dw,
                D_ell_sigma=w / z,
                D_ell_sigma_trials=dw / z - w[:, None] * dz / z**2)


def proper_length_material_trial(coordinate, C_profile, *, C_star, normal_velocity):
    """Apply the promoted proper-length response to an actual supplied C profile.

    This is a separate candidate representation, not replacement of the
    retained coordinate-normalized σ.  On a supplied smooth reflection-even
    C(χ)>0 and f0=χ, let J_j=∫_0^(π/4) C*.5*sin(4χ)*sin(jχ)dχ.  The two
    response/eta trace rows determine a1−a3=−v/C_star and
    a1*J_2+a3*J_6=−v/4.  The orbit metric is fixed Eulerian while eta varies.
    Z, σ and their second jets are evaluated with dℓ=C dχ, including Z_ss.

    A full anchored grid containing the wall is required.  Trapezoidal
    refinement measures numerical sensitivity; it is not a rigorous bound.
    Reflection symmetry is checked on supplied samples, not proved between
    them.  No physical mechanical mode or stationary multiplier is selected.
    ``normal_velocity`` is dX/ds of this source chart, not phase-flow velocity.
    """
    x = _grid(coordinate)
    c = _field(C_profile, x.shape, "C_profile")
    if (np.any(c <= 0) or not np.isfinite(C_star) or C_star <= 0
            or not np.isfinite(normal_velocity)):
        raise ValueError("positive finite metric coefficients and finite velocity required")
    if (abs(x[0]) > 1e-14 or abs(x[-1] - np.pi / 2) > 1e-14
            or not np.allclose(x + x[::-1], np.pi / 2, rtol=0, atol=1e-13)
            or not np.allclose(c, c[::-1], rtol=1e-12, atol=0)):
        raise ValueError("the full anchored reflection-symmetric profile is required")
    locations = np.flatnonzero(np.abs(x - np.pi / 4) <= 1e-14)
    if len(locations) != 1:
        raise ValueError("the grid must contain exactly one material wall node")
    wall = int(locations[0])
    if not np.isclose(c[wall], C_star, rtol=1e-12, atol=0):
        raise ValueError("C_star must be the supplied profile value at the wall")
    left = slice(0, wall + 1)
    common = 0.5 * c[left] * np.sin(4 * x[left])
    j1 = float(_cumulative(x[left], common * np.sin(2 * x[left]))[-1])
    j3 = float(_cumulative(x[left], common * np.sin(6 * x[left]))[-1])
    if abs(j1 + j3) <= np.finfo(float).eps * max(abs(j1), abs(j3)):
        raise ValueError("the two material trace rows do not determine this trial")
    k = float(normal_velocity / C_star)
    a1, a3 = np.linalg.solve(np.array([[1., -1.], [j1, j3]]),
                             np.array([-k, -normal_velocity / 4]))
    h = a1 * np.sin(2 * x) + a3 * np.sin(6 * x)
    response = anchored_response_jet(
        x, x, c, f_x=h, f_y=h, f_xy=0,
        length_log_x=0, length_log_y=0, length_log_xy=0)
    w, wx, wxx = response['W'], response['W_x'], response['W_xy']
    z, zx, zxx = response['Z'], response['Z_x'], response['Z_xy']
    gradients = (response['coordinate_sigma_gradient'],
                 response['coordinate_sigma_gradient_x'],
                 response['coordinate_sigma_gradient_xy'])
    rows = np.array([
        gradients[0] / c - w / z,
        gradients[1] / c - wx / z + w * zx / z**2,
        gradients[2] / c - wxx / z + (2 * wx * zx + w * zxx) / z**2
        - 2 * w * zx**2 / z**3])
    hp_wall = 2 * a1 * np.cos(np.pi / 2) + 6 * a3 * np.cos(3 * np.pi / 2)
    # C and W are reflection-even, so ∂χ(C W/Z)=0 at the wall.  The
    # supplied affine wall acceleration is zero; do not infer inertia jets.
    sigma_material_x = response['sigma_x'][wall] + gradients[0][wall] * k
    sigma_material_xx = response['sigma_xy'][wall] + 2 * gradients[1][wall] * k
    return dict(response=response, C_profile=c, C_star=float(C_star),
                J1=j1, J3=j3, eta_trial_coefficients=np.array([a1, a3]),
                f_x=h, f_xx=np.zeros_like(h), wall_index=wall,
                wall_coordinate_x=k, wall_coordinate_xx=0.0,
                base_proper_normal_velocity=float(normal_velocity),
                wall_sigma_eulerian_x=float(response['sigma_x'][wall]),
                wall_sigma_embedding_x=float(gradients[0][wall] * k),
                wall_sigma_eulerian_target=-float(normal_velocity) / (4 * z),
                wall_eta_material_x=float(a1 - a3 + k),
                wall_eta_material_xx=float(2 * hp_wall * k),
                wall_sigma_material_x=float(sigma_material_x),
                wall_sigma_material_xx=float(sigma_material_xx),
                response_constraint_rows=rows,
                chart='PROMOTED_PROPER_LENGTH_CANDIDATE__NOT_RETAINED_COORDINATE_ACTION_REPLACEMENT',
                Eulerian_geometry_fixed=True,
                physical_formation_mode_selected=False)


def orbit_length_pullback_jet(*, C, C_prime, C_second, coordinate_velocity,
                              velocity_prime, coordinate_acceleration, acceleration_prime):
    """Apply the metric and Jacobian motion of dℓ=C(F_s)F_s' dχ.

    At F0=id, F_s=χ+s v+s²a/2, the supplied jets give
    ℓ_s=C'v+C v' and ℓ_ss=C''v²+C'a+2C'v v'+C a'.  The pulled orbit
    derivative is Dℓ=(1/ℓ_density)∂χ.  Both position and Jacobian terms are
    required.  These are pullback jets, distinct from Eulerian δ_E C.
    """
    c = np.asarray(C, dtype=float)
    if not np.all(np.isfinite(c)) or np.any(c <= 0):
        raise ValueError("positive finite C is required")
    cp, cpp, v, vp, acc, accp = [_field(a, c.shape, name) for a, name in
        ((C_prime, "C_prime"), (C_second, "C_second"),
         (coordinate_velocity, "coordinate_velocity"), (velocity_prime, "velocity_prime"),
         (coordinate_acceleration, "coordinate_acceleration"),
         (acceleration_prime, "acceleration_prime"))]
    cx = cp * v + c * vp
    cxx = cpp * v**2 + cp * acc + 2 * cp * v * vp + c * accp
    return dict(length_density=c, length_density_x=cx, length_density_xx=cxx,
                length_log_x=cx / c, length_log_xx=cxx / c - cx**2 / c**2,
                orbit_derivative_coefficient=1 / c,
                orbit_derivative_coefficient_x=-cx / c**2,
                orbit_derivative_coefficient_xx=2 * cx**2 / c**3 - cxx / c**2)


def normal_geometry_first(inverse_metric, gradient, *,
                          inverse_metric_x, gradient_x):
    """Differentiate a nonnull level-set normal, with covector/vector signs explicit.

    The owner's positive-gradient unit conormal is α/sqrt(|α g⁻¹ α|).
    ``raised_conormal`` is its literal metric raise.  ``increasing_normal``
    is sign(α g⁻¹ α) times that vector, so its action on the level-set field
    is positive in either spacelike signature convention.  The latter is an
    explicitly oriented vector, not an unmarked raising of the conormal.
    """
    gi = np.asarray(inverse_metric, dtype=float)
    alpha = np.asarray(gradient, dtype=float)
    if (alpha.ndim != 1 or gi.shape != (alpha.size, alpha.size)
            or not np.all(np.isfinite(gi)) or not np.all(np.isfinite(alpha))
            or not np.allclose(gi, gi.T, rtol=0, atol=1e-14)):
        raise ValueError("finite symmetric inverse metric and one gradient are required")
    dg = _field(inverse_metric_x, gi.shape, "inverse_metric_x")
    da = _field(gradient_x, alpha.shape, "gradient_x")
    if not np.allclose(dg, dg.T, rtol=0, atol=1e-14):
        raise ValueError("inverse metric variation must be symmetric")
    raised = gi @ alpha
    q = float(alpha @ raised)
    if q == 0:
        raise ValueError("null normal requires the separately owned conormal-density domain")
    epsilon = np.sign(q)
    norm = np.sqrt(abs(q))
    dq = float(2 * da @ raised + alpha @ dg @ alpha)
    dnorm = epsilon * dq / (2 * norm)
    conormal = alpha / norm
    dcov = da / norm - alpha * dnorm / norm**2
    up = raised / norm
    dup = (dg @ alpha + gi @ da) / norm - up * dnorm / norm
    return dict(normal_square_sign=float(epsilon), gradient_norm=float(norm),
                gradient_norm_x=float(dnorm), conormal=conormal,
                conormal_x=dcov, raised_conormal=up, raised_conormal_x=dup,
                increasing_normal=epsilon * up,
                increasing_normal_x=epsilon * dup)


def response_constraint_first(*, response_normal, response_normal_x,
                              sigma_gradient, sigma_gradient_x,
                              W, W_x, Z, Z_x):
    """Apply Cσ and δCσ, retaining δn_eta·∇σ as the metric/normal term.

    ``response_normal`` is the orbit derivative n_eta of the response owner;
    it must not be replaced by a different hypersurface normal by name.
    """
    n = np.asarray(response_normal, dtype=float)
    nx = _field(response_normal_x, n.shape, "response_normal_x")
    ds = _field(sigma_gradient, n.shape, "sigma_gradient")
    dsx = _field(sigma_gradient_x, n.shape, "sigma_gradient_x")
    if n.ndim != 1 or not np.all(np.isfinite(n)) or not np.isfinite(Z) or Z <= 0:
        raise ValueError("a finite response normal and positive Z are required")
    if not np.all(np.isfinite([W, W_x, Z_x])):
        raise ValueError("finite weight and normalization jets are required")
    metric_normal = float(nx @ ds)
    return dict(C_sigma=float(n @ ds - W / Z),
                C_sigma_x=float(n @ dsx + metric_normal - W_x / Z + W * Z_x / Z**2),
                metric_normal_variation=metric_normal)


def response_constraint_jet(*, response_normal_jet, sigma_gradient_jet,
                            weight_jet, normalization_jet):
    """Apply the base, x, y and mixed constraint, including D-operator motion.

    Each jet is ordered (0,x,y,xy), with derivative rather than factorial
    coefficients.  The normal/gradient jets are vectors in one fixed common
    pullback.  In the coordinate-measure chart the response D is ∂χ; in a
    covariant chart its supplied normal jets include metric and eta motion.
    """
    if any(len(j) != 4 for j in (response_normal_jet, sigma_gradient_jet,
                                 weight_jet, normalization_jet)):
        raise ValueError("four ordered derivative entries per jet are required")
    n = np.asarray(response_normal_jet[0], dtype=float)
    if n.ndim != 1 or not np.all(np.isfinite(n)):
        raise ValueError("a finite vector response normal is required")
    nn = [_field(v, n.shape, "response normal jet") for v in response_normal_jet]
    gg = [_field(v, n.shape, "sigma gradient jet") for v in sigma_gradient_jet]
    w, wx, wy, wxy = [float(v) for v in weight_jet]
    z, zx, zy, zxy = [float(v) for v in normalization_jet]
    if not np.all(np.isfinite([w, wx, wy, wxy, z, zx, zy, zxy])) or z <= 0:
        raise ValueError("finite scalar jets and positive normalization required")
    ratio = w / z
    rx = wx / z - w * zx / z**2
    ry = wy / z - w * zy / z**2
    rxy = (wxy / z - (wx * zy + wy * zx + w * zxy) / z**2
           + 2 * w * zx * zy / z**3)
    c = nn[0] @ gg[0] - ratio
    cx = nn[0] @ gg[1] + nn[1] @ gg[0] - rx
    cy = nn[0] @ gg[2] + nn[2] @ gg[0] - ry
    cxy = (nn[0] @ gg[3] + nn[1] @ gg[2] + nn[2] @ gg[1]
           + nn[3] @ gg[0] - rxy)
    return dict(C_sigma=float(c), C_sigma_x=float(cx), C_sigma_y=float(cy),
                C_sigma_xy=float(cxy),
                operator_motion_x=float(nn[1] @ gg[0]),
                operator_motion_y=float(nn[2] @ gg[0]),
                operator_motion_xy=float(nn[1] @ gg[2] + nn[2] @ gg[1]
                                         + nn[3] @ gg[0]))


def response_constraint_weak_jet(coordinate, *, measure_jet,
                                 multiplier_jet, constraint_jet):
    """Apply ∫dℓ μ_Q λσ Cσ to supplied test/multiplier and measure jets.

    Ordered jets are (0,x,y,xy).  ``measure_jet`` is the actual common-chart
    density dℓ μ_Q/dχ and its ordinary derivatives, including its pullback
    motion.  λ is supplied, never physically selected by this routine.
    The returned mixed multiplier contact keeps λ_x C_y+λ_y C_x, even when
    the base constraint vanishes.  Reduced response tangency may cancel this
    sector; that cancellation does not eliminate the full adjoint reaction.
    """
    x = _grid(coordinate)
    if any(len(j) != 4 for j in (measure_jet, multiplier_jet, constraint_jet)):
        raise ValueError("four ordered derivative entries per jet are required")
    m, mx, my, mxy = [_field(v, x.shape, "measure jet") for v in measure_jet]
    l, lx, ly, lxy = [_field(v, x.shape, "multiplier jet") for v in multiplier_jet]
    c, cx, cy, cxy = [_field(v, x.shape, "constraint jet") for v in constraint_jet]
    if np.any(m <= 0):
        raise ValueError("the base action measure must be positive")
    density = m * l * c
    density_x = mx * l * c + m * lx * c + m * l * cx
    density_y = my * l * c + m * ly * c + m * l * cy
    contact = m * (lx * cy + ly * cx)
    density_xy = (mxy * l * c + mx * (ly * c + l * cy)
                  + my * (lx * c + l * cx)
                  + m * (lxy * c + l * cxy) + contact)
    return dict(action=float(_cumulative(x, density)[-1]),
                action_x=float(_cumulative(x, density_x)[-1]),
                action_y=float(_cumulative(x, density_y)[-1]),
                action_xy=float(_cumulative(x, density_xy)[-1]),
                multiplier_contact_xy=float(_cumulative(x, contact)[-1]),
                density=density, density_x=density_x, density_y=density_y,
                density_xy=density_xy, multiplier_contact_density_xy=contact)


def eulerian_embedding_split(*, eulerian_sigma, sigma_gradient,
                             embedding_velocity):
    """Apply d_s(F_s*σ_s)=δ_Eσ+L_vσ; compatibility requires its value zero."""
    gradient = np.asarray(sigma_gradient, dtype=float)
    velocity = _field(embedding_velocity, gradient.shape, "embedding_velocity")
    if gradient.ndim != 1 or not np.all(np.isfinite(gradient)):
        raise ValueError("a finite gradient is required")
    if not np.isfinite(eulerian_sigma):
        raise ValueError("a finite Eulerian response is required")
    advective = float(velocity @ gradient)
    return dict(eulerian=float(eulerian_sigma), embedding=advective,
                pulled_material_derivative=float(eulerian_sigma + advective))


def compatible_normal_trial(eulerian_sigma_trial, normal_sigma_rate):
    """Infer ψ_trial=−δ_Eσ_trial/D_nσ on a supplied transverse material level set.

    This enforces the material equation only.  A trial representation is not
    an initiating projector, a formation eigenmode, or a full-I normalization.
    """
    value, rate = np.broadcast_arrays(np.asarray(eulerian_sigma_trial, float),
                                      np.asarray(normal_sigma_rate, float))
    if not np.all(np.isfinite(value)) or not np.all(np.isfinite(rate)) or np.any(rate == 0):
        raise ValueError("finite trials and a nonzero owned normal rate are required")
    return -value / rate


def anchored_coordinate_advection(coordinate, *, f_coordinate_gradient,
                                  length_coordinate_log_gradient,
                                  coordinate_velocity, coordinate_velocity_gradient):
    """Owned orbit reparameterization jets, with fixed coordinate anchors.

    δ_Ef=−v∂χf and δ_E log a=−v'−v∂χlog a imply δ_E(Wa)=−∂χ(vWa).
    With v=0 at both anchors, δZ=0 and δ_Eσ=−v∂χσ.  Its material pullback
    vanishes by covariance.  This gauge identity does not identify a relative
    eta/geometry variation or an initiating physical formation mode.
    """
    x = _grid(coordinate)
    fp, ap, v, vp = [_field(a, x.shape, name) for a, name in
                    ((f_coordinate_gradient, "f_coordinate_gradient"),
                     (length_coordinate_log_gradient, "length_coordinate_log_gradient"),
                     (coordinate_velocity, "coordinate_velocity"),
                     (coordinate_velocity_gradient, "coordinate_velocity_gradient"))]
    if np.any(np.abs(v[[0, -1]]) > 1e-14):
        raise ValueError("fixed-anchor coordinate advection requires zero endpoint velocities")
    return dict(f_x=-v * fp, length_log_x=-vp - v * ap,
                embedding_coordinate_velocity=v,
                kind='ANCHORED_ORBIT_REPARAMETERIZATION',
                physical_formation_mode_selected=False)


def response_action_first(coordinate, orbit_length_density, *,
                          orbit_action_density, multiplier, C_sigma,
                          orbit_action_log_x, length_log_x,
                          multiplier_x, C_sigma_x):
    """Apply δ∫dℓ μ_Q λσ Cσ with measure and multiplier response intact.

    This is the response action on one common time slice.  Additional bulk,
    odd-FR, gauge/reset and corner contributions are separate owned terms.
    It does not infer λσ or impose its adjoint equation.
    """
    x = _grid(coordinate)
    a, mu, lam, c, mux, ax, lamx, cx = [_field(v, x.shape, name) for v, name in
        ((orbit_length_density, "orbit_length_density"),
         (orbit_action_density, "orbit_action_density"), (multiplier, "multiplier"),
         (C_sigma, "C_sigma"), (orbit_action_log_x, "orbit_action_log_x"),
         (length_log_x, "length_log_x"), (multiplier_x, "multiplier_x"),
         (C_sigma_x, "C_sigma_x"))]
    if np.any(a <= 0) or np.any(mu <= 0):
        raise ValueError("positive orbit length and action densities are required")
    base = a * mu * lam * c
    first = a * mu * (lamx * c + lam * cx + lam * c * (ax + mux))
    return dict(action=float(_cumulative(x, base)[-1]),
                action_x=float(_cumulative(x, first)[-1]),
                base_density=base, first_density=first)
