"""Same-geometry annular quadrupole bound and steady-speed Fourier check."""
from jackpot_annular_tide import *
from scipy.integrate import quad
from scipy.optimize import brentq
a,b=bounds
i,o=sorted(np.linalg.norm(pair,axis=1))
d=json.loads((P/'jackpot_ring_differential.json').read_text())
W=ep.W[u.z0,u.z3]
extremal={k:1000*W*u.A0*v['added_excess_Msun']*(b*b-a*a)/o**3 for k,v in d['models'].items()}
# Extremal verification using two antiphasic point-like angular components at the edges.
wi=a*a/(a*a+b*b); wo=1-wi
assert abs(-wi/a**2+wo/b**2)<1e-14
assert np.isclose(-wi*a*a+wo*b*b,b*b-a*a)
# Frozen coherent flow arm. Compute its optical moments without a new fit.
g=np.array(json.loads((P/'jackpot_annular_tide.json').read_text())['variants']['whole_band']['both']['g'])
r=a+(b-a)*x
dMdr=dk*radial(r*dk,1)
k2_over_r=(u.A0*.75*.5*dMdr*16*x*x*(1-x)**2/(2*r*r))
I=(b-a)*np.sum(w*k2_over_r)
O=(b-a)*np.sum(w*k2_over_r*r**4)
# Values in arcsec, before lens-equation image amplification.
frozen_inner_bend_mas=W*1000*i*I
frozen_outer_bend_mas=W*1000*O/o**3
assert a**4 < O/I < b**4
assert 0<frozen_outer_bend_mas < extremal['Chabrier']
# Stronger bound when the fixed Chabrier circular mass map is retained.
def dMdr_scalar(r):return float(dk*radial(r*dk,1))
assert min(dMdr)>0
def weighted_mass(lo,hi):
    return quad(lambda r:dMdr_scalar(r)/r**2,lo,hi,epsrel=2e-10)[0]
half=weighted_mass(a,b)/2
switch=brentq(lambda s:weighted_mass(a,s)-half,a,b)
def out_m(lo,hi):return quad(lambda r:dMdr_scalar(r)*r*r,lo,hi,epsrel=2e-10)[0]
outer_bound=out_m(switch,b)-out_m(a,switch)
dual=quad(lambda r:dMdr_scalar(r)*abs(r*r-switch**4/r**2),a,b,points=[switch],epsrel=2e-10)[0]
assert np.isclose(outer_bound,dual,rtol=2e-9)
tight_bend=1000*W*u.A0*outer_bound/o**3
assert 0<tight_bend<extremal['Chabrier']
angles=np.linspace(0,2*np.pi,4096,endpoint=False)
fourier={}
for e in (.2,.5,-.5):
    flux=1.0
    v=1+e*np.cos(2*angles)
    S=flux/v
    q=-e/(1+np.sqrt(1-e*e))
    for n in range(1,6):
        assert np.isclose(np.mean(S*np.cos(2*n*angles))/S.mean(),q**n,atol=1e-14)
    fourier[str(e)]=dict(q2=q,q4=q*q) # complex moments, not cosine series prefactors
out=dict(angular_radii_arcsec=[i,a,b,o],reduction=W,
    fixed_monopole_max_direct_bend_mas=tight_bend,
    fixed_monopole_pure_m2_max_direct_bend_mas=tight_bend/2,
    fixed_monopole_optimal_phase_switch_arcsec=switch,
    zero_inner_tide_bound_direct_bend_mas=extremal,
    frozen_flow_m2_direct_bend_mas_at_B_A=[frozen_inner_bend_mas,frozen_outer_bend_mas],
    frozen_flow_outer_to_inner_moment_arcsec4=O/I,constant_flux_speed_moments=fourier)
(P/'jackpot_annular_moment_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(out)
