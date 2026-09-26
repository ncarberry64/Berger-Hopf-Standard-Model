"""Owner identity and frozen point-fiber replay; no scientific producers."""
import argparse
import ast
import io
import json
from pathlib import Path

import numpy as np
from flint import arb, ctx, fmpq

from checkpoint_n12_gate7_66d_tangent_binding import (
    ROOT, BASE, FIXED, PHYSICAL, SCALE, amat, mid, bound, digest, encoded,
)

C = ROOT/BASE/'gate7_66d_checkpoint_20260926'
NULL = ROOT/BASE/'gate7_local_null_classification_20260926'
LINK = ROOT/BASE/'gate7_shared_eigenbranch_links_20260923/certificate.json'
HIST = ROOT/BASE/'BHSM_N12_C2_FRESH_DESCRIPTOR_FIBER_EIGENLINE_CHART.npz'
BIRTH = ROOT/BASE/'BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.npz'
DIRECT = ROOT/BASE/'gate7_8reaction_center_20260926/source/BHSM_GATE7_STAGEB_DIRECT_INTERFACE_20260925_163714.npz'
ACTION = 'src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py'
HIST_SCRIPT = 'scripts/certify_n12_c2_fresh_descriptor_fiber_eigenline_chart.py'
CURRENT_FIELD = 'src/bhsm/interface/aether_forward_c2_exact_fixed_s_field.py'
PROVENANCE = {
    'scripts/certify_n12_c2_regularized_launch_segment.py': [(96,128)],
    HIST_SCRIPT: [(60,102),(242,269),(295,307)],
    'scripts/audit_n12_c2_descriptor_fiber_denominator.py': [(90,101)],
    CURRENT_FIELD: [(20,38),(51,87),(108,145),(197,217)],
    'scripts/materialize_n12_gate7_augmented_fixed_descriptor_newton_endpoint_candidate.py': [(68,100),(127,134),(153,171)],
    'scripts/materialize_n12_gate7_correlated_descriptor_newton_endpoint_candidate.py': [(59,83)],
    'scripts/certify_n12_gate7_affine_eigenpair_pilot.py': [(50,61),(66,105),(136,149)],
    'theory/n12_c2_descriptor_fiber_denominator.md': [(1,30)],
    'theory/n12_c2_fresh_descriptor_fiber_eigenline_chart.md': [(1,19)],
}


def interval_record(x):
    return dict(lower_exact=str(x.lower().fmpq()),upper_exact=str(x.upper().fmpq()),
                midpoint=float(x.mid()),radius_upper=float(x.rad().upper()),contains_zero=bool(x.contains(0)))


