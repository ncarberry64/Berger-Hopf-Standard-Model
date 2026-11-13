"""Analytic checks for the saved joint-input relaxation, not physical closure."""
from fractions import Fraction
import importlib.util
from pathlib import Path
import pytest
from flint import arb, ctx

spec = importlib.util.spec_from_file_location('joint_input_column',
    Path(__file__).resolve().parents[1]/'scripts/evaluate_n12_gate7_joint_input_column.py')
joint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(joint)


def test_product_ball_support_and_all_directions():
    ctx.prec = 128
    groups = [dict(start=0, stop=2, norm='euclidean'), dict(start=2, stop=3, norm='box')]
    support = joint.row_support([arb(3), arb(-4), arb(2)], groups)
    assert support >= 7 and support < arb('7.00000001')
    with pytest.raises(ValueError, match='partition'):
        joint.row_support([arb(3), arb(-4), arb(2)], groups[:1])


def test_common_input_excludes_independent_output_corners():
    # H0=(1,1)^T and one scalar input: outputs must coincide. The Cartesian
    # corner (1,-1) is excluded by y0-y1=0, not by picking favorable inputs.
    H0 = joint.matrix([[arb(1)], [arb(1)]])
    separator = joint.matrix([[arb(1), arb(-1)]])
    assert (separator*H0)[0,0].is_zero()
    assert (separator*joint.matrix([[arb(1)], [arb(-1)]]))[0,0] == 2


def test_independent_remainder_restores_bad_pair_at_one_input():
    # Keeping xi shared is insufficient if the coefficient error has already
    # become independent. Both matrices below belong to H0+[-2,2]^(2x1).
    H0 = [Fraction(1), Fraction(1)]
    plus = [v+e for v,e in zip(H0, [Fraction(2), Fraction(-2)])]
    minus = [v-e for v,e in zip(H0, [Fraction(2), Fraction(-2)])]
    assert plus == [3,-1] and minus == [-1,3]
    assert abs(plus[0]-minus[0])/2 == 2 > 1


def test_exact_witness_obeys_original_group_balls():
    groups = [dict(start=0, stop=1, norm='interval'),
              dict(start=1, stop=75, norm='euclidean'),
              dict(start=75, stop=174, norm='box')]
    x = joint.witness(groups, 174)
    assert x[0] == 1
    assert sum(v*v for v in x[1:75]) == Fraction(74,81) <= 1
    assert max(abs(v) for v in x[75:]) == 1


def test_interval_uncertainty_is_retained_in_support():
    groups = [dict(start=0, stop=1, norm='interval')]
    assert joint.row_support([arb(0, 2)], groups) >= 2
    with pytest.raises(ValueError):
        joint.witness([dict(start=0,stop=2,norm='interval')], 2)
