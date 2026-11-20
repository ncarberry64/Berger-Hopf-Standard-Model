"""Exact known radial columns 0,1,3 only. No omission-based solve."""
import numpy as np,json
from pathlib import Path
from scipy.special import eval_jacobi,gammaln
p=Path(__file__).parent
ns={'__file__':str(p/'materialize_radial_graph_coefficients.py')}
exec((p/'materialize_radial_graph_coefficients.py').read_text().split('records=[]')[0],ns)
coeff=ns['coeff'];WALL=np.pi/2;alpha=(np.sqrt(45)-3)/2;norm=.0003208119454588855
def basis(rho):
 x=rho/WALL;cols=[]
 for j in range(2):
  a=2.;b=4+2*alpha;ln=gammaln(j+a+1)+gammaln(j+b+1)-gammaln(j+1)-gammaln(j+a+b+1)-np.log(2*j+a+b+1)
  cols.append(x**alpha*(1-x)*np.exp(-ln/2)*eval_jacobi(j,a,b,2*x-1))
 return np.column_stack(cols+[x**alpha])
results=[];arrays={}
for side in ['incoming','outgoing']:
 z=np.load(p/(side+'_history.npz'))
 for label in ['lo','q000','q001','q002','q003','hi']:
  raw=z[label+'_raw_fields'];mats=[]
  for order in [96,192,384]:
   x,w=np.polynomial.legendre.leggauss(order);rho=(x+1)*WALL/2;w=w*WALL/2;B=basis(rho);c=coeff(raw,rho);cs=coeff(raw,rho,s=raw[98]+1e-20j).imag/1e-20
   M=B.T@((norm*w*c[:,0])[:,None]*B);Ms=B.T@((norm*w*cs[:,0])[:,None]*B)
   mats.append((M,Ms))
  M,Ms=mats[1];arrays[side+'_'+label+'_kinetic_known']=M;arrays[side+'_'+label+'_shape_derivative']=Ms
  results.append(dict(side=side,label=label,wall_wall=float(M[-1,-1]),min_eigenvalue=float(np.linalg.eigvalsh(M)[0]),wall_wall_shape_derivative=float(Ms[-1,-1]),quadrature_192_384_max=float(max(np.max(abs(a-b)) for a,b in zip(mats[1],mats[2])))))
np.savez(p/'known_radial_kinetic_blocks.npz',**arrays)
out=dict(scope='electric kinetic principal block in original radial indices0,1,3; not inverse, not full response',missing_index2='actual affine profile complement; never replaced with polynomial',records=results,physical_moment=None)
(p/'KNOWN_RADIAL_KINETIC_BLOCKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
