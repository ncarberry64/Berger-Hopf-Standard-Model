"""Bounded graph storage, reusing the two completed new scalar expressions.

The retained-expression semantics are unchanged. Only addition tree shape
changes after the initial two scalar blocks. Repeat mode evaluates those
NEW blocks independently, with the same graph prefix and frozen inputs.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
import regenerate_n12_gate7_shared_site_models as base
from bhsm.interface.shared_expression_graph import ExpressionDomain,Expression


def run(evidence,site,work,out,seed):
    original_setup,original_evaluator=base.setup,base.Evaluator
    def setup(evidence,site):
        old=ExpressionDomain.flatten_limit_default
        ExpressionDomain.flatten_limit_default=None
        try:s=original_setup(evidence,site)
        finally:ExpressionDomain.flatten_limit_default=old
        s['sources'][str(Path(__file__).resolve())]=base.sha(Path(__file__))
        return s
    class Evaluator(original_evaluator):
        def __init__(self,s,work):
            super().__init__(s,work);self.initial_scalar_count=0
        def calculate(self,legs,all_rows):
            if self.initial_scalar_count>=2:
                value=super().calculate(legs,all_rows)
                if self.receipts:
                    item=self.receipts[-1]
                    self.receipts[-1]={'sequence':len(self.receipts),'SHA256':item['SHA256'],'new_derived_evidence':True}
                return value
            if all_rows or len(legs)!=3:raise ValueError('expected two initial missing scalar contractions')
            d=self.s['domain']
            if seed is None:
                values=super().calculate(legs,all_rows)
            else:
                inherited=json.loads((seed/'immutable_inputs.json').read_bytes())
                if inherited['site']!=site:raise ValueError('matching new scalar site required')
                for name,h in inherited['sources'].items():
                    p=Path(name)
                    if base.sha(p)!=h:
                        backup=seed.parent/'source_snapshot'/p.name
                        if not backup.exists() or base.sha(backup)!=h:raise ValueError('saved new scalar source binding failed: '+name)
                key=hashlib.sha256(base.encode({'gradient':False,'legs':[[x.index for x in leg] for leg in legs],
                    'state':[x.index for x in self.s['state']],'prefix':d.digest.hexdigest(),'sources':inherited['sources']})).hexdigest()
                path=seed/(key+'.json.gz');record=json.loads(gzip.decompress(path.read_bytes()))
                if record['prefix']!=d.digest.hexdigest() or record['start']!=len(d.nodes):raise ValueError('saved new scalar graph prefix differs')
                for i,n in enumerate(record['nodes'],record['start']):
                    if d.node(n).index!=i:raise ValueError('saved scalar node identity differs')
                d.leaf_provenance.update(record['leaf_provenance'])
                values=Expression(d,record['roots'][0])
                self.receipts.append({'file':str(path.resolve()),'SHA256':base.sha(path),'new_derived_evidence':True,'completed_new_scalar_reused':True})
                print(json.dumps({'phase':'REUSED_COMPLETED_NEW_SCALAR','key':key[:12],'nodes':len(d.nodes)}),flush=True)
            self.initial_scalar_count+=1
            item=self.receipts[-1]
            self.receipts[-1]={'sequence':len(self.receipts),'SHA256':item['SHA256'],'new_derived_evidence':True}
            if self.initial_scalar_count==2:d.flatten_limit=32
            return values
    base.setup,base.Evaluator=setup,Evaluator
    try:base.run(evidence,site,work,out)
    finally:base.setup,base.Evaluator=original_setup,original_evaluator


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--site',choices=('left','right'),required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=Path)
    a=p.parse_args();run(a.evidence_root.resolve(),a.site,a.work.resolve(),a.out.resolve(),a.seed.resolve() if a.seed else None)
