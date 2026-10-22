"""Prospective validation-partition correction v2.1, before predictive outcomes.

Scientific likelihood/baseline/profiles remain frozen. The v2 UTC-boundary
conditional score is retained separately and is not leak-free nightly validation.
"""
import sys,json,copy,hashlib,datetime
from pathlib import Path
import numpy as np
sys.path.insert(0,'product')
from bhtracker.joint_mass_v2 import JointData,fit_joint
from run_v2_blocked_prediction import retained_modes,predictive_score
P=Path(__file__).resolve().parent
LONGITUDE_DEG=-70.692


def partition(document):
    training=copy.deepcopy(document);held=[];kept=[]
    for row in training['photometry']:
        # Local mean solar noon is JDfraction=-longitude/360. This lies in
        # LasCampanas daylight, grouping the entire actual observing night.
        if row['instrument']=='OGLE' and int(np.floor(row['time_jd_tdb']+LONGITUDE_DEG/360))%5==0:held.append(row)
        else:kept.append(row)
    training['photometry']=kept;training['metadata']['blocked_validation']={'version':'v2.1','longitude_deg_east_positive':LONGITUDE_DEG,'rule':'floor(JD_TDB+longitude/360), mod5=0 heldout; localmeanSolarNoon dayboundary; HSTretained','heldout_source_row_ids':[r['source_row_id'] for r in held],'role':'TRAINING_ONLY_NIGHT_PARTITION; rawfiles/allnativeOGLErows retained'}
    return training,held


def freeze():
    document=json.loads((P/'JOINT_2023_NATIVE_INPUT_v1.json').read_text());training,held=partition(document);rows=sorted([r for r in document['photometry'] if r['instrument']=='OGLE'],key=lambda r:r['time_jd_tdb']);heldids={r['source_row_id'] for r in held};cross=[b['time_jd_tdb']-a['time_jd_tdb'] for a,b in zip(rows,rows[1:]) if (a['source_row_id'] in heldids)!=(b['source_row_id'] in heldids)]
    receipt={'schema':'bhtracker.joint_validation_partition_freeze.v2.1','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'before_any_prediction_outcome':True,'changes_scientific_likelihood':False,'parent_protocol':'JOINT_PROTOCOL_V2_FREEZE.json','corrected_intent':'Chile whole-observing-night grouping using fixed localmeanSolarNoon; originalv2UTC-boundary score preserved as conditionaldiagnostic only','longitude_deg_east_positive':LONGITUDE_DEG,'longitude_role':'LasCampanas approximate geolocation, not fitted; shiftinglongitude0.01deg shiftsdayboundary2.4sec, far fromobservations','day_boundary_JD_fraction':-LONGITUDE_DEG/360,'rule':'floor(JD_TDB+longitude_deg/360), mod5=0 heldout','full_input_sha256':JointData(document).sha256,'training_input_sha256':JointData(training).sha256,'heldout_count':len(held),'heldout_source_row_ids':[r['source_row_id'] for r in held],'minimum_adjacent_crosspartition_gap_days':min(cross),'adjacent_crosspartition_gap_below_point1_days':sum(x<.1 for x in cross),'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'original_driver_sha256':hashlib.sha256((P/'run_v2_blocked_prediction.py').read_bytes()).hexdigest()}
    if receipt['adjacent_crosspartition_gap_below_point1_days']:raise ValueError('daylight grouping did not separate fullnightblocks')
    (P/'JOINT_VALIDATION_PARTITION_V2_1_FREEZE.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='heldout_source_row_ids'}))


def main():
    if len(sys.argv)==1:freeze();return
    name=sys.argv[1];baseline=json.loads((P/name).read_text());training,held=partition(baseline['dataset_input']);modes=retained_modes(baseline)
    trained=fit_joint(training,initial_states=modes,max_nfev=600,**baseline['model_options']);(P/(Path(name).stem+'_V2_1_BLOCKED_TRAIN.json')).write_text(json.dumps(trained,indent=2)+'\n')
    score={'status':'TRAINING_SEARCH_UNRESOLVED','accepted':False} if 'best_internal_state' not in trained else predictive_score(baseline['dataset_input'],training,trained,held)
    score['validation_partition_version']='v2.1';score['longitude_deg_east_positive']=LONGITUDE_DEG
    (P/(Path(name).stem+'_V2_1_BLOCKED_PREDICTION.json')).write_text(json.dumps(score,indent=2)+'\n');print(json.dumps({k:v for k,v in score.items() if k!='heldout_source_row_ids'}))

if __name__=='__main__':main()
