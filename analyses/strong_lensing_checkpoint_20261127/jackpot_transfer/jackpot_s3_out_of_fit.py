"""Two frozen continuations of the local template; circular primary and bounded intermediate terms."""
from pathlib import Path
import json, numpy as np
P=Path(__file__).resolve().parent
s=P/'jackpot_equilibrium_calibration.py'
e={'__file__':str(s),'__name__':'cal'}
exec(compile(s.read_text().split('out=dict(scope=',1)[0],str(s),'exec'),e)
D,z=e['D'],e['z']
R0,R1=e['ang']
L=np.log(R1/R0)
w=lambda a,b:D(a,b)/D(0,b)
z1,z2,z3=.609,2.035,5.975
s1=.16*w(z1,z3)/w(z1,z2)
s2=4*np.pi*(150/e['speed'])**2/e['xrad']*w(z2,z3)
# Freeze tangent power-law at either edge (C^1 at joins) as primary option.
# The unchanged log-quadratic is a local extrapolation sensitivity control only.
template=json.loads((P/'jackpot_settled_envelope_template.json').read_text())['shape']
obs=json.loads((P/'s3_stellar_transfer.json').read_text())
th=np.array(obs['image_offsets_arcsec'])
r=np.linalg.norm(th,axis=1)
def run(label,ms,law,eta):
    record=template[label]; a=record['A_Msun']
    q,c=map(record['targets'][str(eta)].get,('p','c'))
    def f(r):
        x=np.log(r/R0)
        if law=='tangent' and x<0: return a*np.exp(q*x)
        if law=='tangent' and x>L: return a*np.exp(q*L+c*L*L+(q+2*c*L)*(x-L))
        return a*np.exp(q*x+c*x*x)
    assert np.isclose(f(R1)+e['stars'](R1,ms),e['M2'])
    assert np.isclose(f(R0)+e['stars'](R0,ms),e['M1'])
    mass=np.array([f(t)+e['stars'](t,ms) for t in r]); fac=R0**2/e['M1']*w(z,z3)/w(z,z1)
    beta=th*(1-fac*mass/r**2)[:,None]
    pair=beta[0]-beta[1]
    gap=float(np.linalg.norm(pair))
    u=th[0]/r[0]
    transverse=float(np.linalg.norm(pair-np.dot(pair,u)*u))
    # No positions assumed: reduced SIS kick norm per ray is bounded by its Einstein angle
    # even when the upstream deflection changes where that ray hits the later plane.
    floor=max(0.,gap-2*(s1+s2))
    # Nominal concentric S1/S2 sensitivity; their actual source-plane centers need not coincide.
    def trace(t,M):
        kick0=(R0**2/e['M1'])*M/np.dot(t,t)/w(z,z1)*t
        x1=t-w(z,z1)*kick0
        u1=x1/np.linalg.norm(x1)
        x2=t-w(z,z2)*kick0-.16*u1
        u2=x2/np.linalg.norm(x2)
        x3=t-w(z,z3)*kick0-s1*u1
        return x3,x3-s2*u2
    t=np.array([trace(d,m) for d,m in zip(th,mass)])
    return dict(law=law,eta=eta,stellar=label,primary_pair_arcsec=gap,primary_pair_transverse_to_outer_ray_arcsec=transverse,post_SIS_floor_arcsec=floor,
                concentric_s1_arcsec=float(np.linalg.norm(t[0,0]-t[1,0])),
                concentric_s1_s2_arcsec=float(np.linalg.norm(t[0,1]-t[1,1])),
                mass_Msun_at_rays=mass.tolist())
out=dict(assumptions='Use S1 0.16 arcsec Einstein angle to S2; S2 optionally 150 km/s. Circular primary held fixed; no actual intermediate centroids, ellipticity, external shear, or MUSE model covariance included.',
s1_reduced_arcsec_s3=s1,s2_150kms_reduced_arcsec_s3=s2,
runs=[run(l,m,k,eta) for l,m in [('Chabrier',[10.85,11.27]),('Salpeter',[11.13,11.52])] for k in ('tangent','logquad') for eta in (.93,.96)])
for a in out['runs']:
    assert a['concentric_s1_s2_arcsec']>=a['post_SIS_floor_arcsec']-1e-12
(P/'jackpot_s3_out_of_fit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
