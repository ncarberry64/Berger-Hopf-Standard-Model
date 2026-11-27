"""Light-only rule audit: fixed wide affine, nearest-six as sensitivity, hull as extrapolation label.
Freeze: remove query plus its two nearest reference points; compare on identical query set.
Retain pairs with at least six matches after removal. Do not use target texture or mass.
"""
from pathlib import Path
import json
from itertools import combinations
import numpy as np
from scipy.spatial import ConvexHull
P=Path(__file__).resolve().parent
ns={'__file__':__file__}
exec((P/'sunburst_crystal_transfer.py').read_text().split('res=[]')[0],ns)
r=json.loads((P/'refsdal_treu_table4.json').read_text())
knot=list(range(1,11))+list(range(12,21))+list(range(22,25))
ref={c:{k:(np.array(r[f'1.{k}.{c}'])-[177.4,22.4])*np.array([np.cos(np.deg2rad(22.4)),1])*3600 for k in knot} for c in [1,2,3]}
def fit(X,Y,x):
    xc=X-X.mean(0)
    assert np.linalg.matrix_rank(xc)==2
    return (x-X.mean(0))@np.linalg.lstsq(xc,Y-Y.mean(0),rcond=None)[0]+Y.mean(0)
def rows(sets):
    out=[]
    for a,b in combinations(sorted(sets),2):
        f=sorted(sets[a].keys()&sets[b].keys())
        if len(f)<9: continue
        for i,j in [(a,b),(b,a)]:
            X,Y=[np.array([sets[t][u] for u in f]) for t in [i,j]]
            for k,x in enumerate(X):
                order=np.argsort(np.sum((X-x)**2,axis=1),kind='stable')
                order=order[order!=k]
                for block in [0,2]:
                    ids=order[block:]
                    assert k not in ids and len(ids)>=6
                    pp=fit(X[ids],Y[ids],x)
                    pl=fit(X[ids[:6]],Y[ids[:6]],x)
                    q=ConvexHull(X[ids]).equations
                    inside=bool(np.max(q[:,:2]@x+q[:,2])<=1e-9)
                    ql=ConvexHull(X[ids[:6]]).equations
                    inside_local=bool(np.max(ql[:,:2]@x+ql[:,2])<=1e-9)
                    assert not inside_local or inside
                    out.append(dict(pair=[a,b],direction=[i,j],knot=f[k],n=len(ids),block=block,inside=inside,inside_local=inside_local,excluded=[f[k]]+[f[z] for z in order[:block]],wide=float(np.linalg.norm(pp-Y[k])),local=float(np.linalg.norm(pl-Y[k])),mid=float(np.linalg.norm((pl+pp)/2-Y[k])),spread=float(np.linalg.norm(pp-pl)),pred=pp.tolist()))
    return out
def scores(rows):
    out={}
    for block in [0,2]:
        s=[r for r in rows if r['block']==block]
        for group in ['all','inside','outside','inside_local','outside_local']:
            p=[r for r in s if group=='all' or r['inside_local' if group.endswith('_local') else 'inside']==group.startswith('inside')]
            t={}
            if not p: continue
            for k in ['wide','local','mid']:
                x=np.array([r[k] for r in p])
                t[k]=dict(rms=np.sqrt(np.mean(x*x)).item(),median=np.median(x).item(),p90=np.percentile(x,90).item(),max=x.max().item(),miss05=int(sum(x>=.5)))
            out[f'{block}_{group}']=dict(n=len(p),**t)
    return out
out={}
for name,sets in [('Sunburst',ns['sets']),('Refsdal',ref)]:
    rr=rows(sets)
    assert sum(r['block']==0 for r in rr)==sum(r['block']==2 for r in rr)
    out[name]=dict(scores=scores(rr),rows=rr)
(P/'crystal_blocked_rule.json').write_text(json.dumps(out,indent=2)+'\n')
for n,d in out.items():
    print(n)
    for k,v in d['scores'].items():
        print(k,v['n'],[(m,*[round(v[m][f],3) for f in ['rms','median','p90','max']],v[m]['miss05']) for m in ['wide','local','mid']])
