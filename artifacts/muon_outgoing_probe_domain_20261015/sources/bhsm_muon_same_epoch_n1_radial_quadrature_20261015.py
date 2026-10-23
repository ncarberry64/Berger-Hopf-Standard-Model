"""Same frozen-field/profile n1 radial quadrature, no physical exterior claim.

Only radial integration nodes and weights change. The exact saved raw268,
affine profile, original gauge/Higgs rows, wall and frame maps are retained.
This is new coefficient integration, not a background/source/D5 replay.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import sys
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'


def run(repository, output, orders):
    import numpy as np
    root,out=Path(repository).resolve(),Path(output).resolve()
    out.mkdir(parents=True,exist_ok=False)
    sys.path[:0]=[str(root/'src')]
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_birth_attached_phase import enriched_representation_from_values
    from bhsm.interface.muon_holomorphic_n1_magnetic_action import original_signed_stage,signed_n1_forms
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root)
    source=next(k.rsplit('/',1)[0] for k in phase['receipt']['input_hashes'] if k.endswith('/finite_moving_trace_run_1/result.json'))
    pins={}
    def read(path):
        p=Path(path);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}
    receipt=read(root/source/'result.json');values=read(root/source/'application.npz')
    base=root/'artifacts/muon_angular_retarded_polynomial_20261015/coefficients/coefficients_run_1'
    baseline=read(base/'result.json')
    stages=[read(base/f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz') for j in range(2)]
    keys=('M','B_forward','B_reverse','K');records=[];previous={};archives={}
    for order in orders:
        rep=enriched_representation_from_values(receipt,values,radial_points=order)
        folder=out/f'order{order}';folder.mkdir()
        stage_records=[];stage_archives={}
        for j,s in enumerate(stages):
            # The same original source law uses these affine geometry rates.
            affine=lambda a:np.r_[a[37:74],np.zeros(61,complex),a[99],np.zeros(169,complex)]
            candidate=read(root/'artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000/candidate.npz')
            trial=read(root/'artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/result.json')
            b=original_signed_stage(s['raw268'],s['actual_raw_coordinate_time'][:,None],s['parent_raw268'],
                affine(candidate['raw_pair'][0])[:,None],s['reference_raw_pair'],
                np.array([affine(a)for a in candidate['reference_pair']])[:,:,None],rep,
                side='child',lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=trial['action_parameters']['nu_squared_action'])
            forms=signed_n1_forms(b)
            payload=dict(s)
            for k,v in forms.items():
                if isinstance(v,np.ndarray):payload[k]=v
            # Changes to the retained field coordinates would invalidate refinement.
            for k in ('wall_value_map','frame_rows'):
                if not np.array_equal(payload[k],s[k]):raise ValueError('Radial refinement changed a physical coordinate map: '+k)
            diffs={k:dict(relative_to_finer=float(np.linalg.norm(payload[k]-previous[j][k])/max(np.linalg.norm(payload[k]),1e-300)),
                          absolute_max=float(np.max(abs(payload[k]-previous[j][k])))) for k in keys} if j in previous else None
            baseline_diffs={k:dict(relative=float(np.linalg.norm(payload[k]-s[k])/max(np.linalg.norm(payload[k]),1e-300)),
                                   absolute_max=float(np.max(abs(payload[k]-s[k]))))for k in keys}
            path=folder/f'stage_{j:04d}_exact_raw_signed_n1_forms_and_source.npz';_compressed_npz(path,payload)
            stage_archives[path.name]=sha256(path.read_bytes()).hexdigest();archives[path.relative_to(out).as_posix()]=stage_archives[path.name]
            previous[j]=payload
            stage_records.append(dict(stage=j,radial_points=order,previous_order_difference=diffs,
                baseline48_difference=baseline_diffs,original_336_and_nonzero_H_spin_preserved=True))
        md=dict(classification='SAME_FROZEN_PROFILE_RAW_EPOCH_RADIAL_QUADRATURE_N1_COEFFICIENTS',archives=stage_archives,
            input_hashes=pins,records=stage_records,physical_radial_convergence=False,source_D5_background_campaigns_repeated=False,
            producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        (folder/'result.json').write_text(json.dumps(md,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
        records.extend(stage_records)
        print(json.dumps(dict(event='assembled',order=order,records=stage_records)),flush=True)
    result=dict(classification='SAME_FROZEN_336_ROW_WEAK_FIELD_RADIAL_QUADRATURE_DIAGNOSTIC',orders=orders,records=records,
        input_hashes=pins,archives=archives,physical_outgoing_operator_evaluated=False,physical_radial_convergence=False,
        physical_muon_magnetic_moment=None,coupled_corrections_applied=0,physical_derivative_pass=False,
        source_D5_background_profile_history_canonical_pairing_campaigns_repeated=False,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    p.add_argument('--orders',nargs='+',type=int,default=[48,64,96,128])
    a=p.parse_args();run(a.repository,a.output,a.orders)
