"""Verified point evaluations at a numerical reset guess, not a root proof."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import solve_n12_gate7_fiber_constrained_center as c
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from recenter_n12_gate7_current_history_box import recentered_eigenline
from bhsm.interface.physical_hs_value import verified_eigenline
from bhsm.interface.indexed_eigenpair_proposal import indexed_proposal


def calculate(candidate,out):
    ctx.prec=512
    candidate=Path(candidate).resolve();out=Path(out).resolve()
    with np.load(candidate) as z:
        state=z['joint_state_raw'];weights=z['state_weights'];reference=z['branch_reference']
    arrays={};records={}
    for name,part,index in [('outgoing_C2',slice(0,98),24),('incoming_E1',slice(98,196),23)]:
        raw=np.array([arb(float(v)) for v in state[part]],dtype=object)
        checks=[];selected={};original=c.action._eigenline
        def proposal(hessian,midpoint,ref):
            return indexed_proposal(hessian[37:,37:],index,ref)
        c.action._eigenline=recentered_eigenline(proposal)
        try:
            with c.sparse.use_optimized_mixed(c.action),c.factored.use_ball_factored_integrand(c.action,raw):
                with verified_eigenline(c.action,checks,expected_index=index,normalize_proposal_center=True):
                    verified=c.action._eigenline
                    def retain(*args):
                        result=verified(*args);selected['lambda']=result[1];return result
                    c.action._eigenline=retain
                    try:rate=c.action._rate_enclosure(raw,arb(0),weights,reference,None)
                    finally:c.action._eigenline=verified
                value=c.action_value(raw)
                jets=rate.action_jets
                energy=sum((raw[37+i]*jets.gradient_arb[37+i] for i in range(37)),arb(0))-value
                constraint=np.r_[jets.gradient_arb[74:],energy]
        finally:c.action._eigenline=original
        arrays[name+'_rate']=rate.value
        arrays[name+'_eigenvalue']=np.array([selected['lambda']],dtype=object)
        arrays[name+'_constraints']=constraint
        records[name]=dict(selected_index=index,eigenpair_proof=checks[0],
            eigenvalue=str(selected['lambda']),zero_in_eigenvalue=selected['lambda'].contains(0),
            descriptor_arc_rate=str(rate.value[98]),
            expected_orientation_verified=bool(rate.value[98]>0 if index==24 else rate.value[98]<0),
            constraint_absolute_norm_upper=float(c.norm(constraint).upper()),
            floating_gap_diagnostic=float(rate.gap_lower))
        print(name,records[name]['eigenvalue'],records[name]['descriptor_arc_rate'],flush=True)
    out.mkdir(parents=True,exist_ok=False)
    save_arrays(out/'arrays.npz',arrays)
    report=dict(status='CURRENT_RESET_GUESS_SELECTED_BRANCH_POINT_DIAGNOSTIC',branches=records,
        point_enclosures_are_not_reset_root_or_flow_certificates=True,
        current_reset_member_certified=False,incoming_parent_history_certified=False,
        current_first_73_jet_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in [candidate,Path(__file__),
            Path(c.__file__),Path(c.action.__file__),ROOT/'scripts/recenter_n12_gate7_current_history_box.py',
            ROOT/'src/bhsm/interface/indexed_eigenpair_proposal.py']},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();calculate(a.candidate,a.out)
