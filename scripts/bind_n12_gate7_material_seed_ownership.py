"""Replay actual canonical seed data; distinguish outputs from action seeds.

Consumes frozen arrays only. No action evaluation or history integration.
"""
import argparse
import ast
import json
from pathlib import Path
import sys

import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from checkpoint_n12_gate7_66d_tangent_binding import amat, bound, digest, encoded, FIXED
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from diagnose_n12_gate7_eight_reaction_center import block, identity, action_hessian_lift
from derive_n12_gate7_slaved_interface import attachment, attachment_variation

BASE = ROOT/'artifacts/flagship_integration'
OWNER = ROOT/'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py'


def calculate(out):
    ctx.prec = 512
    sources = []
    packets = {}
    for name in ('gate7_comoving_interface_20260927/node13', 'gate7_launch_response_20260927'):
        directory = BASE/name
        report = json.loads((directory/'report.json').read_bytes())
        if digest(directory/'arrays.npz') != report['arrays_SHA256']:
            raise ValueError('frozen packet changed: '+name)
        packets[name] = load(directory/'arrays.npz')
        sources += [directory/'arrays.npz', directory/'report.json']
    child = packets['gate7_comoving_interface_20260927/node13']
    launch = packets['gate7_launch_response_20260927']
    center = BASE/'gate7_coupled_fiber_center_20260927/neighborhood/arrays.npz'
    geometry = load(center)
    state_action = arb_mat(launch['corrected_state_action'].tolist())
    center_replay = state_action - arb_mat(geometry['left_state_domain'][:98,None].tolist())
    if not all(x.contains(0) for x in center_replay.entries()):
        raise ValueError('canonical and launch centers differ')
    child_report = json.loads((BASE/'gate7_comoving_interface_20260927/node13/report.json').read_bytes())
    if digest(center) not in child_report['source_SHA256'].values():
        raise ValueError('canonical lifts are not bound to current center')
    with np.load(ROOT/FIXED) as z:
        weights = [arb(float(x)) for x in z['state_weights']]
    q = [state_action[i,0]/weights[i] for i in range(37)]
    B, signs, t, sech2 = attachment(q)
    T = arb_mat(launch['launch_action'].tolist())
    raw_T = np.array([[T[i,j]/weights[i] for j in range(73)] for i in range(98)], dtype=object)
    dB = attachment_variation(raw_T, signs, t, sech2)
    Lq = arb_mat(child['canonical_lift_q'][:37].tolist())
    Lv = arb_mat(child['canonical_lift_v'][:37].tolist())
    # KKT rows 37:63 are dual multipliers, not 26 extra state components.
    E = arb_mat(98,4)
    for i in range(37):
        for a in range(2):
            E[i,a] = weights[i]*Lq[i,a]
            E[37+i,2+a] = weights[37+i]*Lv[i,a]
    beta_event = arb_mat(launch['native_event_7x98'].tolist())
    beta_child = arb_mat(child['derivative_action'].tolist())
    native_pairing = beta_event*E
    constraints = arb_mat(launch['constraint_derivative'].tolist())*E
    # Rank certificate for the FOUR actual canonical vectors only.
    Emid = arb_mat(98,4,[x.mid() for x in E.entries()])
    inverse_proposal = (Emid.transpose()*Emid).solve(Emid.transpose())
    rank_replay = inverse_proposal*E-identity(4)
    if bound(rank_replay)['approximate_upper'] >= 1:
        raise ArithmeticError('four-vector rank not certified')

    # Replay the historical seven-column Hessian complement at its OWN point.
    cap = BASE/'gate7_66d_checkpoint_20260926'
    direct = BASE/'gate7_8reaction_center_20260926/source/BHSM_GATE7_STAGEB_DIRECT_INTERFACE_20260925_163714.npz'
    refinement = cap/'BHSM_GATE7_STAGEB_RANK_REFINEMENT_20260925_173630.npz'
    adjudication = cap/'BHSM_GATE7_STAGEB_FINAL_NUMERICAL_ADJUDICATION_20260925_180354.json'
    if digest(direct) != '8005D5060E631EB9A7C65C42CF3ECFD64B2CE7A0C1900E44762CF9AD81278B10':
        raise ValueError('historical Stage-B input changed')
    receipt = json.loads((cap/'reproduction.json').read_bytes())
    for path in (refinement, adjudication):
        if digest(path) != receipt[path.name]['SHA256']:
            raise ValueError('historical refinement changed: '+path.name)
    with np.load(direct) as z:
        T_old = amat(z['node_013_constraint_tangent_action'])
        H_old = amat(z['node_013_H_action_98x98'])
    with np.load(refinement) as z:
        R_old = amat(z['node_013_R23'])
    rowledger = json.loads(adjudication.read_bytes())['rows'][0]['rowwise']
    scale = arb_mat(7,7)
    for i,row in enumerate(rowledger):
        scale[i,i] = 1/arb(float(row['fixed_scale']))
    beta_old = scale*R_old
    Ht, L_old = action_hessian_lift(T_old, H_old, beta_old)
    duality = beta_old*L_old-identity(7)

    sources += [center, ROOT/FIXED, direct, refinement, adjudication, OWNER,
        ROOT/'src/bhsm/interface/aether_n3_required_child_cauchy_flux_v17_93.py',
        ROOT/'src/bhsm/interface/canonical_boundary_material_seeds.py',
        ROOT/'scripts/derive_n12_gate7_slaved_interface.py',
        ROOT/'scripts/diagnose_n12_gate7_eight_reaction_center.py', cap/'reproduction.json', Path(__file__),
        BASE/'gate7_current_history_20260927/core/report.json',
        BASE/'gate7_current_history_20260927/core/arrays.npz']
    names = {'_trace_jacobian_at_order','_attachment_jacobian_at_order','_boundary_lift',
             '_canonical_pair_at_order','_metric_radial_flux_covector_at_order','_child_rows_at_order'}
    spans = {n.name:dict(first_line=n.lineno,last_line=n.end_lineno)
             for n in ast.parse(OWNER.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names}
    out.mkdir(parents=True,exist_ok=False)
    save_arrays(out/'arrays.npz',dict(
        canonical_attachment_2x37=B, attachment_material_derivative_2x37x73=dB,
        canonical_configuration_seed_raw_37x2=Lq, canonical_velocity_seed_raw_37x2=Lv,
        canonical_four_seed_action_98x4=E,
        native_event_on_canonical_four_7x4=native_pairing,
        native_child_on_canonical_four_7x4=beta_child*E,
        full_constraint_on_canonical_four_25x4=constraints,
        canonical_q_attachment_replay=B*Lq-identity(2),
        canonical_v_attachment_replay=B*Lv-identity(2),
        canonical_four_rank_replay=rank_replay,
        historical_normalized_beta_7x73=beta_old,
        historical_Hessian_lift_73x7=L_old,
        historical_Hessian_duality_replay=duality))
    rows = []
    for i in range(7):
        kind = 'trace' if i<3 else 'momentum' if i<5 else 'dynamic_flux'
        rows.append(dict(row=i+1,channel=kind,
            native_event=['(Tq)_1','(Tq)_2','(Tq)_3','(Lv^T g_v)_1','(Lv^T g_v)_2','(Lq^T radial)_1','(Lq^T radial)_2'][i],
            complete_child_target=['(Tq)_1','(Tq)_2','(Tq)_3','(Lv^T g_v)_1','(Lv^T g_v)_2','(Lq^T(g_q-radial)-DP[X])_1','(Lq^T(g_q-radial)-DP[X])_2'][i],
            child_balance_sign=1 if i<5 else -1,event_balance_sign=-1 if i<5 else 1,
            action_variation_seed=('NOT_IDENTIFIED: geometric trace output is not its conjugate force' if i<3 else
                'E_v Lv[:,a]: owned local action momentum contraction; not a seven-port right inverse' if i<5 else
                'E_q Lq[:,a]: owned configuration virtual direction; flux additionally requires radial and momentum-rate terms'),
            seed_state_component='none identified' if i<3 else 'zero' if i<5 else 'Lq[:,a]',
            seed_velocity_component='none identified' if i<3 else 'Lv[:,a]' if i<5 else 'zero',
            seed_rate_component='not an independent variable; dynamic flux contains DP[X]',
            history_reaction=None,history_launch_derivative=None))
    report = dict(status='CANONICAL_SEVEN_OUTPUTS_NOT_YET_BOUND_TO_SEVEN_ACTION_SEEDS',
        current_center_replay=bound(center_replay),
        canonical_q_duality=bound(B*Lq-identity(2)),canonical_v_duality=bound(B*Lv-identity(2)),
        canonical_four_rank=4,canonical_four_rank_inverse_defect=bound(rank_replay),
        full_constraint_leakage=bound(constraints),
        canonical_four_lie_in_K73=False if any(not x.contains(0) for x in constraints.entries()) else None,
        constraint_leakage_entry_absolute_lower=max(float(abs(x).lower()) for x in constraints.entries()),
        historical_seven_duality=bound(duality),
        historical_seven_scope='Algebra on frozen Stage-B numerical R23/H; not new current-center interval or variational authority.',
        historical_lift_formula='Ht=T^T H_action T; L=Ht^-1 beta^T (beta Ht^-1 beta^T)^-1; no positivity assumption',
        material_seed_change_of_basis_7x7=None,
        change_of_basis_reason='No seven-column material seed frame has been identified; the four canonical vectors cannot be converted into seven by a 7x7 basis change.',
        KKT_dual_rows_are_not_state_variations=True,
        attachment_motion_formula='DB_0[P]_{25+j}=-2 sech^2(2v) Dv[P] (-1)^j; DB_1=-DB_0',
        canonical_seed_motion_formula='K DL[P]=DE[P]-DK[P] L; E constant in the stored material attachment coordinates',
        canonical_seed_motion_materialized=False,
        canonical_seed_motion_reason='Frozen packets save L but not DL/DK. Contracted output jets do not determine vector-valued DL; no new action producer run before the seven-port pairing is bound.',
        ordinary_reaction_formula='D(DGamma[B_a])[P_j]=D2Gamma[P_j,B_a]+DGamma[D_Pj B_a]',
        first_missing_owner='A variational boundary-pairing identity identifying all seven canonical outputs with DGamma_joint_red[B_a], or the actual channel-dependent variational operator mapping the joint action to those mixed kinematic/canonical outputs.',
        no_impossibility_claim='This identifies the missing binding in the traced owner, not a theorem forbidding another action-owned extended boundary formulation.',
        mixed_object='CURRENT_CENTER_HEAT_ZETA_MIXED_BOUNDARY_LAUNCH_JET_7x73',
        R_history_7x73=None,R_complete_7x73=None,material_response_promoted=False,
        formation_history_reconstructed=False,prefix_rebuilt=False,action_producers_run=0,
        generic_second_operator_tensor_computed=False,rows=rows,source_lines=spans,
        source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        arrays_SHA256=digest(out/'arrays.npz'),Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps({k:report[k] for k in ('status','canonical_q_duality','canonical_v_duality',
        'canonical_four_rank_inverse_defect','full_constraint_leakage','historical_seven_duality')},indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    calculate(parser.parse_args().out)
