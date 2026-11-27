"""Projected annular quadrupole sensitivity, no source-3 coefficient fitting."""
from jackpot_response_tools import *
from jackpot_settled_distributed_graph import optics
from scipy.interpolate import CubicSpline
from scipy.special import roots_legendre

u.stars[:]=10**np.array([10.85,11.27])
saved=json.loads((P/'jackpot_settled_distributed_graph.json').read_text())['Chabrier']['solutions']['total_above_ordinary']['held_out']
grid=np.geomspace(.01,45,500)
radial=CubicSpline(grid,np.concatenate([optics(g,saved['ell'])@np.array(saved['c']) for g in np.array_split(grid,30)]))
x,w=roots_legendre(32); x=(x+1)/2; w=w/2
bounds=(r0,r1)
def terms(r,a,b,turn=None):
    def intg(l,h,p):
        t=l[...,None]+(h-l)[...,None]*x
        z=(t-a)/(b-a)
        # Smooth, unit-peak projected convergence bump.
        switch=1 if turn is None else 2*(z-turn)
        return (h-l)*np.sum(w*16*z*z*(1-z)**2*t**p*switch,axis=-1)
    edge=np.clip(r,a,b)
    i=intg(np.full_like(r,a),edge,3)
    o=intg(edge,np.full_like(r,b),-1)
    # Projected m=2 Green solution to laplacian psi = 2 kappa.
    return -0.5*(i/r**2+r**2*o),i/r**3-r*o
def alpha(t,lo,hi,g,turn=None):
    r=np.linalg.norm(t,axis=1)
    P,d=terms(r,lo,hi,turn)
    er=t/r[:,None]; et=er[:,::-1]*[-1.,1.]
    C=er[:,0]**2-er[:,1]**2
    S=2*er[:,0]*er[:,1]
    return (d*(C*g[0]+S*g[1]))[:,None]*er+(2*P/r*(-S*g[0]+C*g[1]))[:,None]*et
# Derivative and angular average checks. At the inner boundary matches shear;
# beyond outer edge the potential is pure inverse-square multipole.
rr=np.linspace(.5,3.5,40)
psi,dp=terms(rr,*bounds)
assert np.allclose((terms(rr+1e-5,*bounds)[0]-terms(rr-1e-5,*bounds)[0])/2e-5,dp,atol=2e-9)
th=np.arange(100)*np.pi/50
xy=np.column_stack([np.cos(th),np.sin(th)])
for r in (r0,(r0+r1)/2,r1):
    assert abs(np.mean(np.einsum('ij,ij->i',alpha(r*xy,*bounds,[1,0]),xy)))<1e-15
pair=u.pair.copy()
def build(g,an,turn=None):
    def bplus(t):
        r=np.linalg.norm(t,axis=1)
        return basic(t)+(u.A0*radial(r*dk)/r**2)[:,None]*t+alpha(t,*an,g,turn)
    u.basic=bplus
    try:return ep.fn('none')
    finally:u.basic=basic

def run(an,kind,turn=None):
    def unpack(z):
        if kind=='ordinary_shear':return [0,0],z
        if kind=='tide_instead_of_shear':return z[:2],np.r_[0,0,z[2]]
        return z[:2],z[2:]
    def resid(z):
        g,p=unpack(z)
        return build(g,an,turn)(np.r_[0,0,p])
    lo,hi=np.array(u.lo[2:]),np.array(u.hi[2:])
    if kind=='tide_instead_of_shear':
        lo,hi=np.r_[-.25,-.25,lo[-1]],np.r_[.25,.25,hi[-1]]
    if kind=='both':
        lo,hi=np.r_[-.25,-.25,lo],np.r_[.25,.25,hi]
    seeds=[np.clip(np.r_[np.zeros(len(lo)-3),base[2:]],lo,hi), (lo+hi)/2]
    sol=min((least_squares(resid,z,bounds=(lo,hi),ftol=1e-11,xtol=1e-11,gtol=1e-11)
             for z in seeds),key=lambda q:q.cost)
    g,p=unpack(sol.x)
    f=build(g,an,turn)
    fit=np.r_[0,0,p]
    def root_equation(b):
        u.pair=np.vstack([pair[0],b])
        try:return build(g,an,turn)(fit,0,True)
        finally:u.pair=pair
    rt=root(root_equation,[1.,.75])
    valid=rt.success and np.linalg.norm(root_equation(rt.x))<1e-7
    return dict(g=list(g),ring_rms_mas=1000*np.linalg.norm(f(fit))/np.sqrt(14),
        held_out_source_gap_mas=1000*np.linalg.norm(f(fit,0,True)),
        held_out_B_error_mas=1000*np.linalg.norm(rt.x-pair[1]) if valid else None,
        B=rt.x.tolist() if valid else None)
if __name__=='__main__':
    mid=(r0+r1)/2
    out=dict(rings_arcsec=list(bounds), source3_radii_arcsec=np.linalg.norm(pair,axis=1).tolist(),
        conventional=run(bounds,'ordinary_shear'),variants={})
    assert abs(out['conventional']['held_out_B_error_mas']-saved['forward']['B_error_mas'])<.01
    for name,ends in [('whole_band',bounds),('inner_half',(r0,mid)),('outer_half',(mid,r1))]:
        out['variants'][name]={kind:run(ends,kind) for kind in ('tide_instead_of_shear','both')}
    (P/'jackpot_annular_tide.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
