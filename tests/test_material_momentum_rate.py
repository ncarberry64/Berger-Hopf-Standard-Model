"""Full momentum-rate product rule and signed duration/source bookkeeping."""
from pathlib import Path
import sys
import mpmath as mp
import pytest
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.material_momentum_rate import (
    momentum_rate_jet,duration_contraction,sum_disjoint_material_pieces)


def block(value,rows=2):
    result=arb_mat(rows,73);result[0,0]=value
    return result


def test_all_six_terms_against_actual_moving_seed_and_rate():
    # Gamma=y^3/6, B=1+y^2, X=2+y, P=1 at y=1.
    # These are controlled algebraic inputs, not a BHSM replacement model.
    r=momentum_rate_jet(action_third_P_X_B=block(6),
        action_second_X_DB_P=block(6),action_second_P_DB_X=block(6),
        action_first_D2B_P_X=block(3),action_second_DX_P_B=block(2),
        action_first_DB_DX_P=block(1))
    with mp.workdps(60):
        gamma=lambda y:y**3/6
        pi=lambda y:mp.diff(gamma,y)*(1+y*y)
        truth=mp.diff(lambda y:mp.diff(pi,y)*(2+y),mp.mpf(1))
    assert r['momentum_mixed'][0,0]==21
    assert r['momentum_rate_direction'][0,0]==3
    assert r['total'][0,0]==arb(str(truth))==24
    assert sum(x[0,0] for x in r['terms'].values())==24


def test_missing_seed_motion_cannot_be_assumed_zero():
    with pytest.raises(ValueError,match='six owned'):
        momentum_rate_jet(action_third_P_X_B=block(6),action_second_X_DB_P=block(6),
            action_second_P_DB_X=block(6),action_first_D2B_P_X=None,
            action_second_DX_P_B=block(2),action_first_DB_DX_P=block(1))


def test_duration_signs_are_combined_before_norm():
    c=arb_mat(4,2);c[0,0]=100;c[0,1]=-99
    d=arb_mat(2,73);d[0,0]=3;d[1,0]=3
    assert duration_contraction(c,d)[0,0]==3


def test_equal_segment_enclosures_are_not_shared_uncertainty():
    previous=ctx.prec;ctx.prec=512
    try:
        c=arb_mat(4,2);c[0,0]=1;c[0,1]=-1
        d=arb_mat(2,73)
        d[0,0]=arb(0,1);d[1,0]=arb(0,1)
        result=duration_contraction(c,d)[0,0]
        # Independent segment integrals may take +1 and -1, despite equal bounds.
        assert result.contains(2) and result.contains(-2) and not result.is_zero()
        with pytest.raises(ValueError,match='cotangents'):duration_contraction(None,d)
    finally:ctx.prec=previous


def test_disjoint_sources_sum_but_duration_is_not_added_twice():
    formation=block(7,4);c2=block(-3,4)
    result=sum_disjoint_material_pieces({
        'formation':dict(owner_ids=['formation/segment0/duration'],value=formation),
        'C2':dict(owner_ids=['C2/segment0/mixed'],value=c2)})
    assert result[0,0]==4
    with pytest.raises(ValueError,match='duplicate source'):
        sum_disjoint_material_pieces({
            'formation':dict(owner_ids=['formation/segment0/duration'],value=formation),
            'duration':dict(owner_ids=['formation/segment0/duration'],value=formation)})
