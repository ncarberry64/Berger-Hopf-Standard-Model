"""Build compact public joint audit from frozen external outputs; never fits.

Usage: python build_compact_audit.py --results-root PATH
The output is this script's directory. Raw inputs and large fitted vectors are
represented by their exact external file hashes, not copied into Git.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import beta

HERE=Path(__file__).resolve().parent
PREFIXES=['JOINT_V2_G0_DIAGONAL16','JOINT_V2_G1_MARGINAL16','JOINT_V2_G2_CALIBRATED16']

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write_json(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def csv_table(path,rows):
    if not rows:return
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--results-root',type=Path,required=True);parser.add_argument('--formal-product-revision',help='Final full SHA of formal BHSM product source; supplied by release coordinator');args=parser.parse_args();root=args.results_root.resolve()
    if args.formal_product_revision and not re.fullmatch('[0-9a-f]{40}',args.formal_product_revision):raise ValueError('Full lowercase40-digit formal Git SHA required')
    records=[];bins=[];full=[];external={}
    for label,prefix in zip(['G0','G1','G2'],PREFIXES):
        path=root/(prefix+'_CONTINUED.json');result=read(path);full.append(result);external[path.name]={'sha256':sha(path),'bytes':path.stat().st_size,'bundled':False,'role':'full conditional fit, regenerable from source pack'}
        p=result['parameters'];d=result['diagnostics'];structure=result['residual_structure']
        records.append({'candidate':label,'status':result['status'],'accepted_mass':False,'accepted_BH':False,'conditional_mass_msun':p['mass_msun'],'conditional_theta_E_mas':p['theta_E_mas'],'conditional_pi_E':p['pi_E'],'conditional_tE_days':p['tE_days'],'photometric_Q':d['photometry_innovation_chi2'],'photometric_dof_approximate':d['photometry_dof_approximate'],'angular_Q':d['astrometry_chi2'],'angular_dof_conservative':d['astrometry_dof_conservative'],'innovation_lag1':d['OGLE_sorted_innovation_lag1'],'Ljung_Box10_p_approximate':structure['Ljung_Box10_tail_probability_approximate'],'failed_structure_bins':len(structure['failed_bins']),'converged_starts':result['numerical_convergence']['converged_starts'],'attempted_starts':result['numerical_convergence']['attempted_starts'],'active_nonlinear_bounds':';'.join(result['nonlinear_active_bounds'])})
        for b in structure['bins']:
            bins.append({'candidate':label,**b,'failed_declared_bin_screen':b['bin'] in structure['failed_bins']})
    csv_table(HERE/'baseline_summary.csv',records);write_json(HERE/'baseline_summary.json',records);csv_table(HERE/'residual_bin_summary.csv',bins)

    predictions=[];original_predictions=[];controls=[];profiles=[];refined_support=[]
    for label,prefix in zip(['G1','G2'],PREFIXES[1:]):
        continued=root/(prefix+'_CONTINUED_V2_1_BLOCKED_PREDICTION.json')
        path=continued if continued.exists() else root/(prefix+'_V2_1_BLOCKED_PREDICTION.json')
        score=read(path);external[path.name]={'sha256':sha(path),'bytes':path.stat().st_size,'bundled':False,'role':'corrected whole-night conditional score'}
        predictions.append({'candidate':label,'source_file':path.name,'continued_baseline_modes':continued.exists(),'heldout_count':score['heldout_count'],'conditional_Q':score['conditional_photometric_Q'],'conditional_logdet_relative_native':score['conditional_logdet_relative_to_native_D'],'relative_Gaussian_deviance':score['conditional_relative_Gaussian_deviance'],'two_sided_Q_p_approximate':score['conditional_Q_two_sided_probability_approximate'],'approximate_prediction_screen_passed':score['approximate_screen_passed'],'baseline_adequate':False,'accepted_mass':False})
        original_path=root/(prefix+'_CONTINUED_BLOCKED_PREDICTION.json')
        if original_path.exists():
            original=read(original_path);external[original_path.name]={'sha256':sha(original_path),'bytes':original_path.stat().st_size,'bundled':False,'role':'original UTC-boundary conditional diagnostic; splits observing nights'}
            original_predictions.append({'candidate':label,'source_file':original_path.name,'heldout_count':original['heldout_count'],'conditional_Q':original['conditional_photometric_Q'],'relative_Gaussian_deviance':original['conditional_relative_Gaussian_deviance'],'two_sided_Q_p_approximate':original['conditional_Q_two_sided_probability_approximate'],'valid_whole_night_validation':False,'accepted_mass':False})
        control_path=root/(prefix+'_CONTINUED_PARAMETRIC_CONTROLS20.json')
        if control_path.exists():
            control=read(control_path);external[control_path.name]={'sha256':sha(control_path),'bytes':control_path.stat().st_size,'bundled':False,'role':'summary of generated/refitted controls; large sample files external'}
            rows=control['controls'];controls.append({'candidate':label,'control_count':control['control_count'],'required_control_count':20,'complete':control['control_count']==20,'minimum_MC_tail_resolution':1/(control['control_count']+1),'control_failed_structure_counts':[len(r.get('residual_structure',{}).get('failed_bins',[])) for r in rows],'control_lag1':[r.get('diagnostics',{}).get('OGLE_sorted_innovation_lag1') for r in rows],'control_ljung_box_p':[r.get('residual_structure',{}).get('Ljung_Box10_tail_probability_approximate') for r in rows],'control_photometric_Q':[r.get('diagnostics',{}).get('photometry_innovation_chi2') for r in rows],'control_statuses':[r['status'] for r in rows],'truth_profile_statuses':[None if r.get('truth_mass_profile') is None else r['truth_mass_profile']['status'] for r in rows],'truth_profile_delta':[None if r.get('truth_mass_profile') is None else r['truth_mass_profile']['delta_deviance'] for r in rows],'prediction_Q':[None if r.get('prediction') is None else r['prediction']['conditional_photometric_Q'] for r in rows],'qualification':control['limits']})
        profile_path=root/('JOINT_V2_'+label+'_MASS_PROFILE31.json')
        parallel_path=root/('JOINT_V2_'+label+'_MASS_PROFILE31_PARALLEL.json')
        if not profile_path.exists() and parallel_path.exists():profile_path=parallel_path
        if profile_path.exists():
            profile=read(profile_path);external[profile_path.name]={'sha256':sha(profile_path),'bytes':profile_path.stat().st_size,'bundled':False,'role':'conditional nuisance-profile grid; no accepted confidence interval'}
            for row in profile['rows']:
                profiles.append({'candidate':label,'mass_msun':row['mass_msun'],'status':row['status'],'delta_deviance':row.get('delta_deviance'),'local_profile_interval_eligible':row.get('interval_eligible',False),'baseline_adequate':False,'accepted_physical_interval':False,'active_nonlinear_bounds':';'.join(row.get('nonlinear_active_bounds',[])),'active_linear_bounds':';'.join(row.get('linear_active_bounds',[]))})
        refined_path=root/('JOINT_V2_'+label+'_MASS_REFINED_SUPPORT.json')
        if refined_path.exists():
            refined=read(refined_path);external[refined_path.name]={'sha256':sha(refined_path),'bytes':refined_path.stat().st_size,'bundled':False,'role':'conditional crossing refinement; no accepted mass interval'}
            assert refined['coverage_claim'] is False and refined['mass_acceptance'] is False
            refined_support.append({'candidate':label,'source_file':refined_path.name,'row_count':len(refined['rows']),'crossings':refined['crossings'],'levels':refined['levels'],'coverage_claim':False,'mass_acceptance':False})
        sample_paths=sorted(root.glob(prefix+'_CONTINUED_CONTROL_*.json.gz'))
        if controls and controls[-1]['candidate']==label:
            controls[-1]['full_generated_sample_files_present']=len(sample_paths)
            controls[-1]['complete']=controls[-1]['complete'] and len(sample_paths)==20
        for sample_path in sample_paths:
            external[sample_path.name]={'sha256':sha(sample_path),'bytes':sample_path.stat().st_size,'bundled':False,'role':'full generated/refitted control sample; reproducible from frozen seed'}
    for control in controls:
        n=control['control_count'];k=sum(status=='JOINT_MODEL_NOT_REJECTED' for status in control['control_statuses'])
        control['overall_control_pass_fraction_exact_binomial95_interval']=[0. if k==0 else float(beta.ppf(.025,k,n-k+1)),1. if k==n else float(beta.ppf(.975,k+1,n-k))]
        control['binomial_interval_scope']='Local generating-mode control pass probability, not mass interval coverage or real-system truth probability.'
    csv_table(HERE/'prediction_summary.csv',predictions);csv_table(HERE/'original_UTC_prediction_diagnostic.csv',original_predictions);write_json(HERE/'control_summary.json',controls);csv_table(HERE/'conditional_mass_profile.csv',profiles);write_json(HERE/'conditional_refined_support.json',refined_support)

    fig,axes=plt.subplots(2,2,figsize=(9,6.7),layout='constrained');colors=['#245985','#c76d16','#a72e37']
    for label,result,color in zip(['G0','G1','G2'],full,colors):
        structure=result['residual_structure'];axes[0,0].plot(range(1,11),structure['OGLE_lags1_to10'],'.-',label=label,color=color)
        for ax,token in [(axes[0,1],'Julian_year_'),(axes[1,0],'native_sigma_quartile_'),(axes[1,1],'native_seeing_quartile_')]:
            rows=[r for r in structure['bins'] if r['bin'].startswith(token)]
            ax.plot([int(r['bin'].split('_')[-1]) for r in rows],[r['Q_per_row'] for r in rows],'.-',label=label,color=color)
    axes[0,0].axhline(0,color='.6',lw=.7);axes[0,0].set(xlabel='Observation-order lag (irregular cadence)',ylabel='Innovation correlation',title='Serial structure');axes[0,0].legend(frameon=False,ncol=3)
    for ax in [axes[0,1],axes[1,0],axes[1,1]]:ax.axhline(1,color='.6',lw=.7);ax.set_ylabel('Innovation Q / observations')
    axes[0,1].set(xlabel='Julian season',title='Season-dependent scatter');axes[0,1].tick_params(axis='x',rotation=30)
    axes[1,0].set(xlabel='Native-error quantile-cut bin (unequal counts)',title='Reported-error structure',xticks=[1,2,3,4]);axes[1,1].set(xlabel='Native-seeing quantile-cut bin',title='Seeing-dependent scatter',xticks=[1,2,3,4])
    for ax in axes.flat:ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.18)
    fig.savefig(HERE/'joint_noise_diagnostics.png',dpi=180,metadata={'Software':'BHSM compact joint audit'});plt.close(fig)

    copies={
      'JOINT_PROTOCOL_V2_FREEZE.json':'protocol/JOINT_PROTOCOL_V2_FREEZE.json',
      'JOINT_VALIDATION_PARTITION_V2_1_FREEZE.json':'protocol/JOINT_VALIDATION_PARTITION_V2_1_FREEZE.json',
      'JOINT_MASS_BENCHMARK_PROTOCOL_V2.md':'protocol/JOINT_MASS_BENCHMARK_PROTOCOL_V2.md',
      'JOINT_V2_INDEPENDENT_FREEZE_REVIEW.json':'review/JOINT_V2_INDEPENDENT_FREEZE_REVIEW.json',
      'JOINT_V2_1_PARTITION_INDEPENDENT_REVIEW.json':'review/JOINT_V2_1_PARTITION_INDEPENDENT_REVIEW.json',
      'JOINT_V2_1_PREDICTION_DRIVER_INDEPENDENT_REVIEW.json':'review/JOINT_V2_1_PREDICTION_DRIVER_INDEPENDENT_REVIEW.json',
      'JOINT_V2_INDEPENDENT_MEASURED_OUTCOME_REVIEW.json':'review/JOINT_V2_INDEPENDENT_MEASURED_OUTCOME_REVIEW.json',
      'JOINT_V1_NOISE_REVIEW_AND_PROSPECTIVE_COVARIANCE.json':'review/JOINT_V1_NOISE_REVIEW_AND_PROSPECTIVE_COVARIANCE.json',
      'PORTABLE_WRAPPER_INDEPENDENT_REVIEW.json':'review/PORTABLE_WRAPPER_INDEPENDENT_REVIEW.json',
      'PORTABLE_WRAPPER_FORMAL_LAYOUT_VALIDATION.json':'review/PORTABLE_WRAPPER_FORMAL_LAYOUT_VALIDATION.json',
      'PORTABLE_2023_SOURCEPACK_VERIFICATION.json':'review/PORTABLE_2023_SOURCEPACK_VERIFICATION.json',
      'MANUAL_CALIBRATION_DATA_REQUEST_TEMPLATE.txt':'MANUAL_CALIBRATION_DATA_REQUEST_TEMPLATE.txt',
      'JOINT_BENCHMARK_PLAIN_LANGUAGE_RESULT.txt':'PLAIN_LANGUAGE_RESULT.txt',
      'portable_2023_benchmark_v1/ACQUISITION_MANIFEST.json':'sourcepack/ACQUISITION_MANIFEST.json',
      'portable_2023_benchmark_v1/CITATIONS_AND_RIGHTS.md':'sourcepack/CITATIONS_AND_RIGHTS.md',
      'portable_2023_benchmark_v1/RIGHTS_EVIDENCE.json':'sourcepack/RIGHTS_EVIDENCE.json',
      'run_v2_parallel_profile.py':'drivers/run_v2_parallel_profile.py',
      'JOINT_V2_G2_SERIAL_PARALLEL_COMPARISON.json':'review/JOINT_V2_G2_SERIAL_PARALLEL_COMPARISON.json',
      'JOINT_V2_G2_PARALLEL_OVERLAP_RECEIPT.json':'review/JOINT_V2_G2_PARALLEL_OVERLAP_RECEIPT.json',
      'ROBUST_ESTIMATOR_FEASIBILITY_ASSESSMENT.txt':'review/ROBUST_ESTIMATOR_FEASIBILITY_ASSESSMENT.txt',
      'SAVED_G0_CLUSTER_ESTIMATOR_FEASIBILITY.json':'review/SAVED_G0_CLUSTER_ESTIMATOR_FEASIBILITY.json',
    }
    for source,destination in copies.items():
        path=HERE/destination;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/source,path)
    dispatch=root/'JOINT_V2_G2_MASS_PROFILE31_PARALLEL/dispatch.json'
    if dispatch.exists():shutil.copyfile(dispatch,HERE/'review/G2_PARALLEL_DISPATCH.json')
    for optional_name in ['JOINT_V2_ACCEPTANCE_RECEIPT.json','JOINT_V2_FINAL_ARTIFACT_INVENTORY.json','JOINT_V2_G2_PARALLEL_AUXILIARY_STOP.json']:
        if (root/optional_name).exists():shutil.copyfile(root/optional_name,HERE/'review'/optional_name)
    driver_names=['run_v2_blocked_prediction.py','run_v2_1_blocked_prediction.py','run_v2_parametric_controls.py','continue_v2.py','refine_v2_profiles.py']
    driver_hashes={name:sha(root/name) for name in driver_names if (root/name).exists()}
    manifest={'schema':'bhtracker.compact_joint_public_audit.v1','framework':'BHSM','formal_reviewer_repository':'https://github.com/ncarberry64/Berger-Hopf-Standard-Model','formal_product_path':'products/blackhole_tracker/','formal_product_revision':{'state':'PENDING_PARENT_FINAL_RELEASE_PIN','must_resolve_before_final_release':True},'scientific_development_freeze':'5bb94198565fb25414f1f05908c00d49838c4b73','scientific_source_sha256':read(root/'JOINT_PROTOCOL_V2_FREEZE.json')['files']['product/bhtracker/joint_mass_v2.py'],'canonical_input_sha256':'d4fc2bfc9320c7eab8a33b93517f68f035a5d498ffb35ff548a638648143af96','sourcepack':{'filename':'BHSM_OB110462_2023_SourcePack_v1.zip','sha256':sha(root/'BHSM_OB110462_2023_SourcePack_v1.zip'),'bytes':(root/'BHSM_OB110462_2023_SourcePack_v1.zip').stat().st_size,'release_location_state':'PENDING_PARENT_RELEASE_ASSET_LINK','inventory':'sourcepack/ACQUISITION_MANIFEST.json','rights':'sourcepack/CITATIONS_AND_RIGHTS.md'},'driver_hashes':driver_hashes,'external_result_files':external,'conditional_mass_acceptance':False,'BH_identification_acceptance':False,'candidate_stop_reason':'All frozen candidates fail residual adequacy;G2 also numerical tau cap. Passing plug-in prediction does not override failure.','required_control_outputs_complete':len(controls)==2 and all(r['complete'] for r in controls),'profile_grid_rows_present':len(profiles),'scope':'Small public derived tables/figure/protocols/reviews. No full fitted-vector or control-sample copies. Native source bytes available through attributed portable pack; original frozen100 pilot remains separate.','public_files':{str(f.relative_to(HERE)).replace('\\','/'):{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(HERE.rglob('*')) if f.is_file() and f.name!='PROVENANCE_MANIFEST.json'}}
    manifest['figure_environment']={'matplotlib':matplotlib.__version__}
    manifest['required_profile_outputs_complete']=len(profiles)==62
    manifest['required_prediction_continued_modes_complete']=all(row['continued_baseline_modes'] for row in predictions)
    manifest['required_original_partition_diagnostics_present']=len(original_predictions)==2
    manifest['required_refined_support_outputs_complete']=len(refined_support)==2
    manifest['fixed_campaign_acceptance_receipt_present']=(HERE/'review/JOINT_V2_ACCEPTANCE_RECEIPT.json').exists()
    manifest['sourcepack'].update({'formal_repository_path':'museum/public/research/blackhole-tracker/BHSM_OB110462_2023_SourcePack_v1.zip','planned_Pages_URL':'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/research/blackhole-tracker/BHSM_OB110462_2023_SourcePack_v1.zip','publication_status':'DRAFT_NOT_YET_PUBLISHED; release coordinator verifies after authorized publication'})
    manifest['portable_reproduction']={'formal_repository_wrapper':'products/blackhole_tracker/research/reproduce_joint_campaign.py','instructions':'products/blackhole_tracker/research/README_JOINT_REPRODUCTION.md','science_files_unchanged':True}
    if args.formal_product_revision:manifest['formal_product_revision']={'sha':args.formal_product_revision,'url':'https://github.com/ncarberry64/Berger-Hopf-Standard-Model/tree/'+args.formal_product_revision+'/products/blackhole_tracker/','must_resolve_before_final_release':False}
    write_json(HERE/'PROVENANCE_MANIFEST.json',manifest)
    print(json.dumps({'baseline_rows':len(records),'prediction_rows':len(predictions),'profile_rows':len(profiles),'controls_complete':manifest['required_control_outputs_complete'],'output':str(HERE)}))

if __name__=='__main__':main()
