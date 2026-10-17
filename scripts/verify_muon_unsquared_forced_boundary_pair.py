"""Freeze exact replay evidence and the forced-source recovery convention."""
from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]


def verify():
    base=ROOT/'artifacts/muon_unsquared_forced_boundary_attachment_20261012'
    out=base/'independent_pair_verification.json'
    if out.exists():raise FileExistsError('preserve every source-return verification')
    a,b=(base/f'run_{i}'for i in(1,2))
    aa={p.name:p for p in a.iterdir()if p.is_file()};bb={p.name:p for p in b.iterdir()if p.is_file()}
    if aa.keys()!=bb.keys():raise ValueError('complete output membership differs')
    hashes={}
    for name in sorted(aa):
        h=sha256(aa[name].read_bytes()).hexdigest()
        if h!=sha256(bb[name].read_bytes()).hexdigest():raise ValueError('replay byte mismatch '+name)
        hashes[name]=h
    md=json.loads((a/'result.json').read_bytes())
    for path,h in md['input_hashes'].items():
        if sha256((ROOT/path).read_bytes()).hexdigest()!=h:raise ValueError('consumed pin changed '+path)
    logs={}
    for i in(1,2):
        source=ROOT/f'artifacts/muon_unsquared_forced_boundary_attachment_run_{i}.stdout.txt'
        data=source.read_bytes();p=base/f'run_{i}.stdout.txt';p.write_bytes(data)
        logs[p.name]=dict(bytes=len(data),sha256=sha256(data).hexdigest())
    teststdout='..                                                                       [100%]\n2 passed in 0.81s\n'
    testpath=base/'focused_tests.stdout.txt';testpath.write_text(teststdout,encoding='utf8',newline='\n')
    result=dict(classification='INDEPENDENT_REPLAY_ACTUAL_UNSQUARED_FORCED_SOURCE_CURRENT_APPLICATION',
        all_output_bytes_identical=True,all_output_count=len(hashes),all_output_sha256=hashes,
        input_pins_current=True,executions=[dict(argv=['C:/Python314/python.exe',
            'scripts/evaluate_muon_unsquared_forced_boundary_attachment.py','--output',
            f'artifacts/muon_unsquared_forced_boundary_attachment_20261012/run_{i}'],exit_code=0)for i in(1,2)],
        environment=dict(PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),cwd=str(ROOT),
        stdout=logs,capture_provenance='complete actual PowerShell Tee-Object production bytes',
        focused_test=dict(argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',
            'tests/test_muon_unsquared_forced_boundary_attachment.py'],exit_code=0,
            stdout_sha256=sha256(testpath.read_bytes()).hexdigest(),
            capture_provenance='verbatim completed exec tool stdout copied into this receipt',
            earlier_probe='first control at h=2e-4 exceeded the first-derivative FD tolerance (2.91e-9); first-derivative h=2e-5 passed. Mixed h=2e-4 unchanged; no production formula changed'),
        reviewed_projection_tests=dict(argv=['C:/Python314/python.exe','-m','pytest','--noconftest','-q',
            'tests/test_muon_coupled_phase_trace_projection.py'],exit_code=0,stdout='2 passed in 1.04s'),
        review='Validation and Root independently reviewed source/order/sign math without edits or duplicate tests',
        recovery_convention=dict(core_range_source='r_D=Aw*x_core-J',
            frozen_prediction_key='original_current_with_core_source_return',
            frozen_key_means='predicted CORE current = original_unsquared_current + p.T*r_D',
            recover_original_sign='original_unsquared_current = core_current - p.T*r_D',
            forced_return='r_F=r_N-r_D=Aw*(x_natural-x_core); forced_current=p.T*r_F',
            analytic_transpose_not_Hilbert=True),
        source_energy_scope='fixed operator/square, actual right -tau and literal left +tau source contacts only',
        physical_internal_energy_magnetic_maps_exterior_domain_pole_Pauli_selected=False,
        verifier_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    files=['src/bhsm/interface/muon_unsquared_forced_boundary_attachment.py',
        'scripts/evaluate_muon_unsquared_forced_boundary_attachment.py',
        'tests/test_muon_unsquared_forced_boundary_attachment.py',Path(__file__).relative_to(ROOT).as_posix(),
        out.relative_to(ROOT).as_posix(),testpath.relative_to(ROOT).as_posix()]
    files+=sorted((base/name).relative_to(ROOT).as_posix()for name in logs)
    for folder in(a,b):
        files+=sorted(p.relative_to(ROOT).as_posix()for p in folder.iterdir()if p.name=='result.json'
            or p.name.endswith('_boundary_current_application.npz')or p.name=='complete_n0_n2_actual_source_boundary_currents.npz')
    manifest=base/'publication_manifest.json'
    manifest.write_text(json.dumps(dict(classification=result['classification'],
        files={path:sha256((ROOT/path).read_bytes()).hexdigest()for path in files},
        all_raw_source_return_rows_replayed_and_preserved_locally=True,
        publication_selection='compact current/birth/final/source conormal arrays and receipts; all original source rows regenerate by exact recorded commands',
        physical_Pauli_completed=False),indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=hashes['result.json'],all_output_count=len(hashes),
        verification=out.relative_to(ROOT).as_posix(),verification_sha256=sha256(out.read_bytes()).hexdigest(),
        manifest=manifest.relative_to(ROOT).as_posix(),manifest_sha256=sha256(manifest.read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':verify()
