import sys
from pathlib import Path
import pytest
import numpy as np
from flint import arb,ctx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_accepted_replay_center_outward_74d as action
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.shared_action_gradient import gradient
from bhsm.interface.uniform_action_contraction import contract


def test_zero_leg_gradient_matches_independent_point_action_jets(monkeypatch):
    old=ctx.prec;ctx.prec=256
    try:
        # The one-node action still contains bulk polynomial/exponential terms,
        # the global inertia reciprocal, and the unchanged boundary action.
        monkeypatch.setattr(action,'POINTS',1)
        d=TaylorDomain([(0,1,'interval')],1)
        center=[arb(0)]*98
        center[0],center[37],center[74]=arb('0.01'),arb('0.02'),arb('0.03')
        coefficients=[arb(0)]*98
        coefficients[0],coefficients[86]=arb('1e-6'),arb('4e-7')
        state=[d.affine(c,[a]) for c,a in zip(center,coefficients,strict=True)]
        result=gradient(action,state,[])
        assert len(result)==98
        for theta in (arb('-0.5'),arb(0),arb('0.5')):
            point=np.array([c+a*theta for c,a in zip(center,coefficients,strict=True)],dtype=object)
            expected=action._arb_action_jets(point).gradient_arb
            for actual,value in zip(result,expected,strict=True):
                predicted=actual.c+actual.a[0,0]*theta+arb(0,actual.r)
                assert predicted.overlaps(value)
                if theta.is_zero():
                    assert actual.c.overlaps(value)
    finally:ctx.prec=old


def test_zero_leg_gradient_matches_shared_scalar_directional_contraction(monkeypatch):
    old=ctx.prec;ctx.prec=256
    try:
        monkeypatch.setattr(action,'POINTS',1)
        d=TaylorDomain([(0,1,'interval')],1)
        state=[d.affine(0,[arb('1e-6') if i==0 else arb(0)]) for i in range(98)]
        result=gradient(action,state,[])
        for k in (0,37,74,86):
            basis=[arb(int(i==k)) for i in range(98)]
            expected,_=contract(action,state,[basis])
            assert result[k].c.overlaps(expected.c)
            assert result[k].a[0,0].overlaps(expected.a[0,0])
            assert result[k].enclosure().overlaps(expected.enclosure())
    finally:ctx.prec=old


def test_zero_leg_gradient_rejects_different_state_namespaces():
    old=ctx.prec;ctx.prec=256
    try:
        d=TaylorDomain([(0,1,'interval')],1);e=TaylorDomain([(0,1,'interval')],1)
        state=[d.affine(0)]*98
        state[4]=e.affine(0)
        with pytest.raises(ValueError,match='common state namespace'):
            gradient(action,state,[])
    finally:ctx.prec=old


def test_reverse_gradient_matches_independent_scalar_action(monkeypatch):
    old=ctx.prec;ctx.prec=256
    try:
        monkeypatch.setattr(action,'POINTS',1)
        d=TaylorDomain([(0,1,'interval')],1)
        state=[d.affine(0,[arb('1e-6') if i==0 else arb(0)]) for i in range(98)]
        leg=[arb(int(i==0)) for i in range(98)]
        # Nonzero states/legs include boundary, polynomial and global I^-1.
        result=gradient(action,state,[leg,leg,leg])
        for k in (0,37,74,86):
            basis=[arb(int(i==k)) for i in range(98)]
            expected,_=contract(action,state,[basis,leg,leg,leg])
            assert result[k].c.overlaps(expected.c)
            assert result[k].enclosure().overlaps(expected.enclosure())
            assert result[k].a[0,0].overlaps(expected.a[0,0])
    finally:ctx.prec=old


def test_reverse_gradient_rejects_different_shared_namespace():
    old=ctx.prec;ctx.prec=256
    try:
        d=TaylorDomain([(0,1,'interval')],1);e=TaylorDomain([(0,1,'interval')],1)
        with pytest.raises(ValueError,match='identical shared'):
            gradient(action,[d.affine(0)]*98,[[e.affine(1)]*98])
    finally:ctx.prec=old
