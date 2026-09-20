"""Enclose all velocities using finished corrections and unchanged raw rows.

This intermediate bound measures the remaining dependency loss. Missing
corrections use the original implicit-solve boxes, never zeros or estimates.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor
import bhsm.interface.input_linear_taylor as arithmetic
import evaluate_n12_gate7_coupled_residual_saved as saved
from certify_n12_gate7_endpoint_vector_transport import restore,upper


def evaluate(root,parent_path,adjoint_path,refined_path,folders,out):
    import bhsm.interface
    bhsm.interface.__path__.insert(0,str(root/'src/bhsm/interface'))
    verified=saved.evaluate(root)
    parent=json.loads((parent_path/'record.json').read_bytes())
    adjoint=json.loads(adjoint_path.read_bytes())
    refined=json.loads(refined_path.read_bytes())
    family=parent['family'];middle=family=='midpoint'
    if (family not in ('midpoint','endpoint') or adjoint['family']!=family
            or parent['physical_input_columns']!=74 or parent['input_map']!=adjoint['input_map']):
        raise ValueError('matching complete physical input family required')
    for record in (parent,adjoint,refined):
        if any(record['source_hashes'].get(k)!=v for k,v in verified['paired_source_hashes'].items()):
            raise ValueError('unchanged original physical source family required')
    if (parent['source_hashes']['adjoint']!=saved.sha(adjoint_path)
            or parent['source_hashes']['refined_base_radii']!=saved.sha(refined_path)):
        raise ValueError('unchanged anchor and base inclusion required')
    sources={**parent['source_hashes'],'evaluator':saved.sha(Path(__file__)),
             'implementation':saved.sha(Path(arithmetic.__file__)),
             'parent_record':saved.sha(parent_path/'record.json')}
    chosen={}
    for number,folder in enumerate(folders):
        manifest=folder.with_suffix('.terms')/'sources.json'
        reference=json.loads(manifest.read_bytes());reference_binding=saved.sha(manifest)
        for key in (*verified['paired_source_hashes'],'adjoint','refined_base_radii'):
            if reference.get(key)!=parent['source_hashes'][key]:
                raise ValueError('matching physical inputs required for completed row')
        sources[f'completed_manifest_{number}']=reference_binding
        for row_path in sorted(folder.glob('component_*.json')):
            row=json.loads(row_path.read_bytes());i=row['component']
            if i in chosen: raise ValueError('disjoint completed components required')
            model_path=folder/f'component_{i:02d}.json.gz'
            if row['models_SHA256']!=saved.sha(model_path): raise ValueError('completed payload fingerprint required')
            payload=json.loads(gzip.decompress(model_path.read_bytes()))
            if payload['source_binding']!=reference_binding or payload['component']!=i:
                raise ValueError('completed payload source binding required')
            chosen[i]=(payload,row)
            sources[f'completed_component_{i:02d}']=saved.sha(model_path)
    dimension=373 if middle else 199;nstate=dimension-124
    domain=TaylorDomain(parent['original_state_groups'],dimension)
    groups=parent['input_groups']
    pair='bhsm_midpoint_center_mean_value_right_pair_20260913' if middle else 'bhsm_endpoint_trial_mean_value_bootstrap_right_pair_20260913'
    eigen='.coupled_midpoint_eigenpair_pilot_work/interval_013' if middle else '.affine_eigenpair_pilot_work/endpoint_014'
    with np.load(root/'tmp'/pair/'value/first/column.npz',allow_pickle=False) as z,np.load(root/'artifacts/flagship_integration'/eigen/'eigenpair.npz',allow_pickle=False) as e:
        centers=[saved.read_matrix(z,f'point_center_{i}',center=True) for i in range(7)]
        ep=saved.read_matrix(e,'eigenpair_center',center=True)
        directions=saved.read_matrix(z,'weighted_tube_directions');raw=saved.read_matrix(z,'raw_domain')
    radii=[arb(v) for v in refined['correction_radii_exact'][:124]]
    rho=[arb(v) for v in parent['axis_correction_radii']]
    def model(c,a,rows,offset):
        values=[]
        for i in range(rows):
            coefficients=[a[i,j] for j in range(nstate)]+[arb(0)]*124
            coefficients[nstate+offset+i]=radii[offset+i]
            values.append(domain.affine(c[i,0],coefficients))
        return values
    def linear(c):
        value=InputLinearTaylor(domain,arb_mat(1,198,c),arb_mat(dimension,198),input_groups=groups)
        value._linear=arb(0)
        return value
    def axis(key,offset):
        point=arb_mat([[arb(v) for v in row] for row in adjoint[key]])
        values=[]
        for i in range(62):
            c=[point[i,j] for j in range(74)]+[arb(0)]*124
            c[74+offset+i]=rho[offset+i];values.append(linear(c))
        return values
    psi=model(ep,centers[3],61,0);hard=model(centers[0],centers[4],62,62)
    psi_u=axis('point_line_map',0);hard_u=axis('point_response_map',62)
    s=domain.affine(raw[98,0].mid(),[directions[98,j] for j in range(nstate)]+[arb(0)]*124)
    su=linear([arb(v) for v in adjoint['input_map'][98]]+[arb(0)]*124)
    source_bytes=saved.encoded(sources);binding=hashlib.sha256(source_bytes).hexdigest().upper()
    if out.exists() or out.with_suffix('.terms').exists(): raise FileExistsError('fresh snapshot required')
    out.mkdir(parents=True);out.with_suffix('.terms').mkdir()
    (out.with_suffix('.terms')/'sources.json').write_bytes(source_bytes)
    records=[]
    for i in range(61):
        if i in chosen:
            payload,old=chosen[i]
            v=[restore(pair) for pair in payload['coefficients']]
            if len(v)!=198+dimension*198+1: raise ValueError('complete corrected coefficient row required')
            value=InputLinearTaylor(domain,arb_mat(1,198,v[:198]),arb_mat(dimension,198,v[198:-1]),v[-1],groups)
            if str(value.support().fmpq())!=old['cancelled_support']['exact']: raise ArithmeticError('completed support must replay exactly')
            payload={**payload,'source_binding':binding}
        else:
            value=hard_u[61]*psi[i]+hard[61]*psi_u[i]+su*hard[i]+s*hard_u[i]
            payload=dict(component=i,coefficients=[[str(v.mid().fmpq()),str(v.rad().fmpq())]
                         for v in value.c.entries()+value.a.entries()+[value.r]],source_binding=binding)
        archive=out/f'component_{i:02d}.json.gz';archive.write_bytes(gzip.compress(saved.encoded(payload),mtime=0))
        record=dict(component=i,cancelled_support=upper(value.support()),linear=upper(value.linear_bound()),
                    nonlinear=upper(value.r),models_SHA256=saved.sha(archive),residual_cancellation_applied=i in chosen)
        records.append(record)
    result=dict(algorithm='FULL_INPUT_HYBRID_NUMERATOR_SNAPSHOT_V1',family=family,components=list(range(61)),
                all_61_velocity_components_certified=True,all_61_velocity_residuals_cancelled=len(chosen)==61,
                cancelled_components=sorted(chosen),unmodified_raw_components=sorted(set(range(61))-set(chosen)),
                original_state_groups=parent['original_state_groups'],input_groups=groups,input_map=parent['input_map'],
                axis_correction_radii=parent['axis_correction_radii'],source_hashes=sources,records=records,
                physical_input_columns=74,full_history_certified=False,Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(family=family,corrected=len(chosen),raw=61-len(chosen))),flush=True)


def main():
    parser=argparse.ArgumentParser()
    for key in ('evidence-root','parent','adjoint','refined','out'): parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--completed',type=Path,nargs='+',required=True)
    args=parser.parse_args();ctx.prec=512
    evaluate(args.evidence_root.resolve(),args.parent.resolve(),args.adjoint.resolve(),args.refined.resolve(),
             [p.resolve() for p in args.completed],args.out.resolve())


if __name__=='__main__': main()
