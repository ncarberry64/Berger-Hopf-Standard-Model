"""Regression checks for the local interval dimension obstruction."""
import json
import sys
from pathlib import Path

import numpy as np
from flint import arb,ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import diagnose_n12_gate7_local_child_flow_dimension as d

OUT=d.ROOT/d.BASE/'gate7_local_child_flow_dimension_20260926'


def test_null_direction_and_missing_equation():
    ctx.prec=512
    r=json.loads((OUT/'report.json').read_bytes())
    with np.load(OUT/'arrays.npz') as z:K=z['K_cut'];v=z['null_vector']
    assert K.shape==(74,75)
    assert v[0]==1
    error=d.bound(d.amat(K[:,1:])*d.amat(v[1:,None])+d.amat(K[:,0:1]))
    assert arb(error['exact_upper'])<=arb(r['stored_null_vector_replay']['exact_upper'])
    assert r['nullity']==1 and r['injectivity_minimum_gain']==0
    assert r['inverse_replay_residual'] is None


def test_ledgers_and_stop_flags():
    r=json.loads((OUT/'report.json').read_bytes())
    for name in ('internal_ledger','projected_equation_ledger','full_equation_ledger'):
        row=r[name];assert row['total']==sum(v for k,v in row.items() if k!='total')
    assert r['internal_ledger']['total']-r['projected_equation_ledger']['total']==1
    for key in ('invertible_internal_jacobian','old_Mqq_modified','old_Mqq_schur_replay_performed','nonlinear_proof_attempted','physical_radii_changed','scientific_producers_run','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert r[key] is False
    for name,sha in r['source_SHA256'].items():assert d.digest(d.ROOT/name)==sha
    assert d.digest(OUT/'arrays.npz')==r['arrays_SHA256']
