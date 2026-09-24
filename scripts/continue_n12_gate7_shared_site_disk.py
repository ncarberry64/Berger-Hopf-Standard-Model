"""Continue saved new expressions using bounded RAM, without action reruns."""
import argparse,gzip,hashlib,json
from pathlib import Path
import regenerate_n12_gate7_shared_site_models as base
import resume_n12_gate7_shared_site_models as resumed
from bhsm.interface.disk_expression_graph import DiskExpressionDomain
from bhsm.interface.shared_expression_graph import Expression


def run(args):
    original_domain,original_setup,original_evaluator=base.ExpressionDomain,base.setup,base.Evaluator
    previous=json.loads((args.previous/'immutable_inputs.json').read_bytes()) if args.previous else None
    def setup(evidence,site):
        s=original_setup(evidence,site)
        for p in (Path(__file__),base.ROOT/'src/bhsm/interface/disk_expression_graph.py'):
            s['sources'][str(p.resolve())]=base.sha(p)
        return s
    class Evaluator(original_evaluator):
        def calculate(self,legs,all_rows):
            if previous is not None:
                d=self.s['domain']
                key=hashlib.sha256(base.encode({'gradient':all_rows,'legs':[[x.index for x in leg] for leg in legs],
                    'state':[x.index for x in self.s['state']],'prefix':d.digest.hexdigest(),'sources':previous['sources']})).hexdigest()
                path=args.previous/(key+'.json.gz')
                if path.exists():
                    for p,h in previous['sources'].items():
                        if base.sha(Path(p))!=h:raise ValueError('completed new expression source changed')
                    record=json.loads(gzip.decompress(path.read_bytes()))
                    if record['start']!=len(d.nodes) or record['prefix']!=d.digest.hexdigest():raise ValueError('completed new expression prefix differs')
                    for i,n in enumerate(record['nodes'],record['start']):
                        if d.node(n).index!=i:raise ValueError('completed new expression node differs')
                    d.leaf_provenance.update(record['leaf_provenance'])
                    values=[Expression(d,i) for i in record['roots']]
                    self.receipts.append({'file':str(path.resolve()),'SHA256':base.sha(path),'new_derived_evidence':True})
                    print(json.dumps({'phase':'REUSED_COMPLETED_NEW_EXPRESSION','key':key[:12],'nodes':len(d.nodes)}),flush=True)
                    return values if all_rows else values[0]
            return super().calculate(legs,all_rows)
    base.ExpressionDomain,base.setup,base.Evaluator=DiskExpressionDomain,setup,Evaluator
    try:resumed.run(args.evidence_root.resolve(),args.site,args.work.resolve(),args.out.resolve(),args.seed.resolve() if args.seed else None)
    finally:base.ExpressionDomain,base.setup,base.Evaluator=original_domain,original_setup,original_evaluator


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--site',choices=('left','right'),required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=Path);p.add_argument('--previous',type=Path)
    run(p.parse_args())
