"""Focused algebra checks; no physical action or atlas calculations."""
from pathlib import Path
import hashlib
import json

import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.shared_hs_output_operator import (
    composed_operators, evaluate_same_leaves, projected_operator)


@pytest.fixture(autouse=True)
def precision():
    old = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = old


def test_same_endpoint_cancels_between_direct_and_incidence_terms():
    # h=1/4, A=-2/h makes the complete H0 coefficient zero. Boxing the
    # two occurrences separately loses this identity even for one output.
    h = arb(1)/4
    P, A = arb_mat([[1]]), arb_mat([[-8]])
    x = arb_mat([[arb(0, 100)]])
    zero = arb_mat([[0]])
    got = evaluate_same_leaves(composed_operators(P, A, h), (x, zero, zero))
    assert got[0, 0].contains(0) and abs(got[0, 0]).upper() < arb('1e-60')
    separate = h*P*x/6 + h*h*P*A*x/12
    assert separate[0, 0].rad() > 1


def test_output_projection_preserves_shared_row_cancellation():
    # Two equal output rows depend on the same uncertain input. Projecting
    # the rows after enclosure would count them independently.
    P = arb_mat([[1], [1]])
    axis = arb_mat([[1], [-1]])
    L, T = projected_operator(P, axis)
    leaf = arb_mat([[arb(0, 10)]])
    assert (L*leaf)[0, 0].is_zero()
    assert not (axis.transpose()*(P*leaf))[0, 0].is_zero()
    assert T == P


def test_fused_operator_matches_exact_hs_chain_rule():
    h = arb(1)/4
    P = arb_mat([[2, -3], [1, 4]])
    A = arb_mat([[3, 5], [-7, 2]])
    leaves = [arb_mat([[x], [y]]) for x, y in ((2, 3), (5, 7), (11, 13))]
    got = evaluate_same_leaves(composed_operators(P, A, h), leaves)
    msecond = h*(leaves[0]-leaves[2])/8
    expected = h*P*(leaves[0]+4*(leaves[1]+A*msecond)+leaves[2])/6
    assert all((x-y).contains(0) for x, y in zip(got.entries(), expected.entries()))


def test_incomplete_site_or_output_rejected():
    P, A = arb_mat([[1]]), arb_mat([[1]])
    with pytest.raises(ValueError):
        evaluate_same_leaves(composed_operators(P, A, arb(1)), [P, P])
    with pytest.raises(ValueError):
        composed_operators(arb_mat([[1, 2]]), A, arb(1))
    with pytest.raises(ValueError):
        projected_operator(P, arb_mat([[1], [0]]))


def test_frozen_correlation_audit_is_reproduced_and_not_promoted():
    root = Path(__file__).resolve().parents[1]
    package = root/'artifacts/flagship_integration/gate7_layer_c_correlation_20260924'
    first, repeat = (package/name for name in ('first.json', 'repeat.json'))
    assert first.read_bytes() == repeat.read_bytes()
    z = json.loads(first.read_bytes())
    assert z['frozen_checkpoint'] == 'baf41b96'
    assert z['Layer_B_cover_reused'] and z['new_action_evaluations'] == 0
    assert not z['full_Layer_C_certificate_produced']
    assert not z['physical_budget_debit'] and not z['Gate7_closed']
    assert not z['intervals14_to18_evaluated']
    assert z['global_kappa_L'] is None and z['global_kappa_T'] is None
    assert not z['cellwise_absolute_sum_present_in_old_code']
    for p, digest in z['source_SHA256'].items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest().upper() == digest
    assert all(a['approximate'] < b['approximate'] for a, b in zip(
        z['recovered_linear_only_isolated_kappa_upper'], z['old_isolated_kappa_upper']))
