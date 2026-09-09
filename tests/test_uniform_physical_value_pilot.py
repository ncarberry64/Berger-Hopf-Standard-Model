"""Uniform domain propagation and failure handling; fixtures are not BHSM data."""
from contextlib import contextmanager
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import numpy as np
import pytest
from flint import arb, ctx, fmpq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_uniform_physical_value_pilot as p


def proof():
    return dict(validation_passed=True, normalized_eigenpair_enclosed=True,
        proposal_center_normalized_before_verification=True, positive_stored_reference_overlap=True,
        selected_zero_based_index_verified=24, spectral_index_verification=dict(validation_passed=True))


@pytest.fixture
def pilot(tmp_path, monkeypatch):
    previous = ctx.prec
    ctx.prec = 512
    monkeypatch.setattr(p, 'WORK', tmp_path)
    boxes = np.full((371, 99), arb(0), dtype=object)
    boxes[13, 0], boxes[14, 0] = arb(2, 1), arb(4, 1)
    source = dict(binding=dict(files={}, normalized_inputs={}, value_point_binding={}), boxes=boxes,
                  weights=np.ones(98), reference=np.ones(61), steps=np.ones(370))
    monkeypatch.setattr(p, 'load_inputs', lambda: source)
    monkeypatch.setattr(p, 'verify_sources', lambda expected: p.values.verify_binding(dict(files=expected['files'])))
    monkeypatch.setattr(p.df, 'file_key', lambda path: str(path))
    calls = []
    def evaluate(raw, source):
        assert raw.shape == (99,) and all(isinstance(v, arb) for v in raw)
        calls.append(raw.copy())
        return np.array([raw[0]**2]+[arb(1)]*98), proof()
    def center(stage, index, expected):
        x = arb(2 if index == 13 else 4) if stage == 'endpoint' else arb(fmpq(3, 2))
        return None, None, None, None, np.array([x**2]+[arb(1)]*98), {}
    monkeypatch.setattr(p, 'evaluate', evaluate)
    monkeypatch.setattr(p.df, 'point_inputs', center)
    monkeypatch.setattr(sys, 'argv', ['pilot', '--interval', '13'])
    yield source, calls, tmp_path/'interval_013'
    ctx.prec = previous


def test_all_three_uniform_evaluations_and_genuine_repeat(pilot, monkeypatch):
    source, calls, directory = pilot
    p.main()
    assert len(calls) == 3
    # Both endpoints retain unit uncertainty. Nonlinear endpoint rates
    # propagate to a midpoint containing zero, unlike center-only rates.
    assert calls[0][0].contains(arb(1)) and calls[0][0].contains(arb(3))
    assert calls[1][0].contains(arb(3)) and calls[1][0].contains(arb(5))
    assert calls[2][0].contains(arb(0))
    first = {q.name: q.read_bytes() for q in directory.iterdir()}
    monkeypatch.setattr(sys, 'argv', ['pilot', '--interval', '13', '--recompute'])
    p.main()
    assert len(calls) == 6
    assert all((directory/name).read_bytes() == data for name, data in first.items())
    receipt = json.loads((directory/'reproduction.json').read_text())
    assert receipt['byte_identical'] and receipt['independent_recomputation'] and receipt['points'] == 3
    assert not receipt['neighborhood_remainder_enclosed']
    _, record = p.read_point(directory, 'midpoint', 13, source, p.point_domain(directory, 'midpoint', 13, source)[1])
    assert record['uniform_endpoint_rates_used_for_midpoint']
    assert not record['pointwise_rate_substituted_for_uniform_rate']


def test_endpoint_failure_preserves_attempted_domain_and_stops_midpoint(pilot, monkeypatch):
    source, _, directory = pilot
    def fail(raw, source):
        error = ArithmeticError('interval bordered solve unresolved')
        error.eigenpair_inclusion = {'validation_passed': False}
        raise error
    monkeypatch.setattr(p, 'evaluate', fail)
    with pytest.raises(ArithmeticError, match='bordered solve'):
        p.main()
    assert not (directory/'manifest.json').exists()
    assert not list(directory.glob('midpoint*'))
    attempts = list(directory.glob('endpoint_013.attempt_*.json'))
    assert len(attempts) == 1
    failure = json.loads(attempts[0].read_text())
    assert failure['method_failure_does_not_prove_domain_singular']
    assert failure['eigenpair_inclusion']['validation_passed'] is False
    with np.load(attempts[0].with_suffix('.npz')) as data:
        raw = p.hs.restore_balls(data['raw_domain_mid_q'], data['raw_domain_rad_q'])
        assert raw[0].contains(source['boxes'][13, 0])


