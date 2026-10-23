"""Focused retained endpoint/tube contraction and dependent interface updates."""
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
import numpy as np

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def read(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}

def run(root,out):
    if out.exists():raise FileExistsError('new output required; previous arrays remain immutable')
    out.mkdir(parents=True);began=time.perf_counter();sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_endpoint_clock_actions import endpoint_rates,apply_endpoint
    b=root/'artifacts/flagship_integration';r=root/'artifacts/muon_radial_inclusion_action_20261004/replay_reference'
    refs=dict(step=b/'BHSM_N12_C2_LOHNER_STEP_1222.npz',step_report=b/'BHSM_N12_C2_LOHNER_STEP_1222.json',
        branch=b/'BHSM_N12_C2_LOHNER_BORDERED_MATRIX_1221.npz',growth=b/'BHSM_N12_C2_LOHNER_GROWTH_1221.json',
        response_bounds=b/'BHSM_N12_C2_LOHNER_RESPONSE_BALL_1221.json',
        geometry=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        contact=root/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        corrected=root/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
        pairing=root/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz',
        old=r/'radial_source_action_and_interface.npz',norm=r/'full_normalization.json',
        module=root/'src/bhsm/interface/muon_endpoint_clock_actions.py',script=Path(__file__),
        field_producer=root/'scripts/audit_n12_c2_exact_center_fixed_s_field_matrix.py',
        response_producer=root/'scripts/audit_n12_c2_bordered_hard_response_matrix.py',
        clock_and_domain_producer=root/'scripts/certify_n12_c2_cancelled_field_lohner_step.py',
        geometry_producer=root/'src/bhsm/interface/muon_parent_maxwell_velocity.py')
    save(out/'input_hashes.json',{k:dict(path=str(p.relative_to(root)) if p.is_relative_to(root) else str(p),sha256=sha(p)) for k,p in refs.items()})
    git=lambda *a:subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(out/'workspace.json',dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),status=git('status','--short'),
        reference='524ed90689bd5923c249bba2e699abf627e703cd',starting_head='a5fc2429c89e2c8e374852ac687cc9c78d1f959e'))
    step=read(refs['step']);rec=json.loads(refs['step_report'].read_text());branch=read(refs['branch'])
    growth=json.loads(refs['growth'].read_text());response=json.loads(refs['response_bounds'].read_text())
    point=endpoint_rates(step,rec,branch,growth,response,tube=False);tube=endpoint_rates(step,rec,branch,growth,response,tube=True)
    save(out/'endpoint_point_rates.json',point['result']);save(out/'endpoint_tube_rates.json',tube['result'])
    save(out/'stage.json',dict(stage='Delta-free endpoint lapse rates enclosed on retained selected branch; source/interface application next',higher_derivative_campaigns=0))
    geometry=read(refs['geometry']);contact=read(refs['contact']);corrected=read(refs['corrected']);pairing=read(refs['pairing']);old=read(refs['old']);norm=json.loads(refs['norm'].read_text())
    arrays,result=apply_endpoint(geometry,contact,corrected,pairing,old,norm,point,tube)
    # Only compare the instantaneous inputs: do not re-integrate valid I/T.
    from bhsm.interface.muon_parent_maxwell_velocity import current_parent_fields
    from bhsm.interface.aether_forward_boundary_radius import boundary_log_radius
    y=step['endpoint_predictor_center'];fields=current_parent_fields(y[None],np.array([boundary_log_radius(12,y[:37])]),geometry['rho'])
    result['instantaneous_comparison']={k:dict(array_equal=bool(np.array_equal(fields[k][0],geometry[k][0])),
        max_absolute_difference=float(np.max(abs(fields[k][0]-geometry[k][0])))) for k in ('C_rho','base_radius','proper_lapse','A','B','proper_shift_rho')}
    result['instantaneous_scope']='source and interface changes evaluated at fixed saved instantaneous operands; endpoint q is unchanged but reconstructed nu/shift differences remain explicit; no silently relabeled overlap certificate'
    result['elapsed_seconds']=time.perf_counter()-began
    result['execution']=dict(old_productions_rerun=0,old_checks_replayed=0,old_I_T_integrals_recomputed=0,
        new_action_I_dot_integrals=2,new_action_hessians=0,new_eigensolves=0,derivative_campaigns=0,native_heat=0)
    np.savez_compressed(out/'endpoint_clock_source_and_interface.npz',**arrays)
    save(out/'result.json',result)
    save(out/'checkpoint.json',dict(id='BHSM_MUON_DELTA_FREE_ENDPOINT_CLOCK_INTERFACE_20261004',
        arrays='endpoint_clock_source_and_interface.npz',result='result.json',physical_prediction=False,
        next='assemble the same-owner exterior/interface contributions on the full projected-plus-complement field; updated local rows alone do not supply the stratified operator'))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ('source_Lnu_range','source_Lnu_tube_range','action_I_dot','preserved_nodal_I_dot','action_H','instantaneous_comparison','norms','elapsed_seconds')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
