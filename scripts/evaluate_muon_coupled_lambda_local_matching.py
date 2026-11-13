"""Consume the coupled stiffness correction in actual field/pole/rate equations."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_lambda_coupled_birth_continuation import load_lambda_coupled_birth
from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from bhsm.interface.muon_birth_finite_normal_trace_graph import pointwise_finite_normal_action
from bhsm.interface.muon_birth_inherited_finite_normal_phase import inherited_child_finite_normal_action
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_coupled_lorentz_field_symbol import coupled_field_symbol
from bhsm.interface.muon_coupled_lorentz_radial_green import coupled_radial_trace_application,coupled_radial_pole_application
from bhsm.interface.muon_static_coupled_charged_current import static_coupled_charged_current
from bhsm.interface.muon_coupled_tensor_decay_rate import tensor_tree_decay_rate,temporal_charged_current_series
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_coupled_lorentz_radial_green import encode


def materialize(output,*,coupled_directory):
    out=Path(output);out=out if out.is_absolute()else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier coupled local matching applications')
    changed=load_lambda_coupled_birth(coupled_directory,side='incoming',repository=ROOT)
    baseline=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side='incoming',repository=ROOT)
    with np.load(baseline['source']/'application.npz',allow_pickle=False)as f:old={k:f[k].copy()for k in f.files}
    cfg_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json';cfg=json.loads(cfg_path.read_bytes());v=cfg['selected_consumer_values'];M=v['m_mu_GeV']['value'];m=v['m_e_GeV']['value']
    refs=dict(changed['input_hashes']);refs.update(baseline['input_hashes']);refs[cfg_path.relative_to(ROOT).as_posix()]=sha256(cfg_path.read_bytes()).hexdigest()
    arrays={};records=[];pencils={}
    for kind,loaded,values in(('original',baseline,old),('changed',changed,changed['arrays'])):
        rep=deepcopy(loaded['representation']);params=loaded['receipt']['action_parameters'];pair=values['updated_raw_pair'];reference=values.get('reference_raw_pair',values.get('reference_pair'))
        for arm,side in enumerate(('incoming','outgoing')):
            raw=pair[arm];w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99]);N=w['induced_lapse'].value;R=w['R4'].value
            print(json.dumps(dict(stage='same_birth_coupled_local_action',kind=kind,side=side),sort_keys=True),flush=True)
            action=(pointwise_finite_normal_action(raw,rep,**params)if arm==0 else inherited_child_finite_normal_action(raw,0.,pair,reference,rep,**params))
            symbol=coupled_field_symbol(action,rep,lapse=N,H=raw[260:264]);C=symbol['proper_frequency_coefficients'];Q=symbol['field_quotient_lift'];T=symbol['joint_trace_map'];r=symbol['scalar_radial_source'];F=symbol['central_radial_frame_rows']
            green=coupled_radial_trace_application(C,Q,T,r,F,frequency=0.)
            poles=coupled_radial_pole_application(C,Q,T,r,F)
            H=raw[260:262]+1j*raw[262:264];current=static_coupled_charged_current(green['joint_wall_Green'],H,radius=R,lapse=N,family=1,out_family=2)
            static=tensor_tree_decay_rate(current['full_charged_current_tensor'],muon_mass_GeV=M,electron_mass_GeV=m,radial_order=24)
            tau=cfg['primary_measurements']['positive_muon_lifetime']['value']*1e-12;hbar=float(cfg['unit_convention']['hbar_GeV_s']);E=(static['tree_rate_coefficient_GeV5']*tau/hbar)**.25
            series=temporal_charged_current_series(C,Q,T,current['charged_current_right_vertices'],current['charged_current_left_vertices'],maximum_frequency=M/E)
            rate=tensor_tree_decay_rate(current['full_charged_current_tensor'],muon_mass_GeV=M,electron_mass_GeV=m,radial_order=24,temporal_coefficients=series['temporal_current_coefficients'],action_energy_unit=E)
            prefix=kind+'_'+side+'_';pencils[kind,side]=C
            for label,obj in(('symbol',symbol),('green',green),('poles',poles),('current',current),('series',series)):
                arrays.update({prefix+label+'_'+k:z for k,z in obj.items()if isinstance(z,np.ndarray)})
            arrays[prefix+'raw_fields']=raw;arrays[prefix+'full_action_gradient']=action['gradient'];arrays[prefix+'full_action_hessian']=action['hessian']
            record=dict(kind=kind,side=side,lambda_H=rep['scalar_matching']['lambda_H'],lapse=N,radius=R,
                static_rate_coefficient_GeV5=static['tree_rate_coefficient_GeV5'],temporal_rate_coefficient_GeV5=rate['tree_rate_coefficient_GeV5'],
                conditional_static_E_kappa_GeV=E,conditional_temporal_E_kappa_GeV=(rate['tree_rate_coefficient_GeV5']*tau/hbar)**.25,
                finite_field_poles=poles['finite_pole_count'],infinite_field_poles=poles['infinite_pole_count'],
                maximum_field_pole_imaginary_part=float(np.max(abs(poles['local_poles'].imag))),
                temporal_tensor_tail_estimate=series['uniform_tensor_series_tail_estimate'],field_action_gradient_norm=float(np.linalg.norm(symbol['field_action_gradient'])),
                full_tensor_VA_remainder=current['VA_relative_remainder'])
            records.append(record);print(json.dumps(encode(record),sort_keys=True),flush=True)
    changes=[]
    for side in('incoming','outgoing'):
        d=pencils['changed',side]-pencils['original',side];arrays[side+'_coupled_frequency_pencil_change']=d
        changes.append(dict(side=side,full_change_norm=float(np.linalg.norm(d)),gauge_kinetic_change_norm=float(np.linalg.norm(d[2,:64,:64])),gauge_H_cross_change_norm=float(np.linalg.norm(d[:, :64,64:68]))))
    for p in(Path(__file__).relative_to(ROOT).as_posix(),'src/bhsm/interface/muon_lambda_coupled_birth_continuation.py','src/bhsm/interface/muon_coupled_lorentz_field_symbol.py','src/bhsm/interface/muon_coupled_lorentz_radial_green.py','src/bhsm/interface/muon_static_coupled_charged_current.py','src/bhsm/interface/muon_coupled_tensor_decay_rate.py','scripts/evaluate_muon_reached_trace_action.py','scripts/evaluate_muon_coupled_lorentz_radial_green.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same coupled matching input changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays);path=out/'application.npz'
    md=dict(classification='EVALUATED_COUPLED_BIRTH_HIGGS_STIFFNESS_RESPONSE_IN_ORIGINAL_LOCAL_POLE_AND_FULL_DECAY_RATE',records=records,coupled_field_changes=changes,input_hashes=refs,
        archive=dict(path=path.name,bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest()),
        matched_equation_role='coupled minimum-weight same226 continuation changes both fields and action; evaluates actual original84 source poles and full mu-plus current tensor',
        compared_on_same_true_birth_coefficient_chart=True,old_phase_midpoint_fields_substituted=False,
        physical_phase_repropagated=False,physical_scalar_pole_or_energy_unit_selected=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 original finite action/row/Schur/pole/rate application; no nonVA QED, spatial momentum, source-cell/physical external domain or continuum error enclosure')
    (out/'result.json').write_text(json.dumps(encode(md),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest(),archive=md['archive'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--coupled-directory',type=Path,default=Path('artifacts/muon_lambda_coupled_birth_continuation_20261011/run_2'));a=p.parse_args();print(json.dumps(materialize(a.output,coupled_directory=a.coupled_directory),sort_keys=True))
