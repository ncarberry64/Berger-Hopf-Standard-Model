"""Read-only exact-component provenance and fixed-frame guard."""
from pathlib import Path
from hashlib import sha256
import argparse,importlib.util,json,sys
import numpy as np


def run(root,position,clock,jacobi,output):
    root,position,clock,jacobi,out=map(lambda p:Path(p).resolve(),(root,position,clock,jacobi,output));out.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).read_bytes();(out/'executed_guard.py').write_bytes(source);pins={}
    def pin(p):
        p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest();return p
    def load(p):
        p=pin(p)
        if p.suffix=='.json':return json.loads(p.read_bytes())
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    def module(name,p):
        p=pin(p);spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    sys.path.insert(0,str(root/'src'))
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    ctx.prec=256
    family=root/'artifacts/muon_baton_zoo_maximal_current_realization_20261013';rt=family/'actual_new620_fresh_native_MP_new_exact_R7_clock_control_run_1'
    module('bhsm_baton_zoo_exact_acb_packets',rt/'bhsm_baton_zoo_exact_acb_packets_imported_runtime.py');ex=module('bhsm_exact_action_balls',rt/'bhsm_exact_action_balls_imported_runtime.py')
    def exact(z,k):return ex.parse_acb_exact_dyadic(z,k+'_exact')
    def hi(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])
    def cat(*args):return acb_mat([[a[i,j]for j in range(a.ncols())]for a in args for i in range(a.nrows())])
    expected={position:('d6b0dbb2e34185011f243f7f571da2f536ebc58c6138fab380f856a2f5db96b9','bhsm_original_ea02_same_field_position_euler_20261016.py'),clock:('95a64f63e2a541abf698ce7e65afc75a3f4eddb5932f239b74458a171e5be1be','bhsm_original_ea02_same_field_seven_clock_20261016.py'),jacobi:('a761a939cffb6b426ac254f59a8263feeb644ebdfc3843f69b061ee607b4ba3f','bhsm_original_ea02_same_field_position_jacobi_20261016.py')}
    metas={}
    for folder,(h,name)in expected.items():
        m=load(folder/'result.json');metas[folder]=m
        if m['source_sha256']!=h or sha256(pin(folder/'executed_producer.py').read_bytes()).hexdigest()!=h or sha256(pin(root/'audits'/name).read_bytes()).hexdigest()!=h:raise ValueError('Exact reviewed source bytes required')
    if not metas[clock]['admitted_original210_and_frame7_clock']:raise ValueError('Unadmitted clock')
    cp=load(clock/'actual_same_cut_seven_continuous_response_clock.npz')
    seed=load(family/'actual_linear_cut_enlarged_Gauss_Legendre_prolongation_run_2/actual_original_Gauss_and_old_Legendre_complete_current_Cauchy_prolongation.npz')
    R=exact(cp,'actual_complete_seven_response');Rdot=exact(cp,'actual_complete_seven_response_clock');reference=cat(hi(seed,'actual_parent_source252'),hi(seed,'actual_solved_child_field368'))
    seed_difference=_upper(R-reference)
    if seed_difference>1e-60:raise ValueError('The exact retained seven response fields changed')
    pp=load(position/metas[position]['archive']['name']);jp=load(jacobi/metas[jacobi]['archive']['name'])
    projection=load(root/'artifacts/muon_baton_zoo_radial_convergence_20261014/actual_common_cut_degree4_momentum_projection_run_1/actual_common_cut_new_field_momentum_projection_and_Gauss_guards.npz')
    oldmap=pp['old368_to_enlarged_child'];carried=hi(projection,'full_common_cut_action_direction')
    from_projected=acb_mat([[carried[int(i),j]for j in range(7)]for i in np.r_[np.arange(252),252+oldmap]])
    projection_difference=_upper(R-from_projected)
    if projection_difference>1e-24:raise ValueError('Different preprojection carried seven fields')
    rates={}
    for key,old in [('actual_enlarged_seven_field',R),('actual_enlarged_seven_field_clock',Rdot)]:
        a=exact(jp,key);selected=acb_mat([[a[int(i),j]for j in range(7)]for i in np.r_[np.arange(252),252+oldmap]]);rates[key]=_upper(selected-old)
        if rates[key]>1e-60:raise ValueError('Jacobi input does not reproduce the admitted same-cut field/clock')
    target=load(family/'actual_linear_cut_compatible368_MP_full_operator_blocked_run_2/actual_precise_direct_CHILD620_and_full368_canonical_source_operands.npz')
    fpacket=load(root/'artifacts/muon_baton_zoo_radial_convergence_20261014/compatible_explicit_maps_all_epochs_run_1/birth_degree_02_compatible_literal_central_frames.npz')
    F=np.zeros((7,210),complex);F[np.arange(7),185+4*np.arange(7)]=1
    if not np.array_equal(F,target['completed_frames'])or not np.array_equal(F,seed['completed_frames'])or not np.array_equal(F,fpacket['frames_completed'])or not fpacket['material_At_frame_first_zero'].item():raise ValueError('The exact owned fixed coefficient frame differs')
    pin(root/'artifacts/muon_baton_zoo_radial_convergence_20261014/compatible_central_all_epochs_run_2/executed_bhsm_baton_zoo_compatible_radial_complex.py')
    report=dict(classification='EXACT_REVIEWED_EA02_SEVEN_CLOCK_AND_JACOBI_INCIDENCE_GUARD',source_sha256=sha256(source).hexdigest(),input_hashes=dict(sorted(pins.items())),
        retained_seven_response_seed_difference_upper=seed_difference,preprojection_seven_field_difference_upper=projection_difference,Jacobi_carried_field_and_clock_difference_upper=rates,
        fixed_named_frame_exact_selector_columns=(185+4*np.arange(7)).tolist(),frame_first_zero_owned=True,
        F_depends_on_H=False,generator_Z_depends_on_H=True,all_reviewed_source_sha_guards_pass=True,
        no_action_or_history_solve_repeated=True,full_physical_gate_pass=False,original_coupled_corrections_applied=0)
    (out/'result.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n');print(json.dumps({k:v for k,v in report.items()if k not in ['input_hashes']}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--position',required=True);p.add_argument('--clock',required=True);p.add_argument('--jacobi',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.repository,a.position,a.clock,a.jacobi,a.output)