def test_repeat_failure_archives_old_receipt_and_retains_candidate(pilot, monkeypatch):
    _, _, directory = pilot
    p.main()
    monkeypatch.setattr(sys, 'argv', ['pilot', '--interval', '13', '--recompute'])
    p.main()
    monkeypatch.setattr(p, 'evaluate', lambda raw, source: (np.array([arb(0, 100)]*99), proof()))
    with pytest.raises(ArithmeticError, match='differs'):
        p.main()
    assert not (directory/'reproduction.json').exists()
    assert list(directory.glob('reproduction.before_attempt_*.json'))
    assert list(directory.glob('endpoint_013.attempt_*.candidate.npz'))


def test_nonoverlapping_center_rate_cannot_publish(pilot, monkeypatch):
    _, _, directory = pilot
    monkeypatch.setattr(p, 'evaluate', lambda raw, source: (np.array([arb(999)]*99), proof()))
    with pytest.raises(ArithmeticError, match='overlap'):
        p.main()
    assert not (directory/'endpoint_013.npz').exists()
    assert not (directory/'reproduction.json').exists()


def test_midpoint_requires_uniform_endpoint_records_not_center_cache(pilot):
    source, _, directory = pilot
    directory.mkdir()
    with pytest.raises(FileNotFoundError):
        p.point_domain(directory, 'midpoint', 13, source)


def test_changed_endpoint_proof_prevents_midpoint(pilot):
    source, _, directory = pilot
    p.main()
    path = directory/'endpoint_013.json'
    record = json.loads(path.read_text())
    record['eigenpair_inclusion']['spectral_index_verification']['validation_passed'] = False
    path.write_bytes(p.geometry.encoded(record))
    with pytest.raises(RuntimeError, match='proof changed'):
        p.point_domain(directory, 'midpoint', 13, source)


def test_source_mutation_during_field_evaluation_prevents_publication(pilot, monkeypatch, tmp_path):
    source, _, directory = pilot
    kernel = tmp_path/'kernel.py'
    kernel.write_text('original')
    source['binding']['files'][str(kernel)] = p.values.sha(kernel)
    def mutate(raw, source):
        kernel.write_text('changed')
        return np.array([arb(0, 100)]*99), proof()
    monkeypatch.setattr(p, 'evaluate', mutate)
    with pytest.raises(RuntimeError, match='input changed'):
        p.main()
    assert not (directory/'endpoint_013.npz').exists()


def test_preflight_never_calls_numerical_kernel(pilot, monkeypatch, capsys):
    _, calls, directory = pilot
    monkeypatch.setattr(sys, 'argv', ['pilot', '--interval', '13', '--preflight'])
    p.main()
    assert calls == [] and not directory.exists()
    assert json.loads(capsys.readouterr().out)['numerical_field_evaluated'] is False


def test_evaluate_preserves_interval_operands_and_requires_independent_proof(monkeypatch):
    @contextmanager
    def checked(cert, checks, **kwargs):
        assert kwargs == dict(expected_index=24, normalize_proposal_center=True)
        checks.append(proof())
        yield
    raw = np.array([arb(2, 1)]*99)
    def kernel(state, descriptor, weights, reference, directions):
        assert all(v.contains(arb(1)) and v.contains(arb(3)) for v in state)
        assert descriptor.contains(arb(1)) and descriptor.contains(arb(3))
        assert directions is None
        return SimpleNamespace(value=[arb(1)]*99)
    monkeypatch.setattr(p.hs, 'verified_eigenline', checked)
    monkeypatch.setattr(p.values.cert, '_rate_enclosure', kernel)
    assert p.evaluate(raw, dict(weights=np.ones(98), reference=np.ones(61)))[1] == proof()


def test_real_verifier_handles_an_entire_symmetric_matrix_family():
    # This is an independently checkable synthetic matrix family, not a
    # substituted physical Hessian or evidence that the BHSM pilot passes.
    def proposal(*args):
        return np.array([arb(1, '.02'), arb(0, '.02')]), arb(1, '.02'), 2., 0.
    cert = SimpleNamespace(_eigenline=proposal, QDIM=0)
    matrix = np.array([[arb(1, '.01'), arb(0)], [arb(0), arb(3)]])
    checks = []
    with p.hs.verified_eigenline(cert, checks, expected_index=0, normalize_proposal_center=True):
        cert._eigenline(matrix, np.diag([1., 3.]), [1., 0.])
    assert checks[0]['normalized_eigenpair_enclosed']
    assert checks[0]['spectral_index_verification']['validation_passed']


