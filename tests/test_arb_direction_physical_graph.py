from pathlib import Path
import sys
from types import SimpleNamespace
import numpy as np
import pytest
from flint import arb,ctx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_batched_mixed_physical_graph as parent
from bhsm.interface import arb_direction_physical_graph as adapter


def test_ball_leaf_preserves_radius_and_sub_binary64_information():
    old=ctx.prec;ctx.prec=256
    try:
        value=arb(1)+arb(2)**-100
        assert adapter.direction_scalar(value) is value
        assert not value.contains(arb(float(value)))
        ball=arb(1,arb(2)**-40)
        assert adapter.direction_scalar(ball) is ball
        assert adapter.direction_scalar(np.float64(0.125))==arb(0.125)
    finally:ctx.prec=old


@pytest.mark.parametrize('value',[float('nan'),float('inf'),arb('nan')])
def test_nonfinite_direction_is_rejected(value):
    with pytest.raises(ValueError):adapter.direction_scalar(value)


def test_pinned_graph_builds_without_mutating_parent_and_checks_layout():
    original=parent.batched_axis_map
    evaluate=adapter.build_ball_direction_graph(parent)
    assert parent.batched_axis_map is original
    with pytest.raises(ValueError):evaluate(None,None,None,None,np.zeros(98),np.zeros((99,2)))
    with pytest.raises(ValueError):evaluate(None,None,None,None,np.zeros(99),np.zeros((99,0)))


def changed_graph():return None


def test_changed_parent_graph_fails_closed():
    with pytest.raises(RuntimeError):adapter.build_ball_direction_graph(SimpleNamespace(batched_axis_map=changed_graph))
