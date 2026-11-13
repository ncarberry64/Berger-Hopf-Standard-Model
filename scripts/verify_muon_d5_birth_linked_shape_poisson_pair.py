"""Immutable compact pair evidence for born-linked SAME D5 source action."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve each born-linked operator verification')
    digest=lambda p:sha256(p.read_bytes()).hexdigest()
    selected,pins,pairs={}, {}, []
    def select(p):
        if p.stat().st_size>=10*1024**2:raise ValueError('compact outputs under10MiB required')
        selected[p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=digest(p))
    root=ROOT/'artifacts/muon_d5_birth_linked_shape_poisson_20261013'
    keep=lambda n:(n=='result.json' or n in ('actual_full18_old_child_inherited_born_joined_total.npz',
        'actual_radial_geometry_density_source.npz','once_only_SH_fixed_point_trace_density_source.npz',
        'original_all226_birth_source_and_residue.npz','linked_initial_and_trueface_source_offsets.npz') or
        n.endswith('_same_field_Poisson_energy_Spin_and_wall_return.npz') or n.endswith('_original_field_and_energy.npz'))
    for sector in ('base','area'):
        one,two=(root/f'{sector}_final_run_{j}' for j in (1,2))
        ns=sorted(p.name for p in one.iterdir() if p.is_file())
        if ns!=sorted(p.name for p in two.iterdir() if p.is_file()):raise ValueError('pair membership changed')
        for n in ns:
            if digest(one/n)!=digest(two/n):raise ValueError('pair bytes differ: '+n)
            if keep(n):select(one/n);select(two/n)
        r=json.loads((one/'result.json').read_bytes())
        for n,h in r['input_hashes'].items():
            if n in pins and pins[n]!=h:raise ValueError('input pin conflict: '+n)
            pins[n]=h
        pairs.append(dict(sector=sector,all_files_byte_identical=len(ns),result_sha256=digest(one/'result.json'),
            local_full_source_rows_and_images_preserved=[n for n in ns if not keep(n)]))
    for n,h in pins.items():
        if digest(ROOT/n)!=h:raise ValueError('current source/action pin changed: '+n)
    code=('scripts/evaluate_muon_d5_birth_linked_shape_poisson.py','scripts/verify_muon_d5_birth_linked_shape_poisson_pair.py',
        'src/bhsm/interface/muon_d5_fixed_radial_source_consumption.py','src/bhsm/interface/muon_d5_fixed_radial_poisson.py',
        'tests/test_muon_d5_fixed_radial_poisson.py','tests/test_muon_d5_fixed_radial_source_consumption.py')
    logs=('artifacts/muon_d5_fixed_radial_poisson_tests_20261013.stdout.txt','artifacts/muon_d5_fixed_radial_source_final_tests_20261013.stdout.txt')
    for n in code+logs:select(ROOT/n)
    for sector in ('base','area'):
        for j in (1,2):select(ROOT/f'artifacts/muon_d5_birth_linked_shape_poisson_20261013_{sector}_final_run_{j}.stdout.txt')
    linked=ROOT/'artifacts/muon_normal_shape_birth_transmission_20261013/run_1'
    for n in ('result.json','base_final_linked_response.npz','area_final_linked_response.npz',
              'base_birth_transmission_and_all226.npz','area_birth_transmission_and_all226.npz'):select(linked/n)
    scope=dict(source='old child total + additional born-induced child, incoming OWN parent TOTAL born direction through actual affine map once; joined child/parent before projection',
        source_incidence='separate high/low slots old_child, inherited_born, joined_total; common area coefficient has no second direct b or new gamma family',
        same_background='exact raw/reference/time equality with original actual complex endpoint, SAME K/KE raw field inverse; no shifted background/source replay',
        matrix_action='full represented Spin4/SM16 particle/conjugate and both eta orientations, n0/four fixed radial profiles; full source and E field images/rows',
        first_return='Gamma_s=L dK P; Gamma_sE=L_E dK P+L dK_E P+L dK P_E with all moving Spin source contacts',
        paired_left='literal transpose Poisson, coefficient left Gamma0 S^-1 Gamma0 because K includes Gamma0 already; source coefficients unconjugated',
        wall='signed outward material-wall Green source kept separately; not retarded external-domain support, normal scalar inclusion/trace firsts unassigned',
        seam='fixedY once-only fixed point-trace SH density/source coefficient; no extra intrinsic kinetic, no silent epsilon/temporal-reset identification',
        birth_scope='selected139+71 held computational coordinates, not physical outer/energy/natural source completion; full226 source residue in selected archive',
        failed_source_relations='base childLy2.528e-8, Ep9.56879, Ec11828.073, port2233.0577558e7,port2252.1591503e7 before missing full phase-port/adjoint weak lifts',
        physical_BASE='original2264.424e-6 and complete all67 not admitted; responses are unit derivative coefficients, not nonlinear state or physical psi',
        physical_Gamma2_pole_positive_clock_charge_LSZ_Pauli_native_and_error_admitted=False,
        errors_not_enclosed=True)
    out.mkdir(parents=True)
    verification=dict(classification='VERIFIED_BORN_LINKED_SAME_D5_SOURCE_OPERATOR_REPLAY',pairs=pairs,input_hashes=pins,
        current_input_pins=len(pins),scope=scope,fresh_ancestor_regeneration_or_physical_admission=False)
    p=out/'verification.json';p.write_text(json.dumps(verification,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');select(p)
    commands=[f'C:/Python314/python.exe scripts/evaluate_muon_d5_birth_linked_shape_poisson.py '+
        ('--sector area ' if sector=='area' else '')+f'--output artifacts/muon_d5_birth_linked_shape_poisson_20261013/{sector}_final_run_{j}'
        for sector in ('base','area') for j in (1,2)]
    manifest=dict(classification='COMPACT_BORN_LINKED_SAME_D5_SOURCE_OPERATOR_MEMBERSHIP',selected_files=selected,
        input_hashes=pins,pairs=pairs,scope=scope,actual_commands=commands,
        exact_environment=dict(python='C:/Python314/python.exe',PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        focused_control_scope='same-field complete complex source/E/Spin/Green and common-area incidence tests already passed; no unchanged suite rerun',
        mathematical_review='transport reviewer accepted linked source incidence, independent left Schur/source/E and Spin/SH/Green algebra; completed numbers reviewed separately',
        local_consumer_replay_and_pin_closure_not_clean_tracked_seed_regeneration=True)
    p=out/'publication_manifest.json';p.write_text(json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=digest(p),verification_sha256=digest(out/'verification.json'),files=len(selected),
        bytes=sum(v['bytes']for v in selected.values()),max_file_bytes=max(v['bytes']for v in selected.values())),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();verify(a.output)