@pytest.mark.parametrize('field', ['validation_passed', 'normalized_eigenpair_enclosed',
    'proposal_center_normalized_before_verification', 'positive_stored_reference_overlap'])
def test_missing_uniform_eigenpair_proof_field_rejected(field):
    record = proof()
    del record[field]
    assert not p.proof_valid(record)


@pytest.fixture
def geometry_pair(tmp_path, monkeypatch):
    monkeypatch.setattr(p.geometry, 'WORK', tmp_path)
    monkeypatch.setattr(p.geometry, 'TRIAL_RADII', tmp_path/'trial.json')
    p.geometry.TRIAL_RADII.write_text(json.dumps({'stored_polynomial_adjudication': {'witness': {'radius': [1., 2.]}}}))
    monkeypatch.setattr(p.df, 'file_key', lambda path: str(path))
    monkeypatch.setattr(p.geometry.residual.foundation.coordinate, '_verified_inputs', lambda r: r['inputs'])
    paths = (Path(p.geometry.__file__), p.geometry.THEORY, p.geometry.TRIAL_RADII,
             Path(p.geometry.neighborhood.__file__), Path(p.geometry.neighborhood.preserve_ball.__code__.co_filename))
    arrays = {key+suffix: np.full((371, 99), '0') for key in ('weighted_box', 'raw_box', 'coordinate_displacement_radius')
              for suffix in ('_mid_q', '_rad_q')}
    np.savez_compressed(tmp_path/'endpoints.npz', **arrays)
    record = dict(algorithm=p.geometry.ALGORITHM, precision_bits=512,
        scope='FROZEN_AFFINE_TRIAL_ENDPOINT_DOMAIN_GEOMETRY', endpoints=list(range(371)), shape=[371, 99],
        initial_endpoint_fixed=True, transverse_domain='FULL_COORDINATE_SPACE_SUPERSET',
        axis_normalization_assumed=False, weighted_center_product_rounding_enclosed=True,
        radii_status='TRIAL_RADII_FROM_OLD_CONDITIONAL_POLYNOMIAL_NOT_RECERTIFIED',
        radii_exact_binary64_rationals=['1', '2'],
        runtime=dict(python=sys.version, numpy=np.__version__, python_flint=p.values.flint.__version__),
        raw_input_SHA256={str(q): p.values.sha(q) for q in paths}, inputs={},
        data_SHA256=p.values.sha(tmp_path/'endpoints.npz'))
    def write():
        (tmp_path/'endpoints.json').write_bytes(p.geometry.encoded(record))
        (tmp_path/'reproduction.json').write_bytes(p.geometry.encoded(dict(byte_identical=True,
            independent_recomputation=True, endpoints=371, record_SHA256=p.values.sha(tmp_path/'endpoints.json'))))
    write()
    return tmp_path, record, arrays, write


def test_complete_geometry_reader_and_runtime_binding(geometry_pair):
    _, record, _, _ = geometry_pair
    loaded, boxes, sources = p.load_geometry()
    assert loaded == record and boxes.shape == (371, 99)
    assert set(record['raw_input_SHA256']) <= set(sources)


@pytest.mark.parametrize('change', ['coverage', 'receipt', 'runtime', 'source', 'array', 'negative_displacement'])
def test_invalid_geometry_cannot_reach_uniform_kernel(geometry_pair, change):
    path, record, arrays, write = geometry_pair
    if change == 'coverage': record['endpoints'].pop()
    elif change == 'runtime': record['runtime']['python_flint'] = 'changed'
    elif change == 'source': record['raw_input_SHA256'][str(Path(p.geometry.neighborhood.preserve_ball.__code__.co_filename))] = 'changed'
    elif change == 'array': arrays.pop('weighted_box_rad_q')
    elif change == 'negative_displacement':
        arrays['coordinate_displacement_radius_mid_q'] = np.full((371, 99), '-1')
    if change in ('array', 'negative_displacement'):
        np.savez_compressed(path/'endpoints.npz', **arrays)
        record['data_SHA256'] = p.values.sha(path/'endpoints.npz')
    write()
    if change == 'receipt':
        receipt = json.loads((path/'reproduction.json').read_text())
        receipt['independent_recomputation'] = False
        (path/'reproduction.json').write_bytes(p.geometry.encoded(receipt))
    with pytest.raises(RuntimeError):
        p.load_geometry()
