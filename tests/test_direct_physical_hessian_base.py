from contextlib import contextmanager
from types import SimpleNamespace
import pytest
from flint import arb, ctx
from bhsm.interface import direct_physical_hessian_base as base


def fixture(monkeypatch):
    events = []
    jets = SimpleNamespace(hessian_arb=object(), hessian_mid=object())
    def action(state):
        assert state[0].rad() > 0
        events.append('original action')
        return jets
    def eigen(*_):
        events.append('original eigenpair')
        return 'verified proposal'
    cert = SimpleNamespace(STATE=2, REDUCED=1, _arb_action_jets=action, _eigenline=eigen)
    @contextmanager
    def verification(module, checks, **options):
        assert module is cert
        assert options == dict(expected_index=24, normalize_proposal_center=True)
        events.append('verification entered')
        yield
        checks.append(dict(validation_passed=True))
        events.append('verification completed')
    monkeypatch.setattr(base, 'verified_eigenline', verification)
    state = [arb(1, .125), arb(2)]
    return cert, state, jets, events


def test_base_is_computed_once_and_full_interval_state_is_required(monkeypatch):
    cert, state, jets, events = fixture(monkeypatch)
    old_jets, old_eigen = cert._arb_action_jets, cert._eigenline
    prepared = base.VerifiedHessianBase(cert, state, [1.])
    assert events == ['original action','verification entered','original eigenpair','verification completed']
    for _ in range(2):
        with prepared.use():
            assert cert._arb_action_jets(state) is jets
            assert cert._eigenline(jets.hessian_arb,jets.hessian_mid,[1.]) == 'verified proposal'
            with pytest.raises(RuntimeError, match='state'):
                cert._arb_action_jets([state[0].mid(), state[1]])
            with pytest.raises(RuntimeError, match='operands'):
                cert._eigenline(jets.hessian_arb,jets.hessian_mid,[-1.])
            with pytest.raises(RuntimeError, match='operands'):
                cert._eigenline(object(),jets.hessian_mid,[1.])
        assert cert._arb_action_jets is old_jets and cert._eigenline is old_eigen
    assert events.count('original action') == 1


def test_precision_and_failure_restore_installed_functions(monkeypatch):
    cert, state, _, _ = fixture(monkeypatch)
    original = cert._arb_action_jets
    prepared = base.VerifiedHessianBase(cert,state,[1.])
    previous = ctx.prec
    try:
        with pytest.raises(LookupError):
            with prepared.use():
                raise LookupError('row failed')
        assert cert._arb_action_jets is original
        ctx.prec = previous+1
        with pytest.raises(RuntimeError, match='precision'):
            with prepared.use():
                pass
        ctx.prec = previous
        with prepared.use():
            ctx.prec = previous+1
            with pytest.raises(RuntimeError, match='precision'):
                cert._arb_action_jets(state)
    finally:
        ctx.prec = previous
    assert cert._arb_action_jets is original


def test_unverified_base_is_rejected(monkeypatch):
    cert, state, _, _ = fixture(monkeypatch)
    @contextmanager
    def missing_proof(*args, **kwargs):
        yield
    monkeypatch.setattr(base,'verified_eigenline',missing_proof)
    with pytest.raises(ArithmeticError, match='verified'):
        base.VerifiedHessianBase(cert,state,[1.])
