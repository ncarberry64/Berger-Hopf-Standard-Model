import sys
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface.sparse_arb_mixed_jets import use_optimized_mixed

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import certify_n12_gate7_accepted_replay_center_outward_74d as original


@pytest.mark.parametrize('order',[1,2,3,4,5])
def test_mixed_product_matches_exact_subset_convolution(order):
    rng=np.random.default_rng(order)
    a=rng.integers(-3,4,size=2**order)
    b=rng.integers(-3,4,size=2**order)
    a[::3]=0;b[::4]=0
    with use_optimized_mixed(original) as mixed:
        value=mixed(tuple(arb(int(v)) for v in a))*mixed(tuple(arb(int(v)) for v in b))
        for mask in range(2**order):
            expected=sum(int(a[s])*int(b[mask^s]) for s in range(2**order) if s&mask==s)
            assert value.d[mask]==expected


def test_zero_products_preserve_broadcast_leg_shapes():
    with use_optimized_mixed(original) as mixed:
        a=mixed((arb(1),np.array([[arb(0)],[arb(0)]],dtype=object),arb(0),arb(0)))
        b=mixed((arb(1),arb(0),np.array([[arb(1),arb(2),arb(3)]],dtype=object),arb(0)))
        result=a*b
        assert np.shape(result.d[3])==(2,3)
        assert all(v.is_zero() for v in result.d[3].flat)


def test_scalar_shortcuts_preserve_all_derivatives():
    with use_optimized_mixed(original) as mixed:
        value=mixed.affine(arb(2),[arb(3),arb(5)])
        result=(7*value+11)*mixed.constant(2,2)
        assert result.d==(arb(50),arb(42),arb(70),arb(0))


def test_zero_times_nonfinite_is_not_silently_discarded():
    with use_optimized_mixed(original) as mixed:
        a=mixed((arb(1),arb(0),arb(1),arb(0)))
        b=mixed((arb(1),arb(1),np.array([arb('nan')],dtype=object),arb(0)))
        result=a*b
        assert not np.asarray(result.d[3]).flat[0].is_finite()


def test_array_mutation_does_not_reuse_stale_finiteness():
    with use_optimized_mixed(original) as mixed:
        entry=np.array([arb(2)],dtype=object)
        a=mixed((arb(1),arb(0),arb(1),arb(0)))
        b=mixed((arb(1),arb(1),entry,arb(0)))
        a*b
        entry[0]=arb('nan')
        result=a*b
        assert not np.asarray(result.d[3]).flat[0].is_finite()


def test_unary_and_power_operations_remain_outward_and_restore_class():
    before=original.Mixed
    previous=ctx.prec
    ctx.prec=128
    try:
        with use_optimized_mixed(original) as mixed:
            x=mixed.affine(arb(2),[arb(1),arb(1)])
            y=x**3+1/x
            # Mixed second derivative: 6*x+2/x^3 at x=2.
            assert y.d[3].contains(arb(49)/4)
        assert original.Mixed is before
        with pytest.raises(RuntimeError):
            with use_optimized_mixed(original):raise RuntimeError('test')
        assert original.Mixed is before
    finally:ctx.prec=previous
