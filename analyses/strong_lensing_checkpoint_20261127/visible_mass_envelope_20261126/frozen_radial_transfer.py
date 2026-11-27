"""Transfer a Jackpot-only radial shape, with no SL2S or per-lens tuning."""
import json,re,numpy as np
from pathlib import Path
from scipy.optimize import least_squares
exec(Path('calibrate.py').read_text().split('\nout={}')[0])
S=json.load(open('slacs_results.json'))
slacs=[t for t in S['rows'] if t['name']!=J]
jp=next(t for t in json.load(open('jackpot_radial_holdout.json'))['central'] if t['photo']=='dev' and t['imf']=='Salpeter')
starfrac=lambda x:stars(0,x)
x0=1.43/2.35; x1=2.07/2.35
eta=jp['implied_growth_slope']
A_j=jp['env1_to_stars']*starfrac(x0)
# M_env/M_star,total = A*(R/(R_e*x0))^eta in the range calibrated by Jackpot.
# Also check an independent normalization fitted on SLACS only, never on SL2S.
def radial(t,R,A,eta=eta):
 u=R/t['Re']; return np.log10(stars(0,u)+A*(u/x0)**eta)+t['logSalp']
def cp(t,R,q):
 return np.log10(stars(0,R/t['Re'])*(1+q))+t['logSalp']
def amp(ts,eta=eta):
 def f(q):return [radial(t,t['R'],np.exp(q[0]),eta)-t['L'] for t in ts]
 return np.exp(least_squares(f,[-1.7],bounds=(-12.,4.)).x[0])
refA=amp(slacs); refQ=np.exp(fit(slacs,[],'Salp')[0])
L=Path('sl2s_iv.txt').read_text()
tab2=L.split('TABLE 2',1)[1].split('TABLE 3',1)[0]
zmap={}
for line in tab2.splitlines():
 t=line.split()
 if len(t)>10 and t[0].startswith('SL2SJ') and all(re.fullmatch(r'\d\.\d+',v) for v in t[7:9]):
  key=t[0]; val=(float(t[7]),float(t[8]))
  assert key not in zmap or zmap[key]==val
  zmap[key]=val
iv=[]
for s in L.split('TABLE 3',1)[1].split('Note.',1)[0].splitlines():
 t=s.split()
 if len(t)<10 or not t[0].startswith('SL2SJ') or 'disky' in t:continue
 name=t[0]; z=float(t[1]); assert name in zmap,(name,z)
 zz,zs=zmap[name];assert z==zz and zs>z
 iv.append(dict(name=name,z=z,src=zs,Re=float(t[2]),R=float(t[3]),logSalp=float(t[7]),critical=sig(z,zs)))
assert len(iv)==23 and len(set(t['name'] for t in iv))==23
assert not {t['name'] for t in iv} & {t['name'] for t in slacs}
def score(T,origin):
 result={}
 for k in ['stars','Jackpot_fixed_ratio','Jackpot_radial','SLACS_constant','Jackpot_shape_SLACS_amp']:
  a=[]
  for t in T:
   if k=='stars': f=lambda r:cp(t,r,0.)
   elif k=='Jackpot_fixed_ratio':f=lambda r:cp(t,r,jp['env1_to_stars'])
   elif k=='Jackpot_radial':f=lambda r:radial(t,r,A_j)
   elif k=='SLACS_constant':
    Q=refQ if origin!='SLACS' else np.exp(fit([g for g in slacs if g['name']!=t['name']],[],'Salp')[0])
    f=lambda r:cp(t,r,Q)
   else:
    A=refA if origin!='SLACS' else amp([g for g in slacs if g['name']!=t['name']])
    f=lambda r:radial(t,r,A)
   P=ring(t,f);a.append(dict(name=t['name'],pred=P,obs=t['R'],err=None if P is None else P/t['R']-1,
       observed_aperture_in_calibrated_range=x0<=t['R']/t['Re']<=x1,ratio_R_Re=t['R']/t['Re']))
  result[k]=a
  for region in [False,True]:
   e=np.array([x['err'] for x in a if x['err'] is not None and (not region or x['observed_aperture_in_calibrated_range'])])
   print(origin,k,'calib_only',region,'N',len(e),'median_signed,median_absolute',np.round([np.median(e),np.median(abs(e))],4))
 return result
s0=score(slacs,'SLACS');s1=score(iv,'SL2S')
rng=np.random.default_rng(91838)
for n,r in [('SLACS',s0),('SL2S',s1)]:
 a=np.array([x['err'] for x in r['SLACS_constant']]);b=np.array([x['err'] for x in r['Jackpot_shape_SLACS_amp']])
 q=rng.integers(0,len(a),(20000,len(a))); delta=np.median(abs(a[q]),axis=1)-np.median(abs(b[q]),axis=1)
 print(n,'paired descriptive interval',np.percentile(delta,[2.5,50,97.5]))
print('frozen',x0,x1,A_j,eta,refQ,refA)
Path('frozen_radial_transfer.json').write_text(json.dumps(dict(sl2s=iv,SLACS=s0,SL2S=s1,x0=x0,x1=x1,A_j=A_j,eta=eta,SLACSamp=refA,SLACSconstant=refQ),indent=2)+'\n')
