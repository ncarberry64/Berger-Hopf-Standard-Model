"""Independent identities for the new high-order shared-action evaluator."""
import sys
from pathlib import Path
import numpy as np
import pytest
from flint import arb, ctx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_accepted_replay_center_outward_74d as action
from bhsm.interface.uniform_action_contraction import contract
from bhsm.interface.shared_action_taylor import TaylorDomain, scalar_taylor_action


@pytest.fixture(autouse=True)
def precision():
    old = ctx.prec
    ctx.prec = 256
    yield
    ctx.prec = old


def test_polynomial_fifth_derivative_vanishes_but_exponential_does_not():
    domain = TaylorDomain([(0,1,'interval')],1)
    x = domain.affine(1,[arb('0.01')])
    with scalar_taylor_action(action):
        jet = action.Mixed.affine(x,[arb(1)]*5)
        assert (jet**4).d[-1].support().is_zero()
        result = jet.exp().d[-1]
    assert result.enclosure().contains(arb('1.01').exp())
    assert result.enclosure().contains(arb('0.99').exp())


def test_factored_fifth_matches_unfactored_action_and_covers_shared_states(monkeypatch):
    # A one-quadrature test action exercises all three terms, including I^-1
    # and boundary. Production keeps all 96 quadrature nodes unchanged.
    monkeypatch.setattr(action,'POINTS',1)
    domain = TaylorDomain([(0,1,'interval'),(1,2,'euclidean')],2)
    center = [arb(0)]*98
    directions = [[arb(0),arb(0)] for _ in range(98)]
    directions[0] = [arb('0.000001'),arb(0)]
    directions[86] = [arb(0),arb('0.0000004')]
    state = [domain.affine(c,d) for c,d in zip(center,directions)]
    leg = [arb(int(i==0)) for i in range(98)]
    legs = [leg]*5
    result, lower = contract(action,state,legs)
    assert lower > 0
    maps = [action._dense_mapping(action._integrand(center,0,0).maps)]
    for theta in ((0,0),(-1,1),(1,-1)):
        point = [c+sum((a*t for a,t in zip(d,theta)),arb(0))
                 for c,d in zip(center,directions)]
        expected = action._contracted_action(np.array(point,dtype=object),
            [np.array(leg,dtype=object)]*5,maps)
        predicted = result.c+sum((a*t for a,t in zip(result.a.entries(),theta)),arb(0))
        assert (predicted+arb(0,result.r)).overlaps(expected)
        if theta==(0,0):
            assert result.c.overlaps(expected)


def test_mixed_parameter_namespaces_rejected():
    d1 = TaylorDomain([(0,1,'interval')],1)
    d2 = TaylorDomain([(0,1,'interval')],1)
    state = [d1.affine(0)]*98
    state[4] = d2.affine(0)
    with pytest.raises(ValueError,match='common parameter'):
        contract(action,state,[[arb(0)]*98]*5)


def test_varying_leg_domain_rejected():
    d1 = TaylorDomain([(0,1,'interval')],1)
    d2 = TaylorDomain([(0,1,'interval')],1)
    with pytest.raises(ValueError,match='parameter identities'):
        contract(action,[d1.affine(0)]*98,[[d2.affine(1)]*98]*5)


def test_adapter_restored_after_domain_failure(monkeypatch):
    monkeypatch.setattr(action,'POINTS',1)
    domain = TaylorDomain([(0,1,'interval')],1)
    state = [domain.affine(0)]*98
    state[86] = domain.affine(10**12)  # Makes the global inertia negative.
    mixed, variables = action.Mixed, action._local_variables
    with pytest.raises(ArithmeticError,match='inertia'):
        contract(action,state,[[arb(int(i==0)) for i in range(98)]]*5)
    assert action.Mixed is mixed and action._local_variables is variables
