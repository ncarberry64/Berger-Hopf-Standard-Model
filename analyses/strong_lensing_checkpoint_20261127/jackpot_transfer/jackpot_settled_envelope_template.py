"""Local calibration surrogate only; does not fit source 3 or HE 0435."""
import json, numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
src=P/'jackpot_equilibrium_calibration.py'
env={'__file__':str(src),'__name__':'calibration'}
exec(compile(src.read_text().split('out=dict(scope=',1)[0],str(src),'exec'),env)
r0,r1=env['ang']; M1,M2=env['M1'],env['M2']
sol={}
for label,ms in [('Chabrier',[10.85,11.27]),('Salpeter',[11.13,11.52])]:
    a,t=env['a'],env['t']
    z=10**np.array(ms)/(t-a)
    stellar=lambda r:env['stars'](r,ms)
    s1=np.sum(z*r0*(1/np.hypot(r0,a)-1/np.hypot(r0,t)))
    s2=np.sum(z*(a*a/np.hypot(r0,a)**3-t*t/np.hypot(r0,t)**3))
    A=M1-stellar(r0)
    L=np.log(r1/r0)
    n=np.log((M2-stellar(r1))/A)/L
    def solve(eta):
        # M_env=A exp(p*x+c*x*x), p=n-c*L.
        # Mtot_x = r0*s1+A*p; Mtot_xx = r0*s1+r0^2*s2 + A*(p^2+2*c).
        # xi=2*(eta-1)= (Mtot_xx-3*Mtot_x+2*M1)/(M1-Mtot_x/2).
        xi=2*(eta-1)
        a0=r0*s1
        a1=a0+r0*r0*s2
        assert L>0
        B= -3-2/L+xi/2
        C=(a1+(-3+xi/2)*a0+(2-xi)*M1)/A+2*n/L
        roots=np.sort(np.roots([1,B,C]))
        p=float(min(roots,key=lambda x:abs(x-n)))
        c=(n-p)/L
        Mx=a0+A*p
        Mxx=a1+A*(p*p+2*c)
        assert np.isclose(1+.5*(Mxx-3*Mx+2*M1)/(M1-Mx/2),eta)
        assert np.allclose([stellar(r)+A*np.exp(p*x+c*x*x) for r,x in [(r0,0),(r1,L)]],[M1,M2])
        assert min(p,p+2*c*L)>0
        return dict(p=p,c=c,outer_log_slope=p+2*c*L,other_algebraic_root=float(max(roots,key=lambda x:abs(x-n))))
    sol[label]=dict(A_Msun=A,mean_log_slope=n,targets={str(e):solve(e) for e in (.93,.94,.96,.98)})
out=dict(fit_range_arcsec=[r0,r1],total_mass_Msun=[M1,M2],shape=sol,
         holdout_radii_arcsec=json.loads((P/'s3_stellar_transfer.json').read_text())['image_radii_arcsec'],
         holdout_scored=False,scope='Local projected surrogate. Model summaries are correlated. No exterior extension selected; no underlying 3D metric or equilibrium calculated.')
(P/'jackpot_settled_envelope_template.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
