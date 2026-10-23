"""Verify the compatible146 launch and original358 step independent replays."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def verify():
    specs=(('muon_high_precision_canonical_compatibility_20261012','evaluate_muon_high_precision_canonical_compatibility.py',
        ['--precision','60','--max-iterations','8'],'BHSM_high_precision_canonical_compatibility_run_2.stdout.txt'),
        ('muon_complex_canonical_exterior_step_20261012','evaluate_muon_complex_canonical_exterior_step.py',
        ['--initial-folder','artifacts/muon_high_precision_canonical_compatibility_20261012/run_1','--step','1e-8','--max-iterations','12'],
        'BHSM_complex_canonical_exterior_step_run_2.stdout.txt'))
    records=[]
    for folder,driver,args,logname in specs:
        base=ROOT/'artifacts'/folder;a,b=base/'run_1',base/'run_2';out=base/'independent_pair_verification.json'
        if out.exists():raise FileExistsError('preserve immutable canonical replay evidence')
        def files(p):return{x.relative_to(p).as_posix():x for x in p.rglob('*')if x.is_file()}
        af,bf=files(a),files(b)
        if af.keys()!=bf.keys():raise ValueError('every output membership must match')
        hashes={}
        for n in sorted(af):
            h=sha256(af[n].read_bytes()).hexdigest()
            if h!=sha256(bf[n].read_bytes()).hexdigest():raise ValueError('byte mismatch '+folder+'/'+n)
            hashes[n]=h
        md=json.loads((a/'result.json').read_bytes())
        for p,h in md['input_hashes'].items():
            if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed pin changed '+p)
        data=(Path('C:/Users/carbe/Downloads')/logname).read_bytes();log=base/'independent_run_2.stdout.txt';log.write_bytes(data)
        argv=['C:/Python314/python.exe','scripts/'+driver,'--output','artifacts/'+folder+'/run_2']+args
        record=dict(classification='INDEPENDENT_BYTE_IDENTICAL_COMPATIBLE_ORIGINAL_CANONICAL_APPLICATION',
            original='artifacts/'+folder+'/run_1',replay='artifacts/'+folder+'/run_2',
            all_output_bytes_identical=True,all_output_count=len(hashes),all_output_sha256=hashes,
            argv=argv,environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
            cwd=str(ROOT),exit_code=0,stdout=dict(path=log.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha256(data).hexdigest(),
                provenance='Complete actual independent PowerShell Tee-Object bytes'),
            consumed_input_pins_current=True,consumed_pin_count=len(md['input_hashes']),
            status=md['status'],full_ancestor_rematerialization_executed=False,
            physical_stop_pole_or_Pauli_selected=False,verifier_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        out.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
        records.append(dict(verification=out.relative_to(ROOT).as_posix(),sha256=sha256(out.read_bytes()).hexdigest(),
            result_sha256=hashes['result.json'],application_sha256=hashes['application.npz'],all_output_count=len(hashes)))
    print(json.dumps(dict(verified=records),sort_keys=True))


if __name__=='__main__':verify()
