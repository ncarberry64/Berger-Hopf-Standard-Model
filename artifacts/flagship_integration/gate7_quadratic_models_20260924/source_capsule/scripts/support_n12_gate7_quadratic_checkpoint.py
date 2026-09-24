"""Support completed descriptor models; no forward DAG replay or mutation."""
import argparse
import gzip
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from flint import arb,ctx,fmpq

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.shared_expression_graph import restore,pair
from bhsm.interface.sparse_quadratic_enclosure import QuadraticDomain,accumulate,clean
from bhsm.interface.block_quadratic_expansion import expand_batched
from bhsm.interface.quadratic_group_support import grouped_range


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();ctx.prec=512
    cp=json.loads(args.checkpoint.read_bytes())
    if cp['graph_SHA256']!='e104d285f142a40dcd307d5a1d6ee633e2b89c3f85ff62aa052041ec572724d9':
        raise ValueError('frozen midpoint graph required')
    path=(args.checkpoint.parent/'quadratics.sqlite').resolve()
    store=SimpleNamespace(db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True))
    d=QuadraticDomain([tuple(g) for g in cp['groups']],450,store)
    def encode(names):
        c=arb(0);a={};tails={};links=[];qb=arb(0)
        for name in names:
            row=cp['models'][name];c+=restore(row['c']);qb+=arb(fmpq(row['qb']))
            for i,v in row['a']:accumulate(a,i,restore(v))
            for k,v in row['tails'].items():accumulate(tails,k,arb(fmpq(v)))
            links.append((row['q'],arb(1)))
        a=clean(a);tails={k:v.upper() for k,v in tails.items()};r=sum(tails.values(),arb(0)).upper()
        print('supporting '+','.join(names),flush=True)
        q=expand_batched(store,links,d.groups,progress=lambda s:print(s,flush=True))
        if not c.is_zero() or a or any(not(150<=i<300<=j<450) for i,j in q):
            raise ValueError('pure mixed physical u/v polynomial required')
        interval,blocks=grouped_range(d,c,a,q);bound=(abs(interval).upper()+r).upper()
        return dict(c=pair(c),a=[[i,pair(v)] for i,v in sorted(a.items())],
                    quadratic=[[i,j,pair(v)] for (i,j),v in sorted(q.items())],
                    retained_quadratic_monomials=len(q),blocks=blocks,
                    residual_scalar_tail=str(r.fmpq()),residual_sources={k:str(v.fmpq()) for k,v in sorted(tails.items())},
                    support_upper=str(bound.fmpq()),support_approximate=float(bound),
                    circuit_triangle_quadratic_upper=str(qb.upper().fmpq()))
    metadata=json.load(gzip.open(ROOT/'artifacts/flagship_integration/gate7_shared_models_20260924/models/middle/metadata.json.gz','rt'))
    names=[f'descriptor/J/uv/term{i}' for i in (13,3,8)]
    # Publish the key combined screen first, then individually supported rows.
    combined=encode(names)
    old=sum((arb(fmpq(metadata['affine_enclosures'][n]['r'])) for n in names),arb(0)).upper()
    preliminary=dict(OLD=float(old),NEW=combined['support_approximate'],
                     reduction=float(old/arb(fmpq(combined['support_upper']))),
                     monomials=combined['retained_quadratic_monomials'],
                     tail=float(arb(fmpq(combined['residual_scalar_tail']))))
    args.out.with_name(args.out.stem+'_key_screen.json').write_text(json.dumps(preliminary,indent=2)+'\n')
    print(json.dumps(preliminary),flush=True)
    # Preserve the combined output immediately; later work cannot lose it.
    with args.out.with_name(args.out.stem+'_combined.json.gz').open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as z:
        z.write((json.dumps(combined,sort_keys=True)+'\n').encode())
    one=encode(names[:1]);two=encode(names[1:2])
    result=dict(frozen_checkpoint='cef38b6b',format='FROZEN_QUADRATIC_PROTOTYPE_V1',scope='descriptor',
        graph_SHA256=cp['graph_SHA256'],parameter_order=cp['parameter_order'],groups=cp['groups'],radius_exact=cp['radius_exact'],
        precision_bits=512,stats=cp['stats'],descriptor_assignments={names[0]:one,names[1]:two,names[2]:two},
        dominant_descriptor_combined=combined,OLD_sum_frozen_affine_scalar_tails=str(old.fmpq()),OLD_approximate=float(old),
        reduction_factor=preliminary['reduction'],Gate7_closed=False,physical_budget_debit=False,scientific_producers_run=False,
        frozen_calculations_rerun=False,intervals=[13],physical_failure_established=False,
        checkpoint_SHA256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest().upper(),
        support_backend='batched_group_matrix_with_exact_longitudinal_vertices')
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('DESCRIPTOR_SUPPORT_COMPLETE',flush=True)


if __name__=='__main__':main()
