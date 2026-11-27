"""Causal steady-drive versus pulse control; no lensing fit and no physical time unit."""
from pathlib import Path
import json
import numpy as np
P=Path(__file__).resolve().parent
a,b=json.loads((P/'jackpot_equilibrium_calibration.json').read_text())['apertures_kpc']
L=18.0; c=1.; qback=2.0
def solve(n,drive='step',outer='reservoir',choke=True):
    dx=L/n
    centers=(np.arange(n)+.5)*dx
    t=np.clip((centers-a)/(b-a),0,1)
    g=.35*(1+(3 if choke else 0)*16*t*t*(1-t)**2)
    gam=np.sum(g)*dx
    end=800 if outer=='closed' else 180
    m=int(np.ceil(end/(.8*dx/c)))
    dt=end/m
    # q is perturbation of a positive reference stock per radial length.
    # q_t+F_x=0, F_t+c²q_x=-g F; use characteristic face flux and split damping.
    q=np.zeros(n); F=np.zeros(n)
    ring=np.argmin(abs(centers[:,None]-np.array([a,b])),axis=0)
    cumulative=0.; arrivals=[None,None]; peak=[0.,0.]
    max_budget=0.; min_stock=qback
    for k in range(m):
        tau=(k+.5)*dt
        q_left=-1. if drive=='step' or (drive=='pulse' and tau<8) else 0.
        damp=np.exp(-.5*dt*g)
        F*=damp
        plus=F+c*q; minus=F-c*q
        pp=np.r_[minus[0]+2*c*q_left,plus]
        mm=np.r_[minus,-plus[-1] if outer=='closed' else plus[-1]]
        # Boundary supplies incoming characteristic: pressure/stock fixed
        # at the reservoir, flux zero at a sealed edge.
        fq=.5*(pp+mm)
        fF=.5*c*(pp-mm)
        q-=dt/dx*np.diff(fq)
        F=(F-dt/dx*np.diff(fF))*damp
        cumulative+=dt*(fq[0]-fq[-1])
        max_budget=max(max_budget,abs(np.sum(q)*dx-cumulative))
        min_stock=min(min_stock,float(np.min(q)+qback))
        for i,j in enumerate(ring):
            peak[i]=max(peak[i],abs(float(F[j])))
            if arrivals[i] is None and abs(F[j])>.15:arrivals[i]=(k+1)*dt
    target=-c*c/gam if drive=='step' and outer=='reservoir' else 0.
    return dict(ring_threshold_crossing_normalized=arrivals,ring_R_over_c=[a/c,b/c],peak_abs_ring_flux=peak,
        late_ring_F=F[ring].tolist(),expected_late_F=target,
        final_stock_perturbation=float(q.sum()*dx),net_in_minus_out=cumulative,
        max_stock_budget_defect=max_budget,minimum_positive_stock=min_stock,
        final_band_mean_stock_perturbation=float(np.mean(q[(centers>=a)&(centers<=b)])))
cases=[('sustained_open','step','reservoir',True),('pulse_open','pulse','reservoir',True),
       ('sustained_closed','step','closed',True),('sustained_no_band','step','reservoir',False),
       ('no_drive','zero','reservoir',True)]
out={k:{str(n):solve(n,d,o,h) for n in (360,720)} for k,d,o,h in cases}
for k,rs in out.items():
    for v in rs.values():
        assert v['max_stock_budget_defect']<3e-10 and v['minimum_positive_stock']>0
        assert np.allclose(v['late_ring_F'],v['expected_late_F'],atol=2e-4)
for k in ('sustained_open','pulse_open'):
    v=out[k]['720']
    assert v["ring_threshold_crossing_normalized"][0]<v["ring_threshold_crossing_normalized"][1]
assert abs(out['sustained_open']['720']['expected_late_F'])<abs(out['sustained_no_band']['720']['expected_late_F'])
assert out['no_drive']['720']['peak_abs_ring_flux']==[0.,0.]
(P/'jackpot_central_drive.json').write_text(json.dumps(out,indent=2)+'\n')
for k,v in out.items():print(k,v['720'])
