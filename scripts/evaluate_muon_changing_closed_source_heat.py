"""Assemble changing heat contact, both insertions and joined birth mean."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_changing_closed_source_heat import changing_source_heat_polynomial,paired_source_heat_y2
from bhsm.interface.muon_coupled_magnetic_field_variation import corrected_magnetic_first_field_interpolation
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from evaluate_muon_corrected_profile_mean_load import bind
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve completed changing source pair')
    refs={};arrays={};records=[];angular=retained_full_q_angular_space(ROOT)
    retained={}
    for key,stem in (('target','muon_changing_closed_fermion_mean'),('mean','muon_joined_chronological_heat_mean')):
        folder=ROOT/'artifacts'/(stem+'_20261011')/'run_1';md=json.loads((folder/'result.json').read_bytes());refs.update(md['input_hashes'])
        for name in('result.json','application.npz'):
            p=folder/name;identity=sha256(p.read_bytes()).hexdigest();refs[p.relative_to(ROOT).as_posix()]=identity
            if name=='application.npz' and identity!=md['archive']['sha256']:raise ValueError('changing source/mean target changed')
        with np.load(folder/'application.npz',allow_pickle=False)as a:retained[key]={k:a[k].copy()for k in a.files}
    for side in('incoming','outgoing'):
        _,phase,a,more=bind(side);refs.update(more)
        sampler=corrected_magnetic_first_field_interpolation(a['primal_and_source'],a['phase'],a['velocity'],a['contacts'])
        values={};forms={}
        for quadrature,contour,lag in((12,24,32),(16,32,48)):
            print(json.dumps(dict(stage='changing_source_heat_assembly',side=side,quadrature=quadrature,contour=contour,lag=lag)),flush=True)
            p=changing_source_heat_polynomial(phase,angular,sampler,quadrature_order=quadrature);forms[quadrature]=p
            r=paired_source_heat_y2(p,1e-11,contour_order=contour,lag_order=lag);values[quadrature]=r
            label=side+'_quadrature_'+str(quadrature)
            for name in('n0_pencil','n1_pencil','contact','first_source'):arrays[label+'_'+name]=np.array(p[name])
            for name in('n0_Gram','n1_Gram'):arrays[label+'_'+name]=p[name]
            for name,value in r['paired_Y2'].items():arrays[label+'_paired_'+name]=value
            target=retained['target'][label+'_weak_P0']
            base_delta=float(np.linalg.norm(p['n0_pencil'][0]-target)/np.linalg.norm(target))
            if base_delta>1e-13:raise ValueError('first insertions are not on the differentiated changing target')
            mean=retained['mean'][side+'_temporal_paired_total_heat_mean_contact']
            total=r['paired_Y2']['available_source_pair']+mean
            arrays[label+'_same_background_joined_mean']=mean
            arrays[label+'_same_background_contact_and_both_insertions']=total
            row=dict(side=side,quadrature=quadrature,contour=contour,lag=lag,
                same_mean_target_base_relative_difference=base_delta,
                n0_Gram_defect=float(np.linalg.norm(p['n0_Gram']-np.eye(48))),
                numerical_accretivity_margin=r['numerical_accretivity_margin'],
                paired_contact_norm=float(np.linalg.norm(r['paired_Y2']['source_square_contact'])),
                paired_ordered_insertion_norm=float(np.linalg.norm(r['paired_Y2']['ordered_two_insertion'])),
                paired_mean_contact_trace=float(np.trace(mean)),
                paired_combined_real_trace=float(np.trace(total).real),paired_combined_imaginary_trace=float(np.trace(total).imag),
                paired_combined_norm=float(np.linalg.norm(total)),source_samples=p['records'])
            records.append(row);print(json.dumps(dict(stage='changing_same_background_pair_evaluated',**{k:v for k,v in row.items()if k!='source_samples'}),sort_keys=True),flush=True)
        records[-1]['combined_rule12_16_change_norm']=float(np.linalg.norm(values[16]['paired_Y2']['available_source_pair']-values[12]['paired_Y2']['available_source_pair']))
    for p in('src/bhsm/interface/muon_changing_closed_source_heat.py','tests/test_muon_changing_closed_source_heat.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same changing source action changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    md=dict(classification='EVALUATED_CHANGING_SAME_BACKGROUND_CONTACT_BOTH_INSERTIONS_AND_JOINED_MEAN',input_hashes=refs,records=records,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        target='same changing n0/C6 temporal8 trace and its full192 n1 magnetic source image',
        normalization='one ungraded Tr E1; source electriccharge already included; canonical normalized unitHaar; measure Ndt once',
        source_order_equation='Tr_n0 Q(P)P_AB + both ordered Duhamel source placements + same target cotangent contracted with joined birth mean',
        first_source_geometry_partial='held geometry; nonzero second mechanical response retained through all268 mean action rows',
        cutoff_probe=1e-11,statistics_factor_applied=False,
        physical_contour_or_starting_loop_complement_or_relative_completion_or_overlap_or_Pauli_completed=False,
        higher_even_Y4_or_source_analytic_alias_outward_bound_supplied=False,
        physical_a_mu=None,physical_g_mu=None,complete_observable=False,
        error_scope='binary64 same-source weak assembly and holomorphic coefficient eigensolvers; split quadrature/contour/lag changes are diagnostics; mean input, source production, Y4, native domain/completion and observable uncertainties remain distinct')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=md['classification'],archive=md['archive']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    materialize(p.parse_args().output)
