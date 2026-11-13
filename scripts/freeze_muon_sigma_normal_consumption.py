"""Immutable compact replay evidence for the evaluated normal consumers.

This checks executed consumer bytes and present input pins. It does not
claim clean ancestor regeneration or physical collar/retarded admission.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def digest(p):return sha256(p.read_bytes()).hexdigest()


def freeze(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve every immutable verification')
    bases=('muon_reached_complex_normal_history_20261012','muon_sigma_collar_d5_weak_action_20261012','muon_sigma_collar_boundary_return_20261012')
    pins={};selection={};pairs=[]
    def selected(p):
        path=p.relative_to(ROOT).as_posix();size=p.stat().st_size
        if size>=10*1024**2:raise ValueError('compact selection requires every file below10MiB: '+path)
        selection[path]=dict(sha256=digest(p),bytes=size)
    for base in bases:
        one=ROOT/'artifacts'/base/'trial_0000_run_1';two=one.with_name('trial_0000_run_2')
        files1=sorted(p.name for p in one.iterdir()if p.is_file());files2=sorted(p.name for p in two.iterdir()if p.is_file())
        if files1!=files2:raise ValueError('complete consumer pair membership differs: '+base)
        for name in files1:
            if digest(one/name)!=digest(two/name):raise ValueError('consumer replay byte difference: '+base+'/'+name)
            selected(one/name);selected(two/name)
        receipt=json.loads((one/'result.json').read_bytes())
        for name,value in receipt['input_hashes'].items():
            if name in pins and pins[name]!=value:raise ValueError('input provenance conflict: '+name)
            if digest(ROOT/name)!=value:raise ValueError('current executed input changed: '+name)
            pins[name]=value
        for run in(1,2):selected(ROOT/'artifacts'/f'{base}_trial_0000_run_{run}.stdout.txt')
        pairs.append(dict(application=base,run_1=one.relative_to(ROOT).as_posix(),run_2=two.relative_to(ROOT).as_posix(),
            all_files_byte_identical=len(files1),result_sha256=digest(one/'result.json')))
    code=(
        'scripts/evaluate_muon_reached_complex_normal_history.py',
        'src/bhsm/interface/muon_sigma_collar_d5_weak_action.py','scripts/evaluate_muon_sigma_collar_d5_weak_action.py','tests/test_muon_sigma_collar_d5_weak_action.py',
        'src/bhsm/interface/muon_sigma_collar_boundary_return.py','scripts/evaluate_muon_sigma_collar_boundary_return.py','tests/test_muon_sigma_collar_boundary_return.py',
        'scripts/freeze_muon_sigma_normal_consumption.py',
        'src/bhsm/interface/muon_sigma_normal_collar_transport.py','scripts/evaluate_muon_sigma_normal_collar_transport.py',
        'tests/test_muon_sigma_normal_collar_transport.py','tests/test_muon_sigma_normal_collar_transport_independent.py')
    for name in code:selected(ROOT/name)
    for name in('artifacts/muon_sigma_collar_d5_weak_action_tests_20261012.stdout.txt','artifacts/muon_sigma_collar_boundary_return_tests_20261012.stdout.txt'):
        selected(ROOT/name)
    normal=ROOT/'artifacts/muon_sigma_normal_collar_transport_20261012/trial_0000_run_2'
    for p in normal.iterdir():
        if p.is_file():selected(p)
    for name in('candidate.npz','stage_0000.npz','endpoint_0000.npz','stage_0001.npz','endpoint_0001.npz','action_and_shooting_rows.npz','result.json'):
        selected(ROOT/'artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000'/name)
    scope=dict(classification='FINITE_NORMAL_DOMAIN_AND_SOURCE_QUALITY_CONSUMPTION',
        original_complex_canonical_extension='same current child Pi, full358 and endpoint146, same parent/reference affine source, reached3e-8-2.292213182e-8i; two cells only, no retarded/physical history admission',
        normal_mode='analytic exp(-logJ/2), independent scalar trial amplitudes explicitly supplied; this run chooses equal amplitudes; finite partial integral is not physical normalization',
        pairing='independent analytic Spin/gauge inverse; ambient right=T*S0 and left=uL*Gamma0*S0^-1*T^-1; Dirac-bar action Gamma0 counted once',
        finite_complement='750 spin/carrier/family coefficient rows are retained within ONE represented normal profile and n0 angular trial; not the complete radial/normal/strong/angular domain',
        gauge_scope='SU2/U1 original twenty field-coordinate basis with full SM16 carriers; strong-gauge background/source/operator beyond that basis is unconsumed, not asserted zero',
        source_scope='held one-line computational transverse coefficient derivative is explicit; physical source Frechet/normal-motion/transverse mode and endpoint-domain derivatives are not supplied by this test',
        angular_scope='n0 trial; actual n1/n3 magnetic and n2/n4 return complement not consumed by this scalar collar action',
        domain_scope='positive-length broken-cell bulk plus once-only SH; five AFTER-minus-BEFORE Green returns remain explicit external action-domain contacts; no sewn global D5 domain inferred',
        surface_work='signed final-initial-sum(after-before) projected through SAME full Poisson and its E response, no new inverse or fitted counterterm',
        independent_half_density_check='returned half-density FD fullstep9.387838832945923e-4 and halfstep1.8584048430783046e-3; worsening is an unenclosed numerical diagnostic, not normal-equation validation',
        original_mode_rows='transport original_normal_mode_rows derive us from the same fn/div and algebraically cancel; they are not independent returned-mode validation',
        residuals='same original226 birth row223=-4.019897650202032e-7-4.405744300638686e-6i; closing finite358/146 or linear field border does not solve this birth/future matching relation',
        regular_pole_scope='Re(rho)=0 is a complex half-plane control face, not proof of regular rho=0',
        physical_Gamma2_pole_charge_LSZ_Pauli_native_total_or_error_admitted=False,
        actual_a_mu=None,actual_g_mu=None,error_enclosure=None)
    verification=dict(classification='VERIFIED_COMPACT_NORMAL_CONSUMER_REPLAY_PAIRS',pairs=pairs,current_input_pins=pins,
        input_pin_count=len(pins),scope=scope,physical_admission=False,
        local_replay_and_current_pin_verification_not_clean_ancestor_regeneration=True,
        compact_selected_files_count=len(selection),compact_selected_bytes=sum(a['bytes']for a in selection.values()),
        maximum_selected_file_bytes=max(a['bytes']for a in selection.values()),
        publication_dependency_closure='compact local consumer membership and current pin ledger; full tracked-seed producer DAG must be checked by the parent publication selection, not inferred here')
    out.mkdir(parents=True)
    for name,value in(('verification.json',verification),('interpretation.json',scope)):
        p=out/name;p.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');selected(p)
    manifest=dict(classification='COMPACT_NORMAL_CONSUMER_PUBLICATION_MEMBERSHIP',selected_files=selection,
        exact_execution_environment=dict(python='C:/Python314/python.exe',PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        actual_commands=[command.format(run=run)for run in(1,2)for command in(
            'C:/Python314/python.exe scripts/evaluate_muon_reached_complex_normal_history.py --trial artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000 --normal-flow artifacts/muon_sigma_normal_collar_transport_20261012/trial_0000_run_2 --output artifacts/muon_reached_complex_normal_history_20261012/trial_0000_run_{run} --steps 2 --nu-squared 4',
            'C:/Python314/python.exe scripts/evaluate_muon_sigma_collar_d5_weak_action.py --trial artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000 --normal-flow artifacts/muon_sigma_normal_collar_transport_20261012/trial_0000_run_2 --output artifacts/muon_sigma_collar_d5_weak_action_20261012/trial_0000_run_{run} --energy 0 --quadrature-order 4',
            'C:/Python314/python.exe scripts/evaluate_muon_sigma_collar_boundary_return.py --collar artifacts/muon_sigma_collar_d5_weak_action_20261012/trial_0000_run_1 --output artifacts/muon_sigma_collar_boundary_return_20261012/trial_0000_run_{run}')]+[
            'C:/Python314/python.exe -m pytest --noconftest -q tests/test_muon_sigma_collar_d5_weak_action.py',
            'C:/Python314/python.exe -m pytest --noconftest -q tests/test_muon_sigma_collar_boundary_return.py'],
        independent_controls=dict(collar_action='2 passed1.40s',signed_surface_work='1 passed1.35s',
            transport_regressions='2 passed20.94s by independent reviewer; source04f6da51b907b477c6964d5534e0357781ddbfa9d7b8d1ccd898a80525656477'),
        current_input_pins=pins,physical_admission=False,clean_seed_only_regeneration_not_executed=True)
    p=out/'publication_manifest.json';p.write_text(json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(publication_manifest_sha256=digest(p),verification_sha256=digest(out/'verification.json'),
        files=len(selection),bytes=sum(a['bytes']for a in selection.values()),max_file_bytes=max(a['bytes']for a in selection.values())),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();freeze(a.output)
