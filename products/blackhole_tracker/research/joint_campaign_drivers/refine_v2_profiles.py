"""Frozen-protocol local profile crossing refinement; no acceptance promotion."""
import sys,json,math,hashlib
from pathlib import Path
sys.path.insert(0,'product')
from bhtracker.joint_mass_v2 import profile_joint_mass
P=Path(__file__).resolve().parent


def main():
 baseline_name,profile_name,output_name=sys.argv[1:4];base=json.loads((P/baseline_name).read_text());profile=json.loads((P/profile_name).read_text());original=profile['rows'];rows=list(original);bestmass=base['parameters']['mass_msun'];levels=[1.,3.841459]
 if not any(abs(r['mass_msun']/bestmass-1)<1e-10 for r in rows):rows.extend(profile_joint_mass(base['dataset_input'],base,[bestmass])['rows'])
 crossings=[];summaries=[]
 for level in levels:
  ordered=sorted(rows,key=lambda r:r['mass_msun']);level_crossings=[]
  for left,right in zip(ordered,ordered[1:]):
   if not left.get('interval_eligible') or not right.get('interval_eligible'):continue
   da,db=left['delta_deviance']-level,right['delta_deviance']-level
   if da*db>=0:continue
   a,b=left,right;refined=[];eligible=True
   for _ in range(20):
    if b['mass_msun']/a['mass_msun']-1<.005:break
    mass=math.sqrt(a['mass_msun']*b['mass_msun']);point=profile_joint_mass(base['dataset_input'],base,[mass])['rows'][0];rows.append(point);refined.append(point)
    if not point.get('interval_eligible'):eligible=False;break
    if (a['delta_deviance']-level)*(point['delta_deviance']-level)<=0:b=point
    else:a=point
   crossing={'level':level,'status':'REFINED_CONDITIONAL_SUPPORT_CROSSING' if eligible else 'CROSSING_SEARCH_UNRESOLVED','bracket_msun':[a['mass_msun'],b['mass_msun']] if eligible else None,'crossing_estimate_msun':math.sqrt(a['mass_msun']*b['mass_msun']) if eligible else None,'regular_asymptotic_state':eligible and all(x.get('regular_asymptotic_interval',False) for x in [a,b]+refined),'refinement_points':len(refined)};crossings.append(crossing);level_crossings.append(crossing)
  lefts=[x for x in level_crossings if x['crossing_estimate_msun'] is not None and x['crossing_estimate_msun']<bestmass];rights=[x for x in level_crossings if x['crossing_estimate_msun'] is not None and x['crossing_estimate_msun']>bestmass];interval=None
  if lefts and rights:
   lo=max(x['crossing_estimate_msun'] for x in lefts);hi=min(x['crossing_estimate_msun'] for x in rights)
   if all(r.get('interval_eligible') for r in rows if lo<r['mass_msun']<hi):interval=[lo,hi]
  summaries.append({'delta_deviance_level':level,'conditional_support_around_best_msun':interval,'accepted_mass_interval':None,'reason':'Noise adequacy and other identification gates are separate; no mass acceptance from profile alone. Caps/unresolved points interrupt support.'})
 result={'schema':'bhtracker.joint_mass_refined_support.v1','baseline':baseline_name,'initial_profile':profile_name,'best_conditional_mass_msun':bestmass,'rows':sorted(rows,key=lambda r:r['mass_msun']),'crossings':crossings,'levels':summaries,'scientific_source_sha256':base['scientific_source_sha256'],'analysis_driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'coverage_claim':False,'mass_acceptance':False}
 (P/output_name).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'levels':summaries,'points':len(rows),'crossings':crossings}))

if __name__=='__main__':main()
