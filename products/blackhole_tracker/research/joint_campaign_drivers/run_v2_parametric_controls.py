"""Prospective v2 parametric controls, truth profile and v2.1 night prediction.

All simulated values are explicitly controls, never substitutions for observations.
One generating-state local refit per control; coverage claims remain unavailable.
"""
import sys,json,copy,gzip,time
from pathlib import Path
import numpy as np
sys.path.insert(0,'product')
from bhtracker.joint_mass_v2 import JointModel,fit_joint,profile_joint_mass
from run_v2_1_blocked_prediction import partition
from run_v2_blocked_prediction import predictive_score
P=Path(__file__).resolve().parent


def main():
 name=sys.argv[1];base=json.loads((P/name).read_text());m=JointModel(base['dataset_input'],**base['model_options']);p=base['parameters'];seed=np.array(base['best_internal_state']);rows=[];family=base['model_options']['noise_model'];firstseed=2026102300 if family=='calibrated_marginal_ou' else 2026102200
 for simulation in range(20):
  rng=np.random.default_rng(firstseed+simulation);d=copy.deepcopy(base['dataset_input']);yp=np.array(base['photometric_predictions_magnitude']);take=m.gp_indices;latent=np.empty(len(take));latent[0]=rng.normal()
  for k,delta in enumerate(np.diff(m.tp[take]),1):
   phi=np.exp(-delta/p['gp_tau_days']);latent[k]=phi*latent[k-1]+np.sqrt(-np.expm1(-2*delta/p['gp_tau_days']))*rng.normal()
  fraction=p['gp_correlation_fraction'];effective=m.sp[take]
  if family=='calibrated_marginal_ou':effective=np.sqrt((p['OGLE_error_calibration_scale']*effective)**2+p['OGLE_extra_noise_floor_mag']**2)
  noise=rng.normal(size=len(yp))*m.sp;noise[take]=effective*(np.sqrt(1-fraction)*rng.normal(size=len(take))+np.sqrt(fraction)*latent);yp+=noise
  ya=np.array(base['astrometric_predictions_NE_mas'])+(m.chol@rng.normal(size=len(m.ya))).reshape(-1,2)
  for row,y in zip(d['photometry'],yp):row['magnitude']=float(y)
  for row,y in zip(d['astrometry'],ya):row.update(north_mas=float(y[0]),east_mas=float(y[1]))
  d['metadata']['simulation_control']={'seed':firstseed+simulation,'role':'PARAMETRIC_CONTROL_NOT_MEASURED_OBSERVATIONS','generating_result':name}
  fitted=fit_joint(d,initial_states=[seed],max_nfev=600,**base['model_options'])
  profile=profile_joint_mass(d,fitted,[p['mass_msun']],mode_limit=1,max_nfev=600) if 'best_internal_state' in fitted else None
  training,held=partition(d);trained=fit_joint(training,initial_states=[seed],max_nfev=600,**base['model_options']);prediction=predictive_score(d,training,trained,held) if 'best_internal_state' in trained else None
  stem=Path(name).stem+f'_CONTROL_{simulation:02d}'
  with gzip.open(P/(stem+'.json.gz'),'wt') as f:json.dump({'full_fit':fitted,'truth_profile':profile,'training_fit':trained,'prediction':prediction},f,separators=(',',':'))
  if prediction:prediction={k:v for k,v in prediction.items() if k!='heldout_source_row_ids'}
  summary={'simulation':simulation,'seed':firstseed+simulation,'status':fitted['status'],'diagnostics':fitted.get('diagnostics'),'residual_structure':fitted.get('residual_structure'),'parameters':fitted.get('parameters'),'truth_mass_profile':None if profile is None else profile['rows'][0],'prediction':prediction};rows.append(summary)
  receipt={'schema':'bhtracker.joint_parametric_diagnostics.v2','base_result':name,'control_count':len(rows),'controls':rows,'observed_diagnostics':base['diagnostics'],'observed_residual_structure':base['residual_structure'],'validation_partition_version':'v2.1','MC_minimum_resolution':1/(len(rows)+1),'limits':'Twenty controls provide coarse diagnostics and local generating-mode calibration only; no precise interval coverage or global-mode claim. All native cadence/errors retained; generated values explicitly simulated.'}
  (P/(Path(name).stem+'_PARAMETRIC_CONTROLS20.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'simulation':simulation,'status':fitted['status'],'Q':fitted.get('diagnostics',{}).get('photometry_innovation_chi2'),'failed_bins':fitted.get('residual_structure',{}).get('failed_bins'),'truth_delta':None if profile is None else profile['rows'][0]['delta_deviance'],'prediction_Q':None if prediction is None else prediction['conditional_photometric_Q']}),flush=True)

if __name__=='__main__':main()
