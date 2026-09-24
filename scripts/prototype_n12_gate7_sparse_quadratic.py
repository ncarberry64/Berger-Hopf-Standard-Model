"""Targeted degree-two compilation of immutable cef38b6b interval-13 DAGs."""
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from flint import arb,ctx,fmpq

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from bhsm.interface.sparse_quadratic_enclosure import QuadraticDomain,QuadraticStore
from bhsm.interface.frozen_quadratic_compiler import FrozenIndex,compile_selected
from bhsm.interface.shared_expression_graph import pair


def encoded(model,block=False):
    # Keep the historical flag accepted; both paths now use batched support.
    bound,q,blocks=model.final_support()
    return dict(c=pair(model.c),a=[[i,pair(v)] for i,v in sorted(model.a.items())],
                quadratic=[[i,j,pair(v)] for (i,j),v in sorted(q.items())],
                retained_quadratic_monomials=len(q),blocks=blocks,
                residual_scalar_tail=str(model.r.fmpq()),
                residual_sources={k:str(v.upper().fmpq()) for k,v in sorted(model.tails.items())},
                support_upper=str(bound.fmpq()),support_approximate=float(bound),
                circuit_triangle_quadratic_upper=str(model.qb.fmpq()))


def circuit_model(model):
    """Restart a numerical compilation without expanding or rebuilding its DAG."""
    return dict(c=pair(model.c),a=[[i,pair(v)] for i,v in sorted(model.a.items())],
                q=model.q,qb=str(model.qb.fmpq()),
                tails={k:str(v.fmpq()) for k,v in sorted(model.tails.items())})


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--index',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--scope',choices=['descriptor','targets'],default='descriptor')
    p.add_argument('--block-expand',action='store_true')
    args=p.parse_args();ctx.prec=512
    meta_path=ROOT/'artifacts/flagship_integration/gate7_shared_models_20260924/models/middle/metadata.json.gz'
    if hashlib.sha256(meta_path.read_bytes()).hexdigest()!='5189d7ec48defa3e57fa5b83f4d97f221bd6603d68dd6e773aa4f93a79c6aff5':
        raise ValueError('changed frozen midpoint root/parameter metadata')
    meta=json.load(gzip.open(meta_path,'rt'))
    receipt=json.loads((args.index/'receipt.json').read_text())
    if receipt['graph_SHA256']!='e104d285f142a40dcd307d5a1d6ee633e2b89c3f85ff62aa052041ec572724d9':
        raise ValueError('frozen midpoint source required')
    for name in ('nodes.jsonl','offsets.bin'):
        with (args.index/name).open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=receipt[name]: raise ValueError('changed read-only index')
    names=[f'descriptor/J/uv/term{i}' for i in (13,3,8)]
    if args.scope=='targets':
        names += [f'nonaffine_midpoint_incidence/{i}' for i in range(99)]
        names += ['normalization/'+x for x in ('norm','norm_u','norm_v','norm_uv')]
        names += [f'rate/{key}/{i}' for key in ('value','u','v') for i in range(99)]
        names += ['history/value/98','response/value/61']
    args.work.mkdir(parents=True,exist_ok=True)
    if (args.work/'quadratics.sqlite').exists(): raise FileExistsError('fresh compiler work directory required')
    d=QuadraticDomain([tuple(g) for g in meta['groups']],450,QuadraticStore(args.work/'quadratics.sqlite'))
    models,stats=compile_selected(FrozenIndex(args.index),meta,d,names,progress=lambda s:print(s,flush=True),
                                  frontier_path=args.work/'frontier.sqlite' if args.scope=='targets' else None)
    # Durable numerical checkpoint before any potentially expensive support.
    checkpoint=dict(models={n:circuit_model(v) for n,v in models.items()},stats=stats,
                    graph_SHA256=receipt['graph_SHA256'],parameter_order=meta['parameter_order'],groups=meta['groups'],
                    frozen_checkpoint='cef38b6b',radius_exact=meta['radius_exact'])
    d.store.db.commit()
    (args.work/'compiled_roots.json').write_text(json.dumps(checkpoint,sort_keys=True)+'\n')
    print('expanding selected outputs',flush=True)
    expanded={}
    assignments={}
    for n in names[:3]:
        node=meta['roots'][n]
        if node not in expanded:expanded[node]=encoded(models[n],args.block_expand)
        assignments[n]=expanded[node]
    combined=sum((models[n] for n in names[:3]),d.model())
    old=sum((arb(fmpq(meta['affine_enclosures'][n]['r'])) for n in names[:3]),arb(0)).upper()
    result=dict(frozen_checkpoint='cef38b6b',format='FROZEN_QUADRATIC_PROTOTYPE_V1',scope=args.scope,
                graph_SHA256=receipt['graph_SHA256'],parameter_order=meta['parameter_order'],groups=meta['groups'],
                radius_exact=meta['radius_exact'],precision_bits=512,stats=stats,
                descriptor_assignments=assignments,dominant_descriptor_combined=encoded(combined,args.block_expand),
                OLD_sum_frozen_affine_scalar_tails=str(old.fmpq()),OLD_approximate=float(old),
                Gate7_closed=False,physical_budget_debit=False,scientific_producers_run=False,
                frozen_calculations_rerun=False,intervals=[13],physical_failure_established=False)
    result['reduction_factor']=float(old/arb(fmpq(result['dominant_descriptor_combined']['support_upper'])))
    if args.scope=='targets':
        # Keep complete selected vector outputs as disk-backed quadratic
        # circuits. Supporting hundreds of components separately would lose
        # the signed projection and duplicate work before booking.
        result['target_circuit_models']={n:circuit_model(models[n]) for n in names}
        result['quadratic_circuit_file']=str((args.work/'quadratics.sqlite').resolve())
        d.store.db.commit()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(OLD=float(old),NEW=result['dominant_descriptor_combined']['support_approximate'],
                         reduction=result['reduction_factor'],stats=stats)),flush=True)


if __name__=='__main__': main()
