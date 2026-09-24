"""Bounded-storage missing-model producer with exact action-symmetry reuse.

Only independently reproduced new artifacts may be frozen. Prior work
directories supply completed new expression blocks, never new confidence
evaluations of inherited scientific certificates.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
import os
import regenerate_n12_gate7_shared_site_models as base
from bhsm.interface.shared_expression_graph import ExpressionDomain,Expression
from bhsm.interface.disk_expression_graph import DiskExpressionDomain


def produce(evidence,site,work,out):
    if out.exists():raise FileExistsError('fresh final artifact required')
    base.ctx.prec=512;work.mkdir(parents=True,exist_ok=True)
    s=base.setup(evidence,site);d=s['domain']
    manifest={'sources':s['sources'],'site':site,'interval':13,'radius_exact':s['radius_exact'],'parameter_order':d.names,'groups':d.groups}
    mp=work/'immutable_inputs.json';data=base.encode(manifest)
    if mp.exists():
        if mp.read_bytes()!=data:raise ValueError('immutable derived input receipt changed')
    else:base.fresh(mp,data)
    def solve(rhs,label,roots):
        proposal=[sum((a*b for a,b in zip(row,rhs)),d.affine(0)) for row in s['R']]
        for i,x in enumerate(rhs):roots[f'{label}/rhs/{i}']=x
        print(json.dumps({'phase':'BOUND_NEW_IMPLICIT_CORRECTION','quantity':label,'nodes':len(d.nodes)}),flush=True)
        scaled=[(x.support()/w).upper() for x,w in zip(proposal,s['w'])]
        if any(not v.is_finite() for v in scaled):raise ArithmeticError('nonfinite implicit correction enclosure')
        error=(max(scaled)*s['q']/(1-s['q'])).upper()
        return [x+d.affine(0,remainder=(w*error).upper(),provenance={'role':'new_implicit_remainder','quantity':label,'row':i,
            'formula':'w_i*q/(1-q)*norm_w(R rhs)','q_exact':str(s['q'].fmpq()),'dependency_unresolved':True}) for i,(x,w) in enumerate(zip(proposal,s['w']))]
    evaluate=base.Evaluator(s,work);rate,roots=base.mixed_graph(evaluate,solve,s)
    roots.update({f'endpoint/state/{i}':x for i,x in enumerate(s['state'])})
    print(json.dumps({'phase':'SERIALIZE_COMPLETE_NEW_GRAPH','nodes':len(d.nodes),'roots':len(roots)}),flush=True)
    graph=d.export(roots,include_bounds=True)
    for name,row in graph['affine_enclosures'].items():
        if not base.arb(base.fmpq(row['r'])).is_finite():raise ArithmeticError('nonfinite exported model: '+name)
    graph.update({'interval':13,'site':site,'radius_exact':s['radius_exact'],'source_SHA256':s['sources'],
        'new_action_receipts':evaluate.receipts,'frozen_checkpoint':'baf41b96','correlation_audit':'f5b6b4b6',
        'inherited_certificates_recomputed':False,'physical_budget_debit':False,'Gate7_closed':False,
        'common_border_exact_identity_used':True,'positive_border_lower_exact':str(s['b_lower'].fmpq()),
        'remaining_input_relaxations':['inherited primal value dependence on theta','inherited first derivative coefficient dependence on theta','implicit correction tails'],
        'full_correlated_Layer_C_certified':False})
    if any(base.sha(Path(p))!=h for p,h in s['sources'].items()):raise ValueError('input changed during missing-model calculation')
    out.parent.mkdir(parents=True,exist_ok=True);pending=out.with_suffix(out.suffix+'.pending')
    with pending.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as stream:
        encoder=json.JSONEncoder(sort_keys=True,separators=(',',':'))
        for chunk in encoder.iterencode(graph):stream.write(chunk.encode())
        stream.write(b'\n')
    os.replace(pending,out)
    print(json.dumps({'phase':'GRAPH_SAVED','SHA256':base.sha(out),'nodes':len(d.nodes)}),flush=True)


def run(args):
    original_domain,original_setup,original_evaluator=base.ExpressionDomain,base.setup,base.Evaluator
    previous=[(p,json.loads((p/'immutable_inputs.json').read_bytes())) for p in args.previous]
    def setup(evidence,site):
        old=ExpressionDomain.flatten_limit_default;ExpressionDomain.flatten_limit_default=None
        try:s=original_setup(evidence,site)
        finally:ExpressionDomain.flatten_limit_default=old
        for p in (Path(__file__),base.ROOT/'src/bhsm/interface/disk_expression_graph.py'):
            s['sources'][str(p.resolve())]=base.sha(p)
        return s
    class Evaluator(original_evaluator):
        def __init__(self,s,work):
            super().__init__(s,work);self.calls=0;self.memo={};self.storage=[]
        def calculate(self,legs,all_rows):
            d=self.s['domain'];legs=[[d.coerce(x) for x in leg] for leg in legs]
            semantic=(all_rows,tuple(sorted(tuple(x.index for x in leg) for leg in legs)))
            if semantic in self.memo:
                value,sequence=self.memo[semantic]
                self.receipts.append({'sequence':len(self.receipts)+1,'same_action_by_leg_symmetry':sequence})
                return value
            value=None
            for folder,manifest in previous:
                if manifest['site']!=self.s['site']:continue
                key=hashlib.sha256(base.encode({'gradient':all_rows,'legs':[[x.index for x in leg] for leg in legs],
                    'state':[x.index for x in self.s['state']],'prefix':d.digest.hexdigest(),'sources':manifest['sources']})).hexdigest()
                path=folder/(key+'.json.gz')
                if not path.exists():continue
                for name,h in manifest['sources'].items():
                    p=Path(name)
                    if base.sha(p)!=h:
                        backup=folder.parent/'source_snapshot'/p.name
                        if not backup.exists() or base.sha(backup)!=h:raise ValueError('completed new block source binding differs')
                record=json.loads(gzip.decompress(path.read_bytes()))
                if record['prefix']!=d.digest.hexdigest() or record['start']!=len(d.nodes):raise ValueError('completed new block prefix differs')
                for i,n in enumerate(record['nodes'],record['start']):
                    if d.node(n).index!=i:raise ValueError('completed new node identity differs')
                d.leaf_provenance.update(record['leaf_provenance'])
                values=[Expression(d,i) for i in record['roots']]
                value=values if all_rows else values[0]
                self.receipts.append({'sequence':len(self.receipts)+1,'SHA256':base.sha(path),'new_derived_evidence':True})
                self.storage.append({'SHA256':base.sha(path),'path':str(path.resolve())})
                print(json.dumps({'phase':'REUSE_COMPLETED_NEW_EXPRESSION','key':key[:12],'nodes':len(d.nodes)}),flush=True)
                break
            if value is None:
                old_count=len(self.receipts);value=super().calculate(legs,all_rows)
                if len(self.receipts)>old_count:
                    row=self.receipts[-1]
                    self.storage.append({'SHA256':row['SHA256'],'path':str((self.work/row['file']).resolve())})
                    self.receipts[-1]={'sequence':len(self.receipts),'SHA256':row['SHA256'],'new_derived_evidence':True}
            self.memo[semantic]=(value,len(self.receipts))
            self.calls+=1
            if self.calls==2:d.flatten_limit=32
            # Execution-location inventory is deliberately separate from the
            # scientific payload so independent fresh work paths reproduce.
            (self.work/'storage.json').write_bytes(base.encode(self.storage))
            return value
    base.ExpressionDomain,base.setup,base.Evaluator=DiskExpressionDomain,setup,Evaluator
    try:produce(args.evidence_root.resolve(),args.site,args.work.resolve(),args.out.resolve())
    finally:base.ExpressionDomain,base.setup,base.Evaluator=original_domain,original_setup,original_evaluator


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--site',choices=('left','right'),required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--previous',type=Path,nargs='*',default=[])
    run(p.parse_args())
