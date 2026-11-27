"""Matched-source forward holdouts of archival, calibrated optical surface brightness."""
from pathlib import Path
import itertools,json,sys
import numpy as np
from scipy.optimize import least_squares
from scipy.signal import fftconvolve
from scipy.ndimage import map_coordinates
from scipy.linalg import cho_factor,cho_solve
from astropy.io import fits
from astropy.wcs import WCS
P=Path.cwd()
source=P.parent/'resolved_galaxies/resolved_control.py'; ns={'__file__':str(source)}
exec(source.read_text().split('empty=tuple(catalog)')[0],ns)
th,Dist=ns['theta'],ns['Dist']
cat,grp=ns['catalog'],ns['grp']
z1,zs=ns['zl'],ns['zs']; xr=ns['xr']
def baseline(t,rad=15):
 d=lambda a,b:Dist(a,b,'R1')
 gal=dict(cat); gal['group']=(z1,tuple(grp),ns['mass']-10**11.1-cat['G4'][2]); gal['main']=(z1,(0.,0.),10**11.1)
 tab={}
 def trace(t,end):
  old={}; t=np.asarray(t)
  for z,items in tab.items():
   if z>=end:break
   zz=t.copy()
   for z0,al in old.items(): zz-=al*d(z0,z)/d(0,z)
   K=d(0,z)*xr
   v=np.zeros_like(zz)
   for key,C,mc in items:
    X=zz-C; R=np.maximum(K*np.linalg.norm(X,axis=-1),1e-12); g=ns['sersic']
    if key=='group': mu=ns['group_cyl'](R)/ns['group_sph'](1.385)
    elif key=='main': mu=g(R,3.51,.0044*np.sqrt(.82))
    elif key=='G1':
     w=1/(1+10**(-.4*(18.8-18.7)));mu=w*g(R,4,.37*K)+(1-w)*g(R,1,1.67834699*.67*K)
    elif key=='G4':mu=1-np.maximum(1-(R/(rad/1000))**2,0)**1.5
    else:mu=R**2/(R**2+.002**2)
    v+=4*ns['G']/ns['c']**2*mc*K/xr*(mu/R**2)[...,None]*X
   old[z]=v
  return t-sum(al*d(z0,end)/d(0,end) for z0,al in old.items())
 for z in sorted({v[0] for v in gal.values()}):tab[z]=[(k,trace(a,z),M) for k,(z0,a,M) in gal.items() if z0==z]
 val=trace(t,zs)
 # Obtain exactly the linear derivative with respect to stellar scale via symmetric finite difference of
 # the analytic stellar-only angular deflection for the base fit; multiplane model remains frozen.
 r=np.maximum(np.linalg.norm(t,axis=-1),1e-8);D=Dist(0,z1,'R1')*xr 
 ds=4*ns['G']/ns['c']**2*10**11.1/(xr*D)*Dist(z1,zs,'R1')/Dist(0,zs,'R1') * ns['sersic'](r*D,3.51,.0044*np.sqrt(.82)) /r**2
 return val,np.stack([ds[...,None]*t,t*np.array([1,-1]),t[...,::-1]],axis=-1)

