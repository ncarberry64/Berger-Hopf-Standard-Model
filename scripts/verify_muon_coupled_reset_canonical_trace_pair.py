"""Freeze same-candidate canonical-force/half-density replay evidence."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def verify():
    base=ROOT/'artifacts/muon_coupled_reset_canonical_trace_20261012'
    out=base/'independent_pair_verification.json'
    if out.exists():raise FileExistsError('preserve every canonical trace receipt')
    a,b=(base/f'run_{i}'for i in(1,2))
    af={p.name:p for p in a.iterdir()if p.is_file()};bf={p.name:p for p in b.iterdir()if p.is_file()}
    if af.keys()!=bf.keys():raise ValueError('output membership differs')
    hashes={}
    for name in sorted(af):
        h=sha256(af[name].read_bytes()).hexdigest()
        if h!=sha256(bf[name].read_bytes()).hexdigest():raise ValueError('byte replay mismatch '+name)
        hashes[name]=h
    md=json.loads((a/'result.json').read_bytes())
    for p,h in md['input_hashes'].items():
        if sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('same candidate/source pin changed '+p)
    logs={}
    for name,source in[(f'run_{i}.stdout.txt',f'artifacts/muon_coupled_reset_canonical_trace_run_{i}.stdout.txt')for i in(1,2)]+[
        ('focused_review.stdout.txt','artifacts/muon_coupled_reset_canonical_trace_review.stdout.txt')]:
        data=(ROOT/source).read_bytes();p=base/name;p.write_bytes(data)
        logs[name]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
    result=dict(classification='INDEPENDENT_REPLAY_SAME_COUPLED_CANDIDATE_CANONICAL_FORCE_AND_TRACE_APPLICATION',
        all_output_bytes_identical=True,all_output_count=len(hashes),all_output_sha256=hashes,input_pins_current=True,
        executions=[dict(argv=['C:/Python314/python.exe','scripts/evaluate_muon_coupled_reset_canonical_trace.py',
            '--output',f'artifacts/muon_coupled_reset_canonical_trace_20261012/run_{i}'],exit_code=0)for i in(1,2)],
        focused_review=dict(argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',
            'tests/test_muon_coupled_reset_canonical_trace_review.py'],exit_code=0,passed=1,duration_seconds=1.67,
            source_sha256=sha256((ROOT/'tests/test_muon_coupled_reset_canonical_trace_review.py').read_bytes()).hexdigest()),
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),cwd=str(ROOT),
        stdout=logs,capture_provenance='complete actual PowerShell Tee-Object bytes',
        initial_import_probe='metadata owner import action_domain_contract failed before any action execution; corrected to the existing action_definition API',
        v2_resume_schema_review='explicit prior application/raw_pair/reference/master lift plus original weights/action parameters and hashes; accepted-probe branch only for original first-probe receipt; all226 absolute rows checked',
        saved_v1_parent_energy_alias='prior continued_run_1 parent_energy alias was Lparent, not Ep; this consumer ignores it and reexecutes Ep=pv*L_v−Lparent. The separate v2 driver writes parent_action_value and correct parent_energy',
        stored302_review='exact-stored Acb solve/transpose/contraction retains full292+6+4; its residual upper bounds apply only to exact stored K/rhs/dual, and midpoint ports inserted into binary original226 are diagnostics',
        candidate_full_reset_guard_passed=md['full_reset_guard_passed'],
        standalone_parent_Ly_evaluated_not_inferred=True,joint_Pi_not_substituted_for_standalone_parent_Pi=True,
        new_proper_clock_span_exterior_Bin_Bout_first_hit_or_Pauli_selected=False,
        verifier_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    files=['scripts/evaluate_muon_coupled_reset_canonical_trace.py','tests/test_muon_coupled_reset_canonical_trace_review.py',
        Path(__file__).relative_to(ROOT).as_posix(),out.relative_to(ROOT).as_posix()]
    files+=sorted((base/n).relative_to(ROOT).as_posix()for n in logs)
    files+=sorted(p.relative_to(ROOT).as_posix()for d in(a,b)for p in d.iterdir()if p.is_file())
    manifest=base/'publication_manifest.json'
    manifest.write_text(json.dumps(dict(classification=result['classification'],
        files={p:sha256((ROOT/p).read_bytes()).hexdigest()for p in files},
        conditional_candidate_guard_false=True,physical_first_hit_or_Pauli_completed=False),indent=2,sort_keys=True)+'\n',
        encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=hashes['result.json'],all_output_count=len(hashes),
        verification=out.relative_to(ROOT).as_posix(),verification_sha256=sha256(out.read_bytes()).hexdigest(),
        manifest=manifest.relative_to(ROOT).as_posix(),manifest_sha256=sha256(manifest.read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':verify()
