"""One bounded rate-saddle correction and its actual all67 shape effect."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from evaluate_muon_per_arm_canonical_source import clean
from bhsm.interface.muon_normal_shape_rate_attribution import bounded_normal_shape_rate_attribution,exact_stored_shape_bulk_pairing
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_actual_normal_shape_source import proper_normal_shape_coefficient
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def run(source,output):
    out=ROOT/output
    if out.exists():raise FileExistsError('one bounded application; preserve prior result')
    pins={};archives={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p)as z:return{k:z[k].copy()for k in z.files}
    md=read(source,'result.json');oldcombined=read(source,'complete_all67_normal_shape_weak_response.npz')
    phase,_=retained_input('outgoing',pins);rep=phase['representation'];P=phase['coordinates']['lift']
    F=None;records=[];results={};out.mkdir(parents=True)
    def save(name,values):
        p=out/name;_compressed_npz(p,{k:v for k,v in values.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split bounded matrix attribution')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    for rec in md['records']:
        name=rec['point'];d=read(source,name+'_shape_weak_application.npz');raw=d['raw_pair'];ref=d['reference_pair']
        # Exactly reproduce the original supplied coefficients once. This
        # does not upgrade the action or change any state/source/frame.
        a=holomorphic_two_arm_action(raw,ref,rep,**md['action_parameters']);H,G=a['hessian'],a['gradient'];Hc=H[252:,252:];Gc=G[252:]
        if F is None:F=canonical_central_frame(raw[1],rep)['named_frame_covectors']
        eta=P.T@raw[1];cl=d['inherited_profile_clock']+d['reference_only_clock']
        rhs=np.r_[Gc[:106]-Hc[106:212,:106]@eta[106:212]-cl[106:212],-Hc[212:,:106]@eta[106:212]-cl[212:],np.zeros(2,complex)]
        oldz=np.r_[d['actual_child_master_rate'][106:],d['named_rate_reactions']]
        K=np.block([[Hc[106:,106:],F.T],[F,np.zeros((2,2),complex)]])
        repeated=Hc[106:,106:]@oldz[:146]-rhs[:146]
        reproduction=float(np.max(abs(repeated-d['original_child_rate_rows'])))
        if reproduction!=0:raise ValueError(f'original stored rate residual did not reproduce bitwise: {name} {reproduction}')
        correction=bounded_normal_shape_rate_attribution(Hc,Gc,eta[106:212],cl,F,rhs,oldz)
        fixed=correction['fixed_rhs'];af=proper_normal_shape_coefficient(raw[1],P)
        da=np.r_[np.zeros(252,complex),af['gradient']];dd=np.zeros((504,504),complex);dd[252:,252:]=af['hessian']
        testhi=np.vstack((np.zeros((252,67),complex),d['all67_phase_direction_high']))
        testlo=np.vstack((np.zeros((252,67),complex),d['all67_phase_direction_low']))
        # Parent-born parameter is fixed. The inherited clock is explicit.
        clock=np.r_[np.zeros(252,complex),cl]
        rates={
            'original_binary':(oldz,np.zeros_like(oldz)),
            'fixed_stored_rhs':(fixed['arrays']['correction_solution_high'],fixed['arrays']['correction_solution_low']),
            'literal_two_term_rhs':(correction['exact_assembly_solution_high'],correction['exact_assembly_solution_low'])}
        modes={};arrays=dict(original_saddle148=K,original_rhs148=rhs,original_rate148=oldz,
            literal_child_Hessian=Hc,literal_child_gradient=Gc,fixed_velocity=eta[106:212],unchanged_clock=cl,
            original_unbordered146_rows=repeated,original_frame_reactions=oldz[146:],
            literal_rhs_high=correction['exact_assembly_rhs_high'],literal_rhs_low=correction['exact_assembly_rhs_low'],
            exact_rhs_assembly_difference=correction['exact_assembly_minus_stored_rhs'],
            exact_assembly_original_rows=correction['exact_assembly_original_rows'],
            exact_assembly_frame_reaction_rows=correction['exact_assembly_frame_reaction_rows'])
        for mode,(hi,lo)in rates.items():
            rh=np.r_[np.zeros(252,complex),eta[106:212],hi[:146]];rl=np.r_[np.zeros(358,complex),lo[:146]]
            applied=exact_stored_shape_bulk_pairing(H,G,a['area_Hessian_per_gamma'],a['area_gradient_per_gamma'],clock,
                rh,rl,af['value'],da,dd,testhi,testlo)
            modes[mode]=applied
            arrays[mode+'_rate_high']=rh;arrays[mode+'_rate_low']=rl
            for sector,x in applied.items():
                for key,value in x.items():
                    if isinstance(value,np.ndarray):arrays[mode+'_'+sector+'_'+key]=value
        arrays.update({k:v for k,v in fixed['arrays'].items()if isinstance(v,np.ndarray)})
        save(name+'_bounded_rate_and_shape.npz',arrays);results[name]=modes
        metric=dict(point=name,recovered_original_residual_difference=reproduction,
            prior_original146_max=float(np.max(abs(repeated))),
            fixed_rhs_high_low_original146_upper=fixed['high_low_state']['original_action_rows_residual_upper'],
            fixed_rhs_high_low_unbordered_upper=fixed['high_low_state']['unbordered_phase_residual_upper'],
            fixed_rhs_bordered_upper=fixed['high_low_state']['bordered_residual_upper'],
            rhs_assembly_difference_upper=fixed['stored_rhs_assembly_difference_upper'],
            literal_two_term_original146_upper=correction['exact_assembly_original_upper'],
            literal_two_term_bordered_upper=correction['exact_assembly_bordered_upper'],
            literal_two_term_frame_reaction_upper=correction['exact_assembly_frame_reaction_upper'],
            original_normal_EL=clean(modes['original_binary']['base']['normal_EL_residual']),
            fixed_rhs_normal_EL=clean(modes['fixed_stored_rhs']['base']['normal_EL_residual']),
            literal_rhs_normal_EL=clean(modes['literal_two_term_rhs']['base']['normal_EL_residual']),
            fixed_rate_change_norm=float(np.linalg.norm(rates['fixed_stored_rhs'][0]+rates['fixed_stored_rhs'][1]-oldz)),
            literal_rate_change_norm=float(np.linalg.norm(rates['literal_two_term_rhs'][0]+rates['literal_two_term_rhs'][1]-oldz)))
        records.append(metric);print(json.dumps(metric,sort_keys=True),flush=True)
    pointsteps={}
    for rec in md['records']:
        if rec['point'].startswith('cell_'):
            k=int(rec['point'][5:]);h=complex(*rec['time'])*2/(2*k+1);pointsteps[rec['point']]=h
    summaries={};combined_arrays={}
    for mode in rates:
        for sector in ('base','area'):
            val=lambda p,key:results[p][mode][sector][key+'_high']+results[p][mode][sector][key+'_low']
            bulk=sum(h*val(p,'bulk_pairing')for p,h in pointsteps.items())
            initial=val('initial','boundary_pairing');final=val('final','boundary_pairing')
            corner=np.zeros_like(bulk) # equal explicit true-face source on both sides as in prior application
            complete=bulk+final-initial+corner
            key=mode+'_'+sector
            combined_arrays[key+'_bulk']=bulk;combined_arrays[key+'_initial']=initial;combined_arrays[key+'_final']=final;combined_arrays[key+'_complete']=complete
            old=oldcombined['complete_shape_action_pairing']if sector=='base'else oldcombined['area_complete_shape_action_pairing']
            summaries[key]=dict(complete_max=float(np.max(abs(complete))),change_from_previous_max=float(np.max(abs(complete-old))),
                bulk_max=float(np.max(abs(bulk))),initial_contact_max=float(np.max(abs(initial))),final_contact_max=float(np.max(abs(final))))
    save('bounded_rate_effect_on_all67_weak_shape.npz',combined_arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path and Path(path).is_relative_to(ROOT):
            p=Path(path);pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for p in (Path(__file__),ROOT/'tests/test_muon_normal_shape_rate_attribution.py'):
        pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('original matrix inputs changed')
    result=dict(classification='ONE_BOUNDED_STORED_RATE_CORRECTION_AND_ACTUAL_ALL67_NORMAL_SHAPE_EFFECT',
        input_hashes=pins,archives=archives,records=records,summaries=summaries,
        original_guard=2e-10,original_birth226_max=md['original_birth226_max'],
        original_all67_mechanical_work=md['original_all67_clock_scaled_mechanical_work'],
        original_action_precision_or_physical_domain_not_upgraded=True,
        original_target_clock_state_frame_source_preserved=True,
        rounded_rhs_vs_literal_H_G_product_assembly_distinguished=True,
        high_low_solutions_are_matrix_representations_not_new_physical_states=True,
        no_further_rate_precision_campaign_authorized_by_this_result=True,
        physical_coupled_birth_formation_exterior_or_pole_admitted=False,
        error_scope='Exactly recovered original binary action coefficients/rate residual; bounded Acb192 fixed matrix correction and separate low-rhs product representation of the same target/source. No action producer/quadrature/continuum/domain/physical-error bound.')
    p=out/'result.json';p.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='bounded_rate_shape_attribution_complete',result_sha256=sha256(p.read_bytes()).hexdigest(),summaries=summaries),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=Path('artifacts/muon_normal_shape_weak_consumption_20261012/run_1'));p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.source,a.output)
