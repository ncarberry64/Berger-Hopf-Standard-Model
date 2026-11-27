"""Normalized v5.7 action derivative audit. No galaxy calibration or optical fit."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import root, brentq

p=Path(__file__).resolve().parent
B=np.array([[1.,-3.],[-3.,1.]])
lam=8.
U=np.array([[1.,1.],[1.,-1.]])/np.sqrt(2)
eq=.5*U[:,0]
def force(x): return B@x+lam*(x@x)*x
def H(x): return B+lam*((x@x)*np.eye(2)+2*np.outer(x,x))
def DH(x,v):return 2*lam*((x@v)*np.eye(2)+np.outer(x,v)+np.outer(v,x))
def shifted(f):
    r=root(lambda x:force(x)-f,eq,jac=H,tol=1e-12)
    assert np.linalg.norm(force(r.x)-f)<2e-13
    return r.x
assert np.linalg.norm(force(eq))<1e-14
assert np.allclose(U.T@H(eq)@U,np.diag([4,6]))
results={}
for label,n in [('parallel',U[:,0]),('opposite',-U[:,0]),('difference',U[:,1])]:
    v=np.linalg.solve(H(eq),n)
    dH=DH(eq,v)
    exact=U.T@dH@U
    for eps in [1e-3,1e-4,1e-5]:
        def fd(g):return (g(shifted(eps*n))-g(shifted(-eps*n)))/(2*eps)
        assert np.max(abs(fd(lambda x:x)-v))<eps**2
        assert np.max(abs(fd(H)-dH))<20*eps**2
        inc=np.linalg.solve(H(eq),U[:,0])
        dex=-np.linalg.solve(H(eq),dH@inc)
        assert np.max(abs(fd(lambda x:np.linalg.solve(H(x),U[:,0]))-dex))<20*eps**2
    plus=shifted(.1*n)
    ev=np.linalg.eigvalsh(H(plus))
    results[label]=dict(dH_dsource_eigenbasis=exact.round(12).tolist(),
        shifted_eigenvalues_at_source_0p1=ev.tolist(),
        derivative_of_unit_parallel_probe_eigenbasis=(U.T@dex).round(12).tolist())
assert np.allclose(results['parallel']['dH_dsource_eigenbasis'],np.diag([6,2]))
assert np.allclose(results['difference']['dH_dsource_eigenbasis'],[[0,4/3],[4/3,0]])
# Exact positive-branch saddle-node for a force along the parallel direction.
# This is only the normalized finite model, not a physical galaxy bound.
scrit=1/np.sqrt(12)
jcrit=-2*scrit+8*scrit**3
assert abs((-2+24*scrit**2))<1e-14
s=brentq(lambda sigma:-2*sigma+8*sigma**3-jcrit*.999,scrit,.5)
assert (U.T@H(s*U[:,0])@U)[0,0]>0
(p/'jackpot_archive_action_response.json').write_text(json.dumps(dict(results=results,
      normalized_parallel_fold_source=jcrit,
      background_H_eigenvalues=[4,6], data_fit=False, metric_readout=False),indent=2)+'\n')
print(json.dumps(results,indent=2))
