"""Assemble and replay all base implicit equations from disjoint ranges."""
import argparse
import gzip
import json
from pathlib import Path
import sys
from flint import arb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.shared_action_taylor import Taylor,TaylorDomain
from certify_n12_gate7_endpoint_vector_transport import restore
import evaluate_n12_gate7_coupled_residual_saved as saved


def evaluate(parts,out):
    if out.exists(): raise FileExistsError('fresh residual assembly required')
    models={};rows={};source=None;template=None;provenance=[]
    for folder in parts:
        record=json.loads((folder/'record.json').read_bytes())
        if (record['algorithm']!='ORIGINAL_DOMAIN_BASE_IMPLICIT_RESIDUAL_VECTOR_V1'
                or record['original_physical_domain_unchanged'] is not True
                or record['vanishes_only_on_inherited_implicit_solution_graph'] is not True
                or saved.sha(folder/'models.json.gz')!=record['models_SHA256']):
            raise ValueError('source-bound original-domain residual models required')
        current={k:v for k,v in record['source_hashes'].items() if k!='reference_manifest'}
        if source is None:
            source=current;template=record
        elif current!=source:
            raise ValueError('identical physical inputs and residual arithmetic required')
        for key in ('family','original_state_groups','state_dimension','base_error_state_indices','equations'):
            if record[key]!=template[key]: raise ValueError('same retained residual family required')
        encoded=json.loads(gzip.decompress((folder/'models.json.gz').read_bytes()))
        if len(encoded)!=record['components'] or len(encoded)!=len(record['component_indices']):
            raise ValueError('complete range coefficients required')
        domain=TaylorDomain(record['original_state_groups'],record['state_dimension'])
        for i,row,values in zip(record['component_indices'],record['rows'],encoded,strict=True):
            if row['component']!=i or len(values)!=domain.dimension+2: raise ValueError('ordered residual rows required')
            v=[restore(pair) for pair in values]
            model=Taylor(domain,v[0],arb_mat(1,domain.dimension,v[1:-1]),v[-1])
            for key,actual in [('support',model.support()),('linear',model.linear_bound()),('nonlinear',model.r)]:
                if str(actual.fmpq())!=row[key]['exact']: raise ArithmeticError('residual bound failed exact replay')
            if i in models:
                if i not in (61,123) or models[i]!=values or rows[i]!=row:
                    raise ValueError('only byte-identical normalization rows may overlap')
            else: models[i]=values;rows[i]=row
        provenance.append(dict(record_SHA256=saved.sha(folder/'record.json'),models_SHA256=record['models_SHA256'],
                               component_indices=record['component_indices'],source_hashes=record['source_hashes']))
    if sorted(models)!=list(range(124)): raise ValueError('every base equation must be enclosed')
    out.mkdir(parents=True)
    archive=out/'models.json.gz';archive.write_bytes(gzip.compress(saved.encoded([models[i] for i in range(124)]),mtime=0))
    result={**template,'components':124,'component_indices':list(range(124)),
            'all_base_components_certified':True,'rows':[rows[i] for i in range(124)],
            'source_hashes':source,'models_SHA256':saved.sha(archive),
            'assembly':dict(evaluator_SHA256=saved.sha(Path(__file__)),sources=provenance,
                            all_residual_supports_replayed=True,action_derivatives_recomputed=False)}
    (out/'record.json').write_bytes(saved.encoded(result))
    print(json.dumps(dict(family=result['family'],residuals=124,all_bounds_replayed=True)),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--part',type=Path,action='append',required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();ctx.prec=512
    evaluate([p.resolve() for p in args.part],args.out.resolve())


if __name__=='__main__': main()
