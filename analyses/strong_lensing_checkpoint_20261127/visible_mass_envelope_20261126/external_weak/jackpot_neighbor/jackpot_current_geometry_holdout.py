"""Identical lens fields, varied distances in the current projected three-source model."""
import sys,json
from pathlib import Path
from functools import lru_cache
import numpy as np
from scipy.integrate import quad
import erosita_matched_planes as ep
u=ep.u
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[2]/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D,bgsol,bg
assert abs(bg.OMEGA_K0+.018)<1e-12
origW=ep.W.copy()
@lru_cache(None)
def sameE(a,b):return quad(lambda z:1/float(bgsol.sol(-np.log1p(z))[2]),a,b,epsabs=2e-11)[0]
Ws={'closed_R1':{(a,b):D(a,b)/D(0,b) for a,b in origW},'same_expansion_flat':{(a,b):sameE(a,b)/sameE(0,b) for a,b in origW},'flat_LCDM_distance_control':origW}
T0=[a.copy() for a in u.observed]; AB0=u.pair.copy()
J=[np.array(x) for x in json.loads((P/'erosita_shared_nodes.json').read_text())['samples']]
assert all(w>0 for m in Ws.values() for w in m.values())
def run(T,AB,names,arms,seeds=u.starts):
  u.observed=T;u.pair=AB
  data={}
  for name in names:
   ep.W=Ws[name]
   data[name]={}
   for arm in arms:
    f=ep.fn(arm,J if arm=='sampled' else np.zeros((2,2)))
    a=ep.fit(f,seeds)
    data[name][arm]=dict(rms_mas=float(np.linalg.norm(a.fun)*1000/np.sqrt(14)),p=a.x.tolist(),
     predictions={str(s2):(f(a.x,s2,True)*1e3).tolist() for s2 in [0,75,150]})
  return data
def stats(r,arm,s):
 a=np.array(r['closed_R1'][arm]['predictions'][s]);b=np.array(r['same_expansion_flat'][arm]['predictions'][s])
 return [np.linalg.norm(a),np.linalg.norm(b),np.linalg.norm(a)-np.linalg.norm(b),np.linalg.norm(a-b)]
def main():
 R=run(T0,AB0,list(Ws),['none','separate','sampled'])
 for n,g in R.items():
  print(n,[(k,round(v['rms_mas'],5),[round(np.linalg.norm(x),5) for x in v['predictions'].values()]) for k,v in g.items()],flush=True)
 print('nominal deltas (closed,flat,closed-flat,vector)',[stats(R,'separate',s) for s in ['0','75','150']],flush=True)
 rng=np.random.default_rng(3752)
 H=[]
 seeds=[R[j]['separate']['p'] for j in ['closed_R1','same_expansion_flat']]
 for _ in range(96):
  T=[t+rng.normal(0,.03,t.shape) for t in T0]
  AB=AB0+rng.normal(0,[[.02,.02],[.05,.04]])
  r=run(T,AB,['closed_R1','same_expansion_flat'],['separate'],seeds)
  H.append([stats(r,'separate',s) for s in ['0','75','150']])
 Q=np.quantile(H,[.16,.5,.84],axis=0).tolist()
 print('sensitivity',Q,flush=True)
 out=dict(separation_comparison_names=['closed','flat_same_expansion','closed_minus_flat','vector_change'],
          lens_fields='unchanged angular deflection fields; vary only distance ratios',
          correction_nominal={arm:{s:stats(R,arm,s) for s in ['0','75','150']} for arm in ['none','separate','sampled']},
          inner_30_mas_and_reported_far_pos_jitter_quantiles=Q,positions=AB0.tolist(),rows=R)
 (P/'jackpot_current_geometry_holdout.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
