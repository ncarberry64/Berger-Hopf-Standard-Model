"""Certify normalized stored midpoint construction, without physical promotion."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_physical_midpoint_hessian_errors as campaign
from bhsm.interface import stored_midpoint_kinematic_error as kinematic

RESULT=ROOT/'artifacts/flagship_integration/.stored_midpoint_kinematic_construction_work'


def build_point(interval):
    values,binding,_=campaign.load_inputs(interval)
    c=campaign.center
    inputs=c.center._load_inputs();axes=c.component._load_axes()
    tangents=inputs['endpoint'][2];mid_tangents=inputs['midpoint'][2]
    with np.load(c.ENDPOINT.with_suffix('.npz')) as source:
        times=source['collocation_arc_parameters'].copy()
    with np.load(c.PRECONDITIONER.with_suffix('.npz')) as source:
        right=source['reduced_right_Newton_blocks'][interval].copy()
    h=float(times[interval+1]-times[interval])
    frames=np.zeros((2,99,74));first=np.zeros_like(frames);derivative_sources={}
    for side,node in enumerate((interval,interval+1)):
        if node==0:continue
        frames[side]=c.cert._frame(tangents[node],c.cert.TRIAL_DESCRIPTOR_SCALE)
        path=c.MIXED_WORK/f'endpoint_{node:03d}.npz'
        derivative_sources[path.relative_to(ROOT).as_posix()]=campaign.cache.file_sha(path)
        with np.load(path) as source:first[side]=source['first_mid'][:,1:]
    target=c._kinematic_midpoint_map(interval,h,axes,tangents,mid_tangents).augmented
    x=np.linalg.solve(values['basis'],target)
    operands=dict(basis=values['basis'],frames=frames,axes=axes[interval:interval+2],
                  first_derivatives=first,step=np.asarray(h),stored_target=target,
                  approximate_coordinates=x)
    arrays,report=kinematic.enclose_midpoint_coordinates(**operands,retained_dimension=73,
                                                        fixed_left=interval==0)
    test=c.cert._frame(tangents[interval+1],c.cert.TEST_DESCRIPTOR_SCALE).T
    output=2*h*(-np.linalg.solve(right,test))/3
    combined=report['combined_construction_and_solve_error']
    pulled=kinematic.bound_stored_tensor_pullback(output,values['tensor'],x,73,
        combined['retained_operator_norm_upper'],combined['complement_operator_norm_upper'])
    construction=report['construction_only_coordinate_error']
    construction_pulled=kinematic.bound_stored_tensor_pullback(output,values['tensor'],x,73,
        construction['retained_operator_norm_upper'],construction['complement_operator_norm_upper'])
    # The latter is around Xhat, not S^-1 Mhat. Report it only as a diagnostic;
    # the combined bound above has the correct replacement target.
    paths=[Path(__file__),Path(kinematic.__file__),Path(kinematic.resolved.__file__),
           Path(kinematic.assembly.__file__),Path(c.__file__),Path(c.component.__file__),
           Path(c.component.scalar.__file__)]
    payload=dict(interval=interval,scope=report['scope'],construction=report,
        combined_stored_tensor_pullback=pulled,
        construction_error_about_approximate_coordinate_diagnostic=construction_pulled,
        diagnostic_is_not_a_separate_additive_certificate=True,
        operand_binary64_SHA256={k:campaign.array_sha(v) for k,v in operands.items()},
        output_map_SHA256=campaign.array_sha(output),stored_tensor_SHA256=campaign.array_sha(values['tensor']),
        physical_operand_source_binding=binding,derivative_source_SHA256=derivative_sources,
        source_SHA256={p.relative_to(ROOT).as_posix():campaign.sha(p) for p in paths},
        exact_stored_first_derivatives_only=True,all_midpoints_covered=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    arrays.update(operands);arrays['output']=output
    for name,digest in derivative_sources.items():
        if campaign.cache.file_sha(ROOT/name)!=digest:raise RuntimeError('stored derivative changed')
    return arrays,payload


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--midpoints');group.add_argument('--all-midpoints',action='store_true')
    args=parser.parse_args();RESULT.mkdir(parents=True,exist_ok=True)
    intervals=list(range(370)) if args.all_midpoints else campaign.parse_intervals(args.midpoints)
    for interval in intervals:
        arrays,payload=build_point(interval);stem=RESULT/f'midpoint_{interval:03d}'
        np.savez_compressed(stem.with_suffix('.npz'),**arrays)
        payload['data_SHA256']=campaign.cache.file_sha(stem.with_suffix('.npz'))
        stem.with_suffix('.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        if args.all_midpoints and (interval+1)%50 and interval!=369:continue
        print(json.dumps(dict(interval=interval,
            target_error=payload['construction']['target_construction_error_frobenius_upper'],
            combined_coordinate_error=payload['construction']['combined_construction_and_solve_error'],
            local_pair_error=payload['combined_stored_tensor_pullback']['local_pair_uniform_quadratic_coefficient_upper'])),flush=True)


if __name__=='__main__':main()
