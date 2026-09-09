"""Derivative pilot domain, direction, provenance and reproduction tests."""
from contextlib import nullcontext
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import numpy as np
import pytest
from flint import arb, ctx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_uniform_physical_derivative_pilot as p


def proof():
    return dict(validation_passed=True, normalized_eigenpair_enclosed=True,
        proposal_center_normalized_before_verification=True, positive_stored_reference_overlap=True,
        selected_zero_based_index_verified=24, spectral_index_verification=dict(validation_passed=True))


@pytest.fixture
def field(tmp_path, monkeypatch):
    previous = ctx.prec
    ctx.prec = 512
    monkeypatch.setattr(p, 'WORK', tmp_path)
    monkeypatch.setattr(p.pilot, 'verify_sources', lambda b: p.pilot.values.verify_binding(dict(files=b['files'])))
    raw = np.array([arb(0)]*99, dtype=object)
    raw[0], raw[98] = arb(2, 1), arb(3, 1)
    context = dict(binding=dict(interval=13, files={}, normalized_inputs={}), stage='midpoint', index=13,
        weighted=raw.copy(), raw=raw, state=raw[:98], descriptor=raw[98], weights=np.ones(98),
        reference=np.ones(61), reference_value=np.array([arb(0, 100), arb(0, 100)]+[arb(0)]*97))
    bases, calls = [], []
    def base(cert, state, reference):
        assert all(isinstance(v, arb) for v in state)
        assert state[0].contains(arb(1)) and state[0].contains(arb(3))
        bases.append(state.copy())
        return SimpleNamespace(use=lambda: nullcontext(), eigenpair_verification=proof())
    def rate(state, descriptor, weights, reference, directions):
        assert directions.shape == (99, 99)
        assert all(v.is_exact() and v == int(i == j) for (i, j), v in np.ndenumerate(directions))
        x, d = state[0], descriptor
        value = np.array([x**3+x*d**2, x*d]+[arb(0)]*97)
        derivative = np.full((99, 99), arb(0), dtype=object)
        derivative[0, 0], derivative[0, 98] = 3*x**2+d**2, 2*x*d
        derivative[1, 0], derivative[1, 98] = d, x
        calls.append('DF')
        return SimpleNamespace(value=value, derivative=derivative)
    def second(state, descriptor, weights, reference, axis, directions):
        assert all(v.is_exact() and v == int(i == 0) for i, v in enumerate(axis))
        assert directions.shape == (99, 2)
        assert all(v.is_exact() and v == int(i == (0, 98)[j]) for (i, j), v in np.ndenumerate(directions))
        result = np.full((99, 2), arb(0), dtype=object)
        result[0, 0], result[0, 1], result[1, 1] = 6*state[0], 2*descriptor, arb(1)
        calls.append('H')
        return result
    monkeypatch.setattr(p.hessian.base, 'VerifiedHessianBase', base)
    monkeypatch.setattr(p.hessian.df.sparse, 'use_optimized_mixed', lambda *a: nullcontext())
    monkeypatch.setattr(p.hessian.bulk, 'use_bulk_matrices', lambda *a: nullcontext())
    monkeypatch.setattr(p.hessian.factored, 'use_ball_factored_integrand', lambda *a: nullcontext())
    monkeypatch.setattr(p.hessian.graph.cert, '_rate_enclosure', rate)
    monkeypatch.setattr(p.hessian.graph, 'batched_axis_map', second)
    yield context, bases, calls
    ctx.prec = previous


def test_full_DF_and_selected_H_enclose_cubic_field_corner_derivatives(field):
    context, bases, calls = field
    result, report = p.evaluate(context, 0, [0, 98])
    for x in (1, 2, 3):
        for d in (2, 3, 4):
            assert result['DF'][0, 0].contains(arb(3*x*x+d*d))
            assert result['DF'][0, 98].contains(arb(2*x*d))
            assert result['H'][0, 0].contains(arb(6*x))
            assert result['H'][0, 1].contains(arb(2*d))
            assert result['H'][1, 1] == 1
    assert len(bases) == 1 and calls == ['DF', 'H'] and p.pilot.proof_valid(report)


def test_repeat_rebuilds_base_DF_H_and_produces_identical_scientific_bytes(field):
    context, bases, calls = field
    path = p.materialize(context, 0, [0, 98])
    before = path.read_bytes(), path.with_suffix('.json').read_bytes()
    p.materialize(context, 0, [0, 98], True)
    assert before == (path.read_bytes(), path.with_suffix('.json').read_bytes())
    assert len(bases) == 2 and calls == ['DF', 'H', 'DF', 'H']
    receipt = json.loads(path.with_suffix('.reproduction.json').read_text())
    assert receipt['byte_identical'] and receipt['independent_recomputation']
    assert not receipt['full_point_Hessian_enclosed']
    record = p.read_result(path, context, 0, [0, 98])
    assert record['uniform_ambient_Jacobian_enclosed'] and not record['neighborhood_remainder_enclosed']


