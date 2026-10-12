"""Apply same full-action lambda variation to lifetime/scalar local equations."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_local_lifetime_scalar_matching import retained_lambda_field_family,local_joint_matching_scan
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_coupled_lorentz_radial_green import encode


def materialize(output):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve original matching applications')
    config_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    config=json.loads(config_path.read_bytes());v=config['selected_consumer_values'];refs={config_path.relative_to(ROOT).as_posix():sha256(config_path.read_bytes()).hexdigest()}
    records=[];pending=[]
    for side in('incoming','outgoing'):
        family=retained_lambda_field_family(side,repository=ROOT);refs.update(family['input_hashes'])
        scan=local_joint_matching_scan(family,muon_mass_GeV=v['m_mu_GeV']['value'],electron_mass_GeV=v['m_e_GeV']['value'],scalar_mass_GeV=v['m_h_GeV']['value'],
            lifetime_seconds=config['primary_measurements']['positive_muon_lifetime']['value']*1e-12,hbar_GeV_seconds=float(config['unit_convention']['hbar_GeV_s']))
        arrays={k:x for k,x in family.items()if isinstance(x,np.ndarray)};arrays.update({k:x for k,x in scan.items()if isinstance(x,np.ndarray)})
        pending.append((side+'_application.npz',arrays))
        record=dict(side=side,lambda_H_base=family['lambda_H_base'],lambda_affinity_residual_max=float(np.max(abs(family['lambda_H_affinity_residual']))),
            positive_candidate_count=len(scan['positive_radial_candidate_equation_rows']),
            positive_candidate_rows=scan['positive_radial_candidate_equation_rows'],joint_local_equation_roots=scan['joint_local_equation_roots'],
            matching_equations=scan['matching_equations'],row_order=scan['row_order'],global_no_solution_theorem=False)
        records.append(record);print(json.dumps(encode(record),sort_keys=True),flush=True)
    for name in('muon_local_lifetime_scalar_matching','muon_profile_preserving_phase_sample','muon_coupled_lorentz_field_symbol','muon_coupled_lorentz_radial_green','muon_static_coupled_charged_current','muon_coupled_tensor_decay_rate'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=sha256((ROOT/path).read_bytes()).hexdigest()
    for path in(Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_coupled_lorentz_radial_green.py','tests/test_muon_local_lifetime_scalar_matching.py'):
        refs[path]=sha256((ROOT/path).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same lambda/action consumer changed')
    out.mkdir(parents=True);files={}
    for name,a in pending:
        p=out/name;deterministic_archive(p,a);files[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    packet=dict(classification='EVALUATED_JOINT_LOCAL_FULL_ACTION_LIFETIME_AND_SCALAR_PARAMETER_EQUATIONS',records=records,array_archives=files,input_hashes=refs,
        fixed_Y_preserved=True,held_base_coefficients=True,positive_lambda_candidates_only_for_rate_application=True,
        all_H4_pole_candidates_retained=True,unstable_original_poles_deleted=False,
        physical_phase_recomputed=False,physical_scalar_resonance_selected=False,physical_unit_selected=False,
        errors='binary64 original finite action/Schur/eigen/phase-space application; sampled positive radial candidate relation is not a global existence theorem. NonVA radiative, spatial momentum, stationary branch, continuum kinetic and outer pole matching remain separate.',
        physical_a_mu=None,physical_g_mu=None)
    (out/'result.json').write_text(json.dumps(encode(packet),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=packet['classification'],result_sha256=sha256((out/'result.json').read_bytes()).hexdigest(),files=files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(materialize(p.parse_args().output),sort_keys=True))
