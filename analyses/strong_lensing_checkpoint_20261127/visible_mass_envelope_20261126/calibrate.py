"""Exploratory projected effective-envelope benchmark, not physical identification.
Auger et al. arXiv:0911.2471 Tables 3 and 4, H0=70, Om=0.3.
"""
from pathlib import Path
import re,json
import numpy as np
from scipy.optimize import least_squares,brentq
from scipy.integrate import quad
from scipy.special import gammainc
from functools import lru_cache
T=Path('auger09.txt').read_text()
J='SDSSJ0946+1006'
@lru_cache(None)
def d(z0,z1): return 299792.458/70/(1+z1)*quad(lambda z:1/(.3*(1+z)**3+.7)**.5,z0,z1)[0]
sig=lambda z,y:299792.458**2/(4*np.pi*4.30091727e-6)*(d(0,y)/(d(0,z)*d(z,y)))/1000
photo={}
for line in T[T.index('                                                                Table 3'):T.index('                                                                              Table 4')].splitlines():
 m=re.match(r'\s*(SDSSJ[\d+−-]+)\s+\S+\s+[+\-−]?\d+◦\s+\S+\s+(\d\.\d+)\s+(\d\.\d+)\s+\d+\s*±\s*\d+\s+(\S+)\s+(.*)',line)
 if not m:continue
 name,z,src,morph,tail=m.groups(); p=tail.split()
 if len(p)<7 or p[5]=='···':continue
 z,src,Re=float(z),float(src),float(p[5])
 photo[name]=(z,src,morph,Re*d(0,z)*np.pi/648.)
rows=[]
for line in T[T.index('                                                                              Table 4'):].splitlines():
 t=line.split()
 if len(t)<8 or not t[0].startswith('SDSSJ') or t[0] not in photo or t[1]=='···' or t[3]=='···':continue
 z,src,morph,Re=photo[t[0]]
 if morph not in ['E','E/S0']:continue
 R,L=float(t[1]),float(t[2]); c,s=[float(q.split('±')[0]) for q in t[6:8]]
 fch,fsa=[float(q.split('±')[0]) for q in t[3:5]]
 rows.append(dict(name=t[0],z=z,src=src,morph=morph,Re=Re,R=R,L=L,logChab=c,logSalp=s,fChab=fch,fSalp=fsa,critical=sig(z,src)))
assert len(rows)>45 and len({t['name'] for t in rows})==len(rows) and any(t['name']==J for t in rows)
# Compare no-envelope, constant gain, stellar-mass-only, and explicit aperture dependence.
xcols={'constant':[],'mass':[0],'aperture':[0,1],'structure':[0,1,2]}
def stars(m,u):
 return 10**m*gammainc(8.,7.6692494425*u**.25)
def env(params,cols,m,u,re):
 xx=np.array([m-11.5,np.log10(u),np.log10(re/5.)])
 return np.exp(params[0]+np.asarray(params[1:])@xx[cols])
def pred(params,cols,t,R,imf):
 m=t['log'+imf];u=R/t['Re']
 return np.log10(stars(m,u)*(1+env(params,cols,m,u,t['Re'])))
def fit(ts,cols,imf):
 def loss(q):return [pred(q,cols,t,t['R'],imf)-t['L'] for t in ts]
 limits=[([-4]* (1+len(cols))),([4]*(1+len(cols)))]
 if 1 in cols: limits[0][1+cols.index(1)]=0;limits[1][1+cols.index(1)]=1.6
 ini=np.r_[-1.4 if imf=='Salp' else .2,np.zeros(len(cols))];
 if 1 in cols: ini[1+cols.index(1)]=.25
 return least_squares(loss,ini,bounds=limits,max_nfev=300,gtol=1e-10).x
def ring(t,mass):
 # Largest crossing of mean convergence=1; no radius observation used here.
 r=np.geomspace(.05,40.,240);f=lambda x:mass(x)-np.log10(np.pi*x*x*t['critical'])
 vals=[f(a) for a in r]
 slots=[i for i in range(len(r)-1) if vals[i]>=0>vals[i+1]]
 return float(brentq(f,r[slots[-1]],r[slots[-1]+1])) if slots else None
out={}
for I in ['Salp','Chab']:
 p0=[t for t in rows if t['name']!=J]
 for name,cs in [('stars',[]),('jackpot_5kpc_fixed',[]),*xcols.items()]:
  if name=='jackpot_5kpc_fixed' and I!='Salp':continue
  tests=[]
  for t in rows:
   if name=='stars':f=lambda R:np.log10(stars(t['log'+I],R/t['Re']))
   elif name=='jackpot_5kpc_fixed':
    if I!='Salp' or t['name']==J:continue
    f=lambda R:np.log10(stars(t['log'+I],R/t['Re'])/(1-.421))
   else:
    coef=fit([u for u in p0 if u['name']!=t['name']],cs,I)
    f=lambda R:pred(coef,cs,t,R,I)
   o=ring(t,f); y=f(t['R'])
   tests.append(dict(name=t['name'],errmass=y-t['L'],R_pred=o,R_obs=t['R'],errR=None if o is None else o/t['R']-1.,gain_pred=10**y/stars(t['log'+I],t['R']/t['Re'])-1.))
  v=[a for a in tests if a['name']!=J]; m=np.array([t['errmass'] for t in v]);r=np.array([t['errR'] for t in v if t['errR'] is not None])
  print(I,name,len(v), 'rmsdex',np.sqrt(np.mean(m*m)),'valid',len(r),'medabsring',np.median(abs(r)),'bias',np.median(r))
  out[I+':'+name]={'tests':tests,'nonJackpot_rms_dex':float(np.sqrt(np.mean(m*m))),'nonJackpot_ring_N':len(r),'nonJackpot_median_abs_ring_error':float(np.median(abs(r)))}
  if name in xcols:
   q=fit(p0,cs,I);out[I+':'+name]['fitted_all_but_jackpot']=q.tolist()
   print('coeff',q,'jackpot',next(a for a in tests if a['name']==J))
Path('slacs_results.json').write_text(json.dumps({'rows':rows,'tests':out},indent=2)+'\n')
