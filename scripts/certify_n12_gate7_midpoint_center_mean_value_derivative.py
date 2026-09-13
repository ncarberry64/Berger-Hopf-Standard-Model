"""Enclose DF_M(w0) on the unchanged actual midpoint domain via uniform D2F."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse,json
from pathlib import Path
import numpy as np
from flint import arb,ctx
import diagnose_n12_gate7_directed_trial_hs_column as base
import n12_gate7_midpoint_center_uniform_mixed_variation as mixed
from bhsm.interface.midpoint_segment_family import validate_midpoint_segment_family
from bhsm.interface import affine_hs_midpoint_domain as grouped

p=base.p
THEORY=base.ROOT/'theory/n12_gate7_midpoint_center_mean_value_derivative.md'
ALGORITHM='UNIFORM_ACTUAL_MIDPOINT_CENTER_DIRECTION_MEAN_VALUE_ARB512_V1'

def evaluate(args):
    engine,source,_,selections=base.load_stage(args.interval,'midpoint',args.primal_pair)
    record,directional,files=base.read_pair(args.evidence_root/('midpoint_'+args.side))
    if (record.get('algorithm')!='CENTER_SPLIT_DIRECTED_FROZEN_TRIAL_HS_COLUMN_ARB512_V1'
            or record.get('interval')!=args.interval or record.get('trial_column')!=args.column
            or record.get('side')!=args.side or record.get('stage')!='midpoint'
            or record['report'].get('complete_original_directional_variation') is not True
            or record['report'].get('verified_point_derivative_contained') is not True):
        raise ValueError('paired complete original midpoint center action required')
    for key,value in source['binding'].items():
        if key=='files':
            if any(record['binding']['files'].get(name)!=digest for name,digest in value.items()):
                raise ValueError('midpoint center seed physical inputs differ')
        elif record['binding'].get(key)!=value:
            raise ValueError('midpoint frozen geometry differs: '+key)
    p.geometry.residual.merge(source['binding']['files'],record['binding']['files'])
    base.bind(source,*files)
    full=base.ROOT/f'artifacts/flagship_integration/.primal_mean_value_component_centered_midpoint_uniform_df_work/interval_{args.interval:03d}/derivative.npz'
    domain=engine.values.eq.midpoint.WORK/f'interval_{args.interval:03d}/domain.npz'
    for path in (full,domain):
        if source['binding']['files'].get(p.df.file_key(path))!=p.values.sha(path):
            raise ValueError('required paired data outside original midpoint binding')
    with np.load(full,allow_pickle=False) as a:
        line=p.hs.restore_balls(a['selected_line_variation_mid_q'],a['selected_line_variation_rad_q'])
        response=p.hs.restore_balls(a['response_variation_mid_q'],a['response_variation_rad_q'])
    with np.load(domain,allow_pickle=False) as a:
        raw=p.hs.restore_balls(a['raw_directions_mid_q'],a['raw_directions_rad_q'])
    if raw.shape!=(99,249) or line.shape!=(62,99) or response.shape!=(62,99):
        raise ValueError('complete midpoint directions and full first variations required')
    grouped.group_row_bounds(raw,source['groups'])
    scaled=raw.copy();unit=[]
    for group in source['groups']:
        scaled[:,group['start']:group['stop']]*=group['radius']
        unit.append(dict(group,radius=arb(1)))
    _,weights,_,_,_=p.values.operands()
    scaled[:98]*=np.array([arb(float(v)) for v in weights],dtype=object)[:,None]
    if directional['center_directions'].shape!=(99,1):
        raise ValueError('exact paired center direction required')
    source.update(_axis=directional['center_directions'][:,0],_weighted_tube_directions=scaled,
        _unit_groups=unit,_axis_seed_line=directional['center_selected_line_variation'],
        _axis_seed_response=directional['center_response_variation'],_full_seed_line=line,_full_seed_response=response)
    eq=engine.values.eq
    eigen=json.loads((eq.WORK/f'interval_{args.interval:03d}/record.json').read_bytes())
    value=json.loads((engine.values.WORK/f'interval_{args.interval:03d}/record.json').read_bytes())
    family=validate_midpoint_segment_family(eigen['report'],value['report'])
    for module in (mixed,mixed.graph,mixed.graph.parent,mixed.graph.parent.original,mixed.signed,
                   mixed.mixed_signed,mixed.normalization,grouped):
        base.bind(source,Path(module.__file__))
    base.bind(source,Path(__file__),THEORY,Path(base.__file__),
        Path(mixed.graph._batch_scalar.__code__.co_filename),Path(mixed.enclose_response_rows.__code__.co_filename),
        Path(validate_midpoint_segment_family.__code__.co_filename))
    p.verify_sources(source['binding'])
    arrays,report=mixed.evaluate(source,args.column)
    previous=directional['center_derivative'];selected=previous.copy()
    changed=base.select_first_variation(selected[:,0],arrays['derivative_candidate'][:,0])
    arrays.update(uniform_center_derivative=selected,previous_uniform_center_derivative=previous)
    report.update(family,same_family_segment_smoothness_established=True,
        uniform_midpoint_center_derivative_enclosed=True,exact_baseline_primal_selection=selections,
        all_249_scaled_directions_verified=True,previous_maximum_radius=float(max(v.rad() for v in previous.flat)),
        selected_maximum_radius=float(max(v.rad() for v in selected.flat)),coordinates_tightened=changed,
        full_trial_basis_enclosed=False,full_path_uniform_contraction=False,physical_quotient_identified=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    p.verify_sources(source['binding'])
    return source,arrays,report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--interval',type=int,default=13)
    parser.add_argument('--column',type=int,default=14)
    parser.add_argument('--side',choices=('left','right'),default='left')
    for name in ('primal-pair','evidence-root','out'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if not 0<args.interval<370 or not 0<=args.column<74:raise ValueError('interior interval and valid trial required')
    args.out=args.out.resolve();args.primal_pair=args.primal_pair.resolve();args.evidence_root=args.evidence_root.resolve()
    args.out.mkdir(parents=True,exist_ok=False);ctx.prec=512
    residual=p.geometry.residual
    targets=[(p.values,'sha'),(residual.center,'_sha'),(residual.foundation.coordinate.center,'_sha')]
    with base.cache.cache_hashes(targets,excluded_roots=[args.out]):
        try:
            source,arrays,report=evaluate(args);encoded={}
            for name,values in arrays.items():encoded[name+'_mid_q'],encoded[name+'_rad_q']=p.hs.rational_balls(values)
            data=args.out/'column.npz';np.savez_compressed(data,**encoded)
            record=dict(algorithm=ALGORITHM,binding=source['binding'],interval=args.interval,trial_column=args.column,
                side=args.side,data_SHA256=p.values.sha(data),report=report,FULL_BHSM_COMPLETE=False)
            (args.out/'record.json').write_bytes(p.geometry.encoded(record))
            print(json.dumps({k:v for k,v in report.items() if not isinstance(v,(dict,list))}),flush=True)
        except BaseException as error:
            (args.out/'failure.json').write_bytes(p.geometry.encoded(dict(error=repr(error),FULL_BHSM_COMPLETE=False)))
            raise

if __name__=='__main__':main()
