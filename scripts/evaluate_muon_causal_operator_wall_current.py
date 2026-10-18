"""Run the reviewed additional current forcing AFTER Phase A is published."""
from __future__ import annotations

import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

from bhsm.interface.muon_causal_operator_wall_current import application


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--field-package',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts/muon_retained_response_20261018')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--phase-a-published-head',required=True)
    parser.add_argument('--resume',action='store_true',help='Verify and reuse completed per-arm checkpoints')
    args=parser.parse_args()
    if len(args.phase_a_published_head)!=40 or any(c not in '0123456789abcdef' for c in args.phase_a_published_head):
        raise ValueError('the parent must supply its verified Phase A published Git head')
    field=args.field_package.resolve();out=args.output.resolve()
    if out.exists() and not args.resume:
        raise FileExistsError('preserve completed or interrupted applications; choose/resume explicitly')
    out.mkdir(parents=True,exist_ok=args.resume)
    from bhsm.interface.retained_response.field_spin_connection import (OpenFieldPath,field_vertices,verify_inputs,verify_application_result,independently_projected_insertion)
    from bhsm.interface.retained_response.finite_time_response import evolve,interpolate,write_npz
    verify_application_result(field/'run_A')
    provenance=verify_inputs()
    result={
        'classification':'EVALUATED_FIXED_GEOMETRY_CANONICAL_OPERATOR_MATTER_CURRENT_AND_CAUSAL_HIGGS_WALL_RETURN',
        'phase_A_publication_head':args.phase_a_published_head,
        'input_package':'artifacts/muon_retained_response_20261018',
        'producer_source_sha256':{n:sha256((Path(__file__).resolve().parents[1]/n).read_bytes()).hexdigest() for n in ('scripts/evaluate_muon_causal_operator_wall_current.py','src/bhsm/interface/muon_causal_operator_wall_current.py','src/bhsm/interface/muon_charged_current_fermi_reduction.py','src/bhsm/interface/muon_static_coupled_charged_current.py')},
        'input_provenance':provenance,
        'normalization':{
            'common_intrinsic_action':'S4_raw/(2*pi^2)^2',
            'canonical_coefficient':'psi=sqrt(2*pi^2)*R4^(-3/2)*phi_Haar*a',
            'unit_coefficient_action':'integral dt a_dagger*(i partial_t-h_t)*a',
            'classical_action_scale':'S_hat=T*S_common',
            'current_stage_source':'-T^2*(partial_h_conditioned h_t) in d tau',
            'original_scalar_momentum':'p_original=J_H^(-T)*p_hat/T',
            'current_dual':'-T*J (J already integrates dt and includes At 1/T)',
            'density':'unselected operator operand; no contraction performed'},
        'scope':'same provisional fixed-geometry n1 histories; four-stage classical rule; finite initial30 and reached84; only additional matter forcing solved',
        'physical_flags':{
            'density_or_reference_selected':False,'physical_collider_solved':False,
            'physical_wall_closed':False,'physical_full_derivative_admitted':False,
            'coupled_physical_corrections':0,'native_completion_evaluated':False,
            'arms_glued':False,'a_mu':None,'g_mu':None,'uncertainty':None},
        'unchanged_limitations':['inherited calibrated scalar ancestry',
            'prior Maxwell gauge-reconstruction nonpass',
            'membrane finite-step nonpass','no continuum/time-error enclosure'],
        'NEXT_OPERAND':'derive/consume same-domain physical current/reference, collision/interface/normal/native/exterior terms and source/domain jets; no zero-wall closure',
        'sides':{}}
    if args.resume:
        previous=json.loads((out/'CHECKPOINT.json').read_text())
        if previous['phase_A_publication_head']!=args.phase_a_published_head or previous['input_provenance']!=provenance:
            raise ValueError('checkpoint input/publication identity changed; review affected application')
        for name,expected in previous['producer_source_sha256'].items():
            actual=result['producer_source_sha256'][name]
            if actual==expected:
                continue
            if name=='scripts/evaluate_muon_causal_operator_wall_current.py':
                registry=json.loads((out.parent/'RESUME_COMPATIBILITY.json').read_text())
                if any(row['before_sha256']==expected and row['after_sha256']==actual
                       for row in registry['reviewed_IO_only_changes']):
                    continue
            if actual!=expected:
                raise ValueError('checkpoint scientific source changed: '+name)
        result=previous
    for side in ('incoming','outgoing'):
        if side in result['sides']:
            record=result['sides'][side]
            file=out/record['artifact']['path']
            if sha256(file.read_bytes()).hexdigest()!=record['artifact']['sha256']:
                raise ValueError('completed arm artifact changed: '+side)
            if not record['all_scoped_checks_pass']:
                raise ValueError('completed arm records a nonpass: '+side)
            print(side+' reused completed hash-verified current application',flush=True)
            continue
        path=OpenFieldPath(side)
        # No Maxwell/Higgs coefficient or saved response producer is called.
        U=evolve(path.history)
        arrays,metrics=application(path,U,field_vertices()['V'],interpolate,
            saved_spin_file=field/'run_A'/f'{side}_spin_response.npz',
            independent_insertion=independently_projected_insertion)
        file=out/f'{side}_causal_operator_current.npz'
        write_npz(file,arrays)
        record={'T':path.T,'metrics':metrics,
                'artifact':{'path':file.name,'sha256':sha256(file.read_bytes()).hexdigest()},
                'checks':{}}
        # These are finite numerical consistency checks, never the physical gate.
        for name in ('new_canonical_stage_residual','independent_original_DAE_residual',
                     'independent_original_DAE_stage_difference','independent_original_DAE_final_difference',
                     'same_rule_scalar_Green_identity','causal_vs_pullback_including_endpoint',
                     'Higgs_current_Hermiticity','causal_wall_Hermiticity',
                     'saved_unperturbed_propagator_difference','sample_U_unitarity',
                     'saved_current_dual_reuse12_difference',
                     'independent_original_point_current_contraction'):
            record['checks'][name]=metrics[name]['maximum_entry_absolute']<2e-10
        record['all_scoped_checks_pass']=all(record['checks'].values())
        result['sides'][side]=record
        (out/'CHECKPOINT.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')
        print(side,json.dumps(record,sort_keys=True),flush=True)
        if not record['all_scoped_checks_pass']:
            raise ArithmeticError('preserved actual finite consistency failure; do not promote')
    target=out/'result.json'
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if not target.exists():
        target.write_text(payload,encoding='utf8')
    elif target.read_text()!=payload:
        raise ValueError('preserve differing completed result; review checkpoint')


if __name__=='__main__':
    main()
