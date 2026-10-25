"""Compact complete saved endpoints, excluding native observations/predictions.

No scientific provider, predictor, density, optimizer, RNG or network call.
The original full audit artifacts remain external and unmodified.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path

def pin(p):
    raw=p.read_bytes();return {'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,obj):
    with p.open('x',encoding='utf-8')as s:json.dump(obj,s,indent=2,allow_nan=False);s.write('\n')
def descriptive(values):
    values=list(values);n=len(values);mean=math.fsum(values)/n
    return {'count':n,'mean':mean,'rms':math.sqrt(math.fsum(v*v for v in values)/n),'population_sd':math.sqrt(math.fsum((v-mean)**2 for v in values)/n),'maximum_absolute':max(map(abs,values)),'calibrated_p_value':None}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    directories=[args.root/f'{prefix}_ST6_SEEING_point_{version}'for version in('v1','v3')for prefix in('authentic2023','actual_cadence')]
    paths=[Path(__file__).resolve()]
    for directory in directories:
        if load(directory/'SUPERVISOR_TERMINAL_v1.json')['execution_complete']is not True:raise ValueError('Original completed supervisor required')
        paths+=sorted(directory.glob('*.json'))+[directory/'ALL_EVALUATIONS_v1.jsonl']
        freeze=load(directory/'freeze.original.json');paths += [Path(r['path'])for r in freeze['source_files']]+[Path(freeze['input']['path'])]
    paths=sorted(set(paths));before=[pin(p)for p in paths];args.output.mkdir(exist_ok=False)
    save(args.output/'INPUT_BINDING_BEFORE_v1.json',before)
    endpoint_rows=[];mode_records=[];campaigns=[]
    for directory in directories:
        outcome=load(directory/'POINT_OUTCOME_v1.json');supervisor=load(directory/'SUPERVISOR_TERMINAL_v1.json');domain=load(directory/'SEEDS_AND_DOMAIN_v1.json');ledger=load(directory/'ALL16_FINAL_LEDGER_v1.json')
        if [r['start_index']for r in ledger]!=list(range(16)):raise ValueError('All16 final identities required')
        if outcome['accepted_mass_interval']is not None or outcome['known_black_hole_recovery_accepted']is not False:raise ValueError('Unaccepted outcome contract differs')
        names=domain['parameter_names'];rows=[];modes=[];selected=outcome['selected']
        for start in outcome['all16_starts']:
            k=start['start_index'];phases=[]
            for summary in start['phases']:
                phase=summary['phase'];p=load(directory/f'start_{k:02d}_{phase}.json')
                if p['start_index']!=k or p['phase']!=phase:raise ValueError('Endpoint identity differs')
                record={'campaign':directory.name,'purpose':outcome['purpose'],'start_index':k,'phase':phase,'status':p['status'],'numerically_eligible':p.get('numerically_eligible',False)}
                if p['status']=='RETURNED':
                    detail=p['detail'];gradient=detail['gradient'];state=p['state'];projected=[]
                    for j,g in enumerate(gradient):
                        g*=domain['scales'][j]
                        if j!=3 and((state[j]==domain['lower'][j]and g>0)or(state[j]==domain['upper'][j]and g<0)):g=0.
                        projected.append(g)
                    score=max(map(abs,projected))
                    if abs(score-p['full_scaled_projected_score'])>1e-10*max(1.,score):raise ValueError('Score arithmetic differs')
                    top=sorted(range(len(names)),key=lambda j:-abs(projected[j]))[:5]
                    trust=p.get('gradient_trust_polish')or{};trace=trust.get('trace')or[{}]
                    record.update(deviance=p['deviance'],full_scaled_projected_score=score,optimizer_success=p['optimizer_success'],message=p['message'],linear_rank=detail['linear_profile_rank'],linear_identified=detail['linear_profile_identified'],linear_KKT_score=detail['linear_profile_projected_score'],feature_knot_count=len(detail['feature_knot_source_ids']),analysis_contacts=p['exact_nonlinear_analysis_contacts'],linear_contacts=p['linear_analysis_contacts'],trust_status=trust.get('status'),trust_failure_reason=trace[-1].get('unresolved_reason'),top_gradient_components=[{'name':names[j],'projected_scaled_gradient':projected[j]}for j in top],conditional_mass_msun=detail['parameters']['conditional_mass_msun'],conditional_parameters=detail['parameters'],nonlinear_state=dict(zip(names,state)),physical_acceptance=False)
                else:record.update(error_type=p.get('error_type'),error=p.get('error'))
                rows.append(record);endpoint_rows.append(record);phases.append(record)
            modes.append({'campaign':directory.name,'start_index':k,'original_seed':dict(zip(names,start['seed'])),'chart_center_angle_rad':start.get('chart_center_angle_rad'),'has_eligible_endpoint':start['has_eligible_endpoint'],'all_phases':phases})
        mode_records+=modes
        selected_compact=None
        if selected:
            detail=selected['detail'];selected_compact={'start_index':selected['start_index'],'phase':selected['phase'],'conditional_parameters':detail['parameters'],'deviance':selected['deviance'],'full_scaled_projected_score':selected['full_scaled_projected_score'],'analysis_contacts':selected['exact_nonlinear_analysis_contacts'],'linear_contacts':selected['linear_analysis_contacts'],'descriptive_only':{'OGLE_unit_variance_Student_innovations':descriptive(detail['OGLE_raw_student_innovations']),'HST_angular_standardized_residuals':descriptive(detail['astrometric_whitened_residuals']),'full_photo_residual_magnitudes':descriptive(detail['photometric_residuals_magnitude'])},'parameters_are_conditional_fitted_values_not_accepted_measurements':True}
        campaigns.append({'campaign':directory.name,'purpose':outcome['purpose'],'numerical_version':'v3_periodic_trust'if directory.name.endswith('_v3')else'v2_original','status':outcome['status'],'all16_starts_retained':len(modes)==16,'eligible_start_indices':[r['start_index']for r in modes if r['has_eligible_endpoint']],'eligible_endpoint_count':outcome['eligible_endpoints'],'endpoint_count':len(rows),'endpoint_status_counts':dict(collections.Counter(r['status']for r in rows)),'trust_status_counts':dict(collections.Counter(r.get('trust_status')for r in rows if r.get('trust_status'))),'trust_failure_counts':dict(collections.Counter(r.get('trust_failure_reason')for r in rows if r.get('trust_failure_reason'))),'all_feature_knot_counts':sum(r.get('feature_knot_count',0)for r in rows),'selected':selected_compact,'elapsed_seconds':supervisor['elapsed_seconds'],'original_model_call_counts':outcome['model_call_counts'],'journal_audit_failure':outcome['journal_audit_failure'],'known_lower_trials':len(outcome['known_lower_feasible_trials']),'accepted_mass_interval':None,'known_BH_recovery_accepted':False,'adequacy':'NOT_REFIT_CALIBRATED','coverage':'NOT_CALIBRATED','original_outcome_pin':pin(directory/'POINT_OUTCOME_v1.json')})
    save(args.output/'ALL64_START_MODES_v1.json',{'schema':'bhsm.known2023.compact_modes.v1','mode_count':len(mode_records),'endpoint_count':len(endpoint_rows),'modes':mode_records,'original_observations_or_predictions_included':False})
    fields=['campaign','purpose','start_index','phase','status','numerically_eligible','deviance','full_scaled_projected_score','optimizer_success','linear_rank','linear_identified','linear_KKT_score','feature_knot_count','conditional_mass_msun','trust_status','trust_failure_reason','analysis_contacts','linear_contacts','top_gradient_components']
    with(args.output/'ALL224_ENDPOINTS_v1.csv').open('x',encoding='utf-8',newline='')as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in endpoint_rows:writer.writerow({k:json.dumps(row.get(k),separators=(',',':'))if isinstance(row.get(k),(list,dict))else row.get(k)for k in fields})
    save(args.output/'CAMPAIGN_COMPARISON_v1.json',{'schema':'bhsm.known2023.compact_comparison.v1','campaigns':campaigns,'publication_hold':True,'new_black_hole_discoveries':0,'accepted_known_BH_recoveries':0,'original_observations_or_predictions_included':False,'BHSM':'One common Einstein/GHY optical exterior, interpreted as surface topography/envelopment and counted once. Conditional geometry is distinct from BH identity and microscopic interface dynamics.'})
    after=[pin(p)for p in paths]
    receipt={'schema':'bhsm.known2023.compact_saved_evidence_receipt.v1','source_and_artifacts_unchanged':before==after,'bound_input_count':len(paths),'campaign_count':len(campaigns),'mode_count':len(mode_records),'endpoint_count':len(endpoint_rows),'all_outcomes_preserved':len(mode_records)==64 and len(endpoint_rows)==224,'new_provider_model_predictor_density_optimizer_rng_network_calls':0,'original_observations_predictions_or_row_residual_arrays_included':False,'accepted_known_BH_recovery':False,'role':'Author saved-output arithmetic/export, not independent scientific validation','input_pins':before,'outputs':[pin(p)for p in sorted(args.output.iterdir())if p.is_file()]}
    save(args.output/'COMPACT_EVIDENCE_RECEIPT_v1.json',receipt);print(json.dumps(pin(args.output/'COMPACT_EVIDENCE_RECEIPT_v1.json')))

if __name__=='__main__':main()
