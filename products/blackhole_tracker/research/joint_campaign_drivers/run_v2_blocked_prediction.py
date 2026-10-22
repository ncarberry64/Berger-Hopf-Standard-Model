"""Prospective v2 whole-night prediction driver. Source science is immutable.

Uses training-only fit parameters. Isolates PHOTOMETRIC Q and logdet to avoid
reprofiled angular-nuisance contributions. No candidate is selected by mass.
"""
import sys,json,copy,math
from pathlib import Path
import numpy as np
from scipy.stats import chi2
sys.path.insert(0,'product')
from bhtracker.joint_mass_v2 import JointData,JointModel,fit_joint
P=Path(__file__).resolve().parent


def retained_modes(result,limit=8):
    modes=[]
    for row in sorted([r for r in result['all_starts'] if r.get('converged')],key=lambda r:r['objective_deviance']):
        x=np.asarray(row['internal_state']);distances=[]
        for previous in modes:
            delta=(x-previous)/np.maximum(1,np.abs(previous));delta[3]=np.arctan2(np.sin(x[3]-previous[3]),np.cos(x[3]-previous[3]));distances.append(np.linalg.norm(delta))
        if not any(distance<.03 for distance in distances):modes.append(x)
        if len(modes)>=limit:break
    return modes


def partition(document):
    training=copy.deepcopy(document);held=[];kept=[]
    for row in training['photometry']:
        if row['instrument']=='OGLE' and int(np.floor(row['time_jd_tdb']-.5))%5==0:held.append(row)
        else:kept.append(row)
    training['photometry']=kept
    training['metadata']['blocked_validation']={'rule':'OGLE whole observer-TDB nights floor(JD-.5), mod5=0 heldout; HST retained','heldout_source_row_ids':[r['source_row_id'] for r in held],'role':'TRAINING_ONLY_PHOTOMETRY_PARTITION; rawfiles/allnativeOGLErows retained'}
    return training,held


def predictive_score(full,training,trained,held):
    # All and training evaluate the IDENTICAL frozen training-fitted state and
    # same covariance hyperparameters. Angular results deliberately excluded.
    options=trained['model_options'];x=np.asarray(trained['best_internal_state'])
    all_eval=JointModel(full,**options).evaluate(x,details=True);train_eval=JointModel(training,**options).evaluate(x,details=True)
    q=all_eval['photometric_innovation_chi2']-train_eval['photometric_innovation_chi2']
    if q < -1e-6:raise ValueError('conditional Gaussian quadratic must be nonnegative')
    logdet=all_eval['GP_log_determinant_ratio_to_native_diagonal']-train_eval['GP_log_determinant_ratio_to_native_diagonal']
    n=len(held);native_constant=2*sum(math.log(row['magnitude_error']) for row in held)
    probability=float(min(1.,2*min(chi2.cdf(q,n),chi2.sf(q,n))))
    return {'schema':'bhtracker.joint_blocked_predictive_score.v1','training_input_sha256':JointData(training).sha256,'full_input_sha256':JointData(full).sha256,'heldout_count':n,'heldout_source_row_ids':[r['source_row_id'] for r in held],
       'conditional_photometric_Q':q,'conditional_logdet_relative_to_native_D':logdet,'conditional_relative_Gaussian_deviance':q+logdet,'conditional_negative2_log_predictive_density':q+logdet+native_constant+n*math.log(2*math.pi),'conditional_Q_two_sided_probability_approximate':probability,'approximate_screen_passed':probability>=.01,
       'evaluation_state':'IDENTICAL_TRAINING_ONLY_FITTED_NONLINEAR_AND_CALIBRATION_PARAMETERS','astrometric_objective_excluded':True,'training_fitted_parameters':trained['parameters'],'qualification':'Conditional stationary Gaussian score, not evidence or calibrated confidence. Mean/noise parameter uncertainty approximated; compare matching parametric/refitted controls.'}


def main():
    name=sys.argv[1];baseline=json.loads((P/name).read_text());training,held=partition(baseline['dataset_input']);modes=retained_modes(baseline)
    trained=fit_joint(training,initial_states=modes,max_nfev=600,**baseline['model_options']);output=P/(Path(name).stem+'_BLOCKED_TRAIN.json');output.write_text(json.dumps(trained,indent=2)+'\n')
    if 'best_internal_state' not in trained:score={'status':'TRAINING_SEARCH_UNRESOLVED','accepted':False}
    else:score=predictive_score(baseline['dataset_input'],training,trained,held)
    (P/(Path(name).stem+'_BLOCKED_PREDICTION.json')).write_text(json.dumps(score,indent=2)+'\n');print(json.dumps(score))

if __name__=='__main__':main()
