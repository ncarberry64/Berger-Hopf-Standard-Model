"""Settled spherical graph control using fixed stellar deprojection and separate pin."""
from functools import lru_cache
from jackpot_response_tools import *
from scipy.integrate import quad
from scipy.special import roots_legendre
from scipy.optimize import brentq
from r1_background_geometry import G,speed
R=np.array([r0,r1])*dk
A,T=a*dk,b*dk
UNIT=1e11
def point(r,L):
    z=r/L
    A=np.where(z<.01,z*z*(.5-z/3+z*z/8-z**3/30),-np.expm1(-z)-z*np.exp(-z))
    return A/r**2
def shell(r,s,L):
    z=np.minimum(r,s)/L
    y=r/L
    ext=np.exp(-np.abs(r-s)/L)*(-np.expm1(-2*s/L))/(2*s/L)
    outer=(1-ext*(1+y))/r**2
    d=np.where(z<.01,np.exp(-s/L)*z*(1/3+z*z/30+z**4/840),
        ((z-1)*np.exp(z-s/L)+(z+1)*np.exp(-z-s/L))/(2*z*z))
    return np.where(r>=s,outer,d/(s*L))
@lru_cache(None)
def nodes(n):
    x,w=roots_legendre(n); return .5*(x+1),.5*w
def dm(s):
    return (2/np.pi)*(T+A)*u.stars*s[...,None]**2/((T*T+s[...,None]**2)*(A*A+s[...,None]**2))
def stellar(r,L,n):
    r=np.asarray(r)[...,None]
    x,w=nodes(n)
    # Integrate in arctan radius at each observed profile's fixed scale.
    ret=np.zeros(r.shape[:-1])
    for i,scale in enumerate(A):
        cut=np.arctan(r/scale)
        for lo,hi in [(np.zeros_like(cut),cut),(cut,np.full_like(cut,np.pi/2))]:
            t=lo+(hi-lo)*x
            s=scale*np.tan(t)
            ret+=np.sum(w*(hi-lo)*scale/np.cos(t)**2*dm(s)[...,i]*shell(r,s,L),axis=-1)/UNIT
    return ret+Mh/UNIT*point(r[...,0],L)
def optics(rad,L,n=128):
    rad=np.asarray(rad)
    x,w=nodes(n)
    rr=rad[...,None]/np.cos(np.pi*x/2)
    D=stellar(rr,L,n)
    P=point(rr,L)
    pref=(speed**2/(4000*G))*rad*np.pi/2
    return np.stack([pref*np.sum(w*val,axis=-1) for val in (P*P,D*P,D*D)],axis=-1)
def check():
    for r,L in [(5.,2.),(7.,15.),(13.,60.),(5.,500.)]:
        direct=sum(quad(lambda s:float(dm(np.array(s)).sum())*shell(r,s,L)/UNIT,lo,hi,epsabs=1e-12)[0]
                   for lo,hi in ((0,r),(r,np.inf)))+Mh/UNIT*point(r,L)
        assert np.isclose(stellar(r,L,120),direct,rtol=2e-8)
        assert np.allclose(optics(R,L,128),optics(R,L,196),rtol=2e-6)
def scan():
    rows={}
    for tag, logs in [('Salpeter',[11.13,11.52]),('Chabrier',[10.85,11.27])]:
        u.stars[:]=10**np.array(logs); check()
        target[:]=np.array([M0-stars(r0)-Mh,M1-stars(r1)-Mh])
        ratios_needed=target[1]/target[0]
        # No scale choice uses S3. Report all predetermined scales.
        ells=np.unique(np.r_[np.geomspace(.1,1000,120),.5,2.,5.,10.,20.,50.,100.])
        ar=np.array([optics(R,ell) for ell in ells])
        ratios=ar[:,1,:]/ar[:,0,:]
        assert (np.diff(ratios,axis=1)>0).all()  # validates the full-response endpoint bracket on the grid
        assert (ar>0).all()
        rows[tag]=dict(required=ratios_needed,component_min=ratios.min(axis=0).tolist(),
            component_max=ratios.max(axis=0).tolist(),
            scale_at_component_max=ells[ratios.argmax(axis=0)].tolist(),solutions={})
        # core added to stars (PP,X), or stars added to a persistent pin (X,SS).
        # In the matched increment each case has only two independent coefficients.
        for name,ij in [('pin_added_to_stars',(0,1)),('stars_added_to_pin',(1,2)),('total_above_ordinary',(0,1,2))]:
            sols=[]
            for ell,mm in zip(ells,ar):
                if len(ij)==2:
                    i,j=ij
                    r=mm[1,[i,j]]/mm[0,[i,j]]
                    if not min(r)<ratios_needed<max(r):continue
                    ci=np.linalg.solve(mm[:,[i,j]],target)
                    assert min(ci)>0
                    c=np.zeros(3)
                    c[list(ij)]=ci
                    if name=='pin_added_to_stars':
                        p=np.sqrt(c[0]); s=c[1]/(2*p)
                    else:
                        s=np.sqrt(c[2]); p=c[1]/(2*s)
                else:
                    def shape(f): return np.array([(1-f)**2,2*f*(1-f),f*f])
                    def match(f):
                        m=mm@shape(f)
                        return m[1]/m[0]-ratios_needed
                    # Cross coefficient constrained by the squares of the two amplitudes.
                    if match(0)*match(1)>=0:continue
                    f=brentq(match,0,1)
                    c=shape(f)*(target[0]/(mm[0]@shape(f)))
                    p,s=np.sqrt(c[[0,2]])
                assert np.allclose(mm@c,target,rtol=1e-10)
                def prof(rad):
                    return optics(rad,ell)@c
                h=.0005
                def M(t):
                    r0t=r0*np.exp(t)
                    return stars(r0t)+Mh+prof(r0t*dk)
                m0=M(0); d=(M(h)-M(-h))/(2*h); dd=(M(h)+M(-h)-2*m0)/h**2
                eta=1+.5*(dd-3*d+2*m0)/(m0-d/2)
                sols.append(dict(ell=float(ell),eta=float(eta),c=c.tolist(),p=p,s=s))
            info=dict(count=len(sols),eta_range=[min(i['eta'] for i in sols),max(i['eta'] for i in sols)] if sols else None,rows=sols)
            # Test only the closest to the central published eta, and only if within its nominal band.
            if sols:
                sel=min(sols,key=lambda v:abs(v['eta']-.96))
                if abs(sel['eta']-.96)<=.02:
                    c=np.array(sel['c'])
                    ell=sel['ell']
                    forward=predict(lambda r:optics(r,ell)@c)
                    assert abs(forward['eta']-sel['eta'])<1e-7
                    radii=np.geomspace(.05,350,200)
                    gradients=sel['p']*point(radii,ell)+sel['s']*stellar(radii,ell,128)
                    info['held_out']=dict(**sel,peak_gradient_on_sample=float(gradients.max()),forward=forward)
            rows[tag]['solutions'][name]=info
    return rows
if __name__=='__main__':
    out=scan()
    (P/'jackpot_settled_distributed_graph.json').write_text(json.dumps(out,indent=2)+'\n')
    for t,d in out.items():print(t,{**d,'solutions':{k:{kk:vv for kk,vv in v.items() if kk!='rows'} for k,v in d['solutions'].items()}})
