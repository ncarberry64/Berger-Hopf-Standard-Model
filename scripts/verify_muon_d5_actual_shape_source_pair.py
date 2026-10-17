"""Immutable compact replay evidence for the partial direct child source."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every source-channel verification')
    root=ROOT/'artifacts/muon_d5_actual_shape_source_20261012';one=root/'run_1';two=root/'run_2'
    digest=lambda p:sha256(p.read_bytes()).hexdigest();names=sorted(p.name for p in one.iterdir()if p.is_file())
    if names!=sorted(p.name for p in two.iterdir()if p.is_file()):raise ValueError('consumer pair file membership differs')
    selected={}
    def select(p):
        if p.stat().st_size>=10*1024**2:raise ValueError('compact selected file must remain under10MiB')
        selected[p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=digest(p))
    for name in names:
        if digest(one/name)!=digest(two/name):raise ValueError('partial source consumer replay differs: '+name)
        select(one/name);select(two/name)
    receipt=json.loads((one/'result.json').read_bytes());pins=receipt['input_hashes'];weak_root=ROOT/'artifacts/muon_d5_weak_shape_source_20261012'
    weak_names=sorted(p.name for p in(weak_root/'run_1').iterdir()if p.is_file())
    if weak_names!=sorted(p.name for p in(weak_root/'run_2').iterdir()if p.is_file()):raise ValueError('weak source pair membership differs')
    for name in weak_names:
        if digest(weak_root/'run_1'/name)!=digest(weak_root/'run_2'/name):raise ValueError('weak source consumer replay differs: '+name)
        select(weak_root/'run_1'/name);select(weak_root/'run_2'/name)
    weak_receipt=json.loads((weak_root/'run_1/result.json').read_bytes())
    for name,value in weak_receipt['input_hashes'].items():
        if name in pins and pins[name]!=value:raise ValueError('source dependency pin conflict: '+name)
        pins[name]=value
    for name,expected in pins.items():
        if digest(ROOT/name)!=expected:raise ValueError('current supplied source pin differs: '+name)
    for name in('src/bhsm/interface/muon_d5_shape_coefficient_source.py','scripts/evaluate_muon_d5_actual_shape_source.py',
        'tests/test_muon_d5_shape_coefficient_source.py','scripts/verify_muon_d5_actual_shape_source_pair.py',
        'artifacts/muon_d5_shape_coefficient_source_tests_20261012.stdout.txt',
        'src/bhsm/interface/muon_d5_weak_shape_source.py','scripts/evaluate_muon_d5_weak_shape_source.py',
        'tests/test_muon_d5_weak_shape_source.py','artifacts/muon_d5_weak_shape_source_tests_20261012.stdout.txt',
        'artifacts/muon_d5_weak_shape_source_20261012_run_1.stdout.txt','artifacts/muon_d5_weak_shape_source_20261012_run_2.stdout.txt',
        'artifacts/muon_d5_actual_shape_source_20261012_run_1.stdout.txt','artifacts/muon_d5_actual_shape_source_20261012_run_2.stdout.txt'):
        select(ROOT/name)
    for name in('actual_shape_source_and_embedding.npz','common_stratum_area_shape_coefficient.npz','result.json'):
        select(ROOT/'artifacts/muon_actual_normal_shape_source_20261012/run_1'/name)
    out.mkdir(parents=True)
    scope=dict(channel='PARTIAL direct child b_raw=P*b_child at fixed complex time; actual pp-rp+rc values retained, parent/reference source directions held',
        source_meaning='unit computational proper-normal graph amplitude, not an admitted physical psi; its velocity coordinate is D_t a even when psi_t=0',
        common_source_complement='incoming normal, parent-born source, reset/constraint/endpoint and induced classical response to g_eta/g_rate are not consumed by this partial coefficient channel',
        pairing='fixed particle/conjugate representations with raw source coefficients unconjugated; full64 coefficient matrices before mode projection; allfive Cliffords',
        normalization_scope='normal mode/physical Gamma0/domain firsts are unassigned, not zero; no physical Bi/Bf, residue, charge, Pauli or native mean',
        strong_radial_angular_scope='twenty supplied SU2/U1 gauge-field directions with fullSM16 carrier coefficients on n0 and48 radial points; strong-gauge/off-mode/radial/angular complement remains explicit',
        weak_source='delta(mu D)=delta(mu)*D+mu*delta(D), including radial principal and all four original fixed radial tests; source trial Vt=0 exactly for this fixed coordinate basis, not a physical mode jet',
        Higgs_source='once-only fixed-trace SH density coefficient contact retained; physical moving trace/normal-mode contacts unassigned, not zero',
        actual_material_wall_f_and_sigma_source_max=1.2362942162360459e-15,
        original_birth_relation='same trial original226 row223 remains -4.019897650202032e-7-4.405744300638686e-6i',
        directional_controls='body difference3.96698e-5→1.08399e-5 and vertex60468.6→16523.2 under halving; finite controls only, no physical error enclosure',
        extra_parent_bulk_or_child_only_gamma_family_added=False,physical_admission=False)
    verification=dict(classification='VERIFIED_PARTIAL_DIRECT_CHILD_D5_SHAPE_SOURCE_REPLAY',all_files_byte_identical=len(names),
        result_sha256=digest(one/'result.json'),weak_files_byte_identical=len(weak_names),weak_result_sha256=digest(weak_root/'run_1/result.json'),input_hashes=pins,current_input_pins=len(pins),scope=scope,
        fresh_ancestor_regeneration_or_physical_admission=False)
    p=out/'verification.json';p.write_text(json.dumps(verification,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');select(p)
    commands=[f'C:/Python314/python.exe scripts/evaluate_muon_d5_actual_shape_source.py --shape-source artifacts/muon_actual_normal_shape_source_20261012/run_1 --output artifacts/muon_d5_actual_shape_source_20261012/run_{run} --energy 0'for run in(1,2)]+[
        f'C:/Python314/python.exe scripts/evaluate_muon_d5_weak_shape_source.py --direct-source artifacts/muon_d5_actual_shape_source_20261012/run_1 --output artifacts/muon_d5_weak_shape_source_20261012/run_{run}'for run in(1,2)]
    manifest=dict(classification='COMPACT_PARTIAL_CHILD_SOURCE_CONSUMER_MEMBERSHIP',selected_files=selected,input_hashes=pins,
        exact_environment=dict(python='C:/Python314/python.exe',PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        actual_commands=commands,focused_controls=['Python314 -m pytest --noconftest -q tests/test_muon_d5_shape_coefficient_source.py;1passed1.44s',
            'Python314 -m pytest --noconftest -q tests/test_muon_d5_weak_shape_source.py;1passed.82s'],scope=scope,
        local_pin_and_consumer_replay_verification_not_clean_tracked_seed_regeneration=True)
    p=out/'publication_manifest.json';p.write_text(json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(publication_manifest_sha256=digest(p),verification_sha256=digest(out/'verification.json'),
        files=len(selected),bytes=sum(v['bytes']for v in selected.values()),max_file_bytes=max(v['bytes']for v in selected.values())),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();verify(a.output)
