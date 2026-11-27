"""ABC-only empirical PSFs; freeze red D displacement and transfer in sky coordinates."""
import sys,itertools,json
import numpy as np
from pathlib import Path
from scipy.ndimage import map_coordinates
from scipy.optimize import least_squares,minimize
from scipy.signal import fftconvolve
from score import read,design,invfit,moff,th
WAVES=['f115w','f150w','f277w','f356w']
EE={'f115w':.134,'f150w':.134,'f277w':.209,'f356w':.246}
GROUPS=[(0,1,2),(0,1),(0,2),(1,2)]
def psf(d,t):
  x,y=np.moveaxis(d,-1,0);c,s=np.cos(t[3]),np.sin(t[3]);X=x*c+y*s;Y=-x*s+y*c
  core=moff(np.hypot(X,Y/t[2]),t[1],t[0])
  r=np.hypot(x,y);phi=np.arctan2(y,x)
  wing=moff(r,1.85,t[5])
  mod=1+(t[6]*np.cos(6*phi)+t[7]*np.sin(6*phi))*r*r/(r*r+.012**2)
  return (1-t[4])*core+t[4]*wing*mod
def calibrate(I,X,nuc,pix,good,band):
  delta=X[:,:,None,:]-nuc
  rn=np.linalg.norm(delta,axis=-1)
  F=max(.044,.0325*int(band[1:-1])/100)
  pts=[]
  for j in range(3):
   m=good&(rn[...,j]<.58)&(rn[...,3]>.70)
   z=delta[...,j,:][m]; xx,yy=z.T
   bg=np.c_[np.ones(len(z)),xx,yy,xx*xx,xx*yy,yy*yy]
   y=I[m]; peak=np.max(y)
   # Wing-sensitive relative weights, capped to retain diffuse-background leverage.
   rn0=rn[...,j][m];e=np.maximum(.0025, .12*moff(rn0,2.5,F))
   pts.append((z,bg,y/peak,e,rn0))
  def predict(t,i):
   z,bg,y,e,R=pts[i]; v=np.c_[psf(z,t),bg]
   bb=np.linalg.lstsq(v/e[:,None],y/e,rcond=None)[0]
   return (v@bb-y)/e,bb
  sols={}
  for g in GROUPS:
   init=[F,2.8,.93,0,.035,1.8*F,0,0]
   lo=[.60*F,1.3,.65,-np.pi,.002,1.02*F,-.44,-.44]
   hi=[1.65*F,6,1.43,np.pi,.37,5*F,.44,.44]
   def f(t):
    return np.r_[np.concatenate([predict(t,j)[0] for j in g]),.1*(t[2]-1),.1*t[6:]]
   t=least_squares(f,init,bounds=(lo,hi),loss='soft_l1',f_scale=.4,max_nfev=240).x
   d=np.arange(-1.575,1.576,.01);a=np.stack(np.meshgrid(d,d),axis=-1);K=psf(a,t)
   rs=np.linalg.norm(a,axis=-1);enc=[float(K[rs<z].sum()/K.sum()) for z in [EE[band],.4]]
   rm=[]
   for j in range(3):
    r,b=predict(t,j); mask=(pts[j][-1]>.10)&(pts[j][-1]<.46)
    rm.append(float(np.sqrt(np.mean(r[mask]**2))))
   sols[g]=(t,dict(t=t.tolist(),encircled_at_nominal_R80_and_point4=enc,ABC_wing_residuals=rm))
  return sols
