"""Use fixed VizieR galaxy locations; calibration S0-S3 only, S4-S5 unchanged."""
from pathlib import Path
import json
import numpy as np
from scipy.linalg import helmert
from scipy.optimize import least_squares
import cswa31_holdout as m
P=Path(__file__).resolve().parent
cat=[]
for s in (P/'cswa31_muse_raw.tsv').read_text().splitlines():
 t=s.split()
 if len(t)==6 and t[0].isdigit():
  k,i,ra,dec,z,qf=map(float,t); cat.append((int(i),ra,dec,z,qf))
assert len(cat)==121
o=next(q for q in cat if q[0]==354)
fac=np.array([np.cos(np.deg2rad(o[2])),1])*3600
def row(q):
 return {'id':q[0],'redshift':q[3],'qf':q[4],'EN_arcsec':((np.array(q[1:3])-o[1:3])*fac).tolist()}
mid=[row(q) for q in cat if 1.35<q[3]<1.37 and q[4]>=3]
assert len(mid)==7
near=[r for r in mid if np.linalg.norm(r['EN_arcsec'])<15]
assert {x['id'] for x in near}=={677,766}
main=[row(q) for q in cat if q[0]!=354 and abs(m.speed*(q[3]-m.zl)/(1+m.zl))<=3000 and q[4]>=2]
assert len(main)==43 # 44 incl. central under this rule, not all published 46.
assert not ({q['id'] for q in mid}&{q['id'] for q in main})
zm=float(np.median([x['redshift'] for x in mid]))
pm=m.D(m.zl,zm)/m.D(0,zm)
p01=m.D(zm,m.zs0)/m.D(0,m.zs0)
wm={k:m.D(zm,z)/m.D(0,z) for k,z in m.zs.items()}
s0_sig=m.speed*np.sqrt(.20*m.xrad/(4*np.pi))
def component(x,coords,core,scale):
 if not scale or not len(coords):return np.zeros_like(x)
 d=np.asarray(x)[...,None,:]-coords
 return scale*np.mean(d/np.sqrt(core*core+(d*d).sum(axis=-1))[...,None],axis=-2)
G=np.array([x['EN_arcsec'] for x in main])
active=None
def configure(sample,has_main,cap,membercap=10.):
 mid_xy=np.array([r['EN_arcsec'] for r in sample]).reshape(-1,2)
 def make(p,sigma,scalar):
  B=p[6] if len(sample) else 0.
  W=p[-1] if has_main else 0.
  def first(x):
   return m.lens(p[:6],x,scalar)+component(x,G,.30,W)
  c_mid=mid_xy-pm*first(mid_xy)
  def earlier(x):
   f=first(x)
   t=x-pm*f
   h=component(t,c_mid,.20,B)
   return f,h
  f,h=earlier(m.xy['S0'])
  cen=(m.xy['S0']-m.prop*f-p01*h).mean(axis=0)
  b0=4*np.pi*(sigma/m.speed)**2/m.xrad
  def trace(x,k):
   x=np.asarray(x); f,h=earlier(x)
   y=x-m.wg[k]*f-wm[k]*h
   if k in ('S3','S4','S5') and b0:
    offs=x-m.prop*f-p01*h
    y-=m.w0[k]*component(offs,cen[None,:],.10,b0)
   return y
  return trace
 low=m.lower+[0.]*(bool(sample)+has_main)
 top=m.upper+([cap] if sample else [])+([membercap] if has_main else [])
 return make,low,top
