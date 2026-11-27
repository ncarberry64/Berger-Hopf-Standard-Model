"""RCS0327 fourth-cluster figure-grade transfer. Do not tune the frozen local-six rule."""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import ConvexHull
P=Path(__file__).resolve().parent
ns={'__file__':str(P/'crystal_blocked_rule.py')}
exec((P/'crystal_blocked_rule.py').read_text().split('out={}\nfor name')[0],ns)
data=json.loads((P/'rcs0327_sharon_fig1.json').read_text())
all_knots=sorted(data['3'])
secure=[k for k in all_knots if k not in data['low_quality']]
assert len(all_knots)==10 and len(secure)==8 and data['3'].keys()==data['4'].keys()
def run(knots,blocks,jitter=None):
    sets={i:np.array([data[i][k] for k in knots],float) for i in ['3','4']}
    if jitter is not None:
        for i,X in sets.items():
            X+=jitter.normal(size=X.shape)*np.array([20 if k in data['low_quality'] else 8 for k in knots])[:,None]
    sets={i:X*data['arcsec_per_crop_pixel'][i] for i,X in sets.items()}
    rr=[]
    for i,j in [('3','4'),('4','3')]:
        X,Y=sets[i],sets[j]
        for k,x in enumerate(X):
            order=np.argsort(np.sum((X-x)**2,axis=1),kind='stable')
            order=order[order!=k]
            for block in blocks:
                ids=order[block:]; l=ids[:6]
                assert len(l)==6 and k not in ids
                local=ns['fit'](X[l],Y[l],x); wide=ns['fit'](X[ids],Y[ids],x)
                if jitter is None:
                    y=Y.copy(); y[[k,*order[:block]]]+=9999
                    np.testing.assert_array_equal(local, ns['fit'](X[l],y[l],x))
                def in_hull(a):
                    q=ConvexHull(a).equations
                    return bool(np.max(q[:,:2]@x+q[:,2])<=1e-9)
                rr.append(dict(pair=[i,j],direction=[i,j],knot=knots[k],block=block,excluded=[knots[t] for t in [k,*order[:block]]],inside=in_hull(X[ids]),inside_local=in_hull(X[l]),local=float(np.linalg.norm(local-Y[k])),wide=float(np.linalg.norm(wide-Y[k])),mid=float(np.linalg.norm((local+wide)/2-Y[k])),spread=float(np.linalg.norm(local-wide))))
    return rr
rng=np.random.default_rng(327)
out={}
for label,knots,blocks in [('higher_quality',secure,[0]),('all_labeled',all_knots,[0,2])]:
    rr=run(knots,blocks)
    out[label]=dict(scores=ns['scores'](rr),rows=rr)
    sim={b:[] for b in blocks}
    for k in range(200):
        jitter=run(knots,blocks,rng)
        for b in blocks:
            group=[r for r in jitter if r['block']==b and r['inside_local']]
            sim[b].append([len(group),float(np.median([r['local'] for r in group])) if group else None])
    out[label]['digitization_perturbation_percentiles']={b:[np.percentile([r[n] for r in sim[b] if r[n] is not None],[10,50,90]).tolist() for n in [0,1]] for b in blocks}
(P/'crystal_frozen_rcs0327.json').write_text(json.dumps(out,indent=2)+'\n')
for label,p in out.items():
    print(label,p['digitization_perturbation_percentiles'])
    for key,x in p['scores'].items():
        if key.endswith('_local') or key.endswith('_all'):
            print(key,x['n'],[tuple(round(x[r][m],3) for m in ['median','rms','max']) for r in ['local','wide','mid']])
    print([(r['direction'],r['knot'],r['block'],round(r['local'],3)) for r in p['rows'] if r['inside_local']])
