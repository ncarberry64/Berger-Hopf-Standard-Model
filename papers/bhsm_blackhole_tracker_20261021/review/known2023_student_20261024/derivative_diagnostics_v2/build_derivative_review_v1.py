"""Portable compact coarse/fine comparison from exact saved derived outcomes."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path

EXPECTED={'coarse':'730b2c809aaaadad64959491461158dcb4307b74bf2a9ce6c1bfbe2585a9c165','fine':'47c7e647c7620d379966cc3b186865ba28bf4130d97c18dc46821841f58e890f'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path,kind):
    raw=path.read_bytes();raw=gzip.decompress(raw)if path.name.endswith('.gz')else raw
    if sha(raw)!=EXPECTED[kind]:raise ValueError('Pinned derived outcome differs: '+kind)
    return raw,json.loads(raw)
def csv_write(path,fields,rows):
    with path.open('x',encoding='utf-8',newline='')as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        writer.writerows({k:json.dumps(r.get(k),separators=(',',':'))if isinstance(r.get(k),(dict,list))else r.get(k)for k in fields}for r in rows)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--coarse',type=Path,required=True);parser.add_argument('--fine',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    rawc,c=load(args.coarse,'coarse');rawf,f=load(args.fine,'fine')
    key=lambda s:(s['purpose'],s['start_index'])
    if len(c['states'])!=32 or list(map(key,c['states']))!=list(map(key,f['states'])):raise ValueError('Same complete32-state roster required')
    args.output.mkdir(exist_ok=False);columns=[];levels=[];rounding=[];states=[]
    for version,outcome in [('coarse',c),('fine',f)]:
        for s in outcome['states']:
            for level in s['levels']:
                values=level['symmetric_free_eigenvalues'];levels.append({'version':version,'purpose':s['purpose'],'start_index':s['start_index'],'step':level['scaled_step'],'minimum_free_eigenvalue':min(values),'maximum_free_eigenvalue':max(values),'geometry5_minimum_eigenvalue':min(level['symmetric_geometry5_eigenvalues']),'skew_infinity_norm':level['skew_infinity_norm'],'max_relative_gradient_difference':level['maximum_relative_gradient_discrepancy'],'profile_faces_same':level['same_profile_faces'],'clip_regime_same':level['same_clip_regime']})
                for col in level['columns']:
                    columns.append({'version':version,'purpose':s['purpose'],'start_index':s['start_index'],'step':level['scaled_step'],**col})
                    if col['coordinate']==0 and 'decoded_t0_JD_step_diagnostic'in col:
                        rounding.append({'purpose':s['purpose'],'start_index':s['start_index'],'step':level['scaled_step'],**col['decoded_t0_JD_step_diagnostic']})
    for old,new in zip(c['states'],f['states']):
        oldsign=[min(l['symmetric_free_eigenvalues'])<0 for l in old['levels']];newsign=[min(l['symmetric_free_eigenvalues'])<0 for l in new['levels']]
        states.append({'purpose':new['purpose'],'start_index':new['start_index'],'coarse_negative_signs':oldsign,'fine_negative_signs':newsign,'coarse_all_positive':not any(oldsign),'fine_all_positive':not any(newsign),'fine_all_negative':all(newsign),'all_profile_faces_same':all(l['same_profile_faces']for l in old['levels']+new['levels']),'all_clip_regimes_same':all(l['same_clip_regime']for l in old['levels']+new['levels'])})
    csv_write(args.output/'ALL256_HESSIAN_LEVELS_v1.csv',list(levels[0]),levels)
    fields=['version','purpose','start_index','step','coordinate','parameter','status','finite_difference_deviance_gradient','analytic_scaled_gradient','absolute_gradient_difference','relative_gradient_difference','same_profile_faces','same_clip_regime','sample_knot_count','stencil']
    csv_write(args.output/'ALL5888_DERIVATIVE_COLUMNS_v1.csv',fields,columns)
    rfields=['purpose','start_index','step','numeric_origin_jd_tdb','baseline_decoded_jd','probe_decoded_jds','signed_offset_steps_days','signed_decoded_JD_steps_days','decoded_to_offset_step_ratios','decoded_JD_ulp_days','any_decoded_step_erased','stencil_uses_unchanged_offset_steps']
    csv_write(args.output/'ALL128_FINE_T0_ROUNDING_LEVELS_v1.csv',rfields,rounding)
    report={'schema':'bhsm.known2023.compact_derivative_comparison.v1','state_count':32,'paired_states':states,'coarse_normalized_model_calls':c['model_calls'],'fine_normalized_model_calls':f['model_calls'],'new_calls_during_export':0,'fit_or_rng_calls_in_diagnostics':0,'outcome_raw_sha256':EXPECTED,'observations_predictions_or_observation_row_residual_arrays_included':False,'accepted_mass_interval':None,'known_BH_recovery_accepted':False,'publication_hold':True,'qualification':'All floating curvature/gradient results retained at all fixed steps. These do not certify exact Hessian signs, a physical covariance, model adequacy or mass coverage.'}
    with(args.output/'COMPARISON32_STATES_v1.json').open('x',encoding='utf-8')as s:json.dump(report,s,indent=2);s.write('\n')
    for name,raw in [('COARSE_DERIVED_OUTCOME_v1.json.gz',rawc),('FINE_DERIVED_OUTCOME_v2.json.gz',rawf)]:
        with(args.output/name).open('xb')as s:s.write(gzip.compress(raw,compresslevel=9,mtime=0))
    print(json.dumps({'states':len(states),'level_rows':len(levels),'column_rows':len(columns),'rounding_rows':len(rounding),'new_model_calls':0}))

if __name__=='__main__':main()