def fit(sample,has_main,cap,sigma,scalar,dev=m.train,membercap=10.,Bfix=None):
 make,low,top=configure(sample,has_main,cap,membercap)
 if Bfix is not None:
  assert sample and 0<Bfix<cap
  low[6]=Bfix-1e-9; top[6]=Bfix+1e-9
 def fun(p):
  ray=make(p,sigma,scalar)
  return np.concatenate([(helmert(len(m.xy[k]))@ray(m.xy[k],k)).ravel() for k in dev])
 p0=[20,1.,0,0,0,0]+([.15*cap] if sample else [])+([1.] if has_main else [])
 if Bfix is not None:p0[6]=Bfix
 starts=[p0[:2]+[u,v,dx,dy]+p0[6:] for (u,v) in ((0,0),(.12,-.12),(-.12,.12)) for dx,dy in [(0,0),(-1,1),(1,-1)]]
 sol=min([least_squares(fun,p,bounds=(low,top),max_nfev=950,ftol=1e-10,xtol=1e-10,gtol=1e-10) for p in starts],key=lambda a:a.cost)
 assert sol.success
 return sol.x,float(np.sqrt(np.mean(fun(sol.x)**2))),make,sol.active_mask.tolist()
def score(p,sigma,scalar,make):
 old=m.make
 m.make=make
 try:return m.model_score(p,sigma,scalar,True)
 finally:m.make=old
if __name__=='__main__':
 out=[]
 for name,book,main_on,k,scalar in [('baseline',[],False,3.,False),
    ('inner_two',near,False,3.,False),('all_seven',mid,False,3.,False),
    ('all_seven_R1_stars',mid,False,3.,True),
    ('all_seven_with_main_members',mid,True,3.,False),
    ('all_seven_with_main_R1_stars',mid,True,3.,True),
    ('all_seven_relaxed_ceiling',mid,False,6.,False)]:
  p,d,make,active=fit(book,main_on,k,s0_sig,scalar)
  res=score(p,s0_sig,scalar,make)
  # With the calibrated group unchanged, switch off only the new route layer.
  # This removes its direct bending and its knock-on to S0's ray intercept.
  if len(book):
   pk=p.copy();pk[6]=0.
   off=make(pk,s0_sig,scalar)
   on=make(p,s0_sig,scalar)
   cross={i:float(np.max(np.linalg.norm((s:=on(m.xy[i],i)-off(m.xy[i],i))[:,None]-s,axis=-1))) for i in ('S4','S5')}
  else:cross={}
  row=dict(model=name,parameters=p.tolist(),active_bounds=active,dev_component_RMS_arcsec=d,
           foreground_angle_budget_arcsec=(p[6] if book else 0),
           primary_member_budget_arcsec=(p[-1] if main_on else 0),fixed_map_foreground_pair_shifts_arcsec=cross,scores=res)
  out.append(row)
  print(name,d,row['foreground_angle_budget_arcsec'],row['primary_member_budget_arcsec'],[(i,res[i]['max_gap_arcsec'],res[i]['matched_distances_arcsec'],res[i]['unmatched_reported_counterimages']) for i in ('S4','S5')],flush=True)
 for name,mc,bf in [('seven_fixed_0p6',None,.60),('seven_with_member_ceiling5',5.,None),('seven_with_member_ceiling20',20.,None)]:
  p,d,make,active=fit(mid,mc is not None,3.,s0_sig,False,membercap=mc or 10.,Bfix=bf)
  res=score(p,s0_sig,False,make)
  row=dict(model=name,parameters=p.tolist(),active_bounds=active,dev_component_RMS_arcsec=d,
       foreground_angle_budget_arcsec=p[6],primary_member_budget_arcsec=(p[-1] if mc else 0),scores=res)
  out.append(row)
  print(name,d,p[6],row['primary_member_budget_arcsec'],[(i,res[i]['max_gap_arcsec'],res[i]['matched_distances_arcsec']) for i in ('S4','S5')],flush=True)
 (P/'cswa31_catalog_planes.json').write_text(json.dumps(dict(catalog_doi='10.26093/cds/vizier.36680162',N=len(cat),midplane_z=zm,mid_members=mid,primary_satellite_proxy=main,
    method='Positions measured; equal member strength per plane because the redshift table has no luminosities or masses. Galaxy locations at intermediate plane are propagated through the primary before computing relative deflection. No held-out positions inform amplitude or model choice; this compares all stated scenarios. Main galaxy group remains calibrated effective potential. No joint BHSM deformation is computed.',
    results=out),indent=2)+'\n')
