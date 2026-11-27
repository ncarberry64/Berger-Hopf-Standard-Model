"""Frozen retained R1: WGD independent photometric input / conditional spherical control."""
from pathlib import Path
import hashlib,json,math,sys
from functools import lru_cache
from scipy.integrate import quad
from scipy.special import gammainc,gammaincinv,gammaln
import numpy as np
p=Path(__file__).resolve().parents[2]/'wgd_frozen_transfer'
src=p/'pr23'
sys.path.insert(0,str(src/'code'))
import background as bg
manifest=json.loads((src/'preregistration/prediction_manifest.json').read_text())['background_R1']
for name,array in [('Omega_m0',bg.OMEGA_M0),('Omega_r0',bg.OMEGA_R0),('Omega_k0',bg.OMEGA_K0),('lambda',bg.LAMBDA),('q',bg.Q)]:
 assert manifest[name]==array
bgsol=bg.integrate(manifest['V0_over_Mpl2H02']); assert bgsol.success
H0=67.4; speed=299792.458; G=4.300917270036279e-9
L=speed/H0; xrad=math.pi/(180*3600)
def cfs(z):
 N=-math.log1p(z); y=bgsol.sol(N)
 v,H=float(y[1]),float(y[2]); d=H*bg.rhs(N,y)[1]
 l=bg.LAMBDA; b=2*v*v/l; C=1+4*(d+2*H*v)/l-2*v**4/l**2
 return b,C,b*b/(2*C),H
def D(z1,z2):
 chi=quad(lambda z:1/float(bgsol.sol(-math.log1p(z))[2]),z1,z2,epsabs=2e-13)[0]
 a=math.sqrt(-bg.OMEGA_K0)
 return L*math.sin(a*chi)/(a*(1+z2))
b0,C0,e0,_=cfs(.3); rv0=(16*b0*(G*1e11/speed**2)*L**2/(bg.LAMBDA*C0*C0))**(1/3)
ref=json.loads((src/'artifacts/strong_lensing_r1_screened_20261020/review/r1_qs_coefficients.json').read_text())
assert abs(rv0/ref['prediction']['rV_Mpc']-1)<1e-10 and abs(e0/ref['prediction']['unscreened_mu_minus_one']-1)<1e-10
