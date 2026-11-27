"""No S3 fit: literature priors, stellar-only profiles and diagnostic mass floor."""
import json
import numpy as np
from scipy.optimize import nnls
import jackpot_physical_geometry as geo
P=geo.P
ep,u,cw=geo.ep,geo.u,geo.cw
def mag(x):return float(np.linalg.norm(x))
def screen(geom,fit):
    geo.set_up(geom,True)
    f=ep.fn('separate')
    assert np.isclose(np.linalg.norm(f(fit))*1000/np.sqrt(14),saved[geom]['separate']['inner_rms_mas'])
    p3,dy=f(fit,0,'rays')
    r=np.linalg.norm(dy,axis=1)
    assert np.all(r>0)
    dk=geo.angular_d(u.z2,geom)*u.asc
    rK=r*dk
    dst=(p3[0]-p3[1])*1000
    w=ep.W[u.z2,u.z3]
    unit=dy/r[:,None]
    k=1000*w*4*cw.G*1e9/(cw.c**2*u.asc)
    assert np.allclose(dst,saved[geom]['separate']['outer']['0'],atol=1e-8)
    sigma={}
    for v in [0,30,45,60,75,80,150]:
        sh=1000*w*4*np.pi*(v/cw.c)**2/u.asc*(unit[0]-unit[1])
        assert np.allclose(dst-sh,f(fit,v,True)*1000,atol=1e-8)
        sigma[str(v)]=dict(residual_mas=mag(dst-sh),shift_mas=mag(sh),mass_in_ray_cylinders_Msun=(np.pi*v*v*rK/cw.G).tolist())
    stars={}
    for lm in [8.5,9.5]:
        stars[str(lm)]={}
        for a in [0,0.5,1,2]:
            proj=10**(lm-9)*rK**2/(rK**2+a*a)
            g=k*proj[:,None]*unit/rK[:,None]
            sh=g[0]-g[1]
            stars[str(lm)][str(a)]=dict(shift_mas=mag(sh),residual_mas=mag(dst-sh))
    # Diagnostic only: what if the masses at both ray radii are varied?
    # Monotone M2D for circular, nonnegative Sigma demands M_far >= M_near.
    A=k*(unit/rK[:,None]).T*np.array([1.,-1.])
    i,j=np.argsort(rK)
    B=np.column_stack((A.sum(axis=1),A[:,j]))
    x,err=nnls(B,dst);ideal=np.linalg.solve(A,dst)
    return dict(impact_kpc=rK.tolist(),base_vec_mas=dst.tolist(),sis=sigma,stars=stars,
                exact_closure_unconstrained_cylinders_1e9_Msun=ideal.tolist(),
                best_possible_monotonic_circular_aperture_diag_mas=float(err),
                necessary_total_mass_1e9_for_exact_closure_if_circular_positive=mag(dst)/(k*sum(1/rK)),
                total_stellar_only_upper_shift_mas=k*10**.5*sum(1/rK))
if __name__=='__main__':
    saved=json.loads((P/'jackpot_physical_geometry.json').read_text())
    ans={g:screen(g,np.array(saved[g]['separate']['fit'])) for g in ['closed_R1','same_expansion_flat']}
    (P/'jackpot_s2_photometric_screen.json').write_text(json.dumps(ans,indent=2)+'\n')
    print(json.dumps(ans,indent=2))
