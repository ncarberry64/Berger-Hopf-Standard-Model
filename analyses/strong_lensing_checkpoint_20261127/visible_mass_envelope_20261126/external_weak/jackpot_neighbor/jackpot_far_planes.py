"""One-plane-at-a-time sensitivities behind S1; frozen inner-ring solution.
Offsets in measured sky angles are backtraced to intermediate planes to locate both
test rays and the candidate galaxy. No U3–U6 mass estimate and no S3 matching.
"""
import json
import numpy as np
import inner_rings_shared_well as u
from functools import lru_cache
from pathlib import Path
P=Path(__file__).resolve().parent
fit=json.loads((P/'inner_rings_shared_well.json').read_text())['fit']['full_sampled_joint']
a,s,g1,g2,b=fit['params']
S=np.array([[g1,g2],[g2,-g1]])
sky={'U2':(1.347,[-5.71,-1.24],True),'U3':(3.508,[-4.01,2.76],False),'U4':(4.768,[2.09,3.96],False),'U5':(5.046,[-3.56,5.88],False),'U6':(5.723,[-3.24,-5.22],False)}
@lru_cache(None)
def chi(z):return u.cw.chi(z)
def w(a,b):return 1-chi(a)/chi(b)
def norm(x):return np.linalg.norm(x,axis=-1,keepdims=True)
def alpha(t):
    n=norm(t)
    return u.basic(t)+a*(n/1.43)**s*t/n+t@S.T+u.get_exact(t)-u.exact_origin
center1=np.mean([(t-w(u.z0,u.z1)*alpha(t)).mean(axis=0) for t in u.observed[:4]],axis=0)
def pred(t,z,disp=0):
    v=alpha(t)
    y=t-w(u.z0,u.z1)*v-center1
    v1=b*y/norm(y)
    P=t-w(u.z0,z)*v-w(u.z1,z)*v1
    if disp and z>u.z2:
        q=t-w(u.z0,u.z2)*v-w(u.z1,u.z2)*v1-s2center
        P-=w(u.z2,z)*4*np.pi*(disp/u.cw.c)**2/u.asc*q/norm(q)
    return P
s2center=pred(u.observed[-1],u.z2).mean(axis=0)
AB=u.pair
assert np.allclose((pred(AB,u.z3)[0]-pred(AB,u.z3)[1])*1000,fit['held']['0']['vector_mas'],atol=1e-7)
out={}
for disp in [0,150]:
    rows={}
    for key,(z,loc,secure) in sky.items():
        t=np.array([loc])
        y=pred(AB,z,disp)-pred(t,z,disp)
        dk=1000*chi(z)/(1+z)*u.asc
        coef=4*u.cw.G*1e10*w(z,u.z3)/(u.cw.c**2*dk*u.asc)
        res={}
        for rr in [0,3,10]:
            N=norm(y)
            v=coef*y/(N*N+(rr/dk)**2)
            res[str(rr)]={'norm_mas':float(norm(v[0]-v[1])[0]*1000),'vector_mas':((v[0]-v[1])*1000).tolist()}
        rows[key]=dict(z=z,secure_redshift=secure,impact_kpc=(norm(y)[:,0]*dk).tolist(),by_Plummer_kpc=res)
    out[str(disp)]=rows
    print(disp,[(k,np.round(v['impact_kpc'],2).tolist(),round(v['by_Plummer_kpc']['0']['norm_mas'],3),round(v['by_Plummer_kpc']['3']['norm_mas'],3)) for k,v in rows.items()])
s2shift=np.linalg.norm((pred(AB,u.z3,150)[0]-pred(AB,u.z3,150)[1])-(pred(AB,u.z3)[0]-pred(AB,u.z3)[1]))*1000
print('S2 illustrative vector shift mas',s2shift)
(P/'jackpot_far_planes.json').write_text(json.dumps(dict(s2_0_to_150kms_vector_difference_mas=s2shift,per_unit_source_mass_1e10=out),indent=2)+'\n')