def read(f):
 with fits.open(f) as h:
  I=np.array(h['SCI'].data,dtype=float); W=h['WHT'].data.copy(); err=h['ERR'].data.copy()
  w=WCS(h['SCI'].header)
 Y,X=np.indices(I.shape);r,d=w.all_pix2world(X,Y,0); C=np.cos(np.radians(-12.28745))
 XY=np.stack([(r-69.5619)*C*3600,(d+12.28745)*3600],axis=-1)
 p0=np.array([1.26,.195]);reg=[]
 for cp in th+p0:
  m=(np.linalg.norm(XY-cp,axis=-1)<.14)&(W>0)&np.isfinite(I)
  a=XY[m];v=I[m]; pos=a[np.argmax(v)]
  def fun(x):return x[2]*np.exp(-.5*np.sum((a-x[:2])**2,axis=-1)/x[3]**2)+x[4]+(a-cp)@x[5:]
  res=least_squares(lambda x:fun(x)-v,np.r_[pos,v.max()-np.median(v),.025,np.median(v),0,0],bounds=(np.r_[cp-.14,0,.006,-np.inf,-np.inf,-np.inf],np.r_[cp+.14,np.inf,.12,np.inf,np.inf,np.inf]))
  reg.append(res.x[:2])
 reg=np.array(reg); off=(reg[:3]-th[:3]).mean(axis=0);XY-=off
 pix=np.sqrt(abs(np.linalg.det(w.pixel_scale_matrix)))*3600
 R=np.linalg.norm(XY,axis=-1)
 good=(R<2.65)&(W>0)&np.isfinite(I)&np.isfinite(err)&(err>0)
 blank=(R>2.45)&(W>0)&np.isfinite(I)
 noise=1.4826*np.median(abs(I[blank]-np.median(I[blank])))
 return I,XY,reg-off,pix,good,np.sqrt(err**2+noise**2)

def design(x,m,held,anchor,rad):
 y,U=baseline(x,rad); p,H=baseline(th,rad)
 j=[k for k in range(4) if k!=held]
 p0=p[j].mean(0);H0=H[j].mean(0)
 q=np.linalg.lstsq((H[j]-H0).reshape(-1,3),(p[j]-p0).ravel(),rcond=None)[0]
 b=y-U@q-p0+H0@q
 B0=p-H@q-p0+H0@q
 if anchor:b-=B0[m]
 return b,q,B0

def moff(R,b,f):return (1+(R/(f/(2*np.sqrt(2**(1/b)-1))))**2)**-b
def invfit(A,y,lam):
 norm=np.maximum(np.linalg.norm(A,axis=0),1e-8);S=A/norm
 Z=S.T@S+np.diag(lam)
 return cho_solve(cho_factor(Z),S.T@y)/norm

