"""Freeze exact replays of reached original-coordinate canonical applications."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
PAIRS=(
 ('muon_high_precision_canonical_compatibility_20261012','run_1','run_2'),
 ('muon_complex_canonical_exterior_step_20261012','run_1','run_2'),
 ('muon_complex_canonical_endpoint_20261012','run_1','run_2'),
 ('muon_precise_complex_canonical_exterior_step_20261012','run_1','run_2'),
 ('muon_complex_canonical_endpoint_20261012','continued_run_1','continued_run_2'),
 ('muon_complex_endpoint_area_clock_20261012','run_1','run_2'))
SOURCES=(
 'src/bhsm/interface/muon_high_precision_constitutive_gradient.py',
 'src/bhsm/interface/muon_high_precision_canonical_compatibility.py',
 'src/bhsm/interface/muon_warm_complex_canonical_compatibility.py',
 'src/bhsm/interface/muon_complex_canonical_midpoint.py',
 'src/bhsm/interface/muon_complex_endpoint_area_action.py',
 'src/bhsm/interface/muon_holomorphic_child_clock_application.py',
 'scripts/evaluate_muon_high_precision_constitutive_gradient.py',
 'scripts/evaluate_muon_high_precision_canonical_compatibility.py',
 'scripts/evaluate_muon_complex_canonical_exterior_step.py',
 'scripts/evaluate_muon_precise_complex_canonical_exterior_step.py',
 'scripts/evaluate_muon_complex_canonical_endpoint.py',
 'scripts/evaluate_muon_complex_endpoint_area_clock.py',
 'scripts/evaluate_muon_original_constitutive_row_labels.py',
 'scripts/verify_muon_compatible_canonical_replays.py',
 'tests/test_muon_high_precision_constitutive_gradient.py',
 'tests/test_muon_high_precision_constitutive_gradient_review.py',
 'tests/test_muon_high_precision_canonical_compatibility.py',
 'tests/test_muon_complex_canonical_midpoint.py',
 'tests/test_muon_complex_endpoint_area_action.py')
LOGS=(
 'artifacts/muon_high_precision_canonical_compatibility_20261012_run_1.stdout.txt',
 'artifacts/muon_high_precision_canonical_compatibility_20261012/independent_run_2.stdout.txt',
 'artifacts/muon_complex_canonical_exterior_step_20261012_run_1.stdout.txt',
 'artifacts/muon_complex_canonical_exterior_step_20261012/independent_run_2.stdout.txt',
 'artifacts/muon_complex_canonical_endpoint_20261012_run_1.stdout.txt',
 'artifacts/muon_complex_canonical_endpoint_20261012_run_2.stdout.txt',
 'artifacts/muon_precise_complex_canonical_exterior_step_20261012_run_1.stdout.txt',
 'artifacts/muon_precise_complex_canonical_exterior_step_20261012_run_2.stdout.txt',
 'artifacts/muon_complex_canonical_endpoint_20261012_continued_run_1.stdout.txt',
 'artifacts/muon_complex_canonical_endpoint_20261012_continued_run_2.stdout.txt',
 'artifacts/muon_complex_endpoint_area_clock_20261012_run_1.stdout.txt',
 'artifacts/muon_complex_endpoint_area_clock_20261012_run_2.stdout.txt',
 'artifacts/muon_high_precision_constitutive_gradient_tests_20261012_run_1.stdout.txt',
 'artifacts/muon_high_precision_canonical_compatibility_tests_20261012_run_1.stdout.txt',
 'artifacts/muon_complex_endpoint_area_action_tests_20261012_run_1.stdout.txt')


def freeze(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every canonical replay verification')
    selected={};pins={};pairs=[]
    def item(path):
        p=ROOT/path;b=p.read_bytes();r=p.relative_to(ROOT).as_posix()
        selected[r]=dict(path=r,bytes=len(b),sha256=sha256(b).hexdigest());return b
    for name,left,right in PAIRS:
        a=Path('artifacts')/name/left;b=Path('artifacts')/name/right
        ma=json.loads(item(a/'result.json'));mb=json.loads(item(b/'result.json'))
        if (ROOT/a/'result.json').read_bytes()!=(ROOT/b/'result.json').read_bytes():raise ArithmeticError('same-input result replay changed: '+name)
        if ma['archives']!=mb['archives']:raise ArithmeticError('same-output archive schema changed')
        for file,record in ma['archives'].items():
            x=item(a/file);y=item(b/file)
            if x!=y or sha256(x).hexdigest()!=record['sha256']:raise ArithmeticError('original array replay mismatch: '+file)
        for p,h in ma['input_hashes'].items():
            if p in pins and pins[p]!=h:raise ValueError('input conflict across canonical applications: '+p)
            if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('current original input changed: '+p)
            pins[p]=h
        pairs.append(dict(left=a.as_posix(),right=b.as_posix(),files_identical=len(ma['archives'])+1,
            result_sha256=sha256((ROOT/a/'result.json').read_bytes()).hexdigest(),
            status=ma.get('status'),all_input_pins_current=True))
    for p in SOURCES+LOGS:item(p)
    for p in ('artifacts/muon_high_precision_canonical_compatibility_20261012/independent_pair_verification.json',
              'artifacts/muon_complex_canonical_exterior_step_20261012/independent_pair_verification.json'):
        item(p)
    item(Path(__file__).relative_to(ROOT))
    precision_contract=dict(
        precise_fields=['phase gradient velocity/algebraic tail','canonical_momentum','value'],
        binary_retained_fields=['phase gradient position force','Hessian and Lxx/Lxv/etc blocks','raw_gradient','raw_hessian','algebraic_Gauss_multiplier_rows alias','explicit inherited-clock tangent application'],
        canonical_guard_consumes='updated original phase gradient, all146 constitutive or all358 midpoint rows',
        future_consumers='do not use retained raw-gradient or raw-Gauss aliases as a precise constitutive guard',
        original_absolute_tolerance=2e-10,transformed_force_used=False,
        outward_upstream_derivative_or_physical_error_enclosure=False)
    result=dict(classification='VERIFIED_SAME_INPUT_PRECISE_ORIGINAL_CANONICAL_CONTINUATION_REPLAY_PAIRS',
        pairs=pairs,input_hashes=pins,selected_file_count=len(selected),precision_contract=precision_contract,
        production_environment=dict(python='C:/Python314/python.exe',PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='4',OMP_NUM_THREADS='4'),
        gamma_law='gamma=alpha_FSC*c^(-m/2); gamma_c=-(m/2)*gamma/c; gamma_cc=(m/2)*(m/2+1)*gamma/c^2',
        alpha_EM_substituted=False,area_affine_held_state_not_nonzero_gamma_stationarity=True,
        physical_first_hit_reference_exterior_domain_or_Pauli_selected=False)
    out.mkdir(parents=True);p=out/'verification.json';p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    item(p.relative_to(ROOT));manifest=dict(classification='IMMUTABLE_PRECISE_CANONICAL_CONTINUATION_PUBLICATION_FILES',
        files=sorted(selected.values(),key=lambda x:x['path']),all_input_pins_current=True,
        excluded='active new two-arm implementation streams and unreached physical stop/normalization applications')
    p=out/'publication_manifest.json';p.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='precise_canonical_continuation_pairs_frozen',pairs=len(pairs),files=len(selected),
        pins=len(pins),manifest_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,
        default=Path('artifacts/muon_precise_canonical_continuation_20261012/pair_verification'))
    freeze(p.parse_args().output)
