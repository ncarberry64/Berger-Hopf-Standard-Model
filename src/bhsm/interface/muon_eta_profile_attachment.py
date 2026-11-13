"""Daughter eta restriction and a local collar realization; no heat solve.

These are functional identities on a compatible collar, with its pairing,
transport, chart and source held fixed. They do not certify a collar chart,
choose another BHSM profile, or assert that varied profiles solve the field equations.
"""
from __future__ import annotations

import sympy as sp


def attachment_equations():
    """The missing action restriction and the contraction that consumes it."""
    return {
        "restriction": "f_eta,current=f_child o X=chi o X=rho(X)/2 on the retained daughter eta-clock branch",
        "normal_action": (
            "D_perp,eps=i eps Gamma_perp [partial_s+"
            "(1/2)partial_s log J_current-partial_s log sin(f_child o X)]"
        ),
        "mode": "u_f=J^(-1/2) v_f; v_f=sin(f)/sqrt(I_f); I_f=integral sin(f)^2 ds",
        "overlap": "T_ij=integral dmu4 ds J u_f^* (U54 e_i)^dagger p_j(X(s,y))",
        "overlap_consumer": "M4 B_required=T; no arbitrary diagonal or interface penalty",
        "fixed_pairing_profile_tangent": (
            "k=h cot(f); mean_k=integral |v_f|^2 k ds; "
            "delta u_f=u_f (k-mean_k); delta m_eta=-partial_s k"
        ),
        "overlap_kernel": (
            "delta T_ij=integral dmu4 ds "
            "[J u_f^* phi_ij-|v_f|^2 T_ij(y)] k; "
            "phi_ij=(U54 e_i)^dagger p_j(X); "
            "T_ij(y)=integral ds J u_f^* phi_ij"
        ),
        "kernel_in_h": (
            "delta T_ij=integral dmu4 ds "
            "[sqrt(J) cos(f) phi_ij/sqrt(I_f) "
            "-sin(f) cos(f) T_ij(y)/I_f] h"
        ),
        "nonlinear_diagnostic_family": (
            "sin(f_epsilon)=exp(epsilon k) sin(f); "
            "v_epsilon=exp(epsilon k) v_f/sqrt(integral |v_f|^2 exp(2 epsilon k) ds); "
            "m_epsilon=m_f-epsilon partial_s k"
        ),
        "normal_source_action": "delta D_perp,eps p_j=-i eps Gamma_perp (partial_s k) p_j",
        "static_scalar_pullback_if_matched": (
            "f_eta,current=F(r_tex(s,y)); "
            "m_eta,current=-F_r(r_tex) partial_s r_tex cot(F(r_tex))"
        ),
        "static_probability_pullback_if_matched": (
            "v_current^2 ds=sin(F(r_tex))^2 |partial_s r_tex| ds/I_static; "
            "m_current=-partial_s log sin(F(r_tex)) "
            "-(1/2)partial_s log |partial_s r_tex|"
        ),
        "join_probability_identity_if_matched": (
            "|v_current|^2 ds=(sin(f_join)^2 cos(f_join)^2/Z_join) |dchi|; "
            "m_current=-(cot(f_join)-tan(f_join)) partial_s f_join "
            "-(1/2)partial_s log |partial_s chi|"
        ),
        "same_source_jet": (
            "delta_b m_eta=-delta_b partial_s log sin(f_child o X); "
            "differentiate the SAME outgoing field and collar/pairing/transport; "
            "delta_b Omega=T_b Y_A(-iQ) remains independent"
        ),
        "current_owner_chain_rule": (
            "D_fjoin Gamma_owner includes D_m Gamma_owner "
            "[-partial_s(cot(f_child o X) delta(f_child o X))] "
            "and the induced interface/pairing/domain derivatives"
        ),
    }


