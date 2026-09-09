"""Check operand preservation and an independent analytic Hessian fixture."""
import ast
import inspect
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest
import sympy as sp
from flint import arb, ctx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_ball_physical_hessian_graph as graph
from bhsm.interface import ball_factored_arb_integrand as factored
from bhsm.interface import factored_arb_integrand as original_factored
from bhsm.interface.bulk_arb_matrices import to_matrix, to_array
from bhsm.interface.physical_arb_inputs import preserve_ball, same_ball_vector


def test_entire_graph_diff_is_exactly_three_operand_conversions():
    parent = inspect.getsource(graph.parent.batched_axis_map)
    assert parent.count('arb(float(value))') == 2
    assert parent.count('arb(float(state[cert.QDIM + i]))') == 1
    expected = parent.replace('arb(float(value))', 'preserve_ball(value)').replace(
        'arb(float(state[cert.QDIM + i]))', 'preserve_ball(state[cert.QDIM + i])')
    assert ast.dump(ast.parse(expected)) == ast.dump(ast.parse(inspect.getsource(graph.batched_axis_map)))


def test_factored_graph_diff_is_only_ball_preservation_and_cache_equality():
    expected = inspect.getsource(original_factored.use_factored_integrand)
    expected = expected.replace('def use_factored_integrand(', 'def use_ball_factored_integrand(')
    expected = expected.replace('selected=tuple(arb(float(v)) for v in state)',
                                'selected=tuple(preserve_ball(v) for v in state)')
    expected = expected.replace('any(not arb(v)==s for v,s in zip(state_values,selected))',
                                'not same_ball_vector(state_values,selected)')
    assert ast.dump(ast.parse(expected)) == ast.dump(ast.parse(inspect.getsource(factored.use_ball_factored_integrand)))


def test_ball_copy_and_cache_equality_do_not_erase_uncertainty():
    value = arb(1, .125)
    copied = preserve_ball(value)
    assert copied.mid() == value.mid() and copied.rad() == value.rad()
    assert same_ball_vector([value], [copied])
    assert not same_ball_vector([value], [value.mid()])
    assert not same_ball_vector([value], [arb(1, .25)])
    assert preserve_ball(2**60+1) == arb(2**60+1)
    assert not same_ball_vector([value], [])
    for bad in (arb('nan'), float('inf'), '1', True):
        with pytest.raises(ValueError):
            preserve_ball(bad)


def test_factored_interval_geometry_encloses_corners_and_restores_parent():
    parent = graph.cert
    original = parent._integrand
    previous = ctx.prec
    ctx.prec = 256
    state = np.array([arb(0) for _ in range(parent.STATE)], dtype=object)
    state[0] = arb(0, .001)
    try:
        with factored.use_ball_factored_integrand(parent, state):
            actual = parent._integrand(state.copy(), 42, 0)
            for corner in (-.001, .001):
                point = state.copy(); point[0] = arb(corner)
                expected = original(point, 42, 0)
                assert actual.bulk.d[0].contains(expected.bulk.d[0])
                assert actual.inertia.d[0].contains(expected.inertia.d[0])
            changed = state.copy(); changed[0] = arb(0, .002)
            with pytest.raises(RuntimeError, match='state'):
                parent._integrand(changed, 42, 0)
            ctx.prec = 192
            with pytest.raises(RuntimeError, match='precision'):
                parent._integrand(state, 42, 0)
    finally:
        ctx.prec = previous
    assert parent._integrand is original