def test_failed_new_box_eigenpair_keeps_attempted_domain(field, monkeypatch):
    context, _, calls = field
    def fail(*args):
        error = ArithmeticError('new outer-box eigenpair unresolved')
        error.eigenpair_inclusion = dict(validation_passed=False)
        raise error
    monkeypatch.setattr(p.hessian.base, 'VerifiedHessianBase', fail)
    with pytest.raises(ArithmeticError, match='outer-box'):
        p.materialize(context, 0, [0, 98])
    path = p.output_path(context, 0, [0, 98])
    assert not path.exists() and calls == []
    attempts = list(path.parent.glob('*.attempt_*.json'))
    assert len(attempts) == 1
    report = json.loads(attempts[0].read_text())
    assert report['method_failure_does_not_prove_domain_singular']
    with np.load(attempts[0].with_suffix('.npz')) as data:
        raw = p.pilot.hs.restore_balls(data['raw_domain_mid_q'], data['raw_domain_rad_q'])
        assert raw[0].contains(context['raw'][0]) and raw[98].contains(context['raw'][98])


@pytest.mark.parametrize('bad', ['DF_shape', 'DF_nonfinite', 'H_shape', 'H_nonfinite', 'value_overlap', 'proof'])
def test_invalid_uniform_derivative_cannot_publish(field, monkeypatch, bad):
    context, _, _ = field
    if bad == 'proof':
        invalid = proof()
        invalid['normalized_eigenpair_enclosed'] = False
        monkeypatch.setattr(p.hessian.base, 'VerifiedHessianBase', lambda *a: SimpleNamespace(eigenpair_verification=invalid))
    elif bad.startswith('H'):
        shape = (98, 2) if bad == 'H_shape' else (99, 2)
        monkeypatch.setattr(p.hessian.graph, 'batched_axis_map', lambda *a: np.full(shape, arb('nan') if bad.endswith('nonfinite') else arb(0)))
    else:
        shape = (99, 98) if bad == 'DF_shape' else (99, 99)
        monkeypatch.setattr(p.hessian.graph.cert, '_rate_enclosure', lambda *a: SimpleNamespace(
            value=np.array([arb(999)]*99) if bad == 'value_overlap' else context['reference_value'],
            derivative=np.full(shape, arb('nan') if bad.endswith('nonfinite') else arb(0))))
    with pytest.raises(ArithmeticError):
        p.materialize(context, 0, [0, 98])
    assert not p.output_path(context, 0, [0, 98]).exists()


def test_changed_repeat_preserves_candidate_and_archives_old_receipt(field, monkeypatch):
    context, _, _ = field
    path = p.materialize(context, 0, [0, 98])
    p.materialize(context, 0, [0, 98], True)
    monkeypatch.setattr(p.hessian.graph, 'batched_axis_map', lambda *a: np.full((99, 2), arb(42)))
    with pytest.raises(ArithmeticError, match='differs'):
        p.materialize(context, 0, [0, 98], True)
    assert not path.with_suffix('.reproduction.json').exists()
    assert list(path.parent.glob('*.reproduction.before_attempt_*.json'))
    assert list(path.parent.glob('*.candidate.npz')) and list(path.parent.glob('*.candidate.json'))


def test_source_change_during_evaluation_prevents_publication(field, monkeypatch, tmp_path):
    context, _, _ = field
    kernel = tmp_path/'kernel.py'
    kernel.write_text('original')
    context['binding']['files'][str(kernel)] = p.pilot.values.sha(kernel)
    def mutate(*args):
        kernel.write_text('changed')
        return np.full((99, 2), arb(1))
    monkeypatch.setattr(p.hessian.graph, 'batched_axis_map', mutate)
    with pytest.raises(RuntimeError, match='input changed'):
        p.materialize(context, 0, [0, 98])
    assert not p.output_path(context, 0, [0, 98]).exists()


def test_context_unweights_the_reconstructed_weighted_domain_and_rejects_other_points(monkeypatch):
    weighted = np.array([arb(2, 1)]*99)
    source = dict(binding=dict(files={}, normalized_inputs={}, runtime={}, trial_radii_rational=['1', '2'],
                              value_point_binding={}), weights=np.full(98, 2.), reference=np.ones(61))
    domains = {('midpoint', 13): dict(weighted_domain=weighted, raw_domain=np.array([arb(1)]*99), value=np.array([arb(0)]*99))}
    monkeypatch.setattr(p, 'paired_uniform_source', lambda i: (source, domains, {}))
    monkeypatch.setattr(p.hessian, 'binding', lambda: dict(value_point_binding={}, files={}))
    monkeypatch.setattr(p.pilot, 'verify_sources', lambda b: None)
    context = p.point_context(13, 'midpoint', 13)
    assert context['state'][0].contains(arb('.5')) and context['state'][0].contains(arb('1.5'))
    assert context['descriptor'].contains(arb(1)) and context['descriptor'].contains(arb(3))
    with pytest.raises(ValueError, match='belong'):
        p.point_context(13, 'midpoint', 14)


def test_preflight_rejects_missing_uniform_pair_without_action_evaluation(monkeypatch, tmp_path):
    monkeypatch.setattr(p.pilot, 'WORK', tmp_path)
    monkeypatch.setattr(p.pilot, 'load_inputs', lambda: {})
    monkeypatch.setattr(p.hessian.base, 'VerifiedHessianBase', lambda *a: pytest.fail('no action evaluation allowed'))
    with pytest.raises(FileNotFoundError):
        p.paired_uniform_source(13)
