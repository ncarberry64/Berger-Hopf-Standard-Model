"""Transfer of frozen trial odd-wake shape into the archived Jackpot ray map.
No physical orbit/strength calibration or selection using source 3."""
from jackpot_response_tools import *
from jackpot_moving_pin_history import run
from jackpot_settled_distributed_graph import optics
from scipy.ndimage import map_coordinates

u.stars[:]=10**np.array([10.85,11.27])
saved=json.loads((P/'jackpot_settled_distributed_graph.json').read_text())['Chabrier']['solutions']['total_above_ordinary']['held_out']
cal_ell=saved['ell']
c0=np.array(saved['c'])
early=np.vstack(u.observed[:5])
def static_profile(rad):return optics(np.asarray(rad),cal_ell)@c0
# Cache expensive static monopole interpolation on range used by the rays.
from scipy.interpolate import CubicSpline
radius=np.geomspace(.01,50,2500)
radial=CubicSpline(radius,np.concatenate([static_profile(q) for q in np.array_split(radius,80)]),extrapolate=False)
def shape(t):
    r=np.linalg.norm(t,axis=1)
    assert min(r*dk)>.01 and max(r*dk)<50
    return (u.A0*radial(r*dk)/r**2)[:,None]*t
def build(add):
    u.basic=lambda t:basic(t)+shape(t)+add(t)
    try:return ep.fn('none')
    finally:u.basic=basic
def refit(add):
    f=build(add)
    bounds=(u.lo[2:],u.hi[2:])
    sol=min((least_squares(lambda x:f(np.r_[0,0,x]),xx,bounds=bounds,ftol=1e-11,xtol=1e-11,gtol=1e-11)
            for xx in [base[2:],[.08,.08,.3],[0,0,.05]]),key=lambda a:a.cost)
    return sol.x
pair=u.pair.copy()
def evaluate(add,x):
    def F(t):
        u.pair=np.vstack([pair[0],t])
        try:return build(add)(np.r_[0,0,x],0,True)
        finally:u.pair=pair
    rr=root(F,[1.,.75])
    assert rr.success and np.linalg.norm(F(rr.x))<1e-7
    return rr.x
zero=lambda t:np.zeros_like(t)
x0=refit(zero)
B0=evaluate(zero,x0)
assert np.linalg.norm(B0-np.array(saved['forward']['B_pred']))<1e-6
def experiment(n,box):
    res=run(n,box,.24,.1,export=True)
    def interp(mm,t):
        coords=(t.T*dk/5/res['spacing'] + n/2)
        return np.column_stack([map_coordinates(component,coords,order=3,mode='grid-wrap') for component in mm])
    rows=[]
    for ang in range(0,360,45):
        th=np.deg2rad(ang)
        M=np.array([[np.cos(th),-np.sin(th)],[np.sin(th),np.cos(th)]])
        sm=lambda t:interp(res['static'],t@M)@M.T
        # Fixed RMS ratio at early knots gives a nominal angular unit; no
        # physical favoring of orientation/strength, no source-3 amplitude.
        scale=np.linalg.norm(shape(early))/np.linalg.norm(sm(early))
        def add(t):
            # Positive radial map convention in the lens equation.
            return -scale*interp(res['odd'],t@M)@M.T
        fit=refit(add)
        b_refit=evaluate(add,fit)
        b_fixed=evaluate(add,x0)
        f=build(add)
        rows.append(dict(angle_deg=ang,normalization=scale,nuisance=fit.tolist(),
                         inner_ring_rms_mas=float(1000*np.linalg.norm(f(np.r_[0,0,fit]))/np.sqrt(14)),
                         fixed_B_shift_mas=(1000*(b_fixed-B0)).tolist(),
                         refitted_B_shift_mas=(1000*(b_refit-B0)).tolist(),
                         B_error_mas=float(1000*np.linalg.norm(b_refit-pair[1]))))
    return rows
rows={str(n):experiment(n,L) for n,L in [(144,24),(180,30)]}
assert np.allclose([x['refitted_B_shift_mas'] for x in rows['144']],
                   [x['refitted_B_shift_mas'] for x in rows['180']],rtol=.15,atol=.7)
out=dict(baseline_B=B0.tolist(), baseline_error_mas=1000*np.linalg.norm(B0-pair[1]),
    baseline_inner_ring_rms_mas=float(1000*np.linalg.norm(build(zero)(np.r_[0,0,x0]))/np.sqrt(14)),grids=rows)
(P/'jackpot_moving_pin_prediction.json').write_text(json.dumps(out,indent=2)+'\n')
for row in rows['180']: print(row)
