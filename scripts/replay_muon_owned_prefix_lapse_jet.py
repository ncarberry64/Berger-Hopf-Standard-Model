"""One cached physical-clock action extraction; no historical producer run."""
import argparse,hashlib,json,sys,time
from pathlib import Path
import numpy as np

def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}

def run(root,out):
    if out.exists():raise FileExistsError('new output required')
    out.mkdir(parents=True);sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_owned_prefix_lapse_jet import evaluate_owned_center
    refs=dict(field=root/'artifacts/flagship_integration/BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1221.npz',
        field_report=root/'artifacts/flagship_integration/BHSM_N12_C2_LOHNER_FIXED_S_FIELD_1221.json',
        metric=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        pairing=root/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz',
        contact=root/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=root/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        module=root/'src/bhsm/interface/muon_owned_prefix_lapse_jet.py',script=Path(__file__),
        producer=root/'scripts/audit_n12_c2_exact_center_fixed_s_field_matrix.py',
        clock_producer=root/'scripts/certify_n12_c2_cancelled_field_lohner_step.py')
    save(out/'input_hashes.json',{k:dict(path=str(p.relative_to(root)) if p.is_relative_to(root) else str(p),sha256=sha(p)) for k,p in refs.items()})
    arrays,result=evaluate_owned_center(read(refs['field']),json.loads(refs['field_report'].read_text()),
        read(refs['metric']),read(refs['pairing']),read(refs['contact']),read(refs['corrected']))
    np.savez_compressed(out/'owned_prefix_center_lapse_action.npz',**arrays)
    save(out/'result.json',result);save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ('clock_factor','normalization_center','direct_source_log_nu_tau_range','nodal_source_log_nu_tau_range','source_spatial_interpolation_max_difference','q_tau_consistency_with_v_over_Nb')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository,a.output)
