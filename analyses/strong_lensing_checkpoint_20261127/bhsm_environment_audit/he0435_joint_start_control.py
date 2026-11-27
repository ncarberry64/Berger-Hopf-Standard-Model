"""Exact elliptic-start and non-superposition diagnostic, not a joint solve."""
import contextlib,io,json,math
from pathlib import Path
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
 from he0435_joint_field_control import m,d1,z1,bg,L,G,speed as c,xrad,cfs
p=Path(__file__).resolve().parent
# Direction arbitrary for the axisymmetric two-center case; real projected separation as proxy.
D=d1*67.1*xrad
C,b,la=m.C,m.b,bg.LAMBDA
s=470.; rt=math.sqrt(2)*s/(10*c/L*cfs(z1)[3])
def stars(r):
 mu,n=m.sphere(r/m.a)
 return 10**11.1*mu,n
def group(r,rc):
 M=lambda v:2*s*s/G*(v-rc*math.atan(v/rc))
 if r>=rt:return M(rt),0.
 mass=M(r); return mass,(2*s*s/G)*r*(r*r/(r*r+rc*rc))/mass
I=np.eye(3)
def H(x,model):
 r=np.linalg.norm(x); nvec=x/r
 M,n=model(r); y=r/L; mn=G*M/c**2/L
 q=16*b*mn/(la*C*C*y**3)
 S=math.sqrt(1+q)
 T=-C*la/8*(q/(S+1))
 R=T-C*la/8*q*(n-3)/(2*S)
 return T*I+(R-T)*np.outer(nvec,nvec),-b*n*mn/y**3
def op(H):
 tr=np.trace(H);return C*tr-(2/la)*(tr*tr-np.sum(H*H))
def A(H):return C*I-4/la*(np.trace(H)*I-H)
rows=[]
for core in [10,20,40]:
 corners=[]
 for x,z in [(7,0),(7,7),(50,30),(D*1000/2,50),(D*1000/2,0),(D*1000+20,0)]:
  X=np.array([x/1000,z/1000,0])
  h1,j1=H(X,stars);h2,j2=H(X-np.array([D,0,0]),lambda r:group(r,core/1000))
  assert abs(op(h1)-j1)<1e-10*max(1,abs(j1))
  assert abs(op(h2)-j2)<1e-10*max(1,abs(j2))
  j=j1+j2
  cross=op(h1+h2)-j
  analytic=-4/la*(np.trace(h1)*np.trace(h2)-np.sum(h1*h2))
  assert abs(cross-analytic)<1e-10*max(1,abs(j))
  mineig=np.linalg.eigvalsh(A(h1+h2))[0]/C
  assert mineig>=math.sqrt(3)-1-1e-13
  corners.append(dict(x_z_kpc=[x,z],relative_sum_residual=cross/max(abs(j),1e-30),min_principal_over_C=mineig))
 rows.append(dict(group_core_assumed_kpc=core,samples=corners))
o=dict(scope=__doc__,group_sep_Mpc=D,nominal_r200_Mpc=rt,exact_combined_start_eigen_lower_over_C=math.sqrt(3)-1,results=rows)
(p/'he0435_joint_start_control.json').write_text(json.dumps(o,indent=2)+'\n')
print(json.dumps(rows[1],indent=2))
