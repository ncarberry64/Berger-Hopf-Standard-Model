"""Compose an existing signed physical source family without new action work.

Source certificates and their independent reproduction are consumed as
lemmas. Only the hashes of the operands actually read here are checked.
Missing intervals remain explicit; they are never promoted to zero errors.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface import direct_causal_quadratic as causal


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def normalized_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest().upper()
def array_sha(array):
    return hashlib.sha256(np.asarray(array,dtype='<f8').tobytes()).hexdigest().upper()


def evaluate(root,family,out):
    ctx.prec=512
    artifacts=root/'artifacts/flagship_integration'
    foundation_path=artifacts/'BHSM_N12_GATE7_STORED_CAUSAL_ARITHMETIC_ENVELOPE.json'
    foundation=json.loads(foundation_path.read_bytes())
    center=artifacts/'BHSM_N12_GATE7_CURRENT_GREEN_SIGNED_TRANSVERSE_CAUSAL_CENTER.npz'
    axes_path=root/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    with np.load(center,allow_pickle=False) as z: maps=z['causal_maps_center'].copy()
    with np.load(axes_path,allow_pickle=False) as z: axes=z['current_center_green_image_unit_mid'].copy()
    axes[1:]/=np.linalg.norm(axes[1:],axis=1)[:,None];axes[0]=0
    if (maps.shape!=(370,74,74) or axes.shape!=(371,74)
            or array_sha(maps)!=foundation['causal_maps_SHA256']
            or array_sha(axes)!=foundation['axes_SHA256']):
        raise ValueError('unchanged full-history maps and axes required')
    paths={p:sha(p) for p in (foundation_path,center,axes_path,Path(__file__),Path(causal.__file__))}
    records={};selected=[]
    q={'LL':1,'LT':74,'TT':5476}[family]
    source_root=artifacts/'.direct_physical_quadratic_source_work'
    for i in range(370):
        folder=source_root/f'interval_{i:03d}'
        manifest_path=folder/'manifest.json';receipt_path=folder/'reproduction.json'
        if not manifest_path.exists() or not receipt_path.exists(): continue
        manifest=json.loads(manifest_path.read_bytes());receipt=json.loads(receipt_path.read_bytes())
        if (manifest.get('interval')!=i or manifest.get('complete_local_source_blocks') is not True
                or manifest.get('algorithm')!='DIRECT_PHYSICAL_HS_FIXED_FRAME_SIGNED_QUADRATIC_SOURCES_ARB512_V1'
                or receipt.get('byte_identical') is not True or receipt.get('independent_recomputation') is not True
                or receipt['manifest_SHA256']!=sha(manifest_path)):
            raise ValueError(f'Completed source lemma required at interval {i}')
        paths.update({p:sha(p) for p in (manifest_path,receipt_path)})
        for pair in ('00','01','10','11'):
            record_path=folder/f'{family}_{pair}.json';data=record_path.with_suffix('.npz')
            record=json.loads(record_path.read_bytes())
            if (record['interval']!=i or record['family']!=family or record['endpoint_pair']!=pair
                    or record['shape']!=[74,q] or record['precision_bits']!=512
                    or record['causal_maps_SHA256']!=foundation['causal_maps_SHA256']
                    or record['axes_SHA256']!=foundation['axes_SHA256']
                    or record['taylor_half_included'] is not True
                    or record['midpoint_second_incidence_included'] is not True
                    or record['data_SHA256']!=sha(data)):
                raise ValueError(f'Original signed {family} operand required at interval {i}')
            for p in (record_path,data):
                relative=p.relative_to(root).as_posix()
                digest=normalized_sha(p) if p.suffix=='.json' else sha(p)
                if manifest['files'].get(relative)!=digest:
                    raise ValueError('Source operand is not in the frozen source lemma')
                paths[p]=sha(p)
            records[i,pair]=data
        selected.append(i)
    def read(i):
        blocks={}
        for pair in ('00','01','10','11'):
            with np.load(records[i,pair],allow_pickle=False) as z:
                mids=z['Q_mid_q'];rads=z['Q_rad_q']
                if mids.shape!=(74,q) or rads.shape!=(74,q): raise ValueError('Complete source shape required')
                blocks[pair]=np.array([arb(str(a))+arb(0,arb(str(b)))
                    for a,b in zip(mids.flat,rads.flat,strict=True)],dtype=object).reshape(74,q)
        return blocks
    print(json.dumps({'family':family,'reused_intervals':selected,'new_action_evaluations':0}),flush=True)
    def progress(atoms,start,count):
        if atoms==1 or atoms%10==0:
            print(json.dumps({'family':family,'completed_atoms':atoms,'input_node':start,'total_nodes':count}),flush=True)
    result=causal.bound_causal_quadratic_family(maps,axes,read,family,
        foundation['frozen_map_perturbation_gain_upper'],active_intervals=selected,progress=progress)
    if any(sha(p)!=digest for p,digest in paths.items()): raise ValueError('A consumed operand changed')
    payload=dict(algorithm='RETAINED_SIGNED_HISTORY_SOURCE_FAMILY_COMPOSITION_V1',family=family,
        certified_source_intervals=selected,missing_source_intervals=sorted(set(range(370))-set(selected)),
        new_action_derivative_evaluations=0,local_interval_13_certificate_reopened=False,
        source_lemmas_recomputed=False,shared_endpoint_coefficients_combined_before_norm=True,
        result=result,source_SHA256={str(p.resolve()):digest for p,digest in paths.items()},
        neighborhood_remainder_enclosed=False,full_history_physical_inequalities_certified=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    with out.open('xb') as stream:
        stream.write((json.dumps(payload,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps({'family':family,'coefficients':result['frozen_inverse_quadratic_coefficients_upper']}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--evidence-root',type=Path,required=True)
    parser.add_argument('--family',choices=('LL','LT','TT'),required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    evaluate(args.evidence_root.resolve(),args.family,args.out)