def run(f):
 I,X,nuc,pix,good,sig=read(f); print(f,pix,nuc-th,flush=True)
 E,N=X[...,0],X[...,1];R=np.hypot(E,N); dn=np.linalg.norm(X[:,:,None,:]-nuc,axis=-1); near=dn.argmin(axis=-1); ds=dn.min(axis=-1)
 band=f.stem; wave=int(band[1:-1])/100; fwhm=max(.043,.034*wave)
 rows=[]
 for held,anchor,rad in itertools.product(range(4),[False,True],[5,65]):
  B,Q,B0=design(X,near,held,anchor,rad); r=np.linalg.norm(B,axis=-1)
  for pf,wd in itertools.product([.93,1.12],[.043,.065]):
   F=fwhm*pf
   yy,xx=np.indices((35,35))-17
   pk=moff(np.hypot(xx,yy)*pix,2.7,F);pk/=pk.sum(); cn=lambda z:fftconvolve(z,pk,mode='same')
   # Geometrically common source support. No measured residual enters template selection.
   POS=np.array([p for p in itertools.product(np.arange(-.16,.161,.05333333333),repeat=2) if .048<np.linalg.norm(p)<.182])
   narrow=np.array([cn(np.exp(-np.sum((B-c)**2,axis=-1)/(2*wd**2))) for c in POS])
   clean=good&(R>.46)&(ds>max(.17,1.75*F))&(ds<.75)&(r<.33)
   S=[clean&(near==j) for j in range(4)]
   if min(m.sum() for m in S)<15:continue
   pow=np.array([[np.sum(t[m]**2) for t in narrow] for m in S])
   use=(pow.min(axis=0)/np.maximum(pow.max(axis=0),1e-30)>.13)&(pow.min(axis=0)>(.028/pix)**2)
   if use.sum()<4:continue
   shape=narrow[use]; widths=POS[use]
   # Keep only image patches belonging to shared source-plane leverage.
   M=[m&(shape.max(axis=0)>.21) for m in S]
   if min(m.sum() for m in M)<10:continue
   ref=[np.ones_like(E),E,N]
   for ax,phi in [(.82,174.8),(1,0)]:
    ph=np.radians(phi);x=E*np.sin(ph)+N*np.cos(ph);y=E*np.cos(ph)-N*np.sin(ph)
    for z in (.15,.28,.53,1.,2.):ref.append(cn(np.exp(-(x*x+(y/ax)**2)/(2*z*z))))
   for i in range(4):
    ref.extend(moff(dn[...,i],beta,z) for beta,z in [(2.7,F),(2.5,.18),(3,.32)])
   # Smooth common source outside compact templates. Fit jointly, never use held arc pixels.
   for c in itertools.product([-.4,-.2,0,.2,.4],repeat=2):
    ref.append(cn(np.exp(-np.sum((B-c)**2,axis=-1)/(2*.205**2))))
   # No sectors other than the held fold are excluded, but keep saturated/poorly sampled PSF centers out.
   ok=good&(ds>max(.095,1.40*F))
   train=ok&~(S[held] | ((near==held)&(shape.max(axis=0)>.025)))
   train &= np.isfinite(sig)
   chk=M[held]
   # Marginalize local signed affine background in held scoring to avoid spurious constant offsets.
   Z=np.stack([np.ones_like(R),E,N],axis=-1)[chk]
   n=len(ref); A=np.moveaxis(np.array(ref+list(shape)),0,-1)
   y=I[train]/sig[train]
   v=A[train]/sig[train,None]
   l=np.r_[np.full(n,.004),np.full(len(shape),.10)]
   beta=invfit(v,y,l)
   beta0=invfit(v[:,:n],y,l[:n])
   def score(im,pred):
    Z0=Z/sig[chk,None];v0=(im-pred)/sig[chk];v0-=Z0@np.linalg.lstsq(Z0,v0,rcond=None)[0]
    return np.mean(v0**2),v0
   q1,r1=score(I[chk],A[chk]@beta); q0,r0=score(I[chk],A[chk,:n]@beta0)
   # Shared synthetic compact perturbation for out-of-sample recovery with all nuisance fitted again.
   co=np.cos(np.arange(len(shape))*1.87); Y1=np.einsum('i,iyx->yx',co,shape)
   delta=invfit(v,Y1[train]/sig[train],l)
   _,recovery=score(Y1[chk],A[chk]@delta)
   _,signal=score(Y1[chk],0.)
   mon=1-np.linalg.norm(recovery)/np.linalg.norm(signal)
   # Score arbitrary common source shifts using held-only template derivative projected
   # against local plane. Body of the prediction is not recentered on arc pixels.
   model=np.zeros_like(I); model[ok]=A[ok]@beta
   signalmap=np.sum(A[...,n:]*beta[n:],axis=-1)
   eta=np.moveaxis(np.stack(np.gradient(signalmap)),0,-1)[chk]
   g=eta/sig[chk,None]
   zz=Z/sig[chk,None];g-=zz@np.linalg.lstsq(zz,g,rcond=None)[0]
   pshift=np.linalg.lstsq(g,r1,rcond=None)[0]*pix if np.linalg.cond(g)<20 else [np.nan]*2
   rows.append(dict(band=band,held='ABCD'[held],anchor=anchor,g4=rad,psf=pf,width=wd,nodes=widths.tolist(),samples=int(chk.sum()),baseline=float(q0),joint=float(q1),frac_gain=float((q0-q1)/q0),random_source_recovery=float(mon),injected_rms_nominal=float(np.sqrt(np.mean(signal**2))),held_local_shift_yx_mas=(np.array(pshift)*1000).tolist(),macro_miss_mas=float(np.linalg.norm(B0[held])*1000)))
  print(band,'ABCD'[held],anchor,rad,len(rows),flush=True)
 @np.vectorize
 def no(x):return x
 return rows
if __name__=='__main__':
 for f in [Path(a) for a in sys.argv[1:]] or list(sorted(P.glob('f*.fits'))):
  r=run(f);(P/(f.stem+'_results.json')).write_text(json.dumps(r,indent=2)+'\n')
