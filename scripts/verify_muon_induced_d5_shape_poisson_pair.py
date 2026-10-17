"""Immutable replay/compact evidence for actual induced action and D5 sources."""
from pathlib import Path
from hashlib import sha256
import argparse,json
ROOT=Path(__file__).resolve().parents[1]


def verify(output):
    out=ROOT/output
    if out.exists(): raise FileExistsError('preserve every source/action replay receipt')
    digest=lambda p:sha256(p.read_bytes()).hexdigest()
    selected,pins,pairs={}, {}, []
    def select(p):
        if p.stat().st_size>=10*1024**2:raise ValueError('compact selected inputs must stay below10MiB')
        selected[p.relative_to(ROOT).as_posix()]=dict(bytes=p.stat().st_size,sha256=digest(p))
    def pair(one,two,compact):
        ns=sorted(p.name for p in one.iterdir() if p.is_file())
        if ns!=sorted(p.name for p in two.iterdir() if p.is_file()):raise ValueError('pair membership changed')
        for n in ns:
            if digest(one/n)!=digest(two/n):raise ValueError('pair bytes differ: '+n)
            if compact(n):select(one/n);select(two/n)
        receipt=json.loads((one/'result.json').read_bytes())
        for n,h in receipt['input_hashes'].items():
            if n in pins and pins[n]!=h:raise ValueError('dependency pin conflict: '+n)
            pins[n]=h
        pairs.append(dict(first=one.relative_to(ROOT).as_posix(),second=two.relative_to(ROOT).as_posix(),
            all_files_byte_identical=len(ns),result_sha256=digest(one/'result.json'),
            local_bulk_arrays_preserved=[n for n in ns if not compact(n)]))
    induced=ROOT/'artifacts/muon_normal_shape_induced_canonical_response_20261013'
    pair(induced/'run_1',induced/'run_2',lambda n:True)
    field=ROOT/'artifacts/muon_d5_induced_shape_poisson_20261013'
    compact=lambda n:(n=='result.json' or n in ('actual_full18_direct_induced_total_and_rate_work.npz',
        'actual_radial_geometry_density_source.npz','once_only_SH_fixed_point_trace_density_source.npz') or
        n.endswith('_same_field_Poisson_energy_Spin_and_wall_return.npz') or n.endswith('_original_field_and_energy.npz'))
    pair(field/'base_final_run_4',field/'base_final_run_5',compact)
    pair(field/'area_final_run_1',field/'area_final_run_2',compact)
    for n,h in pins.items():
        if digest(ROOT/n)!=h:raise ValueError('current action/source pin changed: '+n)
    code=('src/bhsm/interface/muon_normal_shape_induced_canonical_response.py',
        'scripts/evaluate_muon_normal_shape_induced_canonical_response.py','tests/test_muon_normal_shape_induced_canonical_response.py',
        'src/bhsm/interface/muon_d5_fixed_radial_poisson.py','tests/test_muon_d5_fixed_radial_poisson.py',
        'src/bhsm/interface/muon_d5_fixed_radial_source_consumption.py','tests/test_muon_d5_fixed_radial_source_consumption.py',
        'scripts/evaluate_muon_d5_induced_shape_poisson.py','scripts/verify_muon_induced_d5_shape_poisson_pair.py')
    logs=('artifacts/muon_normal_shape_induced_canonical_response_tests_20261013.stdout.txt',
        'artifacts/muon_d5_fixed_radial_poisson_tests_20261013.stdout.txt',
        'artifacts/muon_d5_fixed_radial_source_final_tests_20261013.stdout.txt',
        'artifacts/muon_normal_shape_induced_canonical_response_20261013_run_1.stdout.txt',
        'artifacts/muon_normal_shape_induced_canonical_response_20261013_run_2.stdout.txt',
        'artifacts/muon_d5_induced_shape_poisson_20261013_base_final_run_4.stdout.txt',
        'artifacts/muon_d5_induced_shape_poisson_20261013_base_final_run_5.stdout.txt',
        'artifacts/muon_d5_induced_shape_poisson_20261013_area_final_run_1.stdout.txt',
        'artifacts/muon_d5_induced_shape_poisson_20261013_area_final_run_2.stdout.txt')
    for n in code+logs:select(ROOT/n)
    scope=dict(action='original full complex child canonical Jacobi, g_x/g_v/g_y and full rate covector/offset, fixed2cell same action history',
        initial='original induced dx/dPi0; effective p includes g_v; this is conditional source inverse, not the inherited physical initial trace',
        parent='born parameter source work retained, not parent-future bulk forcing; incoming OWN and inherited child constituents are separate later applications',
        direct_plus_induced='base b+induced raw high/low assembled before coefficient/density/Spin/field projection; area total is mixed coefficient induced only, no second b',
        area_Hb_comparison='upstream provided_source_minus_Hb is a BASE-H benchmark for area, not a failed area source formula; actual area g_eff uses area Hessian/source coefficient',
        matrix_representation='Acb original stored-coefficient assembly bounds and binary source rounding are not original action/physical accuracy enclosures',
        field='same four coordinate radial profiles on48 source points, full64 Spin4/SM16 per fixed particle/conjugate and eta sheet, n0; every represented oppositeSpin/carrier retained',
        Poisson='raw wall value Schur/Literal dual on SAME K; complete source and E Poisson fields plus three mixed source/E contacts; no retarded selector',
        Spin='K already contains Gamma0; left coefficient Gamma0 S^-1 Gamma0/right S and all source-frame contacts, no Hilbert dagger',
        wall='signed outward material wall Green return retained separately; not complete original strong/radial/angular/exterior transmission',
        SH='once-only fixedY fixed point-trace density coefficient, no second intrinsic kinetic; physical normalized scalar mode/trace/domain firsts unassigned',
        physical_coupled_base='original2264.424e-6/all67 not admitted; unit response is a derivative, not nonlinear shifted base or selected psi',
        physical_Gamma2_pole_charge_LSZ_Pauli_native_or_error_admitted=False)
    out.mkdir(parents=True)
    verification=dict(classification='VERIFIED_ACTUAL_INDUCED_CANONICAL_D5_SAME_FIELD_SOURCE_REPLAY',pairs=pairs,
        input_hashes=pins,current_input_pins=len(pins),scope=scope,fresh_ancestor_regeneration_or_physical_admission=False)
    p=out/'verification.json';p.write_text(json.dumps(verification,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n');select(p)
    commands=[f'C:/Python314/python.exe scripts/evaluate_muon_normal_shape_induced_canonical_response.py --output artifacts/muon_normal_shape_induced_canonical_response_20261013/run_{j}' for j in(1,2)]
    commands += [f'C:/Python314/python.exe scripts/evaluate_muon_d5_induced_shape_poisson.py --output artifacts/muon_d5_induced_shape_poisson_20261013/base_final_run_{j}' for j in(4,5)]
    commands += [f'C:/Python314/python.exe scripts/evaluate_muon_d5_induced_shape_poisson.py --sector area --output artifacts/muon_d5_induced_shape_poisson_20261013/area_final_run_{j}' for j in(1,2)]
    manifest=dict(classification='COMPACT_ACTUAL_INDUCED_CANONICAL_D5_SAME_FIELD_SOURCE_MEMBERSHIP',selected_files=selected,
        input_hashes=pins,scope=scope,pairs=pairs,actual_commands=commands,
        exact_environment=dict(python='C:/Python314/python.exe',PYTHONPATH='src;scripts',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
        focused_controls=['original canonical source/full rate dual2passed.86s','same-field Schur/E1passed.79s',
            'whole complex source/frame/E and common-gamma incidence2passed.84s'],
        development='base_final_run1 (prior source images) and run2/3 (before area-incidence clarification) remain local; no physical/scientific input overwritten',
        local_frozen_pins_and_consumers_not_tracked_seed_dependency_closure=True)
    p=out/'publication_manifest.json';p.write_text(json.dumps(manifest,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(manifest_sha256=digest(p),verification_sha256=digest(out/'verification.json'),
        files=len(selected),bytes=sum(v['bytes']for v in selected.values()),max_file_bytes=max(v['bytes']for v in selected.values())),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();verify(a.output)
