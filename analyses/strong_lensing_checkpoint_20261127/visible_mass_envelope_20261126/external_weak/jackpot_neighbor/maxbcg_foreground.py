"""Sensitivity, not a fitted lens. No parameters fitted to Jackpot."""
import numpy as np
from scipy.integrate import quad
import json
c=299792.458; G=4.300917270e-6; asr=206264.806247
zl=.2219305
zlens=zl
zp=.14228
p=np.array([506.620,-132.103])
T=np.array([[-3.,-1.91],[1.03,.87]])
diff=T[0]-T[1]
def E(z): return np.sqrt(.3*(1+z)**3+.7)
def chi(z):return c/70*quad(lambda q:1/E(q),0,z)[0]
def calc(zs,M,conc=None):
    dl=chi(zp)/(1+zp)*1000
    f=1-chi(zp)/chi(zs)
    coef=4*G*M*f*asr**2/(c*c*dl)
    r200=(G*M/(100*(70*E(zp)/1000)**2))**(1/3)
    rs=r200/conc if conc else None
    def alpha(t):
        v=t-p; rr=np.linalg.norm(v,axis=-1)
        factor=1
        if conc:
            x=(rr/asr*dl)/rs
            # all evaluations at x>1; g is analytic projected NFW cumulative.
            assert np.all(x>1)
            factor=(np.log(x/2)+np.arccos(1/x)/np.sqrt(x*x-1))/(np.log(1+conc)-conc/(1+conc))
        return (coef*factor/rr**2)[...,None]*v
    eps=.01*np.eye(2)
    J=((alpha(eps)-alpha(-eps))/.02).T
    k=np.trace(J)/2
    shear=np.hypot(J[0,0]-k,J[0,1])
    delta=alpha(T[0])-alpha(T[1])
    w1=1-chi(zl)/chi(.609)
    bmain=1.43*(1-chi(zl)/chi(zs))/w1
    beta=(1-chi(zp)/chi(zl))/f
    def main(t): return bmain*t/np.linalg.norm(t,axis=-1)[...,None]
    def bend(use_affine):
        a=T@J.T if use_affine else alpha(T)-alpha(np.zeros(2))
        return a+main(T-beta*a)-main(T)
    exact,linear=map(bend,(False,True))
    return dict(mass=M,c=conc,kappa=k,shear=shear,raw_mas=1e3*np.linalg.norm(delta),
                nonaffine_mas=1e3*np.linalg.norm(delta-J@diff),jacobian=J.tolist(),pair_raw_vector_mas=(1e3*delta).tolist(),virial_kpc=r200,
                impact_kpc=np.linalg.norm(p)/asr*dl,beta=beta,
                two_plane_illustrative_raw_mas=1e3*np.linalg.norm(exact[0]-exact[1]),
                two_plane_nonaffine_mas=1e3*np.linalg.norm((exact-linear)[0]-(exact-linear)[1]))
M=8.794e13*(15/20)**1.28/.7
out={z:[calc(z,m,C) for m in [M/2,M,M*2] for C in [None,3,5,8]] for z in [.609,2.035,5.975]}
with open('maxbcg_foreground.json','w') as f:json.dump(out,f,indent=2)
for row in out[5.975][4:8]: print(row)
print('max at twice central mass',max(r['two_plane_nonaffine_mas'] for r in out[5.975]))
