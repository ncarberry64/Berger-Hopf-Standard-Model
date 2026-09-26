"""Frozen first-order ownership tests; never import action producers."""
import ast
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from flint import arb, ctx

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import bind_n12_gate7_full_shooting_reaction as owner

OUT=owner.ROOT/owner.BASE/'gate7_full_shooting_owner_20260926'


def test_chain_rule_against_actual_producer_expression():
    """Differentiate the retained assembler AST with a nonlinear synthetic field."""
    ctx.prec=512
    path=owner.ROOT/'scripts/audit_n12_gate7_correlated_descriptor_newton_midpoint_replay.py'
    module=ast.parse(path.read_text())
    node=next(n.value for n in ast.walk(module) if isinstance(n,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='residual' for t in n.targets))
    expression=compile(ast.Expression(node),str(path),'eval')
    A=np.array([[1.,2.,0.],[-1.,0.,3.],[0.,1.,2.]])
    f=lambda x:A@x+x*x
    left=np.array([.25,-.5,1.]);right=np.array([.5,.25,-.25]);h=.25
    midpoint=(left+right)/2+h*(f(left)-f(right))/8
    jl=owner.amat(A+np.diag(2*left));jr=owner.amat(A+np.diag(2*right));jm=owner.amat(A+np.diag(2*midpoint))
    # Both endpoint directions matter, including opposite midpoint incidence signs.
    for dl,dr in [(np.eye(3)[:,0],np.eye(3)[:,1]),(np.eye(3)[:,2],np.zeros(3)),(np.zeros(3),np.eye(3)[:,2])]:
        eps=1e-25
        ends=np.array([left+1j*eps*dl,right+1j*eps*dr]);rates=np.array([f(v) for v in ends])
        middle=(ends[0]+ends[1])/2+h*(rates[0]-rates[1])/8
        actual=eval(expression,{'__builtins__':{}},dict(endpoints=ends,durations=np.array([h]),endpoint_rates=rates,midpoint_rates=np.array([f(middle)])))
        parts=owner.hs_derivative_parts(jl,jr,jm,owner.amat(dl[:,None]),owner.amat(dr[:,None]),arb(h))
        derived=owner.mid(sum(parts.values(),owner.arb_mat(3,1)))[:,0]
        np.testing.assert_allclose(derived,actual[0].imag/eps,rtol=32*np.finfo(float).eps,atol=32*np.finfo(float).eps)


def test_frozen_hashes_and_exact_provenance():
    report=json.loads((OUT/'report.json').read_bytes())
    for name,expected in report['source_SHA256'].items():
        with (owner.ROOT/name).open('rb') as stream:
            assert hashlib.sha256(stream.read()).hexdigest().upper()==expected
    assert owner.digest(OUT/'arrays.npz')==report['arrays_SHA256']
    for name,ranges in report['source_line_provenance'].items():
        lines=(owner.ROOT/name).read_text().splitlines()
        for r in ranges: assert '\n'.join(lines[r['start']-1:r['end']])==r['text']


def test_center_replay_uses_frozen_allowances_and_stops_before_nonlinear():
    ctx.prec=512
    report=json.loads((OUT/'report.json').read_bytes())
    old=json.loads((owner.D/'report.json').read_bytes())
    assert report['descriptor_frozen_allowance']==old['descriptor_reprojection_allowance_upper']
    assert arb(report['descriptor_error']['exact_upper'])<arb(report['descriptor_frozen_allowance'])
    assert all(arb(r['error_upper'])<arb(r['allowance_upper']) for r in report['boundary_rows'])
    assert report['stored_residual_replay_max_abs']==0
    assert report['midpoint_replay_max_abs']==0
    assert report['center_replay_passes']
    for key in ('frozen_Mqq_reextracted','tolerances_changed','scientific_producers_run','nonlinear_work_performed','nonlinear_row_identity_proved','Gate7_closed','FULL_BHSM_COMPLETE'):
        assert report[key] is False


def test_signed_contributions_preserve_left_forcing():
    with np.load(OUT/'arrays.npz') as z:
        total=sum((z['reaction_'+k] for k in ('right','left','midpoint','history_external')))
        np.testing.assert_allclose(total,z['Dphi_total'],rtol=64*np.finfo(float).eps,atol=64*np.finfo(float).eps)
        assert np.count_nonzero(z['reaction_history_external'])==0
        # This is a historical regression: omitting the left endpoint breaks replay.
        without_left=total-z['reaction_left']
        assert np.linalg.norm(without_left[7]-z['Dphi_truth'][7])>np.linalg.norm(total[7]-z['Dphi_truth'][7])
