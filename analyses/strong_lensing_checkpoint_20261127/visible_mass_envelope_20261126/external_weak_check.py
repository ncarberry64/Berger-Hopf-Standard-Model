"""External frozen envelope amplitude and survey shape controls; no weak amplitude fit except HSC shape-only control."""
import csv,json
from pathlib import Path
import numpy as np
from scipy.special import gammainc,gammaln
F=Path('external_weak')
strong=json.loads(Path('frozen_radial_transfer.json').read_text())
reach=json.loads(Path('joint_reach.json').read_text())['results']
x0,eta=map(strong.get,('x0','eta'))
Z=0.19;h=.7
sdss=np.loadtxt(F/'sm7.dat')[5:8]
R=sdss[:,0]/(1+Z)/h
y,s=sdss[:,1:].T*(1+Z)**2
S=json.loads(Path('slacs_results.json').read_text())['rows']
sizes=[t['Re'] for t in S if abs(t['logSalp']-np.log10(3.96e11))<=.2 and abs(t['z']-Z)<=.1]
Re=np.quantile(sizes,[.16,.5,.84])
def predict(r,re,A,L,M):
 x=r/re
 u=7.6692494425*x**.25
 env=A*(x/x0)**eta*((1+(x0/L)**4)/(1+(x/L)**4))**(eta/4)
 return M*(2*gammainc(8,u)-.25*np.exp(8*np.log(u)-u-gammaln(8))+env*(2-eta/(1+(x/L)**4)))/(2*np.pi*r*r*1e6*h)
sd={}
for L in [.88,3,20,50,1e9]:
 A=reach[str(L)]['A']
 sd[str(L)]=[predict(R,r,A,L,3.96e11).tolist() for r in Re]
den={}
for lum in ('L6faint','L6bright'):
 hi,lo=(np.loadtxt(F/f'{lum}_{k}.dat') for k in ('highden','lowden'))
 assert np.array_equal(hi[:,0],lo[:,0])
 den[lum]=np.c_[hi[:,0],hi[:,1]-lo[:,1],np.hypot(hi[:,2],lo[:,2])][5:8].tolist()
with (F/'wls_zbin_1.csv').open() as f:
 rows=list(csv.DictReader(l for l in f if not l.startswith('#')))
rh=np.array([float(t['rp']) for t in rows])
yh=np.array([float(t['zbin_1_stelM_thresh_11.0']) for t in rows])
C=np.loadtxt(F/'cov_mat_z1_stelM_thresh_11.0.txt')
def sh(it):
 r=rh[it]; d=yh[it]; cov=C[np.ix_(it,it)]
 def gls(m):
  u=np.linalg.solve(cov,m)
  a=u@d/(u@m);err=d-a*m
  return [a,err@np.linalg.solve(cov,err)]
 k=(r[-1]/r[0])**2
 g=np.zeros(len(r));g[-1]=k/d[0];g[0]=-k*d[-1]/d[0]**2
 return dict(r=r.tolist(),ratio=k*d[-1]/d[0],ratio_se=np.sqrt(g@cov@g),compact=gls((r/r[0])**-2),unsaturated=gls((r/r[0])**(eta-2)))
out=dict(sdss=dict(r_phys_hkpc=(R*h).tolist(),d=y.tolist(),se=s.tolist(),n_proxies=len(sizes),size_quantiles_kpc=Re.tolist(),shape=float((R[-1]/R[0])**2*y[-1]/y[0]),pred=sd),density_comoving=den,hsc_first3=sh(np.arange(3)),hsc_first4=sh(np.arange(4)),hsc_first5=sh(np.arange(5)))
print(json.dumps(out,indent=2))
Path('external_weak_check.json').write_text(json.dumps(out,indent=2)+'\n')
