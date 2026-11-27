"""Leading stationary Kerr spin control at fixed ordinary compact monopole."""
from jackpot_response_tools import *
from jackpot_settled_distributed_graph import optics
from r1_background_geometry import G,speed
from scipy.interpolate import CubicSpline

u.stars[:]=10**np.array([10.85,11.27])
frozen=json.loads((P/'jackpot_settled_distributed_graph.json').read_text())['Chabrier']['solutions']['total_above_ordinary']['held_out']
grid=np.geomspace(.01,45,650)
vals=np.concatenate([optics(z,frozen['ell'])@np.array(frozen['c']) for z in np.array_split(grid,30)])
radial=CubicSpline(grid,vals)
pair=u.pair.copy()
def build(spin=(0.,0.)):
    d=np.array(spin)
    def added(t):
        r=np.linalg.norm(t,axis=1)
        s=(u.A0*radial(r*dk)/r**2)[:,None]*t
        # Derivative of a Schwarzschild point deflection under translation;
        # d is the effective Kerr displacement in arcseconds.
        j=2*(t@d)[:,None]*t/r[:,None]**4-d/r[:,None]**2
        return basic(t)+s+u.A0*Mh*j
    u.basic=added
    try:return ep.fn('none')
    finally:u.basic=basic
def calibrate(d):
    f=build(d)
    return min([least_squares(lambda p:f(np.r_[0,0,p]),z,bounds=(u.lo[2:],u.hi[2:]),
                          ftol=1e-12,xtol=1e-12,gtol=1e-12)
            for z in [base[2:],[.08,.08,.3],[0,0,.05]]],key=lambda a:a.cost).x
def trace(d,x):
    def F(B):
        u.pair=np.vstack([pair[0],B])
        try:return build(d)(np.r_[0,0,x],0,True)
        finally:u.pair=pair
    rr=root(F,[1,.75],tol=1e-11)
    assert np.linalg.norm(F(rr.x))<1e-9
    return rr.x
p0=calibrate(np.zeros(2))
B0=trace(np.zeros(2),p0)
assert np.linalg.norm(B0-frozen['forward']['B_pred'])<2e-6
def cols(h,refit):
    def run(d):return trace(d,calibrate(d) if refit else p0)
    return np.column_stack([(run(d*h)-run(-d*h))/(2*h) for d in np.eye(2)])
out={}
for refit in (False,True):
    D=cols(.0005,refit)
    assert np.allclose(D,cols(.001,refit),rtol=2e-2,atol=2e-5)
    out[str(refit)]=float(np.linalg.svd(D,compute_uv=False)[0])
b=np.array([r0,r1,*np.linalg.norm(pair,axis=1)])*dk
cases={}
for M in (Mh,8e9):
    rg=1000*G*M/speed**2
    drift=rg/dk*(M/Mh)
    cases[str(M)]=dict(rg_pc=1000*rg, max_unreduced_bend_mas=(4*(rg/b)**2*206264806.247).tolist(),
        forecast_mas_fixed=out['False']*drift*1000,
        forecast_mas_refit=out['True']*drift*1000)
d=dict(radii_kpc=b.tolist(), gain_from_spin_translation=out, cases=cases)
(P/'jackpot_kerr_spin_control.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps(d,indent=2))