def exact_profile_residuals():
    """Five exact identities, with no numerical witness or profile solve.

    I>0 is the full normal integral. H=integral sin(f)cos(f)h ds.
    The support of h avoids profile zeros and branch turning points; compact
    support preserves endpoint data. Differentiation is justified by smooth
    compact support and a finite positive norm, independently of heat limits.
    """
    s, e = sp.symbols("s e", real=True)
    f, h, k = (sp.Function(name)(s) for name in ("f", "h", "k"))
    J = sp.Function("J", positive=True)(s)
    I = sp.symbols("I", positive=True)
    H, phi, beta = sp.symbols("H phi beta")
    u = sp.sin(f) / sp.sqrt(I * J)
    mass = -sp.diff(sp.log(sp.sin(f)), s)
    zero_mode = sp.simplify(sp.diff(u, s) + sp.diff(sp.log(J), s) * u / 2 + mass * u)
    varied_mass = -sp.diff(sp.log(sp.sin(f + e * h)), s)
    mass_tangent = sp.trigsimp(
        sp.diff(varied_mass, e).subs(e, 0) + sp.diff(h * sp.cot(f), s)
    )
    # Pointwise derivative plus dI/de=2H; this is not a sampled quadrature.
    direct_u_tangent = sp.diff(sp.sin(f + e * h), e).subs(e, 0) / sp.sqrt(I * J) - u * H / I
    centered_u_tangent = u * (h * sp.cot(f) - H / I)
    normalized_tangent = sp.trigsimp(direct_u_tangent - centered_u_tangent)
    # beta=N*int sqrt(J) sin(f) phi ds. The second term is global in s.
    direct_integrand = sp.sqrt(J) * sp.cos(f) * h * phi / sp.sqrt(I) - beta * sp.sin(f) * sp.cos(f) * h / I
    centered_integrand = (J * u * phi - sp.sin(f)**2 * beta / I) * h * sp.cot(f)
    overlap_kernel = sp.trigsimp(direct_integrand - centered_integrand)
    finite_family_mass = sp.simplify(
        -sp.diff(sp.log(sp.exp(e * k) * sp.sin(f)), s) - mass + e * sp.diff(k, s)
    )
    return {
        "normal_zero_mode_identity": zero_mode,
        "normal_mass_profile_tangent": mass_tangent,
        "normalized_mode_tangent": normalized_tangent,
        "actual_overlap_functional_kernel": overlap_kernel,
        "finite_normal_mass_deformation": finite_family_mass,
    }


def probability_pullback_residuals():
    """Differentiate necessary conditional density identities, not selections."""
    s = sp.symbols("s", real=True)
    f = sp.Function("f")(s)
    r_s = sp.Function("r_s", positive=True)(s)
    chi_s = sp.Function("chi_s", positive=True)(s)
    static = -sp.diff(sp.log(sp.sin(f) * sp.sqrt(r_s)), s)
    static_expected = -sp.cot(f) * sp.diff(f, s) - sp.diff(sp.log(r_s), s) / 2
    join = -sp.diff(sp.log(sp.sin(f) * sp.cos(f) * sp.sqrt(chi_s)), s)
    join_expected = -(sp.cot(f) - sp.tan(f)) * sp.diff(f, s) - sp.diff(sp.log(chi_s), s) / 2
    return {
        "static_density_jacobian_term": sp.trigsimp(static - static_expected),
        "join_density_jacobian_and_cosine_terms": sp.simplify((join - join_expected).rewrite(sp.sin)),
    }


