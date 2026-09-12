"""Uniform derivative routing includes the descriptor and restores the producer."""
from contextlib import nullcontext
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import numpy as np
import pytest
from flint import arb,arb_mat

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_coupled_midpoint_uniform_derivatives as pilot


@pytest.fixture
def fixture(monkeypatch):
    paired=dict(full=np.full(98,arb(0)),eigenbox=np.full(62,arb(0)),
        rm=np.array([[arb(int(i==j)) for j in range(62)] for i in range(62)]),
        radii=np.full(62,arb(1)),variation=np.full(62,arb(0)))
    domain=np.full(99,arb(0));domain[98]=arb(7)
    source=dict(paired=paired,response=np.full(62,arb(3)),raw_domain=domain,old_rate=np.full(99,arb(2)))
    cert=SimpleNamespace(_verified_solve=object(),_eigenline=object(),_rate_enclosure=None)
    monkeypatch.setattr(pilot.p.values,'cert',cert)
    monkeypatch.setattr(pilot.p.values,'operands',lambda:(None,None,None,None,None))
    monkeypatch.setattr(pilot.p.df.sparse,'use_optimized_mixed',lambda cert:nullcontext())
    monkeypatch.setattr(pilot.values.eq.engine.affine.factored,'use_ball_factored_integrand',lambda *args:nullcontext())
    return source,cert


def test_descriptor_basis_and_all_three_coupled_solves(fixture):
    source,cert=fixture;original_solve=cert._verified_solve;original_line=cert._eigenline
    def rate(state,descriptor,weights,reference,directions):
        assert descriptor is source['raw_domain'][98]
        assert directions.shape==(99,9) and directions[98,8]==1 and directions[90,0]==1
        assert sum(int(v==1) for v in directions.flat)==9
        physical=cert._verified_solve(arb_mat(62,62),arb_mat(62,1))
        assert physical[0,0]==3
        for _ in range(2):
            variation=cert._verified_solve(arb_mat(62,62),arb_mat(62,9))
            assert all(v.is_zero() for v in variation.entries())
        return SimpleNamespace(value=source['old_rate'],derivative=np.full((99,9),arb(5)))
    cert._rate_enclosure=rate
    derivative,residual,proof=pilot.evaluate_batch(source,90,99)
    assert derivative.shape==(99,9) and residual.shape==(2,62,9) and len(proof)==2
    assert cert._verified_solve is original_solve and cert._eigenline is original_line


def test_extra_bordered_solve_fails_closed_and_restores_functions(fixture):
    source,cert=fixture;original_solve=cert._verified_solve;original_line=cert._eigenline
    def rate(*args):
        cert._verified_solve(arb_mat(62,62),arb_mat(62,1))
        for _ in range(3):cert._verified_solve(arb_mat(62,62),arb_mat(62,9))
    cert._rate_enclosure=rate
    with pytest.raises(ArithmeticError,match='exactly one'):pilot.evaluate_batch(source,0,9)
    assert cert._verified_solve is original_solve and cert._eigenline is original_line


def test_center_only_field_is_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(pilot.values,'WORK',tmp_path)
    monkeypatch.setattr(pilot.values,'load_inputs',lambda index:dict(binding={}))
    directory=tmp_path/'interval_013';directory.mkdir()
    record=dict(binding={},algorithm=pilot.values.ALGORITHM,interval=13,report=dict(
        validation_passed=True,uniform_actual_HS_midpoint_field_enclosed=False))
    (directory/'record.json').write_text(json.dumps(record));(directory/'reproduction.json').write_text('{}')
    with pytest.raises(RuntimeError,match='paired actual midpoint'):pilot.load_inputs(13)