def calculate():
    ctx.prec=512
    sources={}
    def verify(path,expected=None):
        actual=digest(path)
        if expected is not None and actual!=expected:raise ValueError('source changed: '+str(path))
        key=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        sources[key]=actual
    binding=json.loads((C/'binding/report.json').read_bytes())
    for path in (ROOT/FIXED,ROOT/PHYSICAL):verify(path,binding['source_SHA256'][str(path)])
    for folder in (C/'binding',NULL):
        meta=json.loads((folder/'report.json').read_bytes())
        verify(folder/'report.json');verify(folder/'arrays.npz',meta['arrays_SHA256'])
    verify(LINK);links=json.loads(LINK.read_bytes())
    # Resolve the exact already-frozen external packet through its owner ledger.
    record_path=next(Path(k) for k in links['source_SHA256'] if k.endswith('endpoint_013\\record.json'))
    point_data=record_path.with_name('eigenpair.npz')
    for path in (record_path,point_data,record_path.with_name('reproduction.json')):
        verify(path,links['source_SHA256'][str(path)])
    point=json.loads(record_path.read_bytes());proof=point['report']['point_eigenpair_proof']
    verify(ROOT/ACTION,point['binding']['files'][ACTION])
    if point['binding']['files'][FIXED.as_posix()]!=digest(ROOT/FIXED):raise ValueError('point belongs to another endpoint source')
    for path in (HIST,HIST.with_suffix('.json'),BIRTH,FIXED.with_suffix('.json')):
        verify(ROOT/path if not path.is_absolute() else path)
    history=json.loads(HIST.with_suffix('.json').read_bytes())
    verify(HIST,history['data_SHA256'])
    current=json.loads((ROOT/FIXED.with_suffix('.json')).read_bytes())
    with np.load(ROOT/FIXED) as z:
        state=z['projected_states'][13];s=float(z['independent_signed_descriptors'][13])
        reference=z['branch_reference'];weights=z['state_weights'];gradient=z['descriptor_gradient_action_diagnostic'][13]
    with np.load(HIST) as z:historical_reference=z['branch_reference'];historical_weights=z['state_weights']
    with np.load(BIRTH) as z:birth_reference=z['branch_reference']
    with np.load(point_data) as z:
        point_state=z['center_state_mid_q'];point_state_radius=z['center_state_rad_q']
    exact_center_match=all(fmpq(str(a))==fmpq(*float(b).as_integer_ratio()) for a,b in zip(point_state,state,strict=True)) and all(fmpq(str(a))==0 for a in point_state_radius)
    def jet_body(path):
        tree=ast.parse((ROOT/path).read_text(encoding='utf-8'))
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_jet')
        return ast.dump(fn.body[0],include_attributes=False)
    identity_checks=dict(same_jet_call_AST=jet_body(HIST_SCRIPT)==jet_body(CURRENT_FIELD),
        same_stored_reference=np.array_equal(reference,historical_reference) and np.array_equal(reference,birth_reference),
        same_action_weights=np.array_equal(weights,historical_weights),
        historical_branch_24=history['center']['selected_branch']==24,
        current_branch_24=current['rows'][13]['selected_branch']==24,
        certified_point_index_24=proof['selected_zero_based_index_verified']==24,
        positive_reference_overlap=proof['positive_stored_reference_overlap'],
        certified_normalized_line=proof['normalized_eigenpair_enclosed'] and proof['validation_passed'],
        frozen_point_exact_center=exact_center_match)
    if not all(identity_checks.values()):raise ValueError('DESCRIPTOR_IDENTITY_UNPROVEN: '+str(identity_checks))
    provenance={}
    for name,ranges in PROVENANCE.items():
        verify(ROOT/name);lines=(ROOT/name).read_text(encoding='utf-8').splitlines()
        provenance[name]=[dict(start=a,end=b,text='\n'.join(lines[a-1:b])) for a,b in ranges]
    verify(Path(__file__))
    eigenvalue=arb(proof['target_midpoints_rational'][61])+arb(0,arb(proof['target_radii_rational'][61]))
    residual=eigenvalue-arb(s)
    if residual.contains(0):raise ValueError('center adjudication changed; review before building an appended system')
    with np.load(NULL/'arrays.npz') as z:
        null=z['unit_null'];null_lo=str(z['unit_null_lower_exact'][0]);null_hi=str(z['unit_null_upper_exact'][0])
    with np.load(C/'binding/arrays.npz') as z:
        child=z['node_013_child_augmented'];X=z['node_013_fixed_into_physical']
    with np.load(ROOT/PHYSICAL) as z:B=z['endpoint_physical_tangent_action'][13]
    refinement=C/'BHSM_GATE7_STAGEB_RANK_REFINEMENT_20260925_173630.npz'
    adjudication=C/'BHSM_GATE7_STAGEB_FINAL_NUMERICAL_ADJUDICATION_20260925_180354.json'
    for path in (DIRECT,refinement,adjudication):verify(path)
    with np.load(DIRECT) as z:T=z['node_013_constraint_tangent_action'];H=z['node_013_H_action_98x98']
    with np.load(refinement) as z:A=z['node_013_R23']
    scales=np.array([r['fixed_scale'] for r in json.loads(adjudication.read_bytes())['rows'][0]['rowwise']])
    An=A/scales[:,None]
    # The same stored action-Hessian complement convention as the frozen split,
    # now evaluated at node 13. No 8x8 reaction block is extracted or altered.
    HT=amat(T).transpose()*amat(H)*amat(T)
    inverse_times=HT.solve(amat(An).transpose())
    gram=amat(An)*inverse_times
    L=mid(inverse_times*gram.inv())
    boundary=np.vstack((X@L,np.zeros((1,7))))
    fiber_row=np.r_[gradient@B/SCALE,-1.]
    arrays=dict(fiber_row_reduced_proof_diagnostic=fiber_row,child_replay_diagnostic=fiber_row@child,
        boundary_replay_diagnostic=fiber_row@boundary,node13_boundary_lift_fixed=L,
        node13_boundary_directions_reduced=boundary,unit_null=null)
    report=dict(descriptor_identity='SAME_EULER_DIRAC_DESCRIPTOR_PROVED',
        status='STOP_FROZEN_CENTER_OFF_DESCRIPTOR_FIBER',base_commit='7d2a7db789391426dbd3b6529ab3a4e6c5ca7b7d',
        identity_checks=identity_checks,source_SHA256=sources,source_line_provenance=provenance,
        owner='Same finite N12 retained action, 96 quadrature points, raw H[37:,37:] in 61 velocity/multiplier coordinates; normalized real eigenvector, common positive-reference orientation, zero-based selected index 24.',
        identity_scope='Identity of the selected scalar functional, not equality of an independently transported coordinate with its value at every approximate center. Historical event labels the forward-swapped first arm that becomes C2.',
        scaling='s is signed physical eigenvalue, not abs(lambda), lambda^2, an action-congruent eigenvalue or a lapse. Descriptor perturbations use physical ds=1e-7*ds_proof; test scale 1e6 is only residual scaling.',
        node13=dict(s13=s,s13_exact=str(arb(s).fmpq()),lambda_owner=interval_record(eigenvalue),
            residual_physical=interval_record(residual),residual_proof=interval_record(residual/arb(SCALE)),
            branch_index=24,numerical_selected_line_gap=current['rows'][13]['selected_eigenline_gap'],
            certified_connected_link_gap_lower=links['links'][0]['gap_lower'],
            point_witness_radius_exact=proof['target_radii_rational'][61],center_satisfies_fiber=False,
            allowance='The frozen point eigenpair enclosure excludes zero residual. Tangent-reprojection allowances and tube radii are not licenses to erase a center value defect.',
            binary64_eigensolve_used=False,point_or_action_producer_rerun=False),
        covector=dict(formula='D R_fiber=(Dlambda_action dY_action)-ds_physical; divide the row by 1e-7 for proof output.',
            null_proof_lower_exact=str(-fmpq(null_hi)),null_proof_upper_exact=str(-fmpq(null_lo)),
            null_proof_midpoint=-float(null[0]),null_physical_midpoint=-SCALE*float(null[0]),
            null_authority='Exact dY13=0; the only derivative is minus the signed descriptor coordinate. Bounds inherit the frozen exact unit-null enclosure.',
            child_replay_proof_norm_diagnostic=float(np.linalg.norm(arrays['child_replay_diagnostic'])),
            boundary_replay_proof_diagnostic=arrays['boundary_replay_diagnostic'].tolist(),
            boundary_duality_replay=bound(amat(An)*amat(L)-amat(np.eye(7))),
            non_null_covector_authority='Stored diagnostic Dlambda and frozen center lifts only; no new rigorous gradient radius. Child compatibility is not promoted to a certificate.',
            child_tangent_compatibility_proved=False),
        row_appended=False,system_75_rank=None,system_75_condition=None,system_75_inverse_defect=None,
        old_8x8_reextracted=False,reaction_replay_repeated=False,center_modified=False,
        nonlinear_work_attempted=False,scientific_producers_run=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        next_requirement='Resolve the certified nonzero fiber defect at the frozen center with owner-bound recentering/error propagation before any appended-row, Schur or nonlinear claim; this task does not authorize changing the center.')
    return report,arrays


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report,arrays=calculate();args.out.mkdir(parents=True,exist_ok=False)
    buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue());report['arrays_SHA256']=digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(report['descriptor_identity']);print(report['status']);print(report['node13']['residual_physical']['midpoint'])


if __name__=='__main__':main()
