"""Frozen BHSM light-only local-six + input hull on Warhol Arc.
Perera et al. Table 4: eight matches, so block=0 only. Same rule, not reduced budget.
"""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import ConvexHull
P=Path(__file__).resolve().parent
ns={'__file__':str(P/'crystal_blocked_rule.py')}
exec((P/'crystal_blocked_rule.py').read_text().split('out={}\nfor name')[0],ns)
ra=json.loads((P/'warhol_perera_table4.json').read_text())
knots=list('abcdefgh')
assert sorted(ra)==sorted(k+str(i) for k in knots for i in (1,2))
sets={i:np.array([ra[k+str(i)] for k in knots]) for i in (1,2)}
for t in sets:
    sets[t]=(sets[t]-[64.037,-24.067])*np.array([np.cos(np.deg2rad(-24.067)),1])*3600
def run():
    rows=[]
    for i,j in ((1,2),(2,1)):
        X,Y=sets[i],sets[j]
        for k,x in enumerate(X):
            ids=np.argsort(np.sum((X-x)**2,axis=1),kind='stable')
            ids=ids[ids!=k]
            l=ids[:6]
            assert k not in l and len(l)==6
            local=ns['fit'](X[l],Y[l],x)
            wide=ns['fit'](X[ids],Y[ids],x)
            ycopy=Y.copy()
            ycopy[k]+=9999
            np.testing.assert_array_equal(local,ns['fit'](X[l],ycopy[l],x))
            q=ConvexHull(X[l]).equations
            inside=bool(np.max(q[:,:2]@x+q[:,2])<=1e-9)
            rows.append(dict(pair=[1,2],direction=[i,j],knot=knots[k],n=len(ids),block=0,inside=inside,inside_local=inside,wide=float(np.linalg.norm(wide-Y[k])),local=float(np.linalg.norm(local-Y[k])),mid=float(np.linalg.norm((local+wide)/2-Y[k])),spread=float(np.linalg.norm(wide-local)),pred=local.tolist(),training=[knots[z] for z in l]))
    scores=ns['scores'](rows)
    return dict(scores=scores,rows=rows)
d=run()
(P/'crystal_frozen_warhol.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d['scores'],indent=2))
