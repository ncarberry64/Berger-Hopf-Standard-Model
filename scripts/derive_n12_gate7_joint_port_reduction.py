"""Recover historical split and exercise its seven-output local adjoint adapter.

Frozen matrices only. No action, chart, 370-interval or Stage-B producer runs.
The 125-variable check is explicitly a local subproblem, not Gamma_joint.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.joint_boundary_port_reduction import reduce_seven_port
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from checkpoint_n12_gate7_66d_tangent_binding import amat,bound,digest,encoded,PHYSICAL
from diagnose_n12_gate7_eight_reaction_center import block,identity
import derive_n12_c2_reset_launch_adjoint_interface as history

BASE=ROOT/'artifacts/flagship_integration'
CURRENT=BASE/'gate7_launch_response_20260927'
CENTER=BASE/'gate7_coupled_fiber_center_20260927'
NAMES=['trace 1','trace 2','trace 3','canonical momentum 1','canonical momentum 2','dynamic flux 1','dynamic flux 2']


def mat(a):return arb_mat(*np.shape(a),list(np.asarray(a,dtype=object).flat))
def mids(a):return np.array([float(v.mid()) for v in a.entries()]).reshape(a.nrows(),a.ncols())


def normalized_hash(path):
    raw=path.read_bytes()
    if path.suffix in ('.py','.md','.json'):raw=raw.replace(b'\r\n',b'\n')
    return hashlib.sha256(raw).hexdigest().upper()


def historical_binding(out):
    records={};recovered=ROOT/'tmp/gate7_joint_port_20260927/recovered'
    for name in ('BHSM_N12_C2_RESET_LAUNCH_ADJOINT_INTERFACE',
                 'BHSM_N12_C2_FIXED_SEED_UPSTREAM_FORCE_OWNER',
                 'BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY'):
        p=BASE/(name+'.json');d=json.loads(p.read_bytes());checks=[]
        for rel,expected in d['inputs'].items():
            source=ROOT/rel;alternate=recovered/Path(rel).name
            if not alternate.exists():
                alternate=BASE/'gate7_joint_port_20260927/historical_inputs'/Path(rel).name
            if source.exists() and normalized_hash(source)==expected:
                checks.append(dict(path=rel,status='MATCH',SHA256=expected));continue
            if alternate.exists() and normalized_hash(alternate)==expected:
                saved=out/'historical_inputs'/alternate.name;saved.parent.mkdir(exist_ok=True)
                saved.write_bytes(alternate.read_bytes())
                provenance=alternate.with_name(alternate.name+'.provenance.json')
                if provenance.exists():
                    evidence=json.loads(provenance.read_bytes())
                else:
                    frozen=json.loads((BASE/'gate7_joint_port_20260927/report.json').read_bytes())
                    evidence=next(x['recovery'] for x in frozen['historical_binding'][name]['inputs'] if x['path']==rel)
                checks.append(dict(path=rel,status='EXACT_HISTORICAL_VERSION_RECOVERED',SHA256=expected,recovery=evidence));continue
            checks.append(dict(path=rel,status='UNAVAILABLE' if not source.exists() else 'DIFFERENT_CURRENT_VERSION',expected_SHA256=expected))
        records[name]=dict(SHA256=normalized_hash(p),inputs=checks,
            exact_split=d.get('exact_split',d.get('exact_tangent_identity')),
            witness=d.get('numerical_identity_witness',d.get('dimension_and_subspace_witness')),
            claim_boundary=d['claim_boundary'])
    # Only the stored finite-dimensional algebra witness, no history campaign.
    replay=history.build_payload();old=json.loads(history.RESULT.read_bytes())
    return records,dict(stored=old['numerical_identity_witness'],
        replay=replay['numerical_identity_witness'],validation_passed=replay['validation_passed'],
        role='DETERMINISTIC_ALGEBRA_CONTROL_NOT_PHYSICAL_SEVEN_ROW_DATA')


def calculate(out):
    ctx.prec=512
    records,historical_replay=historical_binding(out)
    a=load(CURRENT/'arrays.npz');geom=load(CENTER/'neighborhood/arrays.npz')
    jet=load(CENTER/'jet/arrays.npz');left=load(CENTER/'uniform_inputs/left.npz');mid=load(CENTER/'uniform_inputs/midpoint.npz')
    for folder in (CURRENT,CENTER/'neighborhood',CENTER/'jet'):
        report=json.loads((folder/'report.json').read_bytes())
        if digest(folder/'arrays.npz')!=report['arrays_SHA256']:raise ValueError('frozen packet changed')
    cert=json.loads((CENTER/'uniform_inputs/report.json').read_bytes())
    for n in ('left','midpoint'):
        if digest(CENTER/f'uniform_inputs/{n}.npz')!=cert['local_derivative_SHA256'][n]:raise ValueError('local derivative changed')
    K=mat(jet['J125']);J=mat(a['native_event_7x98']);R=mat(a['response_7x73'])
    N=mat(geom['left_phase_chart'][:98,:25]);G=arb_mat(7,125)
    gn=J*N
    for i in range(7):
        for j in range(25):G[i,j]=gn[i,j]
    # Constraint/fiber rows vanish symbolically on the already defined chart.
    # Only the current interval HS rows have direct physical forcing.
    h=arb(1)/4;I=identity(99);jl=mat(left['derivative']);jm=mat(mid['derivative'])
    dl=-I-jl*(h/6)-jm*(I/2+jl*(h/8))*(2*h/3)
    with np.load(ROOT/PHYSICAL) as z:B=amat(z['endpoint_physical_tangent_action'][14])
    test=arb_mat(74,99)
    for i in range(73):
        for j in range(98):test[i,j]=B[j,i]
    test[73,98]=arb(1000000)
    hs=test*dl*mat(a['launch_augmented']);Fp=arb_mat(125,73)
    for i in range(74):
        for j in range(73):Fp[50+i,j]=hs[i,j]
    result=reduce_seven_port(K,Fp,{'local_native':dict(p=R,n=G)})
    # Small frozen 125-border comparison, not all-history Jacobi generation.
    normal=-K.solve(Fp);forward=R+G*normal
    replay=result['reduced']-forward
    Rmid=arb_mat(7,73,[v.mid() for v in R.entries()])
    right=Rmid.transpose()*(Rmid*Rmid.transpose()).inv()
    rankdef=identity(7)-R*right
    if bound(rankdef)['approximate_upper']>=1:raise ArithmeticError('local port rank not certified')
    rows=[]
    for i,name in enumerate(NAMES):
        rows.append(dict(row=i+1,name=name,local_native='ALREADY INCLUDED',
            upstream_seam_history='ACTIVE',transported_C2='ACTIVE',reset_pullback='ACTIVE',
            pair_contact='ACTIVE',descriptor_constraint_local_border='INTERNAL-CANCELLED',
            total_reduced_joint='ACTIVE',
            status_scope='ACTIVE means retained before projection; its coefficient on this row and any subsequent cancellation remain unproved. Local125 cancellation is not a claim about full joint normals.',
            local_row_norm=bound(block(R,[i],range(73))),
            local125_correction_uncertainty=bound(block(result['correction'],[i],range(73))),
            history_contact_correction_norm=None,complete_row=None))
    save_arrays(out/'arrays.npz',dict(local125_adjoint=result['adjoint'],local125_forcing=Fp,
        local125_port_normal_derivative=G,local125_correction=result['correction'],
        local125_reduced=result['reduced'],local125_normal_forward_control=normal,
        local125_adjoint_forward_replay=replay,local_port_right_inverse_proposal=right,
        local_port_rank_defect=rankdef))
    sources=[Path(__file__),ROOT/'src/bhsm/interface/joint_boundary_port_reduction.py',
        ROOT/'src/bhsm/interface/aether_c2_launch_adjoint_pullback.py',
        ROOT/'src/bhsm/interface/aether_forward_c2_signed_coefficient_adjoint.py',
        Path(history.__file__),ROOT/'scripts/audit_n12_c2_fixed_seed_upstream_force_owner.py',
        ROOT/PHYSICAL]
    sources += [folder/name for folder in (CURRENT,CENTER/'jet',CENTER/'neighborhood') for name in ('arrays.npz','report.json')]
    sources += [CENTER/f'uniform_inputs/{n}.npz' for n in ('left','midpoint')]
    report=dict(status='HISTORICAL_SPLIT_RECOVERED_LOCAL_SEVEN_OUTPUT_ADJOINT_REPLAYED_JOINT_PORT_IDENTITY_OPEN',
        target='N12_COMPLETE_JOINT_HISTORY_BOUNDARY_REACTION_TO_NATIVE_7ROW_IDENTITY',
        historical_binding=records,historical_replay=historical_replay,
        exact_adjoint='F_n=K; Phi_p=-K^-1 F_p; K^T lambda=g_n^T; Dg_red=g_p-lambda^T F_p',
        moving_port='g=B7 Lambda; g_a=(D_a B7)Lambda+B7 D_a Lambda for a=p,n',
        orientation='Canonical residual [Tq_child-Tq_event; P_child-P_event; Gamma_child+DP_child[X_child]-F_child+Gamma_event]; event orientation diag(-I5,+I2). Stored native packet is the unsigned event output.',
        stationarity_does_not_zero_mixed_reaction_derivatives=True,
        local_border_scope='25 left constraints +25 right constraints +74 interval13 HS rows +left descriptor fiber; not the full joint history/contact KKT system',
        local125_adjoint_replay=bound(result['adjoint_replay']),
        local125_adjoint_forward_replay=bound(replay),
        local125_normal_equation_replay=bound(K*normal+Fp),
        local125_correction_uncertainty=bound(result['correction']),
        local_port_rank=7,local_port_rank_inverse_defect=bound(rankdef),
        complete_joint_7x73_rank=None,complete_minus_local_7x73=None,
        row_accounting=rows,
        historical_kernel_cancellation_scope='Downstream C2 force on 67 fixed-seed directions only, not arbitrary current seven-port rows',
        first_missing_representation='Current-center action-owned seven-output g=B7 Lambda_joint and (g_p,g_n), coupled to the full signed internal (F_p,K). Historical p0 and d_upstream were test covectors; the frozen 125 border supplies only the local subset.',
        unknown_corrections_set_to_zero=False,extra_environment_action_added=False,
        promoted_to_N12_FIXED_ENVIRONMENT_MATERIAL_RESPONSE_7x73=False,
        action_or_history_producers_run=False,all_history_73_column_campaign_run=False,
        native_derivative_7x73_recomputed=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        tolerances_changed=False,source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in sources},arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','local_port_rank','local_port_rank_inverse_defect','local125_adjoint_forward_replay','local125_correction_uncertainty')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);calculate(args.out)