def daughter_collar_profile(geometry, *, s_end=0.001, samples=33):
    """One finite inward normal geodesic in the cached nodal metric.

    This covers a small collar patch, not the saved compact source support.
    It uses the Lorentz signature unchanged. Temporal/radial derivatives of
    the metric are those of the declared bilinear nodal reconstruction;
    neither the independently repaired H nor a fitted metric is substituted.
    No normalization integral, transverse Jacobi field, or transport is set
    by this one curve. No outside-cache metric extrapolation is permitted.
    """
    import numpy as np
    from scipy.integrate import solve_ivp

    times = np.asarray(geometry['proper_times'], float)
    rho = np.asarray(geometry['rho'], float)
    fields = np.array([geometry[k] for k in ('proper_lapse', 'C_rho', 'proper_shift_rho')])
    if s_end <= 0 or samples < 3:
        raise ValueError('positive local normal extent and at least three samples required')

    def metric(t, r):
        if not (times[0] <= t <= times[-1] and rho[0] <= r <= rho[-1]):
            raise ValueError('normal curve left supplied metric cache; recover inherited prefix/patch, do not extrapolate')
        it = min(max(int(np.searchsorted(times, t, side='right'))-1, 0), len(times)-2)
        ir = min(max(int(np.searchsorted(rho, r, side='right'))-1, 0), len(rho)-2)
        dt, dr = times[it+1]-times[it], rho[ir+1]-rho[ir]
        a, b = (t-times[it])/dt, (r-rho[ir])/dr
        z = fields[:, it:it+2, ir:ir+2]
        vals = (1-a)*((1-b)*z[:, 0, 0]+b*z[:, 0, 1])+a*((1-b)*z[:, 1, 0]+b*z[:, 1, 1])
        deriv = np.array([((1-b)*(z[:, 1, 0]-z[:, 0, 0])+b*(z[:, 1, 1]-z[:, 0, 1]))/dt,
                          ((1-a)*(z[:, 0, 1]-z[:, 0, 0])+a*(z[:, 1, 1]-z[:, 1, 0]))/dr])
        nu, C, shift = vals
        g = np.array([[nu*nu-C*C*shift*shift, -C*C*shift], [-C*C*shift, -C*C]])
        dg = np.empty((2, 2, 2))
        for d in range(2):
            dn, dc, dz = deriv[d]
            dg[d] = [[2*nu*dn-2*C*shift*shift*dc-2*C*C*shift*dz,
                      -2*C*shift*dc-C*C*dz], [-2*C*shift*dc-C*C*dz, -2*C*dc]]
        inv = np.linalg.solve(g, np.eye(2))
        connection = np.empty((2, 2, 2))
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    connection[i, j, k] = sum(inv[i, l]*(dg[j, l, k]+dg[k, l, j]-dg[l, j, k])/2 for l in range(2))
        return g, connection, vals, (it, ir)

    # An interior wall base point avoids imposing a condition at either
    # temporal face. It is a coordinate sampling point, not a new state.
    wall_time = float((times[23]+times[24])/2)
    _, _, wall, _ = metric(wall_time, float(rho[-1]))
    initial = np.array([wall_time, rho[-1], 0.0, -1.0/wall[1]])
    def rhs(s, y):
        _, connection, _, _ = metric(y[0], y[1])
        return np.r_[y[2:], -np.einsum('ijk,j,k->i', connection, y[2:], y[2:])]

    s = np.linspace(0, s_end, samples)
    sol = solve_ivp(rhs, (0, s_end), initial, t_eval=s, method='DOP853',
                    rtol=2e-10, atol=2e-12, max_step=s_end/40)
    if not sol.success:
        raise ArithmeticError(sol.message)
    f = sol.y[1]/2
    fs = sol.y[3]/2
    mass = -fs/np.tan(f)
    norm = []
    cells = []
    for t, r, nt, nr in sol.y.T:
        g, _, _, cell = metric(t, r)
        norm.append(np.array([nt, nr]) @ g @ np.array([nt, nr]))
        cells.append(cell)
    arrays = dict(s=s, tau=sol.y[0], rho=sol.y[1], tau_s=sol.y[2], rho_s=sol.y[3],
                  f_eta_current=f, f_eta_s=fs, m_eta_current=mass,
                  normal_metric_norm=np.array(norm), metric_cells=np.array(cells))
    summary = dict(classification='evaluated daughter profile on one finite inward collar curve in the cached bilinear Lorentz metric',
        wall_base_tau=wall_time, s_extent=s_end, rho_range=[float(min(sol.y[1])), float(max(sol.y[1]))],
        time_range=[float(min(sol.y[0])), float(max(sol.y[0]))],
        m_eta_endpoints=[float(mass[0]), float(mass[-1])],
        maximum_spacelike_unit_norm_residual=float(max(abs(np.array(norm)+1))),
        ode_function_evaluations=sol.nfev, solver='DOP853', rtol=2e-10, atol=2e-12,
        full_source_support_covered=False, finite_chart_jacobian_evaluated=False,
        normalized_u0=None, actual_overlap_T=None, B54=None,
        scope='single curve, not a full-rank chart or global normal-mode normalization; solver tolerances and norm residual are not rigorous continuum bounds',
        temporal_reconstruction='cached bilinear nu/C/shift; repaired H source rate unchanged and not used as a replacement metric derivative')
    return arrays, summary
