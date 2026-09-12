"""Restore original scientific functions and reject incomplete contraction capture."""
from pathlib import Path
from types import SimpleNamespace
import sys
import numpy as np
import pytest
from flint import arb

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import n12_gate7_coupled_normalization_derivative_refinement as refinement


def test_failed_evaluation_restores_both_original_functions():
    action=lambda *args:None
    inverse=lambda *args:None
    cert=SimpleNamespace(_contracted_action=action)
    engine=SimpleNamespace(p=SimpleNamespace(values=SimpleNamespace(cert=cert)),
        inverse=SimpleNamespace(enclose_columns=inverse))
    def fail(*args):raise ArithmeticError('original physical evaluation failed')
    engine.evaluate_batch=fail
    with pytest.raises(ArithmeticError,match='original physical'):
        refinement.refine_batch(engine,{},0,9)
    assert cert._contracted_action is action and engine.inverse.enclose_columns is inverse


def test_missing_fourth_action_cannot_become_a_refined_derivative():
    cert=SimpleNamespace(_contracted_action=lambda *args:np.full(2,arb(1)))
    engine=SimpleNamespace(p=SimpleNamespace(values=SimpleNamespace(cert=cert)),
        inverse=SimpleNamespace(enclose_columns=lambda *args:None),
        evaluate_batch=lambda *args:(np.full((99,9),arb(1)),None,None))
    with pytest.raises(ArithmeticError,match='complete original descriptor contractions'):
        refinement.refine_batch(engine,{},0,9)
