"""Conditional paired-history control, not a derived galactic evolution law."""
import json
from pathlib import Path
import numpy as np
from scipy.fft import fftfreq, rfftfreq, irfftn, fft2, ifft2
from scipy.ndimage import map_coordinates

# All quantities below are normalized. The positive relaxation law is a toy.
# Length scale for stellar deprojection = 5 kpc; ell/scale=1.
SCALES=np.array([[.066,.50],[.082,6.05]])*3.685968242/5.
WEIGHTS=10**np.array([11.13,11.52]); WEIGHTS/=WEIGHTS.sum()
xyg=np.linspace(-3.0,3.0,33)
x,y=np.meshgrid(xyg,xyg,indexing='ij')
take=(np.hypot(x,y)>=.75)&(np.hypot(x,y)<=3.)
obs=np.column_stack([x[take],y[take]])
def run(n,Lbox, v,stop, source_positions=(0,0), export=False, uniform_centered=False):
    d=Lbox/n
    k=2*np.pi*fftfreq(n,d)
    kz=2*np.pi*rfftfreq(n,d)
    kx=k[:,None,None]
    kk=np.sqrt(kx*kx+k[None,:,None]**2+kz[None,None,:]**2)
    AA=kk**2*(1+kk**2)
    # Suppress box mean; a fixed capture profile moves with the pin. Tiny
    # stellar spectral taper regularizes the same periodic discretization.
    AA[0,0,0]=1.
    cloud=np.exp(-.5*(kk*.35)**2)
    S=np.zeros_like(kk)
    for (a,b),f in zip(SCALES,WEIGHTS):
        S+=f*np.exp(-a*kk)*(-np.expm1(-(b-a)*kk))/np.where(kk>0,(b-a)*kk,1.)
    S*=np.exp(-.5*(kk*.18)**2)
    S[0,0,0]=0.
    cloud[0,0,0]=0.
    pp=cloud/AA*.5*np.exp(-1j*kx*source_positions[0])
    ss=S/AA*.5*np.exp(-1j*kx*source_positions[1])
    def dz(h):
        h=h.copy()
        # Remove derivative Nyquist slice.
        h[...,-1]=0.
        return np.fft.fftshift(irfftn(1j*kz[None,None,:]*h,s=(n,n,n),axes=(0,1,2)))
    def screen(g,f=None):
        W=.5*g*g if f is None else g*f
        v=fft2(W.sum(axis=2)*d)
        kclean=k.copy(); kclean[n//2]=0
        return np.stack([ifft2(1j*kk*v).real for kk in [kclean[:,None],kclean[None,:]]])
    def sample(map_,points=obs):
        coords=(points.T/d+n/2.)
        return np.stack([map_coordinates(c,coords,order=3,mode='grid-wrap') for c in map_],axis=-1).ravel()
    def state(sign):
        # Until time -stop, constant drift arriving at today's position; from
        # -stop until today it stays there. Signed phase comes from retarded solve.
        if uniform_centered:
            # Uniform response time, retaining the same static shape solve.
            # Translate only the pin response back to its moment centroid.
            lag=sign*kx*v
            persistence=np.exp(-stop)
            ph=np.exp(-1j*persistence*lag)
            return ss+pp*ph*(1-persistence+persistence/(1-1j*lag))
        mh=pp*AA/(AA-1j*sign*kx*v)
        return ss+pp+(mh-pp)*np.exp(-AA*stop)
    g0=dz(pp+ss)
    pmap=screen(dz(state(1.)))
    mmap=screen(dz(state(-1.)))
    static=screen(g0)
    if export:
        return dict(spacing=d,odd=(pmap-mmap)/2,static=static)
    plus=sample(pmap)
    minus=sample(mmap)
    st=sample(static)
    odd=(plus-minus)/2
    # Separate first derivatives for shifts of pin and stars, along both axes.
    shifts=[sample(screen(g0,dz(-1j*direction*obj))) for obj in [pp,ss]
             for direction in [kx,k[None,:,None]]]
    xy=obs
    affine=[np.tile(a,len(xy)) for a in [[1.,0.],[0.,1.]]]+[
        xy.ravel(), np.column_stack([xy[:,0],-xy[:,1]]).ravel(), xy[:,::-1].ravel()]
    # Orthogonalize in nested order, avoiding nearly-null lattice artifacts.
    common=[shifts[0]+shifts[2],shifts[1]+shifts[3],*affine]
    y=odd.copy()
    basis=[]
    def remove(columns):
        nonlocal y
        for column in columns:
            v=column/np.linalg.norm(column)
            for _ in range(2):
                for z in basis:
                    v=v-z*(z@v)
            if np.linalg.norm(v)<1e-7:continue
            z=v/np.linalg.norm(v)
            basis.append(z)
            y=y-z*(z@y)
        return float(np.linalg.norm(y)/np.linalg.norm(st))
    after_common=remove(common)
    after_independent=remove(shifts[:2])
    assert after_independent<=after_common+1e-14
    if v==0:
        assert np.array_equal(plus,minus)
    else:
        # Reflection across the axis perpendicular to the drift.
        reflet=sample(screen(dz(state(1.))),obs*np.array([-1.,1.])).reshape(-1,2)*[-1.,1.]
        assert np.linalg.norm(minus-reflet.ravel())/np.linalg.norm(st)<4e-5
    return dict(odd=float(np.linalg.norm(odd)/np.linalg.norm(st)),
        after_common_shift=after_common,
        after_independent_shifts=after_independent, nuisance_rank=len(basis))
if __name__=='__main__':
    out={}
    for name,v,stop in [('static',0,0),('small_drift',.08,0),('larger_drift',.24,0),
                        ('stopped_same_position_and_velocity',.24,.1),('stopped_longer',.24,1.)]:
        results=[run(96,24,v,stop),run(144,24,v,stop),run(180,30,v,stop)]
        out[name]=dict(drift=v,stop=stop,grid=results)
        print(name,results,flush=True)
    assert out['stopped_same_position_and_velocity']['grid'][1]['after_independent_shifts']>0
    assert out['stopped_longer']['grid'][1]['odd']<out['stopped_same_position_and_velocity']['grid'][1]['odd']
    (Path(__file__).parent/'jackpot_moving_pin_history.json').write_text(json.dumps(out,indent=2)+'\n')
