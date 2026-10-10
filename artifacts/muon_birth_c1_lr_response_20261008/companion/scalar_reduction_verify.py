#!/usr/bin/env python3
"""Exact controls for the active-Higgs Jacobi and adjoint reductions.

These tests use rational control data. They do not provide an incoming BHSM
Higgs solution, its scalar domain, an E1 kernel, or a physical muon value.
Only the Python standard library is required.
"""
from fractions import Fraction as Q
import json


def dot(x, y):
    return sum((a*b for a, b in zip(x, y)), Q(0))


def add(x, y):
    return [a+b for a, b in zip(x, y)]


def scale(a, x):
    return [a*b for b in x]


def potential_gradient(x, kappa, nu2):
    return scale(2*kappa*(dot(x, x)-nu2), x)


def potential_jacobi(x, h, kappa, nu2):
    return scale(2*kappa, add(scale(dot(x, x)-nu2, h),
                              scale(2*dot(x, h), x)))


def inverse(a):
    n = len(a)
    m = [[Q(v) for v in row] + [Q(int(i == j)) for j in range(n)]
         for i, row in enumerate(a)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if m[i][j]), None)
        if pivot is None:
            raise ValueError('Singular control matrix')
        m[j], m[pivot] = m[pivot], m[j]
        divisor = m[j][j]
        m[j] = [v/divisor for v in m[j]]
        for i in range(n):
            if i != j:
                factor = m[i][j]
                m[i] = [u-factor*v for u, v in zip(m[i], m[j])]
    return [row[n:] for row in m]


def mv(a, x):
    return [dot(row, x) for row in a]


def transpose(a):
    return [list(row) for row in zip(*a)]


def run_checks():
    checks = []
    x = [Q(2, 3), Q(-1, 5), Q(3, 7), Q(1, 2)]
    kappa, nu2 = Q(2, 7), Q(9, 4)
    directions = [[Q(int(i == j)) for i in range(4)] for j in range(4)]
    directions.append([Q(1, 3), Q(2, 5), Q(-2, 7), Q(3, 11)])
    for h in directions:
        plus = potential_gradient(add(x, h), kappa, nu2)
        minus = potential_gradient(add(x, scale(-1, h)), kappa, nu2)
        # Exact cubic polarization: central difference minus the cubic h term.
        independent_derivative = add(scale(Q(1, 2), add(plus, scale(-1, minus))),
                                     scale(-2*kappa*dot(h, h), h))
        assert independent_derivative == potential_jacobi(x, h, kappa, nu2)
    checks.append({'name': 'real_four_component_potential_jacobi',
                   'directions': len(directions), 'exact_residual': '0'})

    vacuum = [Q(3, 2), Q(0), Q(0), Q(0)]
    radial = potential_jacobi(vacuum, directions[0], kappa, nu2)
    assert radial == [4*kappa*nu2, Q(0), Q(0), Q(0)]
    for h in directions[1:4]:
        assert potential_jacobi(vacuum, h, kappa, nu2) == [Q(0)]*4
    # This is the potential Hessian only; it is not the constrained PDE inverse.
    checks.append({'name': 'potential_radial_and_tangential_directions',
                   'radial_coefficient': str(4*kappa*nu2),
                   'potential_tangent_nullity': 3, 'exact_residual': '0'})

    # Include coefficient variations at fixed H. The Euler potential is -grad V.
    dk, dn = Q(3, 11), Q(-2, 13)
    direct = add(scale(-2*dk*(dot(x, x)-nu2), x), scale(2*kappa*dn, x))
    forcing = add(scale(2*dk*(dot(x, x)-nu2), x), scale(-2*kappa*dn, x))
    assert add(direct, forcing) == [Q(0)]*4
    checks.append({'name': 'moving_action_coefficient_forcing_signs',
                   'exact_residual': '0'})

    # General constrained row system: first row is a boundary condition,
    # remaining rows are bulk equations. The adjoint includes its multiplier.
    a = [[Q(1), Q(0), Q(0)],
         [Q(2), Q(3), Q(1)],
         [Q(-1), Q(2), Q(4)]]
    rhs = [Q(2, 5), Q(3, 7), Q(-5, 11)]
    ell = [Q(7, 13), Q(-2, 3), Q(4, 5)]
    h = mv(inverse(a), rhs)
    p = mv(inverse(transpose(a)), ell)
    assert dot(ell, h) == dot(p, rhs)
    assert dot(p, rhs) != dot(p[1:], rhs[1:])
    checks.append({'name': 'scalar_adjoint_with_nonzero_boundary_forcing',
                   'contraction': str(dot(ell, h)), 'exact_residual': '0',
                   'dropping_boundary_multiplier_changes_result': True})

    # Inhomogeneous boundary lifting gives the same answer as the whole solve.
    h_lift = [rhs[0], Q(0), Q(0)]
    interior = [row[1:] for row in a[1:]]
    residual_rhs = add(rhs[1:], scale(-1, mv(a[1:], h_lift)))
    h_interior = mv(inverse(interior), residual_rhs)
    independent = add(h_lift, [Q(0)] + h_interior)
    assert h == independent
    checks.append({'name': 'boundary_lift_and_full_constraint_solution_agree',
                   'exact_residual': '0'})

    return {'classification': 'EXACT_RATIONAL_CONTROL_ONLY',
            'checks_passed': len(checks), 'checks': checks,
            'physical_H_C1': None, 'physical_scalar_response': None,
            'physical_E1_kernel': None, 'physical_a_mu': None,
            'physical_g_mu': None}


if __name__ == '__main__':
    print(json.dumps(run_checks(), indent=2, sort_keys=True))
