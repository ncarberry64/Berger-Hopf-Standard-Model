"""Evaluate actual chronological external transport and Ward contacts."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_transported_longitudinal_ward import transported_longitudinal_ward_application
from evaluate_muon_reached_trace_action import deterministic_archive


def main(output,order,tolerance):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve previous applications')
    refs={p:sha256((ROOT/p).read_bytes()).hexdigest()for p in(
        'src/bhsm/interface/muon_transported_longitudinal_ward.py',
        'scripts/evaluate_muon_transported_longitudinal_ward.py',
        'tests/test_muon_transported_longitudinal_ward.py')}
    out.mkdir(parents=True);records={};archives={}
    for side in('incoming','outgoing'):
        for family in(1,2):
            result=transported_longitudinal_ward_application(side,family=family,
                quadrature_order=order,tolerance=tolerance,repository=ROOT)
            name=f'{side}_family_{family}.npz';deterministic_archive(out/name,result['arrays'])
            data=(out/name).read_bytes();archives[name]=dict(sha256=sha256(data).hexdigest(),bytes=len(data))
            records[f'{side}_family_{family}']=result['metadata'];refs.update(result['metadata']['input_hashes'])
            print(json.dumps(dict(side=side,family=family,shells=result['metadata']['shell_records']),sort_keys=True),flush=True)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('source changed')
    md=dict(classification='EVALUATED_CHRONOLOGICAL_ACTION_TRANSPORTED_LONGITUDINAL_WARD_PAIRING',
        input_hashes=refs,array_archives=archives,records=records,
        physical_Pauli_or_starting_shell_bound=None)
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--quadrature-order',type=int,default=12);p.add_argument('--tolerance',type=float,default=2e-12)
    a=p.parse_args();main(a.output,a.quadrature_order,a.tolerance)
