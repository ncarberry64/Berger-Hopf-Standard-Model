"""CA14 q and shear robustness screen of frozen circular aperture calibration."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
P=Path(__file__).resolve().parent
s=P/'jackpot_s3_out_of_fit.py'
e={'__file__':str(s),'__name__':'test'}
exec(compile(s.read_text().split('out=dict(assumptions=',1)[0],str(s),'exec'),e)
th,r,R0,R1,L=(e[k] for k in ('th','r','R0','R1','L'))
j,D,z,w,z1,z2,z3=(e[k] for k in ('e','D','z','w','z1','z2','z3'))
norm=R0**2/j['M1']; w3=w(z,z3)/w(z,z1)
b1=.161*w(z1,z3)/w(z1,z2)
b2=lambda v:4*np.pi*(v/j['speed'])**2/j['xrad']*w(z2,z3)
pats={'PA east of north':lambda a:90-a,'angle from east':lambda a:a,
      'PA east of north, reflected RA':lambda a:90+a,'angle from west':lambda a:180-a}
def matrix(a):
    a=np.radians(a)
    return np.array([[np.cos(a),np.sin(a)],[-np.sin(a),np.cos(a)]])
def stage1(r,label,ms):
    item=e['template'][label]
    A=item['A_Msun']
    p0,c=map(item['targets']['0.96'].get,('p','c'))
    x=np.log(r/R0)
    f=p0*x+c*x*x
    k=p0+2*c*x
    if x<0:f,k=p0*x,p0
    if x>L:f,k=p0*L+c*L*L+(p0+2*c*L)*(x-L),p0+2*c*L
    a,t=j['a'],j['t']
    dstar=np.sum(10**np.asarray(ms)*r*(1/np.hypot(r,a)-1/np.hypot(r,t))/(t-a))
    return norm*(dstar+A*np.exp(f)*k/r)/(2*r)
def ell(t,q,phi,K):
    U=matrix(phi); X,Y=U@t
    def vgeom(v):
        u=v**4
        Z=1-(1-q*q)*u
        return np.sqrt(q*u*(X*X+Y*Y/Z)),Z
    def integ(v,k):
        rr,Z=vgeom(v)
        return 4*v**3*K(rr)/Z**(k+.5)
    pts=[brentq(lambda v:vgeom(v)[0]-ri,0,1) for ri in (R0,R1) if ri<vgeom(1)[0]]
    return q*U.T@np.array([X*quad(integ,0,1,args=(0,),points=pts,epsabs=1e-10)[0],
                            Y*quad(integ,0,1,args=(1,),points=pts,epsabs=1e-10)[0]])

def pair(u):return float(np.linalg.norm(u[0]-u[1]))
def trace(a,disp=60):
    x1=th-a
    u1=x1/np.linalg.norm(x1,axis=1)[:,None]
    x2=th-w(z,z2)/w(z,z1)*a-.161*u1
    u2=x2/np.linalg.norm(x2,axis=1)[:,None]
    return pair(th-w3*a-b1*u1-b2(disp)*u2)
out={}
for label,ms in [('Chabrier',[10.85,11.27]),('Salpeter',[11.13,11.52])]:
    K=lambda r:stage1(r,label,ms)
    A=lambda q,phi:np.array([ell(t,q,phi,K) for t in th])
    circ=A(1,0)
    assert abs(pair(th-w3*circ)-e['run'](label,ms,'tangent',.96)['primary_pair_arcsec'])<1e-7
    row={}
    for tag,f in pats.items():
        ea=A(.946,f(30.6))
        gr=matrix(f(-27.20))
        gr=gr.T@np.diag([.069,-.069])@gr
        a=ea+th@gr
        row[tag]={'ellipticity_only':pair(th-w3*ea),'with_shear':pair(th-w3*a),'with_centered_S1_and_S2_60':trace(a),
                  'with_centered_S1_and_S2_150':trace(a,150)}
    # Orientation-agnostic bounded scan: minimum over the shear angle at each
    # ellipse orientation is the norm difference for the fixed-length shear kick.
    dv=th[0]-th[1]
    shear_length=w3*.069*np.linalg.norm(dv)
    gaps=np.array([pair(th-w3*A(.946,ang)) for ang in np.linspace(0,180,91)])
    lower=float(np.min(abs(gaps-shear_length)))
    out[label]=dict(circular=pair(th-w3*circ),conventions=row,nominal_q_all_angles_sampled_min_before_S1_S2=lower,
        same_minus_arbitrary_SIS_kick_bound_S2_60=max(0.,lower-2*(b1+b2(60))),
        shear_difference_arcsec=shear_length)
(P/'jackpot_s3_lens_geometry.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
