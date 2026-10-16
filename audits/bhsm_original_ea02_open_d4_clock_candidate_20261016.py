"""Fresh original277 check of a framed candidate for the saved open clock RHS.

The frame and cached border define a computational particular only. Nonzero
reactions, original equations and actual projected LHS are retained. A failed
candidate cannot exclude an unframed solution or select physical31/domain data.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BACKEND='audits/bhsm_original_ea02_d4_phase_operator_20261016.py'
BACKEND_SHA='c2f11bd4890631c03afee8b0db1fe8a93e505a12071da9cd2b9923744e8a5c6d'
CLOCK_SOURCE_SHA='8d4a7fe4fe24501c6d2e00681ed9ca4f1e2b5eb9d0793b3e775bab4c92b58574'
CLOCK_ARCHIVE_SHA='2e0b2140004e37699f80ed25d14c8d988f657598f6b7d4b1269bce292cf7039d'
FAMILY_SOURCE_SHA='972d919260a53d24bfebf77d3a6890f0cc2621f996cdc60fb62522c97464b83b'
FAMILY_ARCHIVE_SHA='7cb64de2130a2d3967f3a470132f0ae426ca3283da88d3ddc9b354fc040f15d4'


def execute(clock_folder,family_folder,output,*,maximum_checks=5):
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_producer.py').write_bytes(source)
    p=ROOT/BACKEND
    if sha256(p.read_bytes()).hexdigest()!=BACKEND_SHA:raise ValueError('Reviewed frozen phase backend changed')
    spec=importlib.util.spec_from_file_location('ea02_phase_for_clock_candidate',p)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    op=m.ActualEa02D4PhaseOperator();op.pin(p,BACKEND_SHA)
    from flint import acb
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    def packet(folder,source_sha,archive_sha):
        folder=Path(folder).resolve();report=op.read(folder/'result.json');op.pin(folder/'executed_producer.py',source_sha)
        if report['source_sha256']!=source_sha or report['archive']['sha256']!=archive_sha:raise ValueError('Frozen operand producer/metadata changed')
        z=op.read(folder/report['archive']['name'],archive_sha)
        if not np.array_equal(z['master368'],op.target['master368'])or z['coordinate_time'].item()!=op.target['coordinate_time'].item():raise ValueError('No same-time different-state or source splice')
        return z
    clock=packet(clock_folder,CLOCK_SOURCE_SHA,CLOCK_ARCHIVE_SHA)
    family=packet(family_folder,FAMILY_SOURCE_SHA,FAMILY_ARCHIVE_SHA)
    rhs=op.value(clock,'open_phase277_clock_rhs');chi=op.value(clock,'all36_clock_compatibility_compression')
    Z=op.value(family,'literal_gauge_phase_coefficients')
    projected_rhs_guard=Z.transpose()*rhs-chi
    if op.upper(projected_rhs_guard)>1e-25 or any(not projected_rhs_guard[i,j].contains(0)for i in range(36)for j in range(7)):raise ValueError('Exact original projected RHS required')
    def center_unknown(a):
        # This chooses a numerical point proposal for UNKNOWN coordinates.
        # Physical operator, map, source and RHS balls are never centered.
        return op.acb_mat([[acb(a[i,j].real.mid(),a[i,j].imag.mid())for j in range(a.ncols())]for i in range(a.nrows())])
    candidate,reaction,initial_cached_rows=op.precondition(rhs)
    candidate,reaction=center_unknown(candidate),center_unknown(reaction)
    history=[];germchecks=[]
    for k in range(maximum_checks):
        print(json.dumps(dict(stage='fresh_original277_clock_candidate',iteration=k,rights=7)),flush=True)
        Hcandidate,app=op.apply_phase(candidate);germchecks.append(dict(op.last_primal_germ_checks))
        _compressed_npz(out/f'fresh_clock_candidate_application_{k:02d}.npz',app)
        original=Hcandidate-rhs;framed=original+op.F.transpose()*reaction;frame=op.F*candidate
        record=dict(iteration=k,original277_upper=op.upper(original),plus_frame_reaction_upper=op.upper(framed),frame_upper=op.upper(frame),reaction_upper=op.upper(reaction),
            original277_midpoint_upper=op.upper(center_unknown(original)),original277_radius_envelope=op.upper(original-center_unknown(original)),
            plus_frame_reaction_midpoint_upper=op.upper(center_unknown(framed)),plus_frame_reaction_radius_envelope=op.upper(framed-center_unknown(framed)))
        history.append(record);print(json.dumps(record),flush=True)
        # Do not chase a nonzero reaction by repeatedly solving the same
        # imposed computational frame. Check that framed problem honestly.
        if max(record['plus_frame_reaction_upper'],record['frame_upper'])<=2e-10:break
        if k+1<maximum_checks:
            delta,dr,unused=op.precondition(-framed,-frame)
            candidate=center_unknown(candidate+delta);reaction=center_unknown(reaction+dr)
    projected_lhs=Z.transpose()*Hcandidate;projection_residual=projected_lhs-chi
    projection_identity=projection_residual-Z.transpose()*original
    reaction_projection=projected_lhs-chi+Z.transpose()*op.F.transpose()*reaction
    values=dict(saved_full277_clock_rhs=rhs,saved_projected36_clock_rhs=chi,
        computational_known_particular_phase_clock_candidate=candidate,computational_frame_reaction=reaction,
        initial_cached_interval_proposal_rows_separate=initial_cached_rows,fresh_Hphase_clock_candidate=Hcandidate,
        fresh_original277_clock_rows=original,fresh_plus_frame_reaction_rows=framed,
        fixed_computational_frame_clock_rows=frame,actual_projected_clock_LHS=projected_lhs,
        actual_projected_clock_LHS_minus_RHS=projection_residual,
        projected_residual_product_identity=projection_identity,
        projected_LHS_minus_RHS_plus_reaction=reaction_projection,
        open31_initial_phase_rhs_map_retained=op.value(family,'phase_rhs_open31_coefficients'))
    arrays=dict(master368=op.target['master368'],coordinate_time=op.target['coordinate_time'],
        open31_free_new_momentum_coordinate_labels=family['open31_free_new_momentum_coordinate_labels'])
    for key,a in values.items():
        arrays[key+'_high'],arrays[key+'_low']=op.split(a);arrays.update(op.exact.export_acb_exact_dyadic(a,key+'_exact'))
    path=out/'actual_open_D4_clock_candidate_original_rows_and_reactions.npz';_compressed_npz(path,arrays)
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and(name=='bhsm'or name.startswith('bhsm.'))and Path(p).resolve().is_relative_to(ROOT):op.pin(Path(p).resolve())
    op.pin(Path(__file__))
    framed_pass=bool(max(op.upper(framed),op.upper(frame))<=2e-10)
    original_pass=bool(max(op.upper(original),op.upper(frame))<=2e-10)
    report=dict(classification='ACTUAL_ORIGINAL_EA02_FRESH_OPEN_CLOCK_FRAMED_CANDIDATE',source_sha256=sha256(source).hexdigest(),
        input_and_source_sha256=dict(sorted(op.pins.items())),archive=dict(name=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()),
        fresh_check_history=history,fresh_matvec_calls=op.calls,fresh_same_primal_germ_guards=germchecks,
        candidate_phase_clock_coefficient_upper=op.upper(candidate),original277_clock_rows_upper=op.upper(original),
        plus_frame_reaction_rows_upper=op.upper(framed),frame_clock_rows_upper=op.upper(frame),reaction_upper=op.upper(reaction),
        projected_rhs_upper=op.upper(chi),actual_projected_LHS_upper=op.upper(projected_lhs),
        saved_projected_rhs_enclosure_guard_upper=op.upper(projected_rhs_guard),
        actual_projected_LHS_minus_RHS_upper=op.upper(projection_residual),
        projected_residual_product_identity_upper=op.upper(projection_identity),
        original277_midpoint_upper=op.upper(center_unknown(original)),
        original277_radius_envelope=op.upper(original-center_unknown(original)),
        plus_frame_reaction_midpoint_upper=op.upper(center_unknown(framed)),
        plus_frame_reaction_radius_envelope=op.upper(framed-center_unknown(framed)),
        projected_LHS_minus_RHS_plus_reaction_upper=op.upper(reaction_projection),
        row_check_tolerance=2e-10,computational_framed_problem_within_tolerance=framed_pass,
        original277_plus_computational_frame_within_tolerance=original_pass,
        projected_RHS_assumed_zero_or_left_null_certificate_claimed=False,
        reactions_counted_as_unframed_original_equation_pass=False,
        physical_frame_or_open31_values_or_outgoing_domain_selected=False,
        physical_continuous_clock_or_retarded_solution_claimed=False,
        failed_computational_candidate_is_a_physical_nonexistence_claim=False,
        source_primal_or_clock_RHS_recomputed=False,new_history_or_outer_coupled_correction=False,
        only_numerical_unknown_candidate_and_reaction_centered=True,full_physical_operator_and_rhs_balls_retained=True,
        original_coupled_corrections_applied=0,full_physical_derivative_Maxwell226_spin_moment=False)
    (out/'result.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items()if k not in('input_and_source_sha256','archive','fresh_same_primal_germ_guards')}),flush=True)
    if not framed_pass:raise ArithmeticError('Fresh framed candidate not admitted; failed rows and reactions preserved')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in('clock-folder','family-folder','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--maximum-checks',type=int,default=5);a=p.parse_args()
    try:execute(a.clock_folder,a.family_folder,a.output,maximum_checks=a.maximum_checks)
    except Exception as error:
        import traceback
        if a.output.exists():(a.output/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha256(Path(__file__).read_bytes()).hexdigest()),sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
        raise
