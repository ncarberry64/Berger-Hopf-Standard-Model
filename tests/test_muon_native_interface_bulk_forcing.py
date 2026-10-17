"""Targeted one-column controls; no physical BHSM or historical producer runs."""
from pathlib import Path
import sys
import pytest
import sympy as sp
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from control_muon_interface_forcing import exact_control, amat
from bhsm.interface.muon_native_interface_bulk_forcing import (
    seven_port_forcing_direction, solve_bulk_forcing_column, real_stationary_impedance_column,
)
from bhsm.interface.joint_boundary_port_reduction import reduce_seven_port, moving_port_jet


@pytest.fixture(scope='module')
def data():
    ctx.prec = 256
    return exact_control()


def overlaps(actual, expected):
    return all((actual[i, j] - amat(expected)[i, j]).contains(0)
               for i in range(actual.nrows()) for j in range(actual.ncols()))


def port(data):
    return seven_port_forcing_direction(**{key: amat(data[name]) for key, name in (
        ('trace_map', 'T'), ('state_direction', 'direction'), ('trace_shape', 'shape'),
        ('momentum', 'momentum'), ('force', 'force'), ('conormal', 'conormal'),
        ('momentum_mixed', 'mixed'), ('momentum_rate_direction', 'rate'))})


def test_complete_seven_rows_and_dynamic_kinematics(data):
    got = port(data)
    assert (got.nrows(), got.ncols()) == (7, 1)
    assert overlaps(got, data['b'])
    for key in ('shape', 'conormal', 'mixed', 'rate'):
        changed = dict(data); changed[key] = sp.zeros(*data[key].shape)
        assert not overlaps(port(changed), data['b'])


def test_direct_mixed_action_derivative_includes_constraint_source(data):
    assert data['f'] == (data['C'] * data['b']).col_join(-data['s'] * data['b'])
    assert data['f'][2] != 0
    assert (data['d'] * data['delta'][:2, :])[0] == (data['s'] * data['b'])[0]
    assert data['delta'][2] != 0  # Reaction remains in the solve.


def test_single_column_response_and_residual(data):
    got = solve_bulk_forcing_column(amat(data['H']), amat(data['f']))
    assert overlaps(got['response'], data['delta'])
    assert all(v.contains(0) for v in got['replay'].entries())


def test_same_owner_direct_physical_quadratic_equals_schur(data):
    assert sp.simplify(data['physical_direct'] - data['schur']) == 0
    got = real_stationary_impedance_column(amat(data['H']), amat(data['f']), str(data['qxx']))
    assert (got['schur'] - arb(str(data['schur']))).contains(0)
    assert got['difference'].contains(0)
    # The bordered block is indefinite although physical A is positive.
    assert data['A'].det() > 0 and data['H'].det() < 0


def test_signed_output_uses_existing_one_column_adjoint(data):
    got = reduce_seven_port(amat(data['H']), amat(data['f']),
                           {'control': dict(p=amat(data['gp']), n=amat(data['gn']))})
    assert overlaps(got['reduced'], data['gp'] + data['gn'] * data['delta'])
    assert all(v.contains(0) for v in got['adjoint_replay'].entries())


def test_moving_port_keeps_DB_reaction(data):
    got = moving_port_jet(amat(data['B']), amat(data['reaction']),
                         amat(data['reaction_dot']), [amat(data['Bdot'])])
    assert overlaps(got, data['moving_exact'])
    assert data['moving_exact'] != data['B'] * data['reaction_dot']


def test_residual_row_scaling_preserves_response_but_changes_naive_impedance(data):
    got = solve_bulk_forcing_column(amat(data['row_map'] * data['H']), amat(data['row_map'] * data['f']))
    assert overlaps(got['response'], data['delta'])
    assert sp.simplify(data['wrong_schur'] - data['schur']) != 0
    corrected = data['qxx'] + ((data['row_map'] * data['f']).T
                              * data['row_map'].T.LUsolve(data['delta']))[0]
    assert sp.simplify(corrected - data['schur']) == 0


def test_row_identification_requires_derivatives_away_from_stationarity():
    s, n = sp.symbols('s n')
    C = sp.Matrix([[2 + s, n], [0, 3 - s]])
    E = sp.Matrix([n + s, n - 2 * s])
    F = C * E
    assert sp.simplify(F.diff(s) - C * E.diff(s) - C.diff(s) * E) == sp.zeros(2, 1)
    assert sp.simplify(F.diff(n) - C * E.diff(n) - C.diff(n) * E) == sp.zeros(2, 1)
    assert (C.diff(s) * E).subs({s: 1, n: 2}) != sp.zeros(2, 1)


@pytest.mark.parametrize('forcing', [None, arb_mat(2, 1), arb_mat(3, 2)])
def test_no_missing_or_multiple_forcing_columns(data, forcing):
    with pytest.raises(ValueError):
        solve_bulk_forcing_column(amat(data['H']), forcing)


def test_missing_material_is_not_zero(data):
    kwargs = {key: amat(data[name]) for key, name in (
        ('trace_map', 'T'), ('state_direction', 'direction'), ('trace_shape', 'shape'),
        ('momentum', 'momentum'), ('force', 'force'), ('conormal', 'conormal'),
        ('momentum_mixed', 'mixed'), ('momentum_rate_direction', 'rate'))}
    kwargs['conormal'] = None
    with pytest.raises(ValueError):
        seven_port_forcing_direction(**kwargs)
