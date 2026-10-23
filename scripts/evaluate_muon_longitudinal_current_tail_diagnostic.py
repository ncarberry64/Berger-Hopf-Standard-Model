"""Evaluate the actual reference longitudinal/Ward current diagnostic."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_longitudinal_current_tail_diagnostic import retained_longitudinal_current_application
from evaluate_muon_reached_trace_action import deterministic_archive


def main(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve prior application')
    source_files=('src/bhsm/interface/muon_longitudinal_current_tail_diagnostic.py',
        'scripts/evaluate_muon_longitudinal_current_tail_diagnostic.py',
        'tests/test_muon_longitudinal_current_tail_diagnostic.py')
    refs={p:sha256((ROOT/p).read_bytes()).hexdigest()for p in source_files}
    out.mkdir(parents=True);records={};archives={}
    for side in('incoming','outgoing'):
        result=retained_longitudinal_current_application(side,repository=ROOT)
        name=side+'_application.npz';deterministic_archive(out/name,result['arrays'])
        data=(out/name).read_bytes();archives[name]=dict(sha256=sha256(data).hexdigest(),bytes=len(data))
        records[side]=result['metadata'];refs.update(result['metadata']['input_hashes'])
        print(json.dumps(dict(side=side,limits=result['metadata']['exact_Casimir_limits'],
            Ward=result['metadata']['source_identity_residual_norm'],
            external_Euler=result['metadata']['external_Euler_contact_norm']),sort_keys=True),flush=True)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('owner changed during evaluation')
    receipt=dict(classification='EVALUATED_RETAINED_CENTRAL_LONGITUDINAL_REFERENCE_AND_WARD_CURRENT',
        input_hashes=refs,array_archives=archives,records=records,
        physical_angular_tail_or_on_shell_Pauli_annihilation_proved=False,
        error_scope='stored finite-reference algebra/application; no upstream outward, continuum or physical matching enclosure')
    (out/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    main(p.parse_args().output)
