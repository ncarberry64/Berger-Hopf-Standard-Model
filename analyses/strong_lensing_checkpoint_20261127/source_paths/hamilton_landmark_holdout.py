"""Read published Hamilton's Object Fig. 12 landmark markers and predict held-out positions.
Pixel coordinates refer to a 2000 px tall pdftoppm rendering of PDF page 12.
This is a catalog reanalysis (not independent centroid extraction from HST FITS).
"""
from itertools import combinations
from pathlib import Path
import json
import numpy as np

raw={
 'A': [(605,825),(572,830),(554,835),(660,818),(666,864),(623,851),(511,758)],
 'B': [(620,908),(585,904),(560,886),(691,928),(666,871),(629,883),(516,976)],
 'C': [(862,289),(822,292),(797,289),(947,289),(947,271),(884,276),(710,322)],
}
units=np.array([1/67,-2.2/67])
def tr(x,y,z,k):
    m=x.mean(0); n=y.mean(0)
    xx=x-m; yy=y-n
    if k=='shift': j=np.eye(2)
    elif k=='affine': j=np.linalg.lstsq(xx,yy,rcond=None)[0]
    else:
        u,s,v=np.linalg.svd(xx.T@yy)
        want=-1 if k=='mirror' else 1
        q=np.diag([1,want*np.linalg.det(u@v)])
        j=u@q@v*(s@q.diagonal())/np.sum(xx**2)
    return (z-m)@j+n,float(np.linalg.det(j))
models=['shift','rotate','mirror','affine']
trainsets=list(combinations(range(6),4))
def compare(X,Y,all_sets=True):
    out={}
    for k in models:
        errors=[]; ds=[]
        for train,test in (
            [(list(t),list(set(range(6))-set(t))) for t in trainsets] if all_sets else []
        )+[(list(range(6)),[6])]:
            pred,d=tr(X[train],Y[train],X[test],k)
            res=np.linalg.norm(pred-Y[test],axis=-1)
            errors.append(res.tolist()); ds.append(d)
        if all_sets:
            cv=np.ravel(errors[:-1]); interior=(cv@cv/len(cv))**.5
        else: interior=None
        out[k]=dict(inner_RMS=interior,outer_7=errors[-1][0],local_det=ds[-1],
          range_cv_det=[min(ds),max(ds)],held_details=errors if all_sets else None)
    return out
points={k:np.array(a)*units for k,a in raw.items()}
res={d:compare(points[d[0]],points[d[1]]) for d in ('AB','BA','AC','BC')}
# Numerical sensitivity to digitizing the figure only, not a measurement error bar.
rng=np.random.default_rng(6503)
sens={}
for d in res:
    hh={k:[] for k in models}
    for _ in range(350):
        xy=[(np.array(raw[k])+rng.uniform(-2,2,(7,2)))*units for k in d]
        v=compare(*xy)
        for k in models: hh[k].append([v[k]['inner_RMS'],v[k]['outer_7']])
    sens[d]={k:np.percentile(v,[5,95],axis=0).tolist() for k,v in hh.items()}
out={'marker_pixels':raw,'measurement':'Manual centers from figure 12 of 2105.04562. 67 horizontal rendering pixels per 1 arcsec; vertical scale corrected by stated EW stretch 2.2. No foreground inputs.', 
     'training':'all 15 choose-four-of-six inner-feature trainings, predicting the two excluded inner each time; train on all 6 inner to predict outer #7 separately',
     'metrics_arcsec':res,'digitization_sensitivity_5_95_inner_outer':sens}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
for d,r in res.items():
    for k,v in r.items(): print(d,k,*(round(v[key],3) for key in ('inner_RMS','outer_7','local_det')))