def test_fifth_order_factored_interval_jets_enclose_point_corners():
    parent = graph.cert
    previous = ctx.prec; ctx.prec = 256
    state = np.array([arb(0) for _ in range(parent.STATE)], dtype=object)
    state[0] = arb(0, 1e-6)
    rng = np.random.default_rng(491)
    legs = [np.array([arb(float(v)) for v in rng.normal(size=13)/8], dtype=object) for _ in range(5)]
    original = parent._integrand
    try:
        with factored.use_ball_factored_integrand(parent, state):
            actual = parent._integrand(state, 42, 5, legs)
        for corner in (-1e-6, 1e-6):
            point = state.copy(); point[0] = arb(corner)
            expected = original(point, 42, 5, legs)
            assert len(actual.bulk.d) == 32
            for enclosed, exact in ((actual.bulk, expected.bulk), (actual.inertia, expected.inertia)):
                assert all(a.contains(b) for a,b in zip(enclosed.d,exact.d,strict=True))
    finally:
        ctx.prec = previous
    assert parent._integrand is original


def test_complete_ball_graph_encloses_analytic_normalized_rate_hessian(monkeypatch):
    # A two-state quadratic action makes all action derivatives >=3 zero.
    # Its retained graph reduces exactly to f=(s*q,p,0)/sqrt(s*s*q*q+p*p).
    def zeros(shape):
        return np.full(shape, arb(0), dtype=object)
    toy = SimpleNamespace(STATE=2, QDIM=1, REDUCED=1,
        _mat=to_matrix, _array=to_array,
        _arb_dot=lambda a,b: sum((x*y for x,y in zip(a,b,strict=True)), arb(0)),
        metric_data=lambda: ([1], [1], None, None))
    def jets(state):
        return SimpleNamespace(dense_maps=[], gradient_arb=np.array([state[0], 2*state[1]], dtype=object),
            hessian_arb=np.array([[arb(1),arb(0)],[arb(0),arb(2)]],dtype=object), hessian_mid=None)
    toy._arb_action_jets = jets
    toy._eigenline = lambda *_: (np.array([arb(1)],dtype=object), arb(2), None, None)
    monkeypatch.setattr(graph, 'cert', toy)
    monkeypatch.setattr(graph, 'OUTPUTS', 3)
    monkeypatch.setattr(graph, '_solve', lambda k,rhs: to_array(k.solve(to_matrix(rhs))))
    monkeypatch.setattr(graph, '_batch_fixed', lambda *a: (zeros((1,3)),zeros((1,3,3)),zeros((1,3,3))))
    monkeypatch.setattr(graph, '_batch_first', lambda *a: tuple(zeros((1,3)) for _ in range(6)))
    monkeypatch.setattr(graph, '_affine_contraction', lambda *a: zeros((2,3)))
    monkeypatch.setattr(graph, '_batch_scalar', lambda *a: (zeros(2),zeros(2),zeros((3,2)),zeros((3,2))))
    previous = ctx.prec; ctx.prec = 256
    try:
        state = np.array([arb(2, .001), arb(3, .001)], dtype=object)
        descriptor = arb(1, .001)
        directions = np.array([[arb(int(i==j)) for j in range(3)] for i in range(3)], dtype=object)
        # Also preserve uncertainty in an input direction; all corner axes are
        # checked against a separately symbolically differentiated expression.
        axis = directions[:,0].copy(); axis[1] = arb(0, .001); axis[2] = arb(.25)
        result = graph.batched_axis_map(state, descriptor, np.ones(2), np.ones(1), axis, directions)
        p,q,s = sp.symbols('p q s', positive=True)
        norm = sp.sqrt(s*s*q*q+p*p)
        funcs = [s*q/norm, p/norm, sp.Integer(0)]
        hessians = [sp.lambdify((p,q,s), sp.hessian(f,(p,q,s)).tolist(),
                     modules=[{'sqrt':lambda value:value.sqrt()}]) for f in funcs]
        for dp in (-.001, .001):
            for dq in (-.001, .001):
                for ds in (-.001, .001):
                    for da in (-.001, .001):
                        point = [arb(2)+arb(dp), arb(3)+arb(dq), arb(1)+arb(ds)]
                        for output, expression in enumerate(hessians):
                            h = expression(*point)
                            for column in range(3):
                                expected = arb(h[0][column])+arb(da)*arb(h[1][column])+arb(.25)*arb(h[2][column])
                                assert result[output,column].contains(expected)
    finally:
        ctx.prec = previous
