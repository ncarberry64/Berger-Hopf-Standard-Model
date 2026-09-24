import copy
import importlib.util
from pathlib import Path
import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.input_linear_taylor import vector_norm
from bhsm.interface.shared_parameter_residual import linear_support
from bhsm.interface.joint_output_support import joint_constant_support


def load_verifier():
    path = Path(__file__).resolve().parents[1] / 'scripts/verify_n12_gate7_coupled_transport_bounds.py'
    spec = importlib.util.spec_from_file_location('transport_bound_replay', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def upper(value):
    value = arb(value).upper()
    return {'exact': str(value.fmpq()), 'approximate': float(value)}


@pytest.fixture
def example():
    previous = ctx.prec
    ctx.prec = 512
    groups = [[0, 74, 'euclidean'], [74, 322, 'box']]
    original, pulled = arb_mat(74, 322), arb_mat(74, 322)
    for i in range(74):
        original[i, i] = pulled[i, i] = arb(1) / 32
    # A shared pair that cancels after the same physical-input substitution.
    original[0, 74], original[0, 75] = arb(1) / 8, -arb(1) / 8
    long = arb_mat(1, 322)
    long[0, 0] = arb(1) / 64
    rows = []
    for i in range(74):
        c = linear_support([pulled[i, j] for j in range(322)], groups)
        rows.append(dict(component=i, support=upper(c + arb(1)/2048 + arb(1)/4096),
                         linear=upper(arb(1)/2048), nonlinear=upper(arb(1)/4096),
                         longitudinal_input_support=upper(arb(1)/8192)))
    ln = vector_norm([arb(row['linear']['exact']) for row in rows])
    rn = vector_norm([arb(row['nonlinear']['exact']) for row in rows])
    old, new = [joint_constant_support(m, groups) for m in (original, pulled)]
    total = min(vector_norm([arb(row['support']['exact']) for row in rows]),
                (min(old, new) + ln + rn).upper())
    long_support = arb(1)/64 + arb(1)/1024 + arb(1)/2048
    axis = vector_norm([arb(row['longitudinal_input_support']['exact']) for row in rows])
    bounds = [[arb(1)/512, long_support], [axis, total]]
    radii = [arb(1)/8, arb(1)/32]
    weighted = [(sum((bounds[i][j]*radii[j] for j in range(2)), arb(0))/radii[i]).upper()
                for i in range(2)]
    record = dict(algorithm='FULL_INPUT_COUPLED_NUMERATOR_HS_TRANSPORT_V1',
                  physical_input_columns=74, projected_output_rows=74, input_groups=groups,
                  full_history_certified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
                  two_radius_global_contraction_inferred=False, rows=rows,
                  joint_original_constant_support=upper(old), joint_pulled_constant_support=upper(new),
                  linear_vector_bound=upper(ln), nonlinear_vector_bound=upper(rn),
                  complete_local_right_block_norm_upper=upper(total), strict_local_gain_below_one=bool(total<1),
                  longitudinal_input_transverse_output_norm_upper=upper(axis),
                  longitudinal_output=dict(support=upper(long_support), linear=upper(arb(1)/1024),
                      nonlinear=upper(arb(1)/2048), longitudinal_input_support=upper(arb(1)/512)),
                  local_fixed_axis_two_radius_majorant=dict(
                      row_order=['longitudinal_output', 'transverse_output'],
                      column_order=['longitudinal_input', 'Euclidean_superset_of_transverse_input'],
                      all_history_intervals_covered=False, physical_quotient_identification_inferred=False,
                      original_trial_radii_exact=[str(v.fmpq()) for v in radii],
                      bounds=[[upper(v) for v in row] for row in bounds],
                      weighted_row_bounds=[upper(v) for v in weighted],
                      strict_local_weighted_gain_below_one=bool(max(weighted)<1)))
    payload = {name: [[str(v.mid().fmpq()), str(v.rad().fmpq())] for v in matrix.entries()]
               for name, matrix in [('original', original), ('pulled', pulled),
                                    ('longitudinal_original', long), ('longitudinal_pulled', long)]}
    try:
        yield record, payload
    finally:
        ctx.prec = previous


def test_shared_constant_and_weighted_majorant_replay(example):
    result = load_verifier().verify(*example)
    assert result['all_74_output_supports_replayed']
    assert result['fixed_axis_two_radius_majorant_replayed']
    assert result['Gate7_closed'] is False


def test_small_euclidean_norm_does_not_certify_anisotropic_contraction(example):
    record, payload = copy.deepcopy(example)
    majorant = record['local_fixed_axis_two_radius_majorant']
    radii = [arb(1)/8, arb(1)/131072]
    majorant['original_trial_radii_exact'] = [str(v.fmpq()) for v in radii]
    weighted = [(sum((arb(majorant['bounds'][i][j]['exact'])*radii[j]
                      for j in range(2)), arb(0))/radii[i]).upper() for i in range(2)]
    majorant['weighted_row_bounds'] = [upper(v) for v in weighted]
    majorant['strict_local_weighted_gain_below_one'] = False
    module = load_verifier()
    result = module.verify(record, payload)
    assert result['local_norm_upper'] < 1
    assert max(result['local_weighted_rows_upper']) > 1
    majorant['strict_local_weighted_gain_below_one'] = True
    with pytest.raises(ArithmeticError, match='two-radius strictness'):
        module.verify(record, payload)


@pytest.mark.parametrize('corruption', ['component', 'constant', 'weighted', 'claim'])
def test_replay_rejects_missing_dependency_or_false_verdict(example, corruption):
    record, payload = copy.deepcopy(example)
    if corruption == 'component':
        record['rows'][12]['component'] = 13
    elif corruption == 'constant':
        payload['pulled'][0] = ['1', '0']
    elif corruption == 'weighted':
        record['local_fixed_axis_two_radius_majorant']['weighted_row_bounds'][1] = upper(0)
    else:
        record['Gate7_closed'] = True
    with pytest.raises((ValueError, ArithmeticError)):
        load_verifier().verify(record, payload)
