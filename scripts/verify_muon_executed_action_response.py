"""Reproducibility and publication checks for executed finite action responses."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'artifacts/muon_executed_action_response_20261010/verification.json'
MODULES=('muon_parent_gauge_geometry_correction','muon_parent_maxwell_full_retarded',
         'muon_native_dirac_hamiltonian','muon_calibrated_bosonic_higgs_photon',
         'muon_finite_normal_schur','muon_frozen_normal_schur_certificate',
         'muon_material_higgs_gauge_action','muon_finite_orientation_ward',
         'muon_parent_temporal_enrichment','muon_parent_maxwell_corrected_retarded',
         'muon_native_product_factor_graph','muon_birth_coupled_constraint_retraction',
         'muon_native_coupled_source_heat')
PAIRS=(('muon_parent_maxwell_full_retarded_20261010','run_1','run_2'),
       ('muon_parent_gauge_geometry_correction_20261010','canonical_interior_run_1','canonical_interior_run_2'),
       ('muon_parent_gauge_geometry_correction_20261010','canonical_wall_mean_run_1','canonical_wall_mean_run_2'),
       ('muon_native_dirac_hamiltonian_20261010','run_3','run_4'),
       ('muon_calibrated_bosonic_higgs_photon_20261010','run_1','run_2'),
       ('muon_calibrated_finite_projection_ledger_20261010','run_1','run_2'),
       ('muon_frozen_normal_schur_certificate_20261010','interior_run_3','interior_run_4'),
       ('muon_parent_gauge_geometry_correction_20261010','material_wall_mean_run_1','material_wall_mean_run_2'),
       ('muon_parent_gauge_geometry_correction_20261010','normal_interior_run_1','normal_interior_run_2'),
       ('muon_parent_gauge_geometry_correction_20261010','orientation_material_run_3','orientation_material_run_4'),
       ('muon_native_product_factor_graph_20261010','run_1','run_2'),
       ('muon_parent_gauge_geometry_correction_20261010','endpoint_constraint_run_1','endpoint_constraint_run_2'),
       ('muon_parent_gauge_geometry_correction_20261010','material_temporal_order2_run_1','material_temporal_order2_run_2'),
       ('muon_parent_maxwell_corrected_retarded_20261010','run_3','run_4'),
       ('muon_native_coupled_source_heat_20261010','run_1','run_2'))


def identity(path):
    data=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(data),
                sha256=hashlib.sha256(data).hexdigest())


def execute(argv):
    env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='1')
    result=subprocess.run(argv,cwd=ROOT,env=env,text=True,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return dict(argv=argv,cwd=str(ROOT),environment_overrides={
        'PYTHONPATH':str(ROOT/'src'),'OPENBLAS_NUM_THREADS':'1'},
        exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr)


def evidence():
    replays=[]
    for directory,first,second in PAIRS:
        left,right=(ROOT/'artifacts'/directory/name for name in (first,second))
        names=sorted(p.relative_to(left).as_posix() for p in left.rglob('*') if p.is_file())
        other=sorted(p.relative_to(right).as_posix() for p in right.rglob('*') if p.is_file())
        if not names or names!=other:
            raise ValueError('incomplete independent replay pair: '+directory)
        files=[]
        for name in names:
            if (left/name).read_bytes()!=(right/name).read_bytes():
                raise ValueError('independent replay differs: '+directory+'/'+name)
            files.append(dict(first=identity(left/name),second=identity(right/name)))
        replays.append(dict(directory=directory,byte_identical=True,files=files))
    sources=[ROOT/f'src/bhsm/interface/{name}.py' for name in MODULES]
    sources+=[ROOT/f'tests/test_{name}.py' for name in MODULES]
    sources+=[Path(__file__),ROOT/'scripts/evaluate_muon_native_dirac_hamiltonian.py',
              ROOT/'scripts/evaluate_muon_calibrated_bosonic_higgs_photon.py',
              ROOT/'scripts/evaluate_muon_calibrated_finite_projection_ledger.py',
              ROOT/'scripts/verify_muon_finite_projection_ledger.py',
              ROOT/'scripts/certify_muon_frozen_normal_schur.py',
              ROOT/'scripts/evaluate_muon_native_product_factor_graph.py',
              ROOT/'scripts/evaluate_muon_native_coupled_source_heat.py',
              ROOT/'theory/muon_executed_action_response_20261010.md']
    return dict(replays=replays,source_hashes=[identity(p) for p in sources],
        runtime=dict(python=sys.version,executable=sys.executable,
            packages={name:version(name) for name in ('numpy','scipy','sympy','mpmath','pytest','python-flint')}),
        inherited_verification=identity(ROOT/'artifacts/muon_coupled_action_application_20261010/verification.json'),
        calibrated_projection_verification=identity(ROOT/'artifacts/muon_calibrated_bosonic_higgs_photon_20261010/verification.json'),
        additive_ledger_verification=identity(ROOT/'artifacts/muon_calibrated_finite_projection_ledger_20261010/verification.json'),
        normal_arithmetic_verification=identity(ROOT/'artifacts/muon_frozen_normal_schur_certificate_20261010/verification.json'),
        material_orientation_verification=identity(ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/orientation_material_verification.json'),
        finite_sector_verification=identity(ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/finite_sector_verification.json'),
        interior_replay_verification=identity(ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010/interior_replay_verification.json'),
        finite_graph_heat_verification=identity(ROOT/'artifacts/muon_native_product_factor_graph_20261010/verification.json'),
        coupled_response_verification=identity(ROOT/'artifacts/muon_parent_maxwell_corrected_retarded_20261010/verification.json'),
        coupled_first_heat_verification=identity(ROOT/'artifacts/muon_native_coupled_source_heat_20261010/verification.json'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tests',action='store_true')
    parser.add_argument('--audits',action='store_true')
    parser.add_argument('--test-module',action='append',choices=MODULES)
    args=parser.parse_args()
    record=json.loads(OUTPUT.read_text(encoding='utf8')) if OUTPUT.exists() else {}
    record.update(evidence(),action_selected=False,Gate7_closed=False,complete_observable=False,
        scientific_classification=dict(
            DERIVED='Material one-form trace cancels Eulerian radial advection once; same-action Gauss Schur elimination; all-family fixed-Y canonical Dirac applications with distinct covariant factor; finite orientation Ward identity; outward stored normal contraction; common-input signed Pauli ledger',
            EVALUATED='Material-chart common coefficient Newton corrections and TOTAL assigned multiplier density; coupled photon-Higgs retarded and advanced applications; all-family canonical source vertices; actual eight-Q finite-core contact and both heat insertions with full n1/n3 complements; finite transverse W/Hgamma projection',
            CONTROL_ONLY='Local time/radial trial representation and nu-squared parameter trial; superseded130 mixed-chart run; primitive-independence covariance illustration',
            UNEVALUATED='Complete interacting E1 base and physical quotient; physical formation cutoff; full stratified native two-insertion and completed Pauli remainder; remaining finite weak terms',
            OWNER_DEFINITION_GAP='none established'),
        error_scope=dict(finite_ODE_and_Newton_residuals_are_not_continuum_bounds=True,
            nonzero_gauge_consistency_reaction_retained=True,
            finite_Galerkin_stationarity_not_complete_physical_stationarity=True,
            historical_constraint_density_key_is_CAP_only=True,
            material_multiplier_density_not_set_zero_by_Galerkin_residual=True,
            old_wall_mean_mixed_chart_run_not_corrected_material_stationary_base=True,
            canonical_Lorentz_temporal_vertex_not_positive_factor_temporal_vertex=True,
            source_square_contact_not_full_native_response=True,
            finite_eight_Q_heat_not_whole_native_supertrace=True,
            heat_cutoff_probes_not_physical_birth_cutoff=True,
            mesh_difference_estimate_not_continuum_enclosure=True,
            positive_product_factor_not_Lorentz_Euler_heat=True,
            scalar_parameter_trial_not_physical_scale_matching=True,
            numerical_replay_not_observable_enclosure=True,
            full_observable_uncertainty_not_established=True))
    code=0
    if args.tests:
        names=tuple(args.test_module) if args.test_module else MODULES
        result=execute([sys.executable,'-m','pytest','--noconftest','-q']+
            [f'tests/test_{name}.py' for name in names])
        result['tested_source_identities']=[identity(ROOT/f'src/bhsm/interface/{name}.py') for name in names]
        if args.test_module:
            record.setdefault('additional_focused_test_groups',[]).append(result)
        else:
            record['focused_tests']=result
        print(json.dumps(result,indent=2));code=result['exit_code']
    if args.audits:
        audits=dict(status=['tools/audit_bhsm_status.py','--format','json'],
            claims=['tools/audit_forbidden_claims.py','--format','json'],
            frozen=['tools/audit_frozen_prediction_integrity.py','--format','json'],
            precision=['tools/verify_precision.py'],
            public=['tools/audit_public_readiness.py','--format','json'])
        with ThreadPoolExecutor(max_workers=5) as pool:
            results=list(pool.map(execute,([sys.executable]+argv for argv in audits.values())))
        record['publication_audits']=dict(zip(audits,results))
        print(json.dumps(record['publication_audits'],indent=2));code=max(code,max(r['exit_code'] for r in results))
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',
                      encoding='utf8',newline='\n')
    return code


if __name__=='__main__':
    raise SystemExit(main())
