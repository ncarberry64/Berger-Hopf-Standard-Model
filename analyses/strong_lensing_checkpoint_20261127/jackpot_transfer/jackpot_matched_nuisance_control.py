"""Matched ring-only refit of geometry nuisance terms; no S3 enters the objective."""
from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
P=Path(__file__).resolve().parent
s=P/'jackpot_registered_knot_control.py'
e={'__file__':str(s),'__name__':'aux'}
exec(compile(s.read_text().split('\nout={}',1)[0],str(s),'exec'),e)
g,j,z,z1,z2,z3,w,th,rings=(e[k] for k in ('g','j','z','z1','z2','z3','w','th','rings'))
allp=np.vstack(rings+[th]); n=[len(a) for a in rings+[th]]
cut=np.cumsum(n)[:-1]
fac=lambda zs:w(z,zs)/w(z,z1)
def unit(v):
    return v/np.maximum(1e-12,np.linalg.norm(v,axis=1))[:,None]
results={}
for label,ms in [('CA14 fixed slope',None),('Chabrier',[10.85,11.27]),('Salpeter',[11.13,11.52])]:
    K=(lambda r:(2-1.027)*.5*(g['R0']/r)**1.027) if ms is None else lambda r:g['stage1'](r,label,ms)
    rows=[]
    for geo,phi in [('q fixed, knot-ranked axis',180-30.6),('q fixed, N to E axis',90-30.6),('circular',0.)]:
      avec=np.array([g['ell'](v,1 if geo=='circular' else .946,phi,K) for v in allp])
      a1,a2=np.split(avec,[cut[-1]])
      p1,p2=np.split(allp,[cut[-1]])
      def tracer(p,score=False,disp=0):
        g1,g2,b=p
        S=np.array([[g1,g2],[g2,-g1]])
        # Third image coordinates/deflections enter only when score=True.
        a=a1+p1@S.T
        s1=np.split((p1-a)[:cut[3]],cut[:3])
        x1=np.mean([v.mean(axis=0) for v in s1],axis=0)
        t=p1[cut[3]:]; aa=a[cut[3]:]
        d1=b*unit(t-aa-x1)
        s2=t-aa*fac(z2)-d1
        if not score:return np.concatenate([(v-v.mean(axis=0)).ravel() for v in s1+[s2]])
        x2=s2.mean(axis=0)
        a=a2+p2@S.T
        dk=b*unit(p2-a-x1)
        t=p2-fac(z3)*a-dk*w(z1,z3)/w(z1,z2)
        t2=p2-fac(z2)*a-dk
        t-=g['b2'](disp)*unit(t2-x2)
        return g['pair'](t)
      for bmode in ('published S1 bounds','wide S1 sensitivity'):
        bounds=([-.18,-.18,.140],[.18,.18,.186]) if bmode.startswith('published') else ([-.18,-.18,0.],[.18,.18,.4])
        rng=np.random.default_rng(161)
        starts=[[0.,0.,.16]]+[[*rng.uniform(-.09,.09,2),rng.uniform(bounds[0][2]+.001,bounds[1][2]-.001)] for _ in range(15)]
        fit=min([least_squares(tracer,p,bounds=bounds,ftol=1e-12,xtol=1e-12,gtol=1e-12) for p in starts],key=lambda a:a.cost)
        rows.append(dict(geometry=geo,bmode=bmode,ring_rms_arcsec=np.linalg.norm(fit.fun)/np.sqrt(len(p1)),
                        shear=float(np.linalg.norm(fit.x[:2])),g1g2_S1=fit.x.tolist(),
                        third_pair_arcsec={str(v):tracer(fit.x,True,v) for v in (0,60,150)}))
    results[label]=rows
(P/'jackpot_matched_nuisance_control.json').write_text(json.dumps(results,indent=2)+'\n')
for a,rs in results.items():
  print(a)
  for b in rs:print(b['geometry'],b['bmode'],round(b['ring_rms_arcsec'],4),b['g1g2_S1'],b['third_pair_arcsec'])