def run(band):
 I,X,nuc,pix,good,sig=read(Path(band+'.fits'))
 E,N=X[...,0],X[...,1]; R=np.hypot(E,N)
 deltas=X[:,:,None,:]-nuc
 dn=np.linalg.norm(deltas,axis=-1); near=dn.argmin(axis=-1); ds=dn.min(axis=-1)
 jc,ic=np.array(X.shape[:2])//2
 # Sky in [E,N], image coordinates in [x,y] pixels.
 J=np.column_stack((X[jc,ic+1]-X[jc,ic],X[jc+1,ic]-X[jc,ic]))
 inv=np.linalg.inv(J)
 y,x=np.indices((41,41))-20
 skyK=np.stack([x,y],axis=-1)@J.T
 sols=calibrate(I,X,nuc,pix,good,band);rows={};maps={}
 # Use same F356 preselected source node sets for every band (not short-band residuals).
 frozen=json.loads(Path('f356w_matched.json').read_text())
 for anchor,rad in itertools.product([False,True],[5,65]):
  B,_,_=design(X,near,3,anchor,rad);r=np.linalg.norm(B,axis=-1)
  for g,(t,_) in sols.items():
   pk=psf(skyK,t);pk/=pk.sum();cn=lambda z:fftconvolve(z,pk,mode='same')
   f0=.12 if band=='f356w' else .095 if band=='f277w' else .05
   for w in [.043,.065]:
    nodes=next(np.array(c['nodes']) for c in frozen if c['anchor']==anchor and c['g4']==rad and c['width']==w and c['psf']==.93 and c['held']=='D')
    shp=np.array([cn(np.exp(-.5*np.sum((B-c)**2,axis=-1)/w**2)) for c in nodes])
    rg=shp.max(axis=0)
    full=good&(R>.46)&(ds>max(.17,1.75*f0))&(ds<.75)&(r<.33)
    hold=(near==3)&full
    chk=hold&(rg>.21)
    if chk.sum()<20:continue
    ref=[np.ones_like(E),E,N]
    for ax,phi in [(.82,174.8),(1,0)]:
     ph=np.radians(phi);x=E*np.sin(ph)+N*np.cos(ph);y=E*np.cos(ph)-N*np.sin(ph)
     ref += [cn(np.exp(-(x*x+(y/ax)**2)/(2*s*s))) for s in (.15,.28,.53,1.,2.)]
    for j in range(4):
     ref.extend([psf(deltas[...,j,:],t),moff(dn[...,j],2.5,.18),moff(dn[...,j],3,.32)])
    nfg=len(ref)
    ref += [cn(np.exp(-np.sum((B-c)**2,axis=-1)/(2*.205**2))) for c in itertools.product([-.4,-.2,0,.2,.4],repeat=2)]
    n=len(ref)
    A=np.moveaxis(np.array(ref+list(shp)),0,-1)
    # Matched D-host sector excluded from all fits; protected through the convolved kernel footprint.
    train=good&(ds>max(.095,1.4*f0))&~(hold | ((near==3)&(rg>.025)))
    # Don't fit D's point amplitude from the scored region. Model D point terms from remaining train pixels.
    y=I[train]/sig[train];V=A[train]/sig[train,None]
    ridge=np.r_[np.full(n,.004),np.full(len(shp),.10)]
    fit=invfit(V,y,ridge);fit0=invfit(V[:,:n],y,ridge[:n])
    fg=A[chk,:nfg]@fit[:nfg]
    H=np.einsum('yxk,k->yx',A[...,nfg:],fit[nfg:])
    Z=A[chk,:3]/sig[chk,None]
    Q=np.linalg.qr(Z,mode='reduced')[0]
    proj=lambda v,Q=Q:v-Q@(Q.T@v)
    yw=proj((I[chk]-fg)/sig[chk]); yw0=proj((I[chk]-(A[chk,:n]@fit0))/sig[chk]);iy,ix=np.where(chk)
    def pred(s, H=H,iy=iy,ix=ix,inv=inv,proj=proj,wt=sig[chk]):
     dx,dy=inv@(np.array(s)/1000)
     return proj(map_coordinates(H,[iy-dy,ix-dx],order=3)/wt)
    p0=pred((0,0));null=np.mean((yw-p0)**2)
    def fitshift(obs):
     def fun(s):return np.mean((obs-pred(s))**2)
     opt=minimize(fun,[0.,0.],method='L-BFGS-B',bounds=[(-60,60)]*2,options={'ftol':1e-12,'gtol':1e-8})
     return opt.x,float(opt.fun)
    s,loss=fitshift(yw)
    # Paired injection controls: test ideal and real-residual changes independently.
    inj=np.array([15.,-15.])
    recovered,_=fitshift(pred(inj))
    recovered_real,_=fitshift(yw+pred(inj)-p0)
    tag=(anchor,rad,g,w)
    rows[tag]=dict(anchor=anchor,rad=rad,ABC_psf=list(g),w=w,count=len(iy),free_shift_EN_mas=s.tolist(),norm_null=float(null),norm_smooth=float(np.mean(yw0*yw0)),free_gain=float(1-loss/null),ideal_shift_injection_error_mas=float(np.linalg.norm(recovered-inj)),with_residual_shift_injection_delta=recovered_real.tolist(),forced_injection_EN_mas=inj.tolist())
    maps[tag]=(yw,pred)
 print(band,len(rows),flush=True)
 return rows,maps,{','.join(map(str,g)):s for g,(t,s) in sols.items()}
if __name__=='__main__':
 from concurrent.futures import ThreadPoolExecutor
 with ThreadPoolExecutor(4) as exe: all=dict(zip(WAVES,exe.map(run,WAVES)))
 ref=all['f356w'][0]
 out={}
 for b,(rr,mp,p) in all.items():
  rr={k:a for k,a in rr.items() if k in ref}
  for k,a in rr.items():
   s=ref[k]['free_shift_EN_mas'];y,pred=mp[k]
   a['red_shift_EN_mas']=s;a['red_transfer_improvement']=float(1-np.mean((y-pred(s))**2)/a['norm_null'])
  out[b]=dict(rows=list(rr.values()),psfs=p)
 Path('empirical_transfer.json').write_text(json.dumps(out,indent=2)+'\n')
 for b,v in out.items():
  for a in [False,True]:
   r=[i for i in v['rows'] if i['anchor']==a]
   g=np.array([x['red_transfer_improvement'] for x in r])
   print(b,a,len(r),'median,range,p',np.median(g),g.min(),g.max(),(g>0).sum(),'shift',np.median([x['free_shift_EN_mas'] for x in r],axis=0),'inj max',max(x['ideal_shift_injection_error_mas'] for x in r))
