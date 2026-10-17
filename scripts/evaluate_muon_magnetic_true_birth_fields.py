"""Apply the true attached E1 action to reached magnetic canonical fields."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_true_birth_fields import true_magnetic_birth_fields
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    arrays={};records=[];hashes={}
    for side in ('incoming','outgoing'):
        bound=load_magnetic_reached_mean_inputs('artifacts/muon_electromagnetic_soft_magnetic_source_20261011/'+side+'_run_1',repository=ROOT)
        r=true_magnetic_birth_fields(bound,repository=ROOT);hashes.update(r['input_hashes'])
        for key in ('canonical_state','velocity','A_tau','Legendre_residual','Gauss_residual','source_canonical_momentum'):
            arrays[side+'_'+key]=r[key]
        for key,value in r['fields'].items():
            if isinstance(value,np.ndarray):arrays[side+'_'+key]=value
        for key in ('Q','Qdot','Q_first_jet','Qdot_first_jet'):arrays[side+'_'+key]=r['source'][key]
        for key,value in zip(('raw_M','raw_B','raw_K'),r['sample']['raw_forms']):arrays[side+'_'+key]=value
        records.append(dict(side=side,Legendre_maximum_residual=float(np.max(abs(r['Legendre_residual']))),
            Gauss_maximum_residual=float(np.max(abs(r['Gauss_residual']))),
            true_birth_velocity_norm=float(np.linalg.norm(r['velocity'])),
            velocity_difference_from_source_cell=float(np.linalg.norm(r['velocity']-bound['velocity']['velocity'][-1 if side=='incoming' else 0])),
            At_norm=float(np.linalg.norm(r['A_tau'])),action_parameters=r['action_parameters'],
            endpoint_receipt_sha256=r['endpoint']['receipt_sha256']))
    assert np.array_equal(arrays['incoming_canonical_state'],arrays['outgoing_canonical_state'])
    for name in ('src/bhsm/interface/muon_magnetic_true_birth_fields.py','src/bhsm/interface/muon_magnetic_source_mean_load.py',
                 'src/bhsm/interface/muon_trace_enriched_reached_action.py','src/bhsm/interface/muon_electromagnetic_soft_magnetic_source.py',
                 'src/bhsm/interface/muon_parent_maxwell_full_retarded.py',Path(__file__).relative_to(ROOT).as_posix()):
        hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    if (out/'application.npz').stat().st_size>10*1024**2:raise ValueError('lossless archive exceeds publication size')
    if any(sha256((ROOT/n).read_bytes()).hexdigest()!=h for n,h in hashes.items()):raise RuntimeError('consumed action changed')
    r=dict(classification='EVALUATED_TRUE_ATTACHED_BIRTH_MAGNETIC_LEGENDRE_GAUSS_APPLICATION',
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),numerical_bytes=(out/'application.npz').stat().st_size,
        input_hashes=hashes,records=records,canonical_birth_state_bit_identical=True,
        true_E1_endpoint_primal_fields_used=True,source_cell_midpoint_held_velocities_substituted=False,
        complete_sourced_Legendre_and_Gauss_rows_applied=True,velocities_copied_across_birth=False,
        local_endpoint_application_not_new_trajectory=True,full_physical_response_boundary_matching_claimed=False,
        native_loop_or_Pauli_or_LSZ_completed=False,At_rate_slot_used_by_literal_action=False,
        error_scope='binary64 local action and finite constitutive solve; no outward source/operator or continuum error enclosure')
    (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    return dict(classification=r['classification'],numerical_sha256=r['numerical_sha256'],records=records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();print(json.dumps(materialize(args.output),sort_keys=True))
