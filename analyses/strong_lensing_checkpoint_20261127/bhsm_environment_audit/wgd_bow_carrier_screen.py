"""Stationary local WGD R1 cone control; not a physical coupled shock model."""
from pathlib import Path
import json,math
import numpy as np
p=Path(__file__).resolve().parent
owned=p.parent/'wgd_frozen_transfer/wgd_frozen_transfer.py'
ns={'__file__':str(owned)}
exec(compile(owned.read_text().split('\nruns={}',1)[0],str(owned),'exec'),ns)
c=ns['speed']; L=ns['L']; G=ns['G']; a=ns['a']; bg=ns['bg']; sol=ns['bgsol']; lam=bg.LAMBDA
cases=[]
for z in [.230,.2283]:
 N=-math.log1p(z); y=sol.sol(N); v,H=float(y[1]),float(y[2])
 b,C,eps,_=ns['cfs'](z)
 D=1+12*H*v/lam+6*v**4/lam**2
 d=D/C
 assert 0<d<1.5
 for masslog in [11.57,11.82]:
  m=G*10**masslog/c**2
  rows=[]
  for r in [0.001,0.01,.1,.5,1,2,5,20,200,2000]:
   rM=r*a; mu,n=ns['sersic'](r)
   assert 0<=n<3
   S=math.sqrt(C*C+16*b*m*mu*L*L/(lam*rM**3))
   q=(S*S-C*C)*(n-3)/(2*S)
   KR,KA,KT=S,S+q/2,D+1.5*(S-C)+q/2
   assert KT>0 and KR/KT>=2/3 and KA/KT>=1/3
   rows.append(dict(r_over_circRe=r,r_kpc=1000*rM,nM=n,Kt=KT,
                    c_radial_squared_over_c_squared=KR/KT,c_tangent_squared_over_c_squared=KA/KT))
  cases.append(dict(z=z,logM=masslog,b=b,C=C,D=D,D_over_C=d,asymptotic_c_t_over_c=math.sqrt(1/d),
     sampled_min_cone_speed_over_c=math.sqrt(min(min(x['c_radial_squared_over_c_squared'],x['c_tangent_squared_over_c_squared']) for x in rows)),
     nodes=rows))
out=dict(scope="Retained PR23 local static weak-field screened principal symbol with proper time and orthonormal physical space. Carrier is R1 T only, not BHSM qD or full IF5. Monotone spherical density and regular Kt. No WGD relative speed measurement or shock selected.",
   analytic_lower_any_direction_over_c=1/math.sqrt(3),analytic_lower_radial_over_c=math.sqrt(2/3),examples=cases)
(p/'wgd_bow_carrier_screen.json').write_text(json.dumps(out,indent=2)+'\n')
for c1 in cases: print({k:v for k,v in c1.items() if k!='nodes'})
