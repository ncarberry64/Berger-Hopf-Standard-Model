"""Predict projected trace-free tide from independent neighbor proxies; compare without sky-angle fit."""
from pathlib import Path
from contextlib import redirect_stdout
import io,json,sys
import numpy as np
from scipy.linalg import helmert
from scipy.optimize import least_squares
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'))
with redirect_stdout(io.StringIO()):
 import cross_lens_mode_control as c
 import he0435_joint_field_control as h
 import he0435_joint_projected as j
from r1_background_geometry import D,G,speed,xrad
I=np.eye(2)
def tf(A): return A-np.trace(A)*I/2
def soft_point(z,X,M,core):
 K=4*G*M/(speed*speed*D(0,z)*xrad*xrad)
 Z=np.dot(X,X)+core**2
 return K*(I/Z-2*np.outer(X,X)/Z**2)
def getR(n):
 _,tr,_=c.cases[n]
 return float(np.median(np.concatenate([np.linalg.norm(x,axis=1) for z,x in tr.values()])))
def he_group(alt=False,sigma=470):
 X=np.array(j.cfg['offset_normalized_arcsec'])
 if alt:
  X=np.array([-8.74,41.13]);X*=41.9/np.linalg.norm(X)
 r=np.linalg.norm(X)*h.d1*xrad
 a,d=.025,j.r200
 v,w=np.hypot(r,a),np.hypot(r,d)
 m=np.pi*(sigma/speed)**2*r*r*(1/(v+a)-1/(w+d))
 den=np.pi*(sigma/speed)**2*(1/v-1/w)
 H=4*h.d1*(m/r**2*I+(den-2*m/r**2)*np.outer(X,X)/np.dot(X,X))
 return tf(H)
def cass_sat(lo,ap=1,central_flux=3500.,amp=1.):
 phot=json.loads((P/'cswa31_hst_photometry.json').read_text())
 selected=[]
 total=np.zeros((2,2))
 for g in phot['rows']:
  X=np.array(g['EN_arcsec'])
  if g['zone']=='primary' and g['accepted'] and np.linalg.norm(X)>lo:
   y=g['apertures'][ap]
   M=amp*1.6e12*y['flux_e_per_s']/central_flux
   core=np.clip(.60*y['half_positive_flux_radius_arcsec'],.10,.42)
   total+=tf(soft_point(.6828,X,M,core))
   selected.append(g['id'])
 return total,selected
def jack_group(mass,PA):
 # Native compass: north up-left, east down-left, incl. 18.652 degrees.
 a=np.deg2rad(180-161.348)
 Q=np.array([[-np.sin(a),-np.cos(a)],[-np.cos(a),np.sin(a)]])
 assert np.allclose(Q@Q.T,I)
 d=np.deg2rad(PA)
 return tf(soft_point(.222,40*Q@np.array([np.sin(d),np.cos(d)]),mass,2.7))
def solve(n,tag,T,foreground=False):
 zl,train,test=c.cases[n]
 R=getR(n)
 weights={k:D(zl,z)/D(0,z) for k,(z,_) in (train|test).items()}
 B=h.theta_g/xrad-h.positions['G']
 def bend(X,p): # arcsec physical deflection
  r=np.linalg.norm(X,axis=1)
  return p[0]*((r/R)**p[1]/r)[:,None]*X+X@T.T
 def src(X,k,p):
  a=bend(X,p);s=X-weights[k]*a
  if foreground:
   ab=bend(B[None,:],p)[0]
   Y=h.d2*xrad*(X-B)-h.d12*xrad*(a-ab)
   s-=h.w2*np.stack([h.g_photo.apply(x,False)[0]/xrad for x in Y])
  return s
 def dev(p):return np.concatenate([(helmert(len(X))@src(X,k,p)).ravel() for k,(z,X) in train.items()])
 res=min([least_squares(dev,[R/max(weights.values()),a],bounds=([.03*R,-.65],[12*R,.65]),ftol=1e-12,xtol=1e-12,gtol=1e-12) for a in [-.40,0,.40]],key=lambda x:x.cost)
 train_rms=np.sqrt(np.mean(res.fun**2))
 scores={}
 for k,(_,X) in test.items():
  Y=src(X,k,res.x);q=Y[1:]-Y[0]
  scores[k]=float(np.sqrt(np.mean((q*q).sum(axis=1))))
 return dict(lens=n,scenario=tag,includes_separate_G1=foreground,params_radial_only=res.x.tolist(),
       reduced_tidal_stretch_at_nearest_source=float(np.linalg.norm(T,2)*min(weights.values())),unreduced_tide=T.tolist(),
       axis_deg_from_positive_native_x=float(.5*np.rad2deg(np.arctan2(T[0,1],T[0,0]))%180) if np.linalg.norm(T)>0 else None,
       train_RMS=float(train_rms),held_anchor_source_RMS=scores)
rows=[]
for n in c.cases:
 rows.append(solve(n,'radial_only',np.zeros((2,2)),n=='HE0435'))
for alt in [False,True]:
 for sigma in [370,470,570]:
  rows.append(solve('HE0435',('near_group' if alt else 'nominal_group')+f'_{sigma}',he_group(alt,sigma),True))
for lo in [getR('CSWA31'),25.]:
 for flux in [3329.,3639.]:
  T,g=cass_sat(lo,central_flux=flux)
  rows.append(solve('CSWA31',f'photometric_stars_outer_{lo:.2f}_BGG_flux_{flux}',T)|{'members_used':g})
for M in [1e11,1e12]:
 for PA in [210,225,240]:
  rows.append(solve('Jackpot',f'conditional_SW_{M:.0e}_PA_{PA}',jack_group(M,PA)))
out=dict(scope='No tidal angle or amplitude fit to lensing. Round primary still calibrates using nearer image families. Ordinary 1st-order environmental trace-free projection only, no full diffuse group matter or joint BHSM response. For HE separately propagate the fixed stellar G1 on its own screen; other systems do not include their intermediate sources in this control. Jackpot amplitude scenarios are not measurements. CSWA weights are aperture-photometry-proportional stellar masses anchored on BGG SED; incomplete total-mass model.',
   data_refs={'cswa':'Wang 2022 Table 1, CDS and HST GO-15253','he':'Courbin 2011 Table 2, Sluse 2017 Table 4 and B1, Wang 2017 G1 stellar control as in he0435_joint_field_control','jackpot':'Gavazzi 2008 Table 1 and Fig.1; SZ lens-frame axes and SW companion; Smith & Collett 2021 for S2'},
   rows=rows)
(P/'environment_fixed_stretch.json').write_text(json.dumps(out,indent=2)+'\n')
for row in rows:print(row['lens'],row['scenario'],round(row['reduced_tidal_stretch_at_nearest_source'],6),row['train_RMS'],row['held_anchor_source_RMS'])
