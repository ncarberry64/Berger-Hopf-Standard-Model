"""Conditional matter/optical readout of a regular normal displacement.
No Jackpot parameters, physical bending amplitude, or permanent core metric inferred."""
import json
from pathlib import Path
from scipy.integrate import quad
import numpy as np

eta=np.diag([-1.,1.,1.,1.])
k=np.array([1.,0.,0.,1.])
u=np.array([1.,0.,0.,0.])
assert k@eta@k==0 and u@eta@u==-1
b=1.25
kappa=.12
def pi(x,z):return np.exp(-(x*x+z*z)/2)
def optical(K):
    # delta g=2 pi K. Transverse light ray impulse on a flat background.
    return quad(lambda z:-b*pi(b,z)*(k@K@k),-np.inf,np.inf,epsabs=1e-13)[0]
def linear_n(K,x,z):
    # Static diagonal exact optical index along z differentiated at eps=0.
    return pi(x,z)*(K[0,0]+K[3,3])
for name,K in [
    ('umbilic',kappa*eta),
    ('time_space_unequal',np.diag([-kappa,kappa,kappa,1.5*kappa])),
    ('time_space_unequal_plus_conformal',np.diag([-kappa,kappa,kappa,1.5*kappa])+.21*eta)
]:
    eps=1e-6
    def index(t,x,z):
        g=eta+2*t*pi(x,z)*K
        return np.sqrt(g[3,3]/(-g[0,0]))
    for x,z in [(b,0),(.5,1),(2,-.4)]:
        assert np.isclose((index(eps,x,z)-index(-eps,x,z))/(2*eps),linear_n(K,x,z),atol=1e-10)
    if name=='umbilic':
        assert optical(K)==0 and u@K@u!=0
    if name=='time_space_unequal':
        expected=optical(K)
        assert np.isclose(expected,-b*np.exp(-b*b/2)*np.sqrt(2*np.pi)*.5*kappa)
    if name=='time_space_unequal_plus_conformal':
        assert np.isclose(optical(K),expected,atol=1e-15)

# A nonhomogeneous collar check: matching total unweighted force derivative
# does not match its weighted projection. A toy odd-gradient density h(rho)
# integrates to zero before varying the collar; the geometric Jacobian
# derivative per volume d*kappa/(1+kappa*rho) is varying across depth.
# This is an identifiable missing moment, not a chosen physical h.
def shape_measure(rho):return 4*kappa/(1+kappa*rho)
h=lambda rho:2*rho-1
assert abs(quad(h,0,1)[0])<1e-15
weighted=quad(lambda rho:shape_measure(rho)*h(rho),0,1,epsabs=1e-13)[0]
assert weighted<0
rows={'trace_only_dust_coefficient_per_density':-kappa,
      'trace_only_ray_impulse':optical(kappa*eta),
      'nonconformal_fixture_ray_impulse':expected,
      'illustrative_collar_moment':weighted,
      'applied_to_jackpot':False}
(Path(__file__).resolve().parent/'jackpot_boundary_matter_readout.json').write_text(json.dumps(rows,indent=2)+'\n')
print(rows)
