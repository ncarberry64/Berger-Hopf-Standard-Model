"""Fixed observed-ray diagnostic, not a lens fit. Angles E/N in arcsec."""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.special import gammainc,gammaincinv
from functools import lru_cache
p=Path(__file__).parent
xr=np.pi/(180*3600); c=299792.458; G=4.300917270036279e-9
cat=json.loads((p/'he0435_courbin_astrometry.json').read_text())['astrometry']['data']
xy=np.array([[r['delta_alpha'],r['delta_delta']] for r in cat]); theta=xy[:4]-xy[4]
zl=.4546; zs=1.693; mass=10**13.72
grp=np.array(json.loads((p/'he0435_group_direction.json').read_text())['offset_normalized_arcsec'])
alt=(np.array([69.559414-69.5619,-12.276026+12.28745])*np.array([np.cos(np.deg2rad(-12.28745)),1.]))
alt*=41.9/np.linalg.norm(alt)
r1={(a,b):d for a,b,d in json.loads((p/'r1_distances.json').read_text())}
catalog={
 'G1':(.78213,(-2.581,-3.638),10**10.9),
 'G2':(.78062,(2.179,-7.818),10**10.5502),
 'G3':(.41908,(-7.791,4.232),10**9.9445),
 'G4':(zl,(-6.451,7.182),10**10.399),
 'G5':(.77919,(-4.221,-8.888),10**10.742)}
@lru_cache(None)
def Dist(a,b,geometry):
 if geometry=='R1':return r1[a,b]
 return c/70/(1+b)*quad(lambda z:1/np.sqrt(.3*(1+z)**3+.7),a,b)[0]
def sersic(r,n,a):return gammainc(2*n,gammaincinv(2*n,.5)*(r/a)**(1/n))
def group_sph(r):return .761*np.arctan(r/.761)-.025*np.arctan(r/.025)
def group_cyl(r):return np.pi/2*r*r*(1/(np.hypot(r,.025)+.025)-1/(np.hypot(r,.761)+.761))
def alpha(x,mcyl):
 r=np.linalg.norm(x)
 return 4*G/c**2*mcyl(r)*x/r**2/xr if r else np.zeros(2)
def uniform(r,R):
 return -np.expm1(1.5*np.log1p(-(r/R)**2)) if r<R else 1.
def max_pair(v):
 ds=np.linalg.norm(v[:,None]-v,axis=-1); i,j=np.unravel_index(ds.argmax(),ds.shape)
 return float(ds[i,j])*1000, 'ABCD'[i]+'ABCD'[j]

def run(geometry,g4_kpc=15,off=grp,affine=(),compact=True,omit=(),born=False,main_scale=1.):
 d=lambda a,b:Dist(a,b,geometry)
 galaxies=dict(catalog)
 galaxies['main']=(zl,(0,0),10**11.1*main_scale)
 galaxies['group']=(zl,tuple(off),mass-galaxies['main'][2]-(catalog['G4'][2] if compact else 0))
 planes=sorted({v[0] for v in galaxies.values()})
 model={}
 rays={}
 # Backtrace the observed centers of background members as well as image rays.
 def pos(t,z):
  return np.array(t,dtype=float)-sum(d(zi,z)/d(0,z)*a for zi,a in model_ray(t,z).items())
 def model_ray(t,stop):
  arr={}
  for zi in planes:
   if zi>=stop:break
   u=np.array(t,dtype=float)
   if not born:
    for zj,a in arr.items():u-=d(zj,zi)/d(0,zi)*a
   arr[zi]=sum((f(u) for f in model[zi]),start=np.zeros(2))
  return arr
 for zi in planes:
  central=pos((0,0),zi); dist=d(0,zi)*xr; model[zi]=[]
  for name,(z,off0,m) in galaxies.items():
   if zi!=z or name in omit or (name=='G4' and not compact):continue
   center=pos(off0,zi)
   if name=='group': profile=lambda r,m=m: m*group_cyl(r)/group_sph(1.385)
   elif name=='main': profile=lambda r,m=m: m*sersic(r,3.51,.0044*np.sqrt(.82))
   elif name=='G1':
    w=1/(1+10**(-.4*(18.8-18.7)))
    profile=lambda r,m=m,w=w,dist=dist: m*(w*sersic(r,4,.37*dist)+(1-w)*sersic(r,1,1.67834699*.67*dist))
   elif name=='G4': profile=lambda r,m=m:m*uniform(r,g4_kpc/1000)
   else:profile=lambda r,m=m:m*r*r/(r*r+ .002**2)
   f=lambda t,center=center,dist=dist,profile=profile:alpha(dist*(t-center),profile)
   if name in affine:
    h=1e-4
    J=np.column_stack([(f(central+h*e)-f(central-h*e))/(2*h) for e in np.eye(2)])
    J2=np.column_stack([(f(central+h*e/2)-f(central-h*e/2))/h for e in np.eye(2)])
    assert np.max(abs(J-J2))<5e-9 and np.max(abs(J-J.T))<5e-9
    f=lambda t,J=J,a0=f(central),x0=central:a0+J@(t-x0)
   model[zi].append(f)
   rays[name]=[float(np.linalg.norm(dist*(pos(t,zi)-center))*1000) for t in theta]
 return np.array([pos(t,zs) for t in theta]),rays

def summary(d):
 return dict(pair=max_pair(d),delta_mas=(d*1000).tolist())
empty=tuple(catalog)+('main','group')
for geo in ('R1','flat'):
 assert np.array_equal(run(geo,compact=False,omit=empty)[0],theta)
 for R in (.005,.04,.4):
  projected=2*np.pi*quad(lambda u:u/(4*np.hypot(u,.025))-u/(4*np.hypot(u,.761)),0,R,epsabs=1e-12)[0]
  assert abs(projected-group_cyl(R))<1e-10
res={}
for geometry in ('R1','flat'):
 rows=[]
 for off in (grp,alt):
  for main_scale in (1.,3.):
   for radius in (5,15,65):
    kw=dict(off=off,main_scale=main_scale,g4_kpc=radius)
    b,r=run(geometry,**kw)
    a,_=run(geometry,compact=False,**kw)
    result=dict(offset_arcsec=float(np.linalg.norm(off)),main_stellar_shape_scale=main_scale,G4_radius_kpc=radius,
             smooth_mass_reallocation=summary(b-a), impacts_kpc=r,
             effective_source_scatter_arcsec=float(np.sqrt(np.mean(np.sum((b-b.mean(axis=0))**2,axis=1)))))
    for names in [('G1',),('G3',),('G4',),('group',),('G1','G2','G3','G4','G5','group')]:
     q,_=run(geometry,affine=names,**kw)
     result['affine_'+','.join(names)]=summary(b-q)
    result['ordered_minus_undeflected_evaluation']=summary(b-run(geometry,born=True,**kw)[0])
    rows.append(result)
 res[geometry]=rows
(p/'resolved_control.json').write_text(json.dumps(res,indent=2)+'\n')
for geo,rows in res.items():
 print(geo)
 for x in rows:
  print(x['offset_arcsec'],x['main_stellar_shape_scale'],x['G4_radius_kpc'],
   *[x[k]['pair'] for k in ('smooth_mass_reallocation','affine_G1','affine_G3','affine_G4','affine_group','affine_G1,G2,G3,G4,G5,group','ordered_minus_undeflected_evaluation')])
