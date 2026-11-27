"""Independent numerical verification of the centered exponential null."""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from jackpot_moving_pin_history import run

def closed(x,t):
    p=np.exp(-t)
    return np.exp(-1j*p*x)*(1-p+p/(1-1j*x))
def explicit_integral(x,t):
    p=np.exp(-t)
    integrals=[quad(lambda u:np.exp(-u)*f(x*u),0,100,epsabs=2e-13)[0] for f in [np.cos,np.sin]]
    return np.exp(-1j*p*x)*(1-p+p*complex(*integrals))
for x in [0,.003,.01,.1,.3,1,3]:
    for t in [0,.1,1.,3.]:
        z=closed(x,t)
        assert abs(z-explicit_integral(x,t))<1e-12
        assert abs(np.imag(z))<=abs(x)**3/3+1e-13 if t==0 else True
        if x==.003:
            p=np.exp(-t)
            assert np.isclose(abs(np.imag(z))/x**3,p-p*p+p**3/3,rtol=1e-5)
vel=[.04,.02,.01,.005]
rr=[run(96,24,v,.1,uniform_centered=True) for v in vel]
rvar=[run(96,24,v,.1) for v in vel]
def powers(out,key='odd'):
    v=[it[key] for it in out]
    return np.log2(np.array(v[:-1])/v[1:])
pow1,pow2=powers(rr),powers(rvar)
assert np.allclose(pow1,3,rtol=.025)
assert np.allclose(pow2,1,rtol=.025)
clean='after_independent_shifts'
assert np.allclose(powers(rr,clean),3,rtol=.025)
assert np.allclose(powers(rvar,clean),1,rtol=.025)
res=dict(single_mode_at_x_0p3=[abs(closed(.3,t).imag) for t in [0,1,3]],
    velocities=vel,uniform_centered=rr,earlier_scale_dependent_unrecentered=rvar,
    uniform_centered_power=pow1.tolist(),earlier_unrecentered_power=pow2.tolist(),
    uniform_after_nuisance_power=powers(rr,clean).tolist(),
    scale_dependent_after_nuisance_power=powers(rvar,clean).tolist())
(Path(__file__).parent/'jackpot_wake_centered_control.json').write_text(json.dumps(res,indent=2)+'\n')
print(res)
