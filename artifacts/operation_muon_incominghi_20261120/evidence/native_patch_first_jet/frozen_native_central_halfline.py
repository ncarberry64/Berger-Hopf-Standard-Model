"""Scope: constant native wall coefficients on an artificial half-line; no physical exterior."""
from pathlib import Path
import json,numpy as np
from scipy.optimize import brentq
p=Path(__file__).resolve()
z=np.load(p.parent.parent/'native_n0_coupled_static.npz')
K,M,B=[z[k+'84'] for k in 'KMB']
free=np.r_[z['interior64'],z['boundary20'][4:]]
K,M,J=[c[np.ix_(free,free)] for c in (K,M,B.T-B)]
u=(free==z['boundary20'][15]).astype(float)
e,r,d,s,C=(4198.4562263622265,5921.340578763061,5581.932384919164,.0779237798365626,.0003208119454588855)
a=r-e*s*s; cut=(4*d*a/(e*r))**.5
def info(w,pinv=1e-11):
    A=K+w*w*M+1j*w*J
    X=np.linalg.pinv(A,rcond=pinv)@u
    err=np.linalg.norm(A@X-u)
    assert err < 2e-10
    chi=np.vdot(u,X)
    assert abs(chi.imag)<1e-9
    return -1/chi.real,A,X,err
def lam(w): return -C*(4*d*a-e*r*complex(w)**2)**.5
def target(w): return lam(w).real-info(w)[0]
def detfactor(w): return 1-lam(w).real/info(w)[0]
samples=[]
for w in (0.,.1,.25,.5,.85):
    req,A,X,err=info(w)
    samples.append(dict(omega=w,Lambda=lam(w).real,target=req,difference=target(w),support_error=float(err),determinant_factor=detfactor(w)))
w=brentq(target,.1,.5,xtol=1e-13)
req,A,X,err=info(w)
eigint=np.linalg.svd(A,compute_uv=False)
eigjoin=np.linalg.svd(A+req*np.outer(u,u),compute_uv=False)
# Remove any pre-existing numerical nulls (neither they nor the new null imply a particle pole).
def nnull(vals): return int(np.sum(vals<1e-11*vals[0]))
diff=(target(w+1e-5)-target(w-1e-5))/(2e-5)
assert abs(detfactor(w))<1e-10
assert nnull(eigjoin)==nnull(eigint)+1
assert abs(info(w,1e-12)[0]-req)<1e-8
# Check selected radial exponent solves original ODE and its original outward conormal.
for W in [0.,.5,2.,3.+1e-9j,100.+1e-9j]:
    L=lam(W)
    q=(L/C-1j*W*e*s)/a
    raw=a*q*q+2j*W*e*s*q+e*W*W-4*d
    assert abs(raw)<1e-12*max(4*d,e*abs(W)**2)
# Retain exactly the same exterior wall neighborhood and alter only the far tail.
# The phase removing constant shift cancels in the conormal; v satisfies v''=k²v.
def tail(w,ratio,length=.2):
    k=(4*d*a-e*r*w*w)**.5/a
    midpoint=-C*(4*d*ratio*a-e*r*w*w)**.5
    m=C*a*k
    t=np.tanh(k*length)
    return (midpoint-m*t)/(1-midpoint/m*t)
tailcases=[]
for ratio in (.5,1.,2.):
    assert abs(tail(0,1)-lam(0))<1e-12
    vals=[tail(v,ratio)-info(v)[0] for v in (0.,.85)]
    rt=brentq(lambda v:tail(v,ratio)-info(v)[0],0.,.85) if vals[0]*vals[1]<0 else None
    tailcases.append({'d_deep_factor':ratio,'identical_collar_length':.2,'Lambda0':tail(0,ratio),'mismatch_at_0_and_.85':vals,'bracketed_root_0_to_.85':rt})
out={'tail_controls':tailcases,'scope':'Artificial single axial central channel with frozen incoming-hi coefficients throughout half-line. Interior original K84 with held temporal wall. No incident drive, no physical continuum or magnetic spin pole.', 'omega_cut':cut,'samples':samples,'root':{'omega':w,'Lambda':req,'derivative_of_mismatch':diff,'unjoined_numerical_nullity':nnull(eigint),'joined_numerical_nullity':nnull(eigjoin),'joined_residual':float(np.linalg.norm((A+req*np.outer(u,u))@X)),'unjoined_min_singular':float(eigint[-1]),'joined_min_singular':float(eigjoin[-1])}}
p.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
