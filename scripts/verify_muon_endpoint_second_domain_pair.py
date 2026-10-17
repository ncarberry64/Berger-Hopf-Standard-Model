"""Freeze the compact negative endpoint-source quality application."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/muon_endpoint_second_domain_germ_20261012'


def digest(p):return sha256(p.read_bytes()).hexdigest()


def main():
    verification=BASE/'independent_pair_verification.json';manifest=BASE/'publication_manifest.json'
    if verification.exists()or manifest.exists():raise FileExistsError('preserve immutable endpoint germ verification')
    md=json.loads((BASE/'run_1/result.json').read_text());pairs={};files={}
    for name in('result.json',*md['archives']):
        a=BASE/'run_1'/name;b=BASE/'run_2'/name
        if a.read_bytes()!=b.read_bytes():raise ValueError('literal second-domain replay differs '+name)
        pairs[name]=dict(bytes=a.stat().st_size,sha256=digest(a),identical=True)
    for rel,h in md['input_hashes'].items():
        if digest(ROOT/rel)!=h:raise ValueError('consumed action/domain source changed '+rel)
    # Raw branch G/H/rate streams remain local; the final compact archive
    # preserves both-step jets and the receipt preserves every branch row.
    for run in(1,2):
        for name in('result.json','endpoint_second_domain_contacts.npz'):
            p=BASE/f'run_{run}'/name;files[p.relative_to(ROOT).as_posix()]=digest(p)
        p=ROOT/f'artifacts/muon_endpoint_second_domain_germ_20261012_run_{run}.stdout.txt'
        files[p.relative_to(ROOT).as_posix()]=digest(p)
    for rel in('src/bhsm/interface/muon_endpoint_second_domain_germ.py',
        'scripts/evaluate_muon_endpoint_second_domain_germ.py','tests/test_muon_endpoint_second_domain_germ.py',
        Path(__file__).relative_to(ROOT).as_posix()):files[rel]=digest(ROOT/rel)
    data=dict(classification='INDEPENDENT_REPLAY_NEGATIVE_ENDPOINT_TIME_SOURCE_QUALITY_APPLICATION',
        pairs=pairs,all_consumed_pins_current=True,
        exact_commands=[f'C:/Python314/python.exe scripts/evaluate_muon_endpoint_second_domain_germ.py --output artifacts/muon_endpoint_second_domain_germ_20261012/run_{r}'for r in(1,2)],
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        focused_control=dict(command='C:/Python314/python.exe -m pytest --noconftest -q tests/test_muon_endpoint_second_domain_germ.py',
            observed_tool_exit_code=0,observed_tool_result='1 passed in 2.42s',
            source_sha256=digest(ROOT/'tests/test_muon_endpoint_second_domain_germ.py')),
        branch_original_DAE_rows=md['branch_diagnostics'],step_comparisons=md['step_comparisons'],
        physical_normal_second_jet_or_jerk_certified=False,
        endpoint_family_contacts_not_persistent_bulk_glue=True,
        interpretation='Proper-normal/phase-jerk second jets are unstable at the two executed steps. These are preserved negative source-quality diagnostics, not a physical force/error bound or proof of nonexistence.',
        generic_reaction_helper_not_physical_provenance=True,
        raw_branch_provenance_preserved_locally=True,
        ancestor_regeneration_or_extra_precision_campaign=False)
    verification.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    files[verification.relative_to(ROOT).as_posix()]=digest(verification)
    packet=dict(classification=data['classification'],files=files,
        dependencies=[p for p in md['input_hashes']if p.endswith('result.json')],physical_Pauli_completed=False)
    manifest.write_text(json.dumps(packet,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(all_outputs_byte_identical=len(pairs),input_pins_current=len(md['input_hashes']),
        verification_sha256=digest(verification),manifest_sha256=digest(manifest)),sort_keys=True))


if __name__=='__main__':main()
