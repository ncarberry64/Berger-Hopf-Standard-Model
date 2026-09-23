"""A necessary fixed-preconditioner condition, using frozen point operators.

No action or Hessian evaluation: J1 = R1^-1 (I-D1) is an algebraic consequence
of the saved certified defect D1=I-R1*J1. The independently certified target
point eigenpair enclosure then attaches the actual normalized branch root.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_mixed_eigenline_certificate as base


def exact(x):
    return dict(exact=str(x.fmpq()),approximate=float(x))


def run(evidence,import_receipt,out):
    ctx.prec=512
    imported=json.loads(import_receipt.read_bytes());data=[];sources={}
    for index in (18,19):
        folder=evidence/f'artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_{index:03d}'
        record_path=folder/'record.json';path=folder/'eigenpair.npz'
        record=json.loads(record_path.read_bytes())
        # Consume the previously validated direct import; do not recurse into
        # inherited evidence or repeat a point calculation.
        if imported[str(path.resolve())]!=record['data_SHA256']:
            raise ValueError('point operator and import receipt differ')
        for p in (record_path,path,folder/'reproduction.json'):
            sources[str(p.resolve())]=imported[str(p.resolve())]
        trial=next(i for i,t in enumerate(record['report']['trials']) if t['validation_passed'])
        with np.load(path,allow_pickle=False) as z:
            R,D,c,w=[base.read_array(z,k) for k in ('preconditioner','center_defect','eigenpair_center',f'trial_{trial}_radii')]
        data.append((arb_mat(62,62,list(R.flat)),arb_mat(62,62,list(D.flat)),c,w,record))
    R0,D0,c0,w0,_=data[0];R1,D1,c1,w1,record=data[1]
    identity=arb_mat(np.eye(62,dtype=int).tolist())
    inv=R1.inv();residual=identity-R1*inv
    if not all(v.contains(0) for v in residual.entries()):
        raise ArithmeticError('verified inverse residual must contain zero')
    J1=inv*(identity-D1)
    proof=record['report']['point_eigenpair_proof']
    if not proof['normalized_eigenpair_enclosed'] or proof['selected_zero_based_index_verified']!=24:
        raise ValueError('frozen normalized selected point eigenpair required')
    root=[base.restore((m,r)) for m,r in zip(proof['target_midpoints_rational'],proof['target_radii_rational'],strict=True)]
    delta=[v-c for v,c in zip(root,c1,strict=True)]
    correction=arb_mat(62,62)
    for i in range(61):
        correction[i,i]=-delta[-1]
        correction[i,61]=-delta[i]
        correction[61,i]=delta[i]
    error=identity-R0*(J1+correction)
    lower=[];upper=[]
    for i in range(62):
        lower.append((sum((abs(error[i,j]).lower()*w0[j] for j in range(62)),arb(0))/w0[i]).lower())
        upper.append((sum((abs(error[i,j]).upper()*w0[j] for j in range(62)),arb(0))/w0[i]).upper())
    selected=max(range(62),key=lambda i:lower[i])
    witness=[(abs(error[selected,j]).lower()*w0[j]/w0[selected]).lower() for j in range(62)]
    bound=max(lower);obstruction=bool(bound>1)
    for p in (Path(__file__),Path(base.__file__),import_receipt):sources[str(p.resolve())]=base.sha(p)
    result=dict(algorithm='FROZEN_ANCHOR_WEIGHTED_NORM_OBSTRUCTION_ARB512_V1',
        anchor=18,target_endpoint=19,history_interval=18,selected_eigenline_index=24,
        actual_target_normalized_eigenpair_included=True,
        definition='||W18^-1 (I-R18*J(x19,psi19,lambda19)) W18||_infinity',
        J_to_physical_K='K=J*diag(I,-1), R_K=diag(I,-1)*R; weighted infinity defects are sign-conjugate and have identical norm.',
        reconstruction_identity='J19_center=R19^-1*(I-D19_center); add exact eigenpair displacement blocks (-delta_lambda*I,-delta_psi;delta_psi^T,0).',
        source_point_defect_reconstructed_not_recomputed=True,
        verified_inverse_residual_contains_zero=True,
        weighted_inverse_defect_lower=exact(bound),weighted_inverse_defect_upper=exact(max(upper)),
        excess_over_one_lower=exact((bound-1).lower()),
        largest_certified_lower_row=selected,
        witness_row_component_lower_bounds=[exact(x) for x in witness],
        row_lower_bounds=[exact(x) for x in lower],row_upper_bounds=[exact(x) for x in upper],
        fixed_anchor_and_norm_contraction_impossible=obstruction,
        any_subdivision_with_same_R18_and_W18_covering_endpoint19_can_pass=False if obstruction else None,
        interpretation='A necessary contraction condition fails already at the included physical endpoint. This rules out subdivision alone for this FIXED inverse/norm, not eigenbranch continuation using another inverse/norm.',
        existing_right_anchor_available=19,new_anchor_evaluations=0,new_anchor_necessity_undetermined=True,
        point_hessians_recomputed=False,action_derivatives_recomputed=False,
        endpoint19_prototype_recomputed=False,physical_domain_shrunk=False,
        source_SHA256=sources,Gate7_closed=False,kappa_L=None,kappa_T=None,new_physical_budget_debit=False)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(base.encode(result))
    print(json.dumps(dict(lower=float(bound),upper=float(max(upper)),row=selected,
        fixed_anchor_and_norm_contraction_impossible=obstruction)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--import-receipt',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.import_receipt.resolve(),a.out.resolve())
