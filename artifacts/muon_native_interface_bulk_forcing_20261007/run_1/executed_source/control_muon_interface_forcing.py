"""Exact finite KKT control; no BHSM physical source or action is selected."""
import sympy as sp
from flint import arb_mat, ctx

from bhsm.interface.muon_native_interface_bulk_forcing import (
    seven_port_forcing_direction, solve_bulk_forcing_column,
    real_stationary_impedance_column,
)
from bhsm.interface.joint_boundary_port_reduction import reduce_seven_port, moving_port_jet


def amat(matrix):
    return arb_mat([[str(x) for x in row] for row in sp.Matrix(matrix).tolist()])


def exact_control():
    q = sp.Rational
    T = sp.eye(3)
    direction = sp.Matrix([q(1, 5), q(2, 7), -q(1, 3)])
    shape = sp.Matrix([q(1, 11), -q(1, 13), q(1, 17)])
    momentum = sp.Matrix([q(2, 5), -q(3, 7)])
    force = sp.Matrix([q(11, 13), q(5, 17)])
    conormal = sp.Matrix([q(1, 19), -q(2, 23)])
    mixed = sp.Matrix([q(3, 29), -q(5, 31)])
    rate = sp.Matrix([q(7, 37), q(11, 41)])
    b = (T * direction + shape).col_join(momentum).col_join(force - conormal - mixed - rate)
    A = sp.Matrix([[4, 1], [1, 3]])
    d = sp.Matrix([[1, 1]])
    C = sp.Matrix([[q(1, k + 2) for k in range(7)],
                   [(-1)**k * q(1, k + 3) for k in range(7)]])
    s = sp.Matrix([[q(1, k + 7) for k in range(7)]])
    D = 9 * sp.eye(7)
    n0, n1, lam, t = sp.symbols('n0 n1 lam t', real=True)
    n = sp.Matrix([n0, n1]); variables = sp.Matrix([n0, n1, lam])
    # L = 1/2 physical Q plus the same source-dependent constraint.
    L = ((n.T * A * n)[0] / 2 + t * (n.T * C * b)[0]
         + t**2 * (b.T * D * b)[0] / 2 + lam * ((d * n)[0] - t * (s * b)[0]))
    E = sp.Matrix([sp.diff(L, x) for x in variables])
    H = E.jacobian(variables)
    f = E.diff(t)
    delta = H.LUsolve(-f)
    qxx = (b.T * D * b)[0]
    physical_direct = sp.expand((delta[:2, :].T * A * delta[:2, :])[0]
                               + 2 * (delta[:2, :].T * C * b)[0] + qxx)
    schur = qxx + (f.T * delta)[0]
    # A nonunitary residual-row scaling preserves response but not impedance.
    row_map = sp.diag(2, 3, 5)
    wrong_schur = qxx + ((row_map * f).T * delta)[0]
    gp = sp.Matrix([q(k + 1, 17) for k in range(7)])
    gn = sp.Matrix([[q(k + 1, 13), q(1, k + 11), -q(1, k + 19)] for k in range(7)])
    B = sp.Matrix([[q(k + 1, 23), q(1, k + 29)] for k in range(7)])
    Bdot = sp.Matrix([[q(1, k + 31), -q(1, k + 37)] for k in range(7)])
    reaction = sp.Matrix([q(2, 3), -q(1, 5)])
    reaction_dot = sp.Matrix([q(1, 7), q(3, 11)])
    moving_exact = sp.diff((B + t * Bdot) * (reaction + t * reaction_dot), t).subs(t, 0)
    return locals()


def execute_control():
    ctx.prec = 256
    x = exact_control()
    b = seven_port_forcing_direction(**{key: amat(x[name]) for key, name in (
        ('trace_map', 'T'), ('state_direction', 'direction'), ('trace_shape', 'shape'),
        ('momentum', 'momentum'), ('force', 'force'), ('conormal', 'conormal'),
        ('momentum_mixed', 'mixed'), ('momentum_rate_direction', 'rate'))})
    solved = real_stationary_impedance_column(amat(x['H']), amat(x['f']), str(x['qxx']))
    # Arithmetic coercion: Q_XX is a scalar in the same real Arb field.
    reduced = reduce_seven_port(amat(x['H']), amat(x['f']),
                               {'control': dict(p=amat(x['gp']), n=amat(x['gn']))})
    row_solved = solve_bulk_forcing_column(amat(x['row_map'] * x['H']), amat(x['row_map'] * x['f']))
    moved = moving_port_jet(amat(x['B']), amat(x['reaction']), amat(x['reaction_dot']), [amat(x['Bdot'])])
    def enclosed(matrix, expected):
        target = amat(expected)
        return all((matrix[i, j] - target[i, j]).contains(0)
                   for i in range(matrix.nrows()) for j in range(matrix.ncols()))
    checks = dict(
        seven_components=enclosed(b, x['b']) and (b.nrows(), b.ncols()) == (7, 1),
        mixed_derivative_exact=x['f'] == (x['C'] * x['b']).col_join(-x['s'] * x['b']),
        source_dependent_constraint_retained=(x['d'] * x['delta'][:2, :])[0] == (x['s'] * x['b'])[0],
        response_contains_exact=enclosed(solved['response'], x['delta']),
        stationary_residual_contains_zero=all(v.contains(0) for v in solved['replay'].entries()),
        direct_physical_schur_exact=sp.simplify(x['physical_direct'] - x['schur']) == 0,
        direct_schur_arb_overlap=solved['difference'].contains(0),
        signed_output_forward_adjoint=enclosed(reduced['reduced'], x['gp'] + x['gn'] * x['delta']),
        moving_port_full_product_rule=enclosed(moved, x['moving_exact']),
        nonunitary_row_map_preserves_response=enclosed(row_solved['response'], x['delta']),
        residual_row_schur_is_wrong=sp.simplify(x['wrong_schur'] - x['schur']) != 0,
    )
    report = dict(classification='EXACT_AND_ARB_FINITE_CONTROL__NOT_NATIVE_BHSM',
                  checks=checks, all_checks_pass=all(checks.values()), precision_bits=ctx.prec,
                  b_control=[str(v) for v in x['b']], f_control=[str(v) for v in x['f']],
                  response_control=[str(v) for v in x['delta']], impedance_control=str(x['schur']),
                  wrong_residual_row_impedance=str(x['wrong_schur']),
                  response_replay=[str(v) for v in solved['replay'].entries()],
                  direct_schur_difference=str(solved['difference']),
                  counts=dict(solved_forcing_columns=1, physical_forcing_columns=0,
                              heat_evaluations=0, full_7x73_recomputations=0),
                  error_scope='Arb rounding enclosures for prescribed exact finite entries only; no physical, continuum, history or soft-transfer error bound')
    arrays = {name: sp.Matrix(x[name]) for name in ('T', 'direction', 'shape', 'momentum', 'force',
              'conormal', 'mixed', 'rate', 'b', 'A', 'd', 'C', 's', 'D', 'H', 'f', 'delta', 'row_map', 'gp', 'gn')}
    return report, arrays
