"""Action-owned decay tensor matching at the SAME current observation germ."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_owned_static_charged_current import owned_static_charged_current
from bhsm.interface.muon_coupled_lorentz_radial_green import coupled_radial_trace_application
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_coupled_tensor_decay_rate import temporal_charged_current_series,tensor_rate_tail_estimate,tensor_tree_decay_rate
from bhsm.interface.muon_tensor_lifetime_unit_matching import temporal_tensor_lifetime_match
from evaluate_muon_reached_trace_action import deterministic_archive
from evaluate_muon_coupled_lorentz_radial_green import encode


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve prior current-observation rate applications')
    folder=ROOT/'artifacts/muon_literal_wall_external_matching_20261011/run_2'
    refs={};arrays={};records=[]
    def pin(p,h=None):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;actual=sha256(p.read_bytes()).hexdigest()
        if h is not None and actual!=h:raise ValueError('same original observation action changed: '+str(p))
        refs[p.relative_to(ROOT).as_posix()]=actual;return p
    md=json.loads(pin(folder/'result.json').read_bytes());refs.update(md['input_hashes'])
    with np.load(pin(folder/md['archive']['path'],md['archive']['sha256']),allow_pickle=False)as f:data={k:f[k].copy()for k in f.files}
    cfg=json.loads(pin('artifacts/muon_calibrated_pauli_20261009/inputs.json').read_bytes());v=cfg['selected_consumer_values']
    M,m=v['m_mu_GeV']['value'],v['m_e_GeV']['value'];tau=cfg['primary_measurements']['positive_muon_lifetime']['value']*1e-12;hbar=float(cfg['unit_convention']['hbar_GeV_s'])
    for side in('incoming','outgoing'):
        pf=side+'_';raw=data[pf+'observation_raw_fields'];H=data[pf+'observation_H']
        w=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
        N,R=float(w['induced_lapse'].value),float(w['R4'].value)
        symbol={k:data[pf+'symbol_'+k]for k in('proper_frequency_coefficients','field_quotient_lift','joint_trace_map','scalar_radial_source','central_radial_frame_rows')}
        C,Q,T,r,F=(symbol[k]for k in('proper_frequency_coefficients','field_quotient_lift','joint_trace_map','scalar_radial_source','central_radial_frame_rows'))
        green=coupled_radial_trace_application(C,Q,T,r,F,frequency=0.)
        current=owned_static_charged_current(green['joint_wall_Green'],H,radius=R,lapse=N)
        rate=tensor_tree_decay_rate(current['full_charged_current_tensor'],muon_mass_GeV=M,electron_mass_GeV=m,radial_order=24)
        seed=(rate['tree_rate_coefficient_GeV5']*tau/hbar)**.25
        series=temporal_charged_current_series(C,Q,T,current['charged_current_right_vertices'],current['charged_current_left_vertices'],maximum_frequency=M/(.99*seed))
        matched=temporal_tensor_lifetime_match(current['full_charged_current_tensor'],series['temporal_current_coefficients'],muon_mass_GeV=M,electron_mass_GeV=m,lifetime_seconds=tau,hbar_GeV_seconds=hbar)
        allowance=tensor_rate_tail_estimate(matched['tree_rate_coefficient_GeV5'],series['uniform_tensor_series_tail_estimate'],muon_mass_GeV=M)
        arrays[pf+'observation_raw_fields']=raw;arrays[pf+'observation_H']=H
        for label,obj in(('symbol',symbol),('green',green),('current',current),('series',series),('matching',matched)):
            arrays.update({pf+label+'_'+k:a for k,a in obj.items()if isinstance(a,np.ndarray)})
        charge=max(np.max(abs(current[k]))for k in('right_charge_residual','right_neutral_charge_residual','left_charge_residual','left_neutral_charge_residual'))
        old=next(a for a in md['records']if a['side']==side and a['family']==1)
        record=dict(side=side,lapse=N,radius=R,charge_alignment_residual_max=float(charge),VA_relative_remainder=current['VA_relative_remainder'],
            static_rate_coefficient_GeV5=rate['tree_rate_coefficient_GeV5'],
            ratio_to_old_observation_conditional_scale=matched['conditional_E_kappa_GeV']/old['conditional_lifetime_match']['conditional_E_kappa_GeV'],
            tree_matching={k:a for k,a in matched.items()if not isinstance(a,np.ndarray)},
            temporal_series_rate_tail_estimate=allowance['absolute_rate_series_tail_estimate'])
        records.append(record);print(json.dumps(encode(record),sort_keys=True),flush=True)
    for stem in('muon_owned_static_charged_current','muon_coupled_lorentz_radial_green','muon_intrinsic_m4_normal_pullback','muon_coupled_tensor_decay_rate','muon_tensor_lifetime_unit_matching','muon_magnetic_open_lepton_vertex','muon_intrinsic_higgs_weak_action'):
        pin('src/bhsm/interface/'+stem+'.py')
    for p in('tests/test_muon_owned_static_charged_current.py',Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_reached_trace_action.py'):pin(p)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same observation rate producer changed')
    out.mkdir(parents=True);ap=out/'application.npz';deterministic_archive(ap,arrays)
    if ap.stat().st_size>10*1024**2:raise ArithmeticError('split complete archive, do not prune')
    result=dict(classification='EVALUATED_ACTION_OWNED_FULL_DECAY_TENSOR_AT_SAME_LITERAL_CURRENT_OBSERVATION',records=encode(records),input_hashes=refs,
        archive=dict(path=ap.name,bytes=ap.stat().st_size,sha256=sha256(ap.read_bytes()).hexdigest()),
        source_scope='Frozen current observation raw268 and original full84 proper-frequency polynomial, same quotient/natural-wall trace Green; owned weak-major spin2 charged/neutral injection.',
        source_basis_and_local_charge_corrected=True,full_nonVA_spin_sum_retained=True,
        physical_nonVA_inclusive_radiative_correction_completed=False,physical_external_pole_and_domain_matched=False,
        physical_decay_unit_selected=False,measured_anomaly_consumed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='Temporal current-series allowance is a conditional numerical estimate. Original action/domain production, spatial momentum and full nonVA inclusive radiation remain outside it. Independent nonmagnetic masses/lifetime used only in the displayed matching equation.')
    rp=out/'result.json';rp.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(result_sha256=sha256(rp.read_bytes()).hexdigest(),archive=result['archive'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);print(json.dumps(materialize(p.parse_args().output),sort_keys=True))
