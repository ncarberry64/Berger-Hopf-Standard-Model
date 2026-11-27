"""Checks for catalogue coordinate centering, splitting, and off-layer limit."""
import json
import numpy as np
import cswa31_catalog_planes as n
import cswa31_holdout as m
D=json.loads((n.P/'cswa31_catalog_planes.json').read_text())
R={r['model']:r for r in D['results']}
assert len(n.mid)==7 and all(q['qf']==3 for q in n.mid)
assert set(n.m.train).isdisjoint(('S4','S5'))
ptest=np.array([20,1,.1,-.1,0,0])
g=n.configure(n.mid,False,3)[0](np.r_[ptest,0.],n.s0_sig,False)
xg=np.array([[.53,2.7],[-22,-9],[3.5,4.0]])
for k in m.xy:
 assert np.allclose(g(xg,k),m.make(ptest,n.s0_sig,False)(xg,k),atol=1e-12,rtol=0)
q0,d0,_,_=n.fit(n.mid,True,3,n.s0_sig,False)
for k in ('S4','S5'):m.xy[k][:]+=13
q1,d1,_,_=n.fit(n.mid,True,3,n.s0_sig,False)
assert (q1==q0).all() and d1==d0
print('Passed data count, foreground zero limit, and held-out perturbation calibration-leakage check')
